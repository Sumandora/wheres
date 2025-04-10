# where's

A non-bullshit semantic code searcher for big repositories.

## Installation

### Dependencies
- **Python 3.13**: Lower versions don't work, because they are missing proper full path glob support!

### Setup

```bash
git clone https://github.com/Sumandora/wheres
cd wheres
./setup.sh
```

At this point you might want to alias the `wheres` script in your shell, or create a wrapper for it inside your path.

If you want a fancy fzf/bat powered previewer as well, then just invoke `wheres-fzf` instead of `wheres`.

My shell contains the following alias, it should work inside bash just like it does in fish:
```fish
alias "wheres"="~/Documents/code_embedding/wheres-fzf"
```

## Example

```bash
./wheres the code that searches the database
```

Running this inside this repository, should direct you to the usages of db.search inside main.py and the definition in vectordb.py.

The first invocation should also create a `.wheres/config.toml`, which lets you set a bunch of settings. It is recommended, that you read it once.

Note that the first invocation in larger repositories will take significant amount of time because of indexing.

In order to not disturb other people when using git, you might want to add a `.config/git/.gitignore` file with the line `**/.wheres/**`.

## Hardware Requirements

I'm running this on an RTX 2060 with 6GB vram, but the hardware requirements are quite slim, the model is only 161M params loaded at 16 bit.

Because files are chunked by line, large lines might cause issues with memory. Right now these long lines will just be skipped when indexing, for a more sophisticated chunking, I would probably need to use tree sitter, which would massively scale up complexity of this project.

## Credits

- [Embedding model](https://huggingface.co/jinaai/jina-embeddings-v2-base-code)
