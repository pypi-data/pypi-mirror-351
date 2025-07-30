Your `README.md` for **TextCleaner** is off to a solid start—clear, well-organized, and functional. Below is an improved version with a few refinements to grammar, formatting, clarity, and overall polish. I also incorporated your authorship at the end, as you mentioned “my name Emmanuel.”

---

# TextCleaner

A simple Python library for cleaning text and converting it into arrays of clean, lowercase words.

## Installation

Install via pip:

```bash
pip install textcleaner
```

Or install from source:

```bash
git clone https://github.com/yourusername/textcleaner.git
cd textcleaner
pip install -e .
```

## Usage

```python
from textcleaner import clean

# Basic usage
result = clean("Hello, WORLD!! This is an example.")
print(result)
# Output: ['hello', 'world', 'this', 'is', 'an', 'example']

# More examples
print(clean("Python is AWESOME!!! Let's code..."))
# Output: ['python', 'is', 'awesome', 'let', 's', 'code']

print(clean("Remove @#$% special characters & numbers 123"))
# Output: ['remove', 'special', 'characters', 'numbers', '123']
```

## Features

* Converts text to lowercase
* Removes punctuation and special characters
* Tokenizes text into words
* Handles numbers as valid tokens
* Manages empty strings and edge cases gracefully
* Returns a clean list of words

## API Reference

### `clean(text)`

Cleans input text and returns a list of lowercase words.

**Parameters:**

* `text` (`str`): The input string to clean

**Returns:**

* `list`: A list of cleaned, lowercase words

**Example:**

```python
clean("Hello, World!")  
# Returns: ['hello', 'world']
```

## Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch:

   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Commit your changes:

   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. Push to your branch:

   ```bash
   git push origin feature/amazing-feature
   ```
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Changelog

### Version 1.0.0

* Initial release
* Basic text cleaning functionality
* Word tokenization
* Punctuation and special character removal

---

**Author**: Emmanuel

