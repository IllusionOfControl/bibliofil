import argparse

from bibliofil.cli.index import run_indexing
from bibliofil.cli.stats import run_stats
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

    p_clean = subparsers.add_parser("clean", help="Удаление")
    p_clean.add_argument("--dry-run", action="store_true", help="Тестовый запуск")

    subparsers.add_parser("stats")

    args = parser.parse_args()

    database = Database(args.db)

    if args.cmd == "index":
        run_indexing(database, args.path)
    elif args.cmd == "stats":
        run_stats(args.db)
