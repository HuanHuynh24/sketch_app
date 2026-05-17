import re


MOJIBAKE_MARKERS = ("Ã", "Ä", "Â", "áº", "á»", "Æ", "Å")


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None

    return repair_mojibake(normalize_whitespace(value))


def repair_mojibake(value: str) -> str:
    if _mojibake_score(value) < 3:
        return value

    candidates = [value]

    for encoding in ("latin1", "cp1252"):
        try:
            candidates.append(value.encode(encoding).decode("utf-8"))
        except UnicodeError:
            repaired = value.encode(encoding, errors="ignore").decode(
                "utf-8",
                errors="ignore",
            )

            if len(repaired) >= len(value) * 0.5:
                candidates.append(repaired)

    return min(candidates, key=_mojibake_score)


def _mojibake_score(value: str) -> int:
    return sum(value.count(marker) for marker in MOJIBAKE_MARKERS)
