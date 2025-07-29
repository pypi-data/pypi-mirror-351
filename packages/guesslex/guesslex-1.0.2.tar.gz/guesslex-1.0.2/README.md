# Guesslex

[![PyPI version](https://badge.fury.io/py/guesslex.svg)](https://badge.fury.io/py/guesslex)
[![Python Support](https://img.shields.io/pypi/pyversions/guesslex.svg)](https://pypi.org/project/guesslex/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A machine learning-based programming language detection library that identifies programming languages in code snippets with high accuracy. Supports 25+ programming languages with confidence scoring and detailed analysis.

## Features

- **High Accuracy**: 96.9% accuracy on test datasets
- **25+ Languages**: Supports Python, JavaScript, TypeScript, Java, C/C++, Go, Rust, and more
- **Confidence Scoring**: Provides confidence levels and detailed analysis
- **Multiple Interfaces**: Both command-line tool and Python API
- **Enhanced Pattern Matching**: Uses ensemble models with language-specific patterns
- **Robust Detection**: Handles mixed-language files and provides context-aware results

## Installation

```bash
pip install guesslex
```

## Quick Start

### Python API

#### Example 1: Code in Team Communication

```python
from guesslex import detect_language_simple, detect_languages
import json
import numpy as np

# Code from a team discussion about a cross-platform feature
code = """
Hi team, I'm working on a cross-platform feature and wanted your input.

First, here's the Python backend code I wrote to generate a secure token and assign it to a user. It includes error handling and logging:

import secrets
import base64
import logging

logger = logging.getLogger(__name__)

def generate_token(user_id):
    try:
        token = secrets.token_bytes(32)
        encoded = base64.urlsafe_b64encode(token).decode('utf-8')
        logger.info(f"Generated token for user {user_id}")
        return encoded
    except Exception as e:
        logger.error(f"Token generation failed: {str(e)}")
        return None

Next, this is the JavaScript function that runs on the frontend to call the backend API and store the token in local storage. I'm using async/await and basic error handling:

async function fetchToken(userId) {
    try {
        const response = await fetch(`/api/token?user=${userId}`);
        if (!response.ok) throw new Error("Network response was not ok");
        const data = await response.json();
        localStorage.setItem("authToken", data.token);
        console.log("Token saved successfully.");
    } catch (error) {
        console.error("Failed to fetch token:", error);
    }
}

Lastly, here's the SQL used to persist the token in the database. This is PostgreSQL:

CREATE TABLE api_tokens (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    token TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO api_tokens (user_id, token) VALUES ('user_001', 'abc123xyz');

Let me know if you see any issues with this flow or if you'd recommend any improvements.
"""

# Get detailed language detection - works with code embedded in text
result = detect_languages(code)
# Convert numpy types to native Python types for JSON serialization
def convert(obj):
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, np.str_):
        return str(obj)
    return obj

# Print detected languages as a JSON array
print(json.dumps([str(lang) for lang in result['detected_languages']], indent=2))

# Print confidence summary as pretty JSON
print(json.dumps({str(k): v for k, v in result['confidence_summary'].items()}, default=convert, indent=2))
```

#### Example 2: Code in Technical Documentation

```python
from guesslex import detect_language_simple, detect_languages

# Code from deployment documentation
doc_with_code = """
I'm automating a deployment and using a Bash script to trigger a Python script that returns a JSON object. Here's the Bash wrapper:

#!/bin/bash
echo "Starting deployment"
python3 deploy.py --env=prod --verbose
echo "Deployment finished with status $?"

And this is part of the Python script it calls:

import json
import sys

def deploy(env):
    status = {"environment": env, "success": True}
    print(json.dumps(status))

if __name__ == "__main__":
    deploy(sys.argv[1])
"""

# Simple detection returns the most dominant language
language = detect_language_simple(doc_with_code)
print(language)  # Output: python

# Detailed detection shows all languages, even in documentation context
result = detect_languages(doc_with_code)
print([str(lang) for lang in result['detected_languages']])  # Output: ['bash', 'python']
```

These examples demonstrate how Guesslex can:
- Detect multiple programming languages in documentation or communication contexts
- Handle code snippets embedded within regular text
- Identify language boundaries even when mixed with explanatory text
- Provide accurate detection regardless of the surrounding context

### Command Line Interface

```bash
# Analyze a file
guesslex -i script.py

# Pipe code directly
cat script.py | guesslex --json

# Verbose output with detailed analysis
guesslex -i script.py --verbose
```

## API Reference

### `detect_language_simple(text: str) -> str`

Returns the most likely programming language for the given code snippet.

**Parameters:**
- `text`: The code snippet to analyze

**Returns:**
- String representing the detected language

### `detect_languages(text: str) -> Dict`

Performs comprehensive language detection with confidence scoring.

**Parameters:**
- `text`: The code snippet to analyze

**Returns:**
- Dictionary containing:
  - `detected_languages`: List of detected languages
  - `confidence_summary`: Detailed confidence information per language
  - `all_languages`: Combined results including fenced code blocks
  - `analysis`: Analysis metadata

## Supported Languages

Python, Java, JavaScript, TypeScript, C, C++, C#, Go, Rust, PHP, Ruby, Scala, Swift, Kotlin, Haskell, R, Lua, Perl, SQL, HTML, CSS, Shell, MATLAB, Dart, Elixir, Plain Text

## Command Line Options

```
guesslex [OPTIONS]

Options:
  -i, --input FILE        Input file (default: stdin)
  -o, --out FILE         Write JSON results to file
  -m, --model FILE       Custom model file path
  --json                 Output clean JSON format
  --verbose              Show detailed analysis
  --confidence-threshold FLOAT  Confidence threshold (default: 0.70)
  --plain-threshold FLOAT       Plain text threshold (default: 0.50)
  -h, --help             Show help message
```

## Development

To set up for development:

```bash
git clone https://github.com/SidPad03/guesslex.git
cd guesslex
pip install -e .[dev]

# Run tests
pytest

# Format code
black guesslex/

# Type checking
mypy guesslex/
```

## Model Performance

- **Overall Accuracy**: 96.9%
- **Training Data**: 100,000+ code samples across 25+ languages
- **Model Type**: Ensemble of TF-IDF, n-gram analysis, and pattern matching
- **Validation**: Stratified k-fold cross-validation

## Contributing

Contributions are welcome! Please feel free to submit pull requests, report bugs, or suggest features.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
