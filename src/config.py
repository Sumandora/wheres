import os
import sys
import tomllib

from pathlib import Path

_CONFIG_PATH = ".wheres"
_DEFAULT_CONFIG = """# Default config for wheres
# Note: The vector database won't be deleted automatically, when changing settings.
#       When you change settings, you are advised to delete the vector.db file, next to this config

# When chunking, how many lines should two chunks be apart?
# It is recommended to set this to a value that's smaller than chunk_size,
#     so that an interleaved sliding window is created.
read_increment = 25

# How many lines should a single chunk be long?
# It is recommended to set this to a value that's bigger than read_increment,
#     so that an interleaved sliding window is created.
chunk_size = 50

# Should git be used, if available, to figure out the files that are to be indexed?
should_use_git = true

# A list of globs, where at least one needs to match for a file to be indexed
include_globs = []

# A list of globs, where none are allowed to match for a file to be indexed
exclude_globs = []
"""


class Config:
    def __init__(self):
        cwd = Path(os.getcwd()).resolve()
        config_path = cwd
        self.did_exist = True
        while not (config_path / _CONFIG_PATH).is_dir():
            parent = config_path.parent.resolve()
            if config_path == parent:
                self.did_exist = False
                break
            config_path = parent

        if self.did_exist:
            self.root_dir = config_path
        else:
            self.root_dir = cwd
        self.config_dir = self.root_dir / _CONFIG_PATH

        if not self.did_exist:
            print("Creating config directory at " + self.config_dir.as_posix(), file=sys.stderr)
            self.config_dir.mkdir()

        self.config_file = self.config_dir / "config.toml"

        self.did_exist &= self.config_file.exists()

        if not self.config_file.exists():
            self.config_file.write_text(_DEFAULT_CONFIG)
        self.config = tomllib.loads(self.config_file.read_text())

        self.db_file = self.config_dir / "vector.db"

        self.did_exist &= self.db_file.exists()

    def get_last_access_time(self):
        if self.did_exist:
            return self.config_file.stat().st_mtime_ns
        return 0

    def update_config_time(self):
        self.config_file.touch()

    def get_read_increment(self):
        return self.config['read_increment']

    def get_chunk_size(self):
        return self.config['chunk_size']

    def should_use_git(self):
        return self.config['should_use_git']

    def get_include_globs(self):
        return self.config['include_globs']

    def get_exclude_globs(self):
        return self.config['exclude_globs']
