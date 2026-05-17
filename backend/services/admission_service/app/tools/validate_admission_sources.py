import argparse
import json
import unicodedata
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.admission_raw_document import AdmissionRawDocument
from app.models.admission_source import AdmissionSource
from app.models.university import University


MIN_CONTENT_SIZE = 1000


def read_source_file(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Source file must be a JSON array")

    return data


def normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value)
    without_marks = "".join(
        char
        for char in decomposed
        if unicodedata.category(char) != "Mn"
    )
    return without_marks.replace("đ", "d").replace("Đ", "D").casefold()


def find_source(
    db: Session,
    university_code: str,
    source_item: dict[str, Any],
) -> AdmissionSource | None:
    return (
        db.query(AdmissionSource)
        .join(University)
        .filter(
            University.code == university_code,
            AdmissionSource.url == source_item["url"],
            AdmissionSource.document_type == source_item.get(
                "document_type",
                "admission_page",
            ),
            AdmissionSource.year == source_item.get("year"),
        )
        .first()
    )


def latest_document(
    db: Session,
    source: AdmissionSource,
) -> AdmissionRawDocument | None:
    return (
        db.query(AdmissionRawDocument)
        .filter(AdmissionRawDocument.source_id == source.source_id)
        .order_by(AdmissionRawDocument.fetched_at.desc())
        .first()
    )


def validate_source_item(
    db: Session,
    university_code: str,
    source_item: dict[str, Any],
) -> tuple[bool, list[str]]:
    errors = []
    source = find_source(db, university_code, source_item)

    if source is None:
        return False, ["source not found in database"]

    if source.status != "fetched":
        errors.append(f"status is {source.status}")

    document = latest_document(db, source)

    if document is None:
        errors.append("raw document not found")
        return False, errors

    if document.content_size < MIN_CONTENT_SIZE:
        errors.append(f"content_size too small: {document.content_size}")

    text = document.content_text or ""

    if not text:
        errors.append("content_text is empty; parser may need PDF/text support")
        return False, errors

    normalized_text = normalize(text)

    for keyword in source_item.get("expected_keywords", []):
        if normalize(keyword) not in normalized_text:
            errors.append(f"missing keyword: {keyword}")

    return not errors, errors


def validate_sources(source_file: Path) -> int:
    items = read_source_file(source_file)
    db = SessionLocal()
    failed = 0

    try:
        for item in items:
            university_code = item["university_code"]

            for source_item in item.get("sources", []):
                ok, errors = validate_source_item(
                    db=db,
                    university_code=university_code,
                    source_item=source_item,
                )

                label = f"{university_code} {source_item['url']}"

                if ok:
                    print(f"[ok] {label}")
                    continue

                failed += 1
                print(f"[bad] {label}: {'; '.join(errors)}")
    finally:
        db.close()

    print(f"Validation finished: {failed} failed")
    return failed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate fetched admission sources using expected keywords.",
    )
    parser.add_argument(
        "--source-file",
        type=Path,
        required=True,
        help="Path to a JSON source list.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raise SystemExit(validate_sources(args.source_file))


if __name__ == "__main__":
    main()
