# inline_text_fields_component/__init__.py

import os
import streamlit.components.v1 as components
from typing import List, Dict, Optional, Literal, Tuple
import unicodedata  # For accent ignorance

# Attempt to import Levenshtein and provide guidance if not found
try:
    import Levenshtein
except ImportError:
    # This error will guide the user to install the necessary package.
    # You could also implement a pure Python fallback for Levenshtein distance,
    # but it would be significantly slower.
    raise ImportError(
        "The 'python-Levenshtein' package is required for the inline_text_fields component "
        "to calculate Levenshtein distance for 'acceptable' matches. "
        "Please install it by running: pip install python-Levenshtein"
    )

# --- Component Declaration ---
# Set to True when distributing your component
_RELEASE = True  # <<< YOU WILL CHANGE THIS TO True FOR YOUR BUILD

# Name of the component directory and the component in React
COMPONENT_NAME = "inline_text_fields_streamlit"

if not _RELEASE:
    # Point to the frontend dev server URL
    _component_func = components.declare_component(
        COMPONENT_NAME,
        url="http://localhost:3001",  # Default for Vite React dev server
    )
else:
    # Point to the build directory for the production version
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/dist")
    _component_func = components.declare_component(COMPONENT_NAME, path=build_dir)


# --- Type Definitions for Clarity ---
FrontendSegment = Dict[
    str, str
]  # e.g., {"type": "text", "content": "Hi"} or {"type": "field", "solution": "you"}
FrontendSentenceData = List[FrontendSegment]
FrontendSentencesData = List[FrontendSentenceData]

ValidationStatus = Literal["perfect", "acceptable", "false", "empty"]
UserAnswerAndValidation = Tuple[
    str, ValidationStatus
]  # (user_input_string, validation_status)
SentenceValidationOutput = List[UserAnswerAndValidation]
FullValidationOutput = List[SentenceValidationOutput]


# --- Helper Functions ---


def _normalize_text_for_validation(text: str, ignore_accents: bool) -> str:
    """
    Normalizes text for validation purposes: converts to lowercase and optionally removes accents.
    """
    normalized_text = text.lower()
    if ignore_accents:
        # NFKD normalization decomposes characters into base characters and combining marks (accents).
        # We then filter out these combining marks.
        nfkd_form = unicodedata.normalize("NFKD", normalized_text)
        normalized_text = "".join(
            [char for char in nfkd_form if not unicodedata.combining(char)]
        )
    return normalized_text


def _get_validation_status(
    user_input: str,
    correct_solution: str,
    ignore_accents: bool,
    max_levenshtein_distance: int,
) -> ValidationStatus:
    """
    Validates a single user input string against a correct solution string,
    applying normalization and Levenshtein distance rules.
    """
    is_user_input_effectively_empty = not user_input.strip()
    is_correct_solution_effectively_empty = not correct_solution.strip()

    # Handle cases where either or both strings are effectively empty
    if is_user_input_effectively_empty:
        return "perfect" if is_correct_solution_effectively_empty else "empty"
    # If user input is not empty but solution is, it's 'false' unless Levenshtein distance makes it 'acceptable'
    # This will be naturally handled by the comparison logic below.

    # Normalize texts for comparison
    norm_user_input = _normalize_text_for_validation(user_input, ignore_accents)
    norm_correct_solution = _normalize_text_for_validation(
        correct_solution, ignore_accents
    )

    if norm_user_input == norm_correct_solution:
        return "perfect"

    # If not a perfect match, check Levenshtein distance if applicable
    if max_levenshtein_distance > 0:
        # Ensure Levenshtein.distance is callable (it should be if import was successful)
        if not callable(getattr(Levenshtein, "distance", None)):
            raise RuntimeError(
                "Levenshtein.distance function not available. "
                "Ensure 'python-Levenshtein' is installed correctly."
            )

        distance = Levenshtein.distance(norm_user_input, norm_correct_solution)
        if distance <= max_levenshtein_distance:
            return "acceptable"

    return "false"  # Default if no other condition met


def _parse_delimiter_string(delimiter_str: str) -> tuple[str, str]:
    """
    Parses the delimiter string (e.g., "{}", "[[]]", "_") into start and end parts.
    Raises ValueError for invalid configurations.
    """
    n = len(delimiter_str)
    if n == 0:
        raise ValueError("Delimiter string cannot be empty.")
    if n == 1:  # Single character delimiter, e.g., "_" means "_solution_"
        return delimiter_str, delimiter_str
    if n % 2 != 0:  # Odd length > 1, e.g., "{}}" is ambiguous
        raise ValueError(
            f"Delimiter string '{delimiter_str}' has an odd length > 1, which is ambiguous. "
            "Use an even length (e.g., '{}', '[[]]') for distinct start/end parts, "
            "or a single character (e.g., '_') to use for both start and end."
        )
    # Even length, e.g., "{}" -> start="{", end="}"; "[[]]" -> start="[[", end="]]"
    midpoint = n // 2
    return delimiter_str[:midpoint], delimiter_str[midpoint:]


