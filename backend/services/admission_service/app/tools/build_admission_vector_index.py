import argparse

from app.core.database import SessionLocal
from app.services.vector_index_service import index_latest_documents


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build vector chunks for latest fetched admission documents.",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Delete and rebuild chunks for documents that already have vectors.",
    )
    parser.add_argument(
        "--university-code",
        default=None,
        help="Optional university code to index only one school.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional maximum number of latest source documents to process.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db = SessionLocal()

    try:
        stats = index_latest_documents(
            db=db,
            rebuild=args.rebuild,
            university_code=args.university_code,
            limit=args.limit,
        )
    finally:
        db.close()

    print(
        "Vector index finished: "
        f"documents_seen={stats.documents_seen}, "
        f"documents_indexed={stats.documents_indexed}, "
        f"documents_skipped={stats.documents_skipped}, "
        f"chunks_created={stats.chunks_created}, "
        f"chunks_deleted={stats.chunks_deleted}"
    )


if __name__ == "__main__":
    main()
