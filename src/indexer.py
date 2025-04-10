import sys
import chardet

from tqdm import tqdm
from pathlib import Path
from typing import Optional

from vectordb import VectorDB
from model import Model
from config import Config


def get_files_to_reindex(files,
                         last_access_time,
                         include_globs: list[str],
                         exclude_globs: list[str]) -> list[Path]:
    files_to_reindex = []

    for file in files:
        if len(include_globs) > 0 and all(map(lambda glob: not file.full_match(glob),
                                              include_globs)):
            continue
        if len(exclude_globs) > 0 and any(map(lambda glob: file.full_match(glob),
                                              exclude_globs)):
            continue

        file_stat = file.stat()
        if file_stat.st_mtime_ns > last_access_time:
            files_to_reindex.append(file)

    return files_to_reindex


def walk_files(directory: str) -> list[Path]:
    allfiles = []

    for path, dirs, files in Path(directory).walk():
        path = Path(path)

        for file in files:
            allfiles.append(path / file)

    return allfiles


def _record_row(db: VectorDB, model: Model, file: str,
                lines: [str], begin_line: int, end_line: int):
    content = "\n".join(lines[begin_line:end_line])
    embeddings = model.encode(content)
    db.insert(embeddings, file, begin_line, end_line)
    del embeddings


def _read_file(file: Path) -> Optional[str]:
    byte_array = file.open('rb').read()
    result = chardet.detect(byte_array)
    encoding = result['encoding']

    try:
        return file.open('r', encoding=encoding).read()
    except UnicodeDecodeError:
        return None


def reindex_files(db: VectorDB, model: Model, config: Config, files_to_reindex):
    if len(files_to_reindex) == 0:
        return

    print(f'Reindexing {len(files_to_reindex)} files', file=sys.stderr)

    for file in (pb := tqdm(files_to_reindex)):
        pb.set_description(file.as_posix())

        if not file.exists():
            print(f"File doesn't exist anymore: {file.as_posix()}", file=sys.stderr)
            continue

        content = _read_file(file)

        if content is None:
            print(f"Failed to read: {file.as_posix()}", file=sys.stderr)
            continue

        lines = content.split("\n")

        db.delete_file(file.as_posix())

        for line in range(0, len(lines), config.get_read_increment()):
            end_line = line + config.get_chunk_size()
            try:
                _record_row(db, model, file.as_posix(), lines, line, end_line)
            except RuntimeError as e:
                import gc
                gc.collect()
                import torch.cuda
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                print(f"Failed to record row: {e}", file=sys.stderr)