def _generate_frontend_segments(
    sentence_template: str, start_delimiter: str, end_delimiter: str
) -> FrontendSentenceData:
    """
    Parses a single sentence template string into a list of segments (text or field)
    for the frontend.
    Example: "Hello {name}!" with "{", "}" ->
             [{"type": "text", "content": "Hello "},
              {"type": "field", "solution": "name"},
              {"type": "text", "content": "!"}]
    """
    segments: FrontendSentenceData = []
    current_position = 0
    while current_position < len(sentence_template):
        try:
            # Find the next occurrence of the start delimiter from the current position
            start_delim_idx = sentence_template.index(start_delimiter, current_position)
        except ValueError:  # No more start delimiters found
            # Add any remaining part of the sentence as a text segment
            if current_position < len(sentence_template):
                segments.append(
                    {"type": "text", "content": sentence_template[current_position:]}
                )
            break  # Exit loop, sentence parsing is complete

        # Add the text segment before the found start delimiter (if any)
        if start_delim_idx > current_position:
            segments.append(
                {
                    "type": "text",
                    "content": sentence_template[current_position:start_delim_idx],
                }
            )

        # Determine where to search for the end delimiter.
        # This must be *after* the current start delimiter's content.
        search_for_end_from_idx = start_delim_idx + len(start_delimiter)
        try:
            # Find the corresponding end delimiter
            end_delim_idx = sentence_template.index(
                end_delimiter, search_for_end_from_idx
            )
        except ValueError:  # No matching end delimiter found
            # This indicates a malformed template (e.g., "Hello {name without closing brace").
            # Treat the rest of the sentence, including the unmatched start delimiter, as literal text.
            segments.append(
                {"type": "text", "content": sentence_template[start_delim_idx:]}
            )
            break  # Exit loop, cannot parse further reliably

        # Extract the solution text enclosed by the delimiters
        solution_text = sentence_template[search_for_end_from_idx:end_delim_idx]
        segments.append({"type": "field", "solution": solution_text})

        # Update current_position to continue parsing after the processed field
        current_position = end_delim_idx + len(end_delimiter)

    return segments


def _get_solutions_from_frontend_data(
    frontend_data: FrontendSentencesData,
) -> List[List[str]]:
    """
    Extracts all solutions from the parsed frontend data structure, maintaining
    the sentence and field order.
    """
    all_solutions_matrix: List[List[str]] = []
    for sentence_segments in frontend_data:
        solutions_in_sentence = [
            segment["solution"]
            for segment in sentence_segments
            if segment["type"] == "field"
        ]
        all_solutions_matrix.append(solutions_in_sentence)
    return all_solutions_matrix


# --- Main Component Function ---


