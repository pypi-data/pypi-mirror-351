# TermRecord

TermRecord is a simple yet powerful terminal session recorder and player for Linux systems. It allows you to record your terminal sessions and play them back later.

## Features

- Record terminal sessions with timing information
- Play back recorded sessions with original timing
- Supports all terminal operations and ANSI escape sequences
- Lightweight and easy to use

## Installation

You can install TermRecord using pip:

```bash
pip install termrecord
```

Or using Poetry:

```bash
poetry add termrecord
```

## Usage

### Recording a session

To record a terminal session:

```bash
termrecord record <your-command>
```

For example:
```bash
termrecord record ls -la
```

This will create a `record.trc` file in your current directory containing the recorded session.

### Playing back a session

To play back a recorded session:

```bash
termrecord play
```

This will play back the session from the `record.trc` file in your current directory.

## Requirements

- Linux operating system
- Python 3.7 or higher

## License

This project is licensed under the MIT License. See the LICENSE file for details.
