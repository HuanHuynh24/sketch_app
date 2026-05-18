import html
import re
from pathlib import Path

from app.core.config import settings


class DocumentRenderingService:
    def render_source_document(self, source_path: str | None) -> dict:
        if not source_path:
            return {
                "format": "html",
                "source_path": None,
                "markdown": "",
                "html": "",
            }

        markdown = self._read_markdown(source_path)
        return {
            "format": "html",
            "source_path": source_path,
            "markdown": markdown,
            "html": self._markdown_to_html(markdown),
        }

    def _read_markdown(self, source_path: str) -> str:
        root = self._resolve_data_dir(settings.RAG_DATA_DIR)
        file_path = (root / source_path).resolve()

        if not self._is_relative_to(file_path, root):
            return ""
        if not file_path.exists() or not file_path.is_file():
            return ""

        return file_path.read_text(encoding="utf-8").replace("\x00", "").strip()

    def _markdown_to_html(self, markdown: str) -> str:
        blocks = re.split(r"\n\s*\n", markdown.strip())
        html_blocks = []

        for block in blocks:
            lines = [line.rstrip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue

            if self._is_table(lines):
                html_blocks.append(self._render_table(lines))
                continue

            if all(self._is_unordered_list_item(line) for line in lines):
                items = "".join(
                    f"<li>{self._inline(line.lstrip('-* ').strip())}</li>"
                    for line in lines
                )
                html_blocks.append(f"<ul>{items}</ul>")
                continue

            if len(lines) == 1:
                rendered = self._render_single_line(lines[0])
                html_blocks.append(rendered)
                continue

            paragraph = " ".join(line.strip() for line in lines)
            html_blocks.append(f"<p>{self._inline(paragraph)}</p>")

        return "\n".join(html_blocks)

    def _render_single_line(self, line: str) -> str:
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            level = len(heading.group(1))
            return f"<h{level}>{self._inline(heading.group(2))}</h{level}>"

        return f"<p>{self._inline(line)}</p>"

    def _render_table(self, lines: list[str]) -> str:
        rows = [self._split_table_row(line) for line in lines]
        if len(rows) < 2:
            return f"<p>{self._inline(' '.join(lines))}</p>"

        header = rows[0]
        body = rows[2:] if self._is_table_separator(lines[1]) else rows[1:]

        thead = "".join(f"<th>{self._inline(cell)}</th>" for cell in header)
        tbody_rows = []
        for row in body:
            cells = "".join(f"<td>{self._inline(cell)}</td>" for cell in row)
            tbody_rows.append(f"<tr>{cells}</tr>")

        return (
            "<table>"
            f"<thead><tr>{thead}</tr></thead>"
            f"<tbody>{''.join(tbody_rows)}</tbody>"
            "</table>"
        )

    def _inline(self, value: str) -> str:
        escaped = html.escape(value.strip())
        escaped = re.sub(
            r"!\[([^\]]*)\]\((https?://[^)\s]+)\)",
            r'<img src="\2" alt="\1" loading="lazy" />',
            escaped,
        )
        escaped = re.sub(
            r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
            r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>',
            escaped,
        )
        escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
        escaped = re.sub(r"\*(.+?)\*", r"<em>\1</em>", escaped)
        escaped = re.sub(r"`(.+?)`", r"<code>\1</code>", escaped)
        escaped = re.sub(
            r"&lt;(https?://[^&\s]+)&gt;",
            r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>',
            escaped,
        )
        return escaped

    def _is_table(self, lines: list[str]) -> bool:
        return len(lines) >= 2 and "|" in lines[0] and self._is_table_separator(lines[1])

    def _is_table_separator(self, line: str) -> bool:
        return bool(re.match(r"^\s*\|?[\s:-]+\|[\s|:-]+\|?\s*$", line))

    def _split_table_row(self, line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    def _is_unordered_list_item(self, line: str) -> bool:
        return bool(re.match(r"^\s*[-*]\s+", line))

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

        return requested.resolve()

    def _is_relative_to(self, path: Path, root: Path) -> bool:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            return False
