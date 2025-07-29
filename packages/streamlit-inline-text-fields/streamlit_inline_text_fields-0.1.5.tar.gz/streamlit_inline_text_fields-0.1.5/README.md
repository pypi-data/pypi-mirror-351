# Streamlit Inline Text Fields Component

[![PyPI version](https://badge.fury.io/py/streamlit-inline-text-fields.svg)](https://badge.fury.io/py/streamlit-inline-text-fields) <!-- TODO: Update when published -->

A Streamlit component for creating interactive inline text field exercises, perfect for language learning apps and quizzes.

## Features

- **Inline Text Input:** Renders sentences with embedded text fields for user input.
- **Flexible Sentence Parsing:** Define input fields using customizable delimiters (e.g., `{answer}`).
- **Input Validation:**
  - Checks for perfect matches.
  - Supports `ignore_accents` for case-insensitive and accent-insensitive matching.
  - Allows `accepted_levenshtein_distance` for "close enough" answers.
- **Real-time Feedback:** Optionally, `render_results_in_frontend` provides immediate visual cues (colors) for correctness as the user types.
- **Customizable Colors:** Override default validation state colors (perfect, acceptable, false, empty) via the `color_kwargs` parameter.
- **Streamlit Theme Integration:** Automatically adapts to your Streamlit app's current theme for font, text color, and base styling.
- **Stateful:** Remembers user inputs within a Streamlit session.

## Installation

Install the component using pip:

```bash
pip install streamlit-inline-text-fields
```

**Note:** Requires `python-Levenshtein`. If not installed, the component will raise an ImportError:

```bash
pip install python-Levenshtein
```

## Usage

Import `inline_text_fields` and use it in your Streamlit app:

```python
import streamlit as st
from inline_text_fields_component import inline_text_fields, ValidationStatus

# Basic example
sentences = ["The capital of {France} is Paris.", "An apple is a {fruit}."]
results = inline_text_fields(sentences_with_solutions=sentences)
st.write(results)

# Example with custom colors and Levenshtein distance
custom_colors: dict[ValidationStatus, str] = {
    "perfect": "rgba(144, 238, 144, 0.3)",  # LightGreen background
    "acceptable": "rgba(255, 218, 185, 0.4)", # PeachPuff background
    "false": "rgba(255, 160, 122, 0.3)",      # LightSalmon background
}
sentences_lev = ["This is an {example} for testing."]
results_lev = inline_text_fields(
    sentences_with_solutions=sentences_lev,
    accepted_levenshtein_distance=1,
    render_results_in_frontend=True,
    color_kwargs=custom_colors,
    freeze=True  # Example usage of freeze option
)
st.write(results_lev)
```

See `example.py` for more detailed usage.

## API Reference

```python
def inline_text_fields(
    sentences_with_solutions: List[str],
    delimiter: str = "{}",
    ignore_accents: bool = False,
    accepted_levenshtein_distance: int = 0,
    render_results_in_frontend: bool = False,
    freeze: bool = False,
    key: Optional[str] = None,
    color_kwargs: Dict[ValidationStatus, str] = {},
) -> List[List[Tuple[str, ValidationStatus]]]:
```

**Arguments:**

- `sentences_with_solutions: List[str]`  
  List of sentence templates. Fields are marked by delimiter, with the content inside being the correct answer.
- `delimiter: str`, optional (default: `{}`)  
  Delimiter for input fields (e.g., `{answer}`, `_answer_`, `[[answer]]`).
- `ignore_accents: bool`, optional (default: `False`)  
  If True, ignores accents during validation.
- `accepted_levenshtein_distance: int`, optional (default: `0`)  
  Maximum Levenshtein distance for an answer to be "acceptable".
- `render_results_in_frontend: bool`, optional (default: `False`)  
  If True, frontend provides immediate visual feedback on input correctness.
- `freeze: bool`, optional (default: `False`)  
  If True, all input fields will be disabled (non-editable) in the frontend. Useful for displaying results after an interaction session.
- `key: str`, optional  
  Unique Streamlit key for the component.
- `color_kwargs: Dict[ValidationStatus, str]`, optional  
  Overrides default background colors for validation states: "perfect", "acceptable", "false", "empty".  
  Example: `{"perfect": "#90EE90", "false": "lightcoral"}`

**Returns:**

- `List[List[Tuple[str, ValidationStatus]]]`  
  A nested list. Each inner list corresponds to a sentence. Each tuple contains `(user_input_string, validation_status_string)`.  
  `ValidationStatus` can be `"perfect"`, `"acceptable"`, `"false"`, or `"empty"`.

## Development

### Clone & Setup Python Env

```bash
# git clone ... (if applicable)
# cd streamlit-inline-text-fields
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e . python-Levenshtein  # Install local package and Levenshtein
# For full dev dependencies (if you have a [devel] extra in setup.py):
# pip install -e ".[devel]"
```

### Frontend Dev

```bash
cd inline_text_fields_component/frontend
npm install
npm install fast-levenshtein  # If not already in package.json dependencies
npm run dev
```

(Frontend typically runs on http://localhost:3001)

### Run Streamlit Example

Ensure `_RELEASE = False` in `inline_text_fields_component/__init__.py`.

From the project root:

```bash
streamlit run example.py
```

## Building for Production

### Build Frontend

```bash
cd inline_text_fields_component/frontend
npm run build
```

### Set Release Flag

Set `_RELEASE = True` in `inline_text_fields_component/__init__.py`.

### Build Python Package

From project root:

```bash
python setup.py sdist bdist_wheel
# or
python -m build
```

## License

MIT License. See LICENSE file.
