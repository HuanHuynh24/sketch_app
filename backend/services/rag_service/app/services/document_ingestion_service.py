import hashlib
import logging
import re
import unicodedata
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.services.vector_search_service import VectorSearchService


logger = logging.getLogger(__name__)

INGESTION_METADATA_VERSION = 5
MAX_IMAGES_PER_UNIVERSITY = 8

DOMESTIC_REGIONS = {
    "da-nang",
    "ha-noi",
    "khac",
    "mien-bac",
    "mien-nam",
    "mien-trung",
    "tp-hcm",
}


class DocumentIngestionService:
    def __init__(self, db: Session):
        self.document_chunk_repo = DocumentChunkRepository(db)
        self.vector_search = VectorSearchService(db)
        self.chunk_size = settings.RAG_CHUNK_SIZE
        self.chunk_overlap = settings.RAG_CHUNK_OVERLAP

    async def ingest_markdown_directory(self, data_dir: str | None = None) -> dict:
        root = self._resolve_data_dir(data_dir or settings.RAG_DATA_DIR)
        files = sorted(root.rglob("*.md"))

        total_chunks = 0
        skipped_files = 0
        ingested_files = 0

        for file_path in files:
            result = await self._ingest_markdown_file(root, file_path)
            total_chunks += result["chunks"]
            skipped_files += int(result["skipped"])
            ingested_files += int(not result["skipped"])

        return {
            "data_dir": str(root),
            "files": len(files),
            "ingested_files": ingested_files,
            "skipped_files": skipped_files,
            "chunks": total_chunks,
        }

    async def ingest_if_empty(self) -> dict:
        if self.document_chunk_repo.has_chunks():
            return {
                "skipped": True,
                "reason": "document_chunks already contains data",
            }

        result = await self.ingest_markdown_directory()
        result["skipped"] = False
        return result

    async def _ingest_markdown_file(self, root: Path, file_path: Path) -> dict:
        raw_text = self._sanitize_text(file_path.read_text(encoding="utf-8")).strip()
        if not raw_text:
            return {"chunks": 0, "skipped": True}

        relative_path = file_path.relative_to(root).as_posix()
        file_hash = self._sha256(raw_text)

        existing_metadata = self.document_chunk_repo.get_source_metadata(relative_path)
        existing_hashes = {row[0] for row in existing_metadata}
        existing_versions = {row[1] for row in existing_metadata}
        current_version = str(INGESTION_METADATA_VERSION)
        if existing_hashes == {file_hash} and existing_versions == {current_version}:
            return {"chunks": 0, "skipped": True}

        if existing_metadata:
            self.document_chunk_repo.delete_by_source_path(relative_path)

        metadata = self._build_file_metadata(root, file_path, raw_text, file_hash)
        chunks = self._chunk_markdown(raw_text)
        documents = []

        for index, chunk in enumerate(chunks):
            content = self._format_chunk_for_embedding(metadata, chunk)
            documents.append(
                {
                    "source_path": relative_path,
                    "source_name": metadata["source_name"],
                    "region": metadata["region"],
                    "university_name": metadata["university_name"],
                    "chunk_index": index,
                    "content_hash": self._sha256(f"{relative_path}:{index}:{content}"),
                    "content": content,
                    "chunk_metadata": {
                        **metadata,
                        "chunk_index": index,
                    },
                }
            )

        saved = await self.vector_search.save_chunks(documents)
        return {"chunks": len(saved), "skipped": False}

    def _chunk_markdown(self, text: str) -> list[str]:
        sections = self._split_by_markdown_headings(text)
        chunks = []
        for section in sections:
            chunks.extend(self._chunk_text(section))
        return chunks

    def _split_by_markdown_headings(self, text: str) -> list[str]:
        lines = text.splitlines()
        sections = []
        current = []

        for line in lines:
            is_heading = bool(re.match(r"^#{1,4}\s+", line))
            if is_heading and current:
                sections.append("\n".join(current).strip())
                current = [line]
            else:
                current.append(line)

        if current:
            sections.append("\n".join(current).strip())

        return [section for section in sections if section]

    def _chunk_text(self, text: str) -> list[str]:
        normalized = re.sub(r"\n{3,}", "\n\n", text).strip()
        if len(normalized) <= self.chunk_size:
            return [normalized]

        paragraphs = re.split(r"\n\s*\n", normalized)
        chunks = []
        current = ""

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            if len(paragraph) > self.chunk_size:
                if current:
                    chunks.append(current.strip())
                    current = ""
                chunks.extend(self._hard_chunk(paragraph))
                continue

            candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
            if len(candidate) <= self.chunk_size:
                current = candidate
                continue

            if current:
                chunks.append(current.strip())
            current = self._with_overlap(chunks[-1] if chunks else "", paragraph)

        if current:
            chunks.append(current.strip())

        return chunks

    def _hard_chunk(self, text: str) -> list[str]:
        chunks = []
        step = max(self.chunk_size - self.chunk_overlap, 1)
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size].strip()
            if chunk:
                chunks.append(chunk)
        return chunks

    def _with_overlap(self, previous: str, next_text: str) -> str:
        if not previous or self.chunk_overlap <= 0:
            return next_text

        overlap = previous[-self.chunk_overlap :].strip()
        return f"{overlap}\n\n{next_text}".strip()

    def _build_file_metadata(
        self,
        root: Path,
        file_path: Path,
        text: str,
        file_hash: str,
    ) -> dict:
        relative_path = file_path.relative_to(root).as_posix()
        title = self._extract_title(text) or self._title_from_slug(file_path.stem)
        region = file_path.parent.name if file_path.parent != root else None
        country = self._extract_country(text) or self._default_country(region)
        images = self._extract_image_urls(text)
        school_type = self._extract_school_type(text)
        address = self._extract_intro_field(text, "dia chi", "address")
        city = self._extract_intro_field(text, "thanh pho", "city")

        return {
            "source_path": relative_path,
            "source_name": file_path.name,
            "region": region,
            "university_name": title,
            "country": country,
            "city": city,
            "school_type": school_type,
            "address": address,
            "images": images,
            "logo": images,
            "document_type": "university_profile",
            "file_hash": file_hash,
            "metadata_version": INGESTION_METADATA_VERSION,
        }

    def _format_chunk_for_embedding(self, metadata: dict, chunk: str) -> str:
        header = (
            f"University: {metadata['university_name']}\n"
            f"Region: {metadata.get('region') or 'unknown'}\n"
            f"Country: {metadata.get('country') or 'Vietnam'}"
        )
        return f"{header}\n\n{chunk}"

    def _extract_title(self, text: str) -> str | None:
        match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        if not match:
            return None

        return re.sub(r"[*_`]", "", match.group(1)).strip()

    def _extract_country(self, text: str) -> str | None:
        return self._extract_intro_field(text, "quoc gia", "country", "dat nuoc", "nation")

    def _extract_school_type(self, text: str) -> str | None:
        school_type = self._extract_intro_field(text, "loai truong", "school type", "type")
        if school_type:
            return school_type

        intro_text = text[:2500]
        normalized = self._normalize_text(intro_text)
        if "cong lap" in normalized or "public university" in normalized:
            return "Công lập"
        if "dan lap" in normalized or "tu thuc" in normalized or "private university" in normalized:
            return "Dân lập"

        return None

    def _extract_intro_field(self, text: str, *labels: str) -> str | None:
        normalized_labels = {self._normalize_text(label) for label in labels}

        for line in text.splitlines():
            cleaned = re.sub(r"^[\s>*-]+", "", line).strip()
            cleaned = re.sub(r"[*_`]", "", cleaned).strip()
            if ":" not in cleaned:
                continue

            raw_label, raw_value = cleaned.split(":", 1)
            label = self._normalize_text(raw_label)
            if label not in normalized_labels:
                continue

            value = re.sub(r"[<>{}\[\]()*_`]", "", raw_value).strip()
            if value:
                return value

        return None

    def _normalize_text(self, value: str) -> str:
        value = value.replace("Đ", "D").replace("đ", "d")
        normalized = unicodedata.normalize("NFD", value)
        without_accents = "".join(
            char for char in normalized if unicodedata.category(char) != "Mn"
        )
        return without_accents.lower().strip()

    def _extract_image_urls(self, text: str) -> list[str]:
        urls = []
        seen = set()
        patterns = [
            r"!\[[^\]]*\]\((https?://[^)\s]+)\)",
            r"<img[^>]+src=[\"'](https?://[^\"']+)[\"']",
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                url = match.group(1).strip()
                if url and url not in seen:
                    seen.add(url)
                    urls.append(url)

                if len(urls) >= MAX_IMAGES_PER_UNIVERSITY:
                    return urls

        return urls

    def _default_country(self, region: str | None) -> str:
        if region in DOMESTIC_REGIONS:
            return "Vietnam"

        return "Unknown"

    def _title_from_slug(self, slug: str) -> str:
        return " ".join(part.capitalize() for part in slug.split("-"))

    def _resolve_data_dir(self, data_dir: str) -> Path:
        requested = Path(data_dir)
        candidates = [
            requested,
            Path.cwd() / requested,
            Path.cwd() / "backend" / "data",
            Path.cwd().parents[1] / "data" if len(Path.cwd().parents) > 1 else requested,
        ]

        for candidate in candidates:
            if candidate.exists() and candidate.is_dir():
                return candidate.resolve()

        raise FileNotFoundError(f"RAG data directory not found: {data_dir}")

    def _sha256(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def _sanitize_text(self, value: str) -> str:
        return value.replace("\x00", "")
