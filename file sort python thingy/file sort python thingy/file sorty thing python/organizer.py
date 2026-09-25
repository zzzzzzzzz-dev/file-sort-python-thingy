"file sort thingy"

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

CATEGORIES = {
    "Images": {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".heic", ".bmp"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt"},
    "Spreadsheets": {".csv", ".xls", ".xlsx", ".ods"},
    "Archives": {".zip", ".tar", ".gz", ".bz2", ".7z", ".rar"},
    "Audio": {".mp3", ".wav", ".flac", ".m4a", ".ogg"},
    "Video": {".mp4", ".mov", ".mkv", ".avi", ".webm"},
    "Code": {".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".json", ".sql"},
    "Installers": {".dmg", ".pkg", ".deb", ".rpm", ".exe", ".msi", ".appimage"},
}

@dataclass(frozen=True)
class PlannedMove:
    source: str
    destination: str
    category: str
    size: int

    @property
    def filename(self) -> str:
        return Path(self.source).name


def category_for(path: Path) -> str:
    suffix = path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if suffix in extensions:
            return category
    return "Other"


def unique_destination(directory: Path, filename: str) -> Path:
 
    candidate = directory / filename
    if not candidate.exists():
        return candidate
    original = Path(filename)
    for number in range(1, 10_000):
        candidate = directory / f"{original.stem} ({number}){original.suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not find a free name for {filename}")


def plan(source_dir: Path, include_hidden: bool = False) -> list[PlannedMove]:
    if not source_dir.exists():
        raise FileNotFoundError(source_dir)
    moves: list[PlannedMove] = []
    reserved: set[Path] = set()
    for item in sorted(source_dir.iterdir(), key=lambda p: p.name.lower()):
        if not item.is_file() or (item.name.startswith(".") and not include_hidden):
            continue
        category = category_for(item)
        target_dir = source_dir / category
        destination = unique_destination(target_dir, item.name)
        while destination in reserved:
            destination = unique_destination(target_dir, destination.name)
        reserved.add(destination)
        moves.append(PlannedMove(str(item), str(destination), category, item.stat().st_size))
    return moves


def apply_moves(moves: list[PlannedMove], history_dir: Path) -> Path:
    history_dir.mkdir(parents=True, exist_ok=True)
    applied: list[dict[str, str | int]] = []
    for move in moves:
        source, destination = Path(move.source), Path(move.destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        applied.append(asdict(PlannedMove(str(source), str(destination), move.category, move.size)))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    manifest = history_dir / f"{stamp}.json"
    manifest.write_text(json.dumps(applied, indent=2), encoding="utf-8")
    return manifest


def undo(manifest: Path) -> int:
    records = json.loads(manifest.read_text(encoding="utf-8"))
    restored = 0
    for record in reversed(records):
        source, destination = Path(record["source"]), Path(record["destination"])
        if not destination.exists():
            continue
        source.parent.mkdir(parents=True, exist_ok=True)
        final_source = unique_destination(source.parent, source.name)
        shutil.move(str(destination), str(final_source))
        restored += 1
    return restored