def inline_text_fields(
    sentences_with_solutions: List[str],
    delimiter: str = "{}",
    ignore_accents: bool = False,
    accepted_levenshtein_distance: int = 0,
    render_results_in_frontend: bool = False,
    freeze: bool = False,
    key: Optional[str] = None,
    color_kwargs: dict[ValidationStatus, str] = {},
) -> FullValidationOutput:
    """
    Streamlit component for inline text field exercises.

    Displays sentences with blanks (defined by delimiters), collects user input,
    and returns both the input and its validation status.

    Parameters
    ----------
    sentences_with_solutions : List[str]
        List of sentence templates. Fields for user input are marked by `delimiter`.
        The content inside the delimiters is the correct answer.
        Example: ["The capital of {France} is Paris.", "An apple is a {fruit}."]

    delimiter : str, optional
        Delimiter for marking input fields.
        - 2 characters (e.g., "{}"): first is start, second is end (e.g., {answer}).
        - Even length > 2 (e.g., "[[]]"): split in half for start/end (e.g., [[answer]]).
        - 1 character (e.g., "_"): used for both start and end (_answer_).
        Default is "{}".

    ignore_accents : bool, optional
        If True, ignores accents during validation (e.g., "é" matches "e").
        Default is False.

    accepted_levenshtein_distance : int, optional
        Maximum Levenshtein distance for an answer to be "acceptable".
        0 means only exact matches (after normalization) are "perfect".
        Default is 0.

    render_results_in_frontend : bool, optional
        If True, the frontend visually indicates correctness of current inputs.
        Python always performs final validation.
        Default is False.

    freeze : bool, optional
        If True, all input fields will be disabled (non-editable) in the frontend.
        This is useful for displaying results after an interaction session.
        Default is False.


    key : str, optional
        Unique key for the component instance.
        Default is None.

    color_kwargs : Dict[ValidationStatus, str], optional
        Override default colors for validation states.
        Keys: "perfect", "acceptable", "false", "empty".
        Values: background color as a string (e.g., "#90EE90").
        Default is empty dict (frontend uses theme or hardcoded defaults).

    Returns
    -------
    FullValidationOutput : List[List[Tuple[str, ValidationStatus]]]
        Nested list structure matching sentences and their fields.
        Each tuple: (user input, validation status).
        Example: [[("France", "perfect")], [("friut", "acceptable"), ("red", "false")]]

    Raises
    ------
    ValueError
        If `accepted_levenshtein_distance` is negative.
        If `delimiter` is empty or ambiguous.
    """

    if accepted_levenshtein_distance < 0:
        raise ValueError("`accepted_levenshtein_distance` must be non-negative.")

    try:
        start_delim, end_delim = _parse_delimiter_string(delimiter)
    except ValueError as e:
        # Re-raise with more context or let the original error propagate with its message
        raise ValueError(
            f"Invalid `delimiter` configuration: '{delimiter}'. Error: {e}"
        )

    # 1. Parse sentences into a data structure for the frontend
    # This structure includes text segments and field segments (with their solutions).
    frontend_input_data: FrontendSentencesData = []
    for sentence_template_str in sentences_with_solutions:
        frontend_input_data.append(
            _generate_frontend_segments(sentence_template_str, start_delim, end_delim)
        )

    # 2. Extract correct solutions for Python-side validation and for determining default input structure
    correct_solutions_matrix = _get_solutions_from_frontend_data(frontend_input_data)

    # 3. Determine the default return structure for Streamlit (empty inputs for all fields)
    # This is what Streamlit uses if the component hasn't been interacted with yet.
    default_component_return_value: List[List[str]] = [
        ["" for _ in range(len(sentence_sols))]
        for sentence_sols in correct_solutions_matrix
    ]

    # 4. Prepare arguments to pass to the React component
    component_payload = {
        "sentences_data": frontend_input_data,  # Parsed structure with text/field segments and solutions
        "render_results_mode": render_results_in_frontend,
        "validation_rules_for_frontend": {  # Rules for frontend if it does its own styling/validation
            "ignore_accents": ignore_accents,
            "accepted_levenshtein_distance": accepted_levenshtein_distance,
        },
        "color_kwargs": color_kwargs,
        "freeze_inputs": freeze,
    }

    # 5. Call the frontend component
    # The frontend is expected to return a List[List[str]] representing raw user inputs for each field.
    raw_user_inputs_from_frontend: Optional[List[List[str]]] = _component_func(
        **component_payload, key=key, default=default_component_return_value
    )

    # If frontend returns None (e.g., on initial render before any interaction),
    # use the default empty inputs for the validation step.
    current_raw_user_inputs = (
        raw_user_inputs_from_frontend
        if raw_user_inputs_from_frontend is not None
        else default_component_return_value
    )

    # 6. Perform Python-side validation on the received (or default) raw inputs
    final_output_with_validation: FullValidationOutput = []

    for i, sentence_user_inputs in enumerate(current_raw_user_inputs):
        validated_sentence_inputs: SentenceValidationOutput = []
        # Ensure sentence index is valid for the solutions matrix
        if i < len(correct_solutions_matrix):
            solutions_for_this_sentence = correct_solutions_matrix[i]
            for j, single_user_input_str in enumerate(sentence_user_inputs):
                # Ensure field index is valid for this sentence's solutions
                if j < len(solutions_for_this_sentence):
                    correct_solution_str = solutions_for_this_sentence[j]
                    status = _get_validation_status(
                        single_user_input_str,
                        correct_solution_str,
                        ignore_accents,
                        accepted_levenshtein_distance,
                    )
                    validated_sentence_inputs.append((single_user_input_str, status))
                else:
                    # This case implies more inputs received for a sentence than solutions exist.
                    # Should ideally not happen if frontend respects the parsed structure.
                    # Handle defensively: mark as 'false'.
                    validated_sentence_inputs.append((single_user_input_str, "false"))
            final_output_with_validation.append(validated_sentence_inputs)
        else:
            # This case implies more sentences in user inputs than in original `sentences_with_solutions`.
            # Also defensive: mark all inputs in this unexpected sentence as 'false'.
            final_output_with_validation.append(
                [(input_str, "false") for input_str in sentence_user_inputs]
            )

    return final_output_with_validation
