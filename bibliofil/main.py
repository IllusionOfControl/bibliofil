import argparse

from bibliofil.cli import run_cleanup, run_dupes, run_stats, run_index
from bibliofil.database import Database


def main():
    parser = argparse.ArgumentParser(description="Bibliofil")
    parser.add_argument("--db", default="bibliofil.db")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_index = subparsers.add_parser("index", help="Indexing")
    p_index.add_argument("path", help="Путь")

    p_dupes = subparsers.add_parser("dupes", help="Дубликаты")
    p_dupes.add_argument("--exclude", nargs="+", help="Exclude extensions")
    p_dupes.add_argument("--include", nargs="+", help="Include extensions")
    p_dupes.add_argument("--min-size", help="Minimum size", default="-1")
    p_dupes.add_argument("--max-size", help="Maximum size", default="-1")

    p_cleanup = subparsers.add_parser(
        "cleanup", description="Finds and deletes duplicates"
    )
    p_cleanup.add_argument("--exclude", nargs="+", help="Exclude extensions")
    p_cleanup.add_argument("--include", nargs="+", help="Include extensions")
    p_cleanup.add_argument("--min-size", help="Minimum size", default="-1")
    p_cleanup.add_argument("--max-size", help="Maximum size", default="-1")
    p_cleanup.add_argument(
        "--dry-run",
        action="store_true",
        help="It only simulates deletion and outputs a report.",
    )

    p_stats = subparsers.add_parser("stats")
    p_stats.add_argument("--limit", help="Limit rows", default="-1")

    args = parser.parse_args()

    database = Database(args.db)

    match args.command:
        case "index":
            run_index(database, root_path=args.path)
        case "stats":
            run_stats(database, limit=int(args.limit))
        case "dupes":
            run_dupes(
                database,
                include=args.include,
                exclude=args.exclude,
                min_size=args.min_size,
                max_size=args.max_size,
            )
        case "cleanup":
            run_cleanup(
                database,
                include=args.include,
                exclude=args.exclude,
                min_size=args.min_size,
                max_size=args.max_size,
                dry_run=args.dry_run,
            )
        case _:
            raise RuntimeError(f"Unknown command: {args.command}")
