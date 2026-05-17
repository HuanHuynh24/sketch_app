import argparse
import io
import hashlib
import json
import re
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import httpx
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, init_schema
from app.models.admission_raw_document import AdmissionRawDocument
from app.models.admission_source import AdmissionSource
from app.models.university import University
from app.services.text_cleaner import clean_text
from app.services.vector_index_service import index_latest_documents


DEFAULT_TIMEOUT = 30.0
USER_AGENT = "SketchAppAdmissionIngest/0.1"


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._skip_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str):
        if tag in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str):
        if not self._skip_depth:
            text = data.strip()
            if text:
                self._parts.append(text)

    def text(self) -> str:
        return normalize_text(" ".join(self._parts))


def normalize_text(value: str) -> str:
    return clean_text(value) or ""


def extract_html_text(html: str) -> str:
    parser = TextExtractor()
    parser.feed(html)
    return parser.text()


def extract_title(html: str) -> str | None:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)

    if not match:
        return None

    return normalize_text(re.sub(r"<[^>]+>", "", match.group(1)))


def is_json_content_type(content_type: str | None) -> bool:
    if not content_type:
        return False

    media_type = content_type.lower().split(";", maxsplit=1)[0].strip()
    return media_type == "application/json" or media_type.endswith("+json")


def extract_json_string_text(value: str) -> str:
    if "<" in value and ">" in value:
        text = extract_html_text(value)
    else:
        text = normalize_text(value)

    return normalize_text(re.sub(r"\[[^\]]+\]", " ", text))


def extract_json_text(value: Any) -> str:
    parts: list[str] = []

    def collect(item: Any) -> None:
        if isinstance(item, dict):
            for child in item.values():
                collect(child)
            return

        if isinstance(item, list):
            for child in item:
                collect(child)
            return

        if isinstance(item, str):
            text = extract_json_string_text(item)
            if text:
                parts.append(text)

    collect(value)
    return normalize_text(" ".join(parts))


def extract_json_title(value: Any) -> str | None:
    item = value[0] if isinstance(value, list) and value else value

    if not isinstance(item, dict):
        return None

    for key in ("title", "name", "slug"):
        candidate = item.get(key)

        if isinstance(candidate, dict):
            rendered = candidate.get("rendered")
            if isinstance(rendered, str):
                return extract_json_string_text(rendered)

        if isinstance(candidate, str):
            return extract_json_string_text(candidate)

    return None


def extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    parts = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)

    return normalize_text(" ".join(parts))


