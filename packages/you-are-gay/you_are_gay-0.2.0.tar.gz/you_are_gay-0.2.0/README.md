# You Are Gay

A fun Python package that displays any name with "IS GAY" in a colorful, animated way in your terminal.

## Installation

```bash
pip install you-are-gay
```

## Usage

Simply run with a name:

```bash
you-are-gay John
```

Or run without a name to get the default "YOU IS GAY":

```bash
you-are-gay
```

Multiple words work too:

```bash
you-are-gay "John Smith"
# or
you-are-gay John Smith
```

You can also use it in your Python code:

```python
from fancy_text import display_text

# Display with your custom message
display_text("JOHN IS GAY")

# Use the underlying animation function directly
from fancy_text import animate_text
animate_text("ANY TEXT YOU WANT")
```

## Features

- Colorful, animated terminal display
- Gradient text effects
- Sparkle animations
- Auto-sizing to fit your terminal
- Large ASCII art characters

## Requirements

- Python 3.6+
- Works on Linux, macOS, and Windows

## License

MIT
