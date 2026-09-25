from __future__ import annotations

import argparse
from pathlib import Path

from .organizer import apply_moves, plan, undo


def bytes_label(value: int) -> str:
    units = ("B", "KB", "MB", "GB")
    amount = float(value)
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{value} B"


def print_plan(moves) -> None:
    if not moves:
        print("Nothing to organize. Your Downloads folder gets a pass today.")
        return
    print(f"\n{len(moves)} file(s) ready to move:\n")
    for move in moves:
        print(f"  {move.filename:<34} -> {move.category:<14} {bytes_label(move.size):>10}")
    print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Organize a Downloads folder without surprises.")
    sub = parser.add_subparsers(dest="command", required=True)

    for name, help_text in (("plan", "Preview what would move"), ("apply", "Preview, then apply the plan")):
        command = sub.add_parser(name, help=help_text)
        command.add_argument("directory", nargs="?", type=Path, default=Path.home() / "Downloads")
        command.add_argument("--include-hidden", action="store_true", help="Include dotfiles")
        if name == "apply":
            command.add_argument("--yes", action="store_true", help="Skip the confirmation prompt")

    undo_parser = sub.add_parser("undo", help="Reverse a previous run")
    undo_parser.add_argument("manifest", type=Path, help="Path to a history JSON file")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "undo":
        restored = undo(args.manifest)
        print(f"Restored {restored} file(s).")
        return 0

    try:
        moves = plan(args.directory, args.include_hidden)
    except FileNotFoundError:
        print(f"Directory not found: {args.directory}")
        return 2
    print_plan(moves)
    if args.command == "plan" or not moves:
        return 0
    if not args.yes and input("Apply these moves? [y/N] ").strip().lower() != "y":
        print("Cancelled. No files were changed.")
        return 0
    manifest = apply_moves(moves, args.directory / ".tidy-downloads" / "history")
    print(f"Done. Undo this run with: tidy-downloads undo {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