def read_source_file(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Source file must be a JSON array")

    return data


def upsert_university(db: Session, item: dict[str, Any]) -> University:
    code = item["university_code"].strip()
    university = (
        db.query(University)
        .filter(University.code == code)
        .first()
    )

    if university is None:
        university = University(code=code, name=item["university_name"].strip())
        db.add(university)

    university.name = item["university_name"].strip()
    university.type = item.get("type")
    university.province = item.get("province")
    university.region = item.get("region")
    university.website = item.get("website")
    university.admission_url = item.get("admission_url")
    university.source_url = item.get("source_url")
    university.source_year = item.get("source_year")

    db.commit()
    db.refresh(university)

    return university


def upsert_source(
    db: Session,
    university: University,
    source_item: dict[str, Any],
) -> AdmissionSource:
    url = source_item["url"].strip()
    document_type = source_item.get("document_type", "admission_page")
    year = source_item.get("year")

    source = (
        db.query(AdmissionSource)
        .filter(
            AdmissionSource.university_id == university.university_id,
            AdmissionSource.url == url,
            AdmissionSource.document_type == document_type,
            AdmissionSource.year == year,
        )
        .first()
    )

    if source is None:
        source = AdmissionSource(
            university_id=university.university_id,
            url=url,
            document_type=document_type,
            year=year,
        )
        db.add(source)

    source.title = source_item.get("title")
    source.status = "pending"
    source.error_message = None

    db.commit()
    db.refresh(source)

    return source


def fetch_source(client: httpx.Client, source: AdmissionSource) -> httpx.Response:
    response = client.get(source.url, follow_redirects=True)
    response.raise_for_status()
    return response


def build_raw_document(source: AdmissionSource, response: httpx.Response) -> dict[str, Any]:
    content = response.content
    content_type = response.headers.get("content-type")
    content_hash = hashlib.sha256(content).hexdigest()
    text = None
    title = None

    if content_type and "application/pdf" in content_type.lower():
        text = extract_pdf_text(content)
    elif is_json_content_type(content_type):
        payload = response.json()
        text = extract_json_text(payload)
        title = extract_json_title(payload)
    elif content_type and "text/html" in content_type.lower():
        html = response.text
        text = extract_html_text(html)
        title = extract_title(html)
    elif content_type and "text/" in content_type.lower():
        text = normalize_text(response.text)

    return {
        "url": str(response.url),
        "content_type": content_type,
        "content_hash": content_hash,
        "content_size": len(content),
        "content_text": text,
        "metadata_json": {
            "source_url": source.url,
            "final_url": str(response.url),
            "http_status": response.status_code,
            "title": title,
        },
    }


def save_raw_document(
    db: Session,
    source: AdmissionSource,
    document_data: dict[str, Any],
    skip_duplicates: bool,
) -> bool:
    if skip_duplicates:
        existing = (
            db.query(AdmissionRawDocument)
            .filter(
                AdmissionRawDocument.source_id == source.source_id,
                AdmissionRawDocument.content_hash == document_data["content_hash"],
            )
            .first()
        )

        if existing:
            source.status = "fetched"
            source.last_fetched_at = datetime.utcnow()
            source.error_message = None
            db.commit()
            return False

    raw_document = AdmissionRawDocument(
        source_id=source.source_id,
        **document_data,
    )
    db.add(raw_document)

    source.status = "fetched"
    source.last_fetched_at = datetime.utcnow()
    source.error_message = None

    db.commit()

    return True


def mark_source_failed(db: Session, source: AdmissionSource, error: Exception) -> None:
    existing_document = (
        db.query(AdmissionRawDocument)
        .filter(AdmissionRawDocument.source_id == source.source_id)
        .first()
    )

    source.status = "fetched" if existing_document else "failed"
    source.last_fetched_at = datetime.utcnow()
    prefix = "Latest fetch failed" if existing_document else "Fetch failed"
    source.error_message = f"{prefix}: {error}"
    db.commit()


def ingest_sources(
    source_file: Path,
    timeout: float,
    skip_duplicates: bool,
    limit: int | None,
    mark_missing_obsolete: bool,
    skip_vector_index: bool,
) -> None:
    init_schema()
    items = read_source_file(source_file)

    if limit is not None:
        items = items[:limit]

    db = SessionLocal()
    headers = {"User-Agent": USER_AGENT}
    active_source_keys: set[tuple[str, str, str, int | None]] = set()

    try:
        for item in items:
            university = upsert_university(db, item)
            sources = item.get("sources", [])

            if not sources:
                print(f"[skip] {university.code}: no sources")
                continue

            for source_item in sources:
                active_source_keys.add(
                    (
                        university.code,
                        source_item["url"],
                        source_item.get("document_type", "admission_page"),
                        source_item.get("year"),
                    )
                )
                source = upsert_source(db, university, source_item)
                verify_ssl = source_item.get("verify_ssl", True)

                try:
                    with httpx.Client(
                        timeout=timeout,
                        headers=headers,
                        verify=verify_ssl,
                    ) as client:
                        response = fetch_source(client, source)
                    document_data = build_raw_document(source, response)
                    inserted = save_raw_document(
                        db=db,
                        source=source,
                        document_data=document_data,
                        skip_duplicates=skip_duplicates,
                    )
                except Exception as exc:
                    mark_source_failed(db, source, exc)
                    print(f"[failed] {university.code} {source.url}: {exc}")
                    continue

                action = "saved" if inserted else "duplicate"
                print(f"[{action}] {university.code} {source.url}")

        if mark_missing_obsolete:
            mark_obsolete_sources(db, active_source_keys)

        if not skip_vector_index:
            stats = index_latest_documents(db)
            print(
                "[vectors] "
                f"documents_seen={stats.documents_seen}, "
                f"documents_indexed={stats.documents_indexed}, "
                f"documents_skipped={stats.documents_skipped}, "
                f"chunks_created={stats.chunks_created}"
            )
    finally:
        db.close()


def mark_obsolete_sources(
    db: Session,
    active_source_keys: set[tuple[str, str, str, int | None]],
) -> None:
    sources = (
        db.query(AdmissionSource)
        .join(University)
        .all()
    )
    obsolete_count = 0

    for source in sources:
        key = (
            source.university.code,
            source.url,
            source.document_type,
            source.year,
        )

        if key in active_source_keys:
            continue

        source.status = "obsolete"
        obsolete_count += 1

    db.commit()
    print(f"[obsolete] marked {obsolete_count} sources not present in source file")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch official admission source pages and save raw documents to DB.",
    )
    parser.add_argument(
        "--source-file",
        type=Path,
        required=True,
        help="Path to a JSON source list.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="HTTP timeout in seconds.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional number of universities to ingest.",
    )
    parser.add_argument(
        "--allow-duplicates",
        action="store_true",
        help="Save a raw document even when the same content hash already exists.",
    )
    parser.add_argument(
        "--mark-missing-obsolete",
        action="store_true",
        help="Mark DB sources not present in the source file as obsolete.",
    )
    parser.add_argument(
        "--skip-vector-index",
        action="store_true",
        help="Skip building vector chunks after ingestion.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ingest_sources(
        source_file=args.source_file,
        timeout=args.timeout,
        skip_duplicates=not args.allow_duplicates,
        limit=args.limit,
        mark_missing_obsolete=args.mark_missing_obsolete,
        skip_vector_index=args.skip_vector_index,
    )


if __name__ == "__main__":
    main()
