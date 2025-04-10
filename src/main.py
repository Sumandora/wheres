import sys
import os
import subprocess

from pathlib import Path

from indexer import walk_files, get_files_to_reindex, reindex_files
from vectordb import VectorDB
from model import Model
from config import Config


def main():
    config = Config()

    files = []
    if config.should_use_git():
        try:
            files = subprocess.check_output(
                ["git", "ls-tree", "HEAD", "--name-only", "-r"],
                stderr=subprocess.DEVNULL).decode().rstrip("\n").split("\n")
        except subprocess.CalledProcessError:
            files = []

    if len(files) == 0:  # the things before didn't work, just get all files possible
        files = walk_files(os.getcwd())

    paths = [Path(file).absolute().relative_to(config.root_dir) for file in files]
    paths = filter(lambda path: path.is_file(), paths)

    files_to_reindex = get_files_to_reindex(paths,
                                            config.get_last_access_time(),
                                            config.get_include_globs(),
                                            config.get_exclude_globs() + ["**/.wheres/**"])

    files_to_reindex = list(files_to_reindex)

    model = Model()
    db = VectorDB(config.db_file.as_posix(), model.get_out_feature_count())

    reindex_files(db, model, config, files_to_reindex)

    config.update_config_time()

    search = " ".join(sys.argv[1:])

    if len(search) == 0:
        exit(0)

    search_vec = model.encode(search)

    results = db.search(search_vec, 100)

    for distance, entity in results:
        file_path = entity['file_path']
        begin_line_number = entity['begin_line_number']
        end_line_number = entity['end_line_number']
        print(f"{file_path}:{begin_line_number}-{end_line_number} - {distance}")


if __name__ == '__main__':
    main()
