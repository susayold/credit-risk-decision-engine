from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


def package_directory(source_dir: Path, output_zip: Path) -> int:
    source_dir = source_dir.resolve()
    output_zip = output_zip.resolve()
    if not source_dir.exists() or not source_dir.is_dir():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    if output_zip.exists():
        output_zip.unlink()

    file_count = 0
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(source_dir.rglob("*")):
            if file_path.is_file():
                archive_name = file_path.relative_to(source_dir).as_posix()
                archive.write(file_path, archive_name)
                file_count += 1

    with zipfile.ZipFile(output_zip, "r") as archive:
        bad_entries = [info.filename for info in archive.infolist() if "\\" in info.filename]
    if bad_entries:
        raise AssertionError(f"ZIP contains non-portable backslash entries: {bad_entries[:10]}")
    return file_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a portable ZIP using forward-slash archive paths.")
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("output_zip", type=Path)
    args = parser.parse_args()
    file_count = package_directory(args.source_dir, args.output_zip)
    print(f"Created {args.output_zip} with {file_count} files and portable forward-slash paths.")


if __name__ == "__main__":
    main()
