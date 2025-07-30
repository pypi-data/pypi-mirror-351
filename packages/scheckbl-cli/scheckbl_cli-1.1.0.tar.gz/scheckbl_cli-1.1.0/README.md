# scheckbl-cli

**A command-line interface for interacting with the SCheck Blocklist datasets.**
> Actually Version: `1.1.0`
> 
> Our Websites: [scheck-blocklist.vercel.app](https://scheck-blocklist.vercel.app)

## Installation

Install the CLI tool using pip:

```bash
pip install scheckbl-cli
```

## Usage

The CLI provides several commands to interact with the blocklist:

### Check if a keyword exists

```bash
scheckbl-cli check <type_name> <category> <keyword>
```

Example:

```bash
scheckbl-cli check phrases vulgarisms "example_word"
```

### Find any hits in text

```bash
scheckbl-cli find <type_name> <category> <text>
```

Example:

```bash
scheckbl-cli find phrases vulgarisms "This is some sample text."
```

### Retrieve full list and save to file

```bash
scheckbl-cli get <type_name> <category> [options]
```

Options:

- `-f, --filename NAME`
- `-r, --regex PATTERN`
- `-o, --output FILE`
- `--stdout`

Example:

```bash
scheckbl-cli get phrases vulgarisms --stdout
```

### Find entries similar to a given phrase

```bash
scheckbl-cli similar <type_name> <category> <phrase> [options]
```

Options:

- `-t, --threshold FLOAT`
- `--json`
- `-o, --output FILE`
- `--stdout`

Example:

```bash
scheckbl-cli similar phrases vulgarisms "example_phrase" --json
```

## Help

For more information on each command and its options:

```bash
scheckbl-cli --help
scheckbl-cli <command> --help
```

## License

This project is licensed under the MIT License.
