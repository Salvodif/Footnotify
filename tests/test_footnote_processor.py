# tests/test_footnote_processor.py
import pytest
import os

from footnote_processor import (
    preprocess_footnote_for_parsing,
    parse_and_match_footnote,
    format_parsed_footnote,
    get_formatted_and_colored_footnote_segments,
    _parse_html_like_tags_to_format_list
)
from settings_parser import load_settings

# Attempt to import sample data. Adjust names if the worker used different ones.
try:
    # The instruction specified all_sample_footnotes as the variable in sample_footnote_data.py
    from tests.sample_footnote_data import all_sample_footnotes 
    # Based on the sample_footnote_data.py content, each item in all_sample_footnotes 
    # is a dictionary containing various expected keys.
    # We will use this comprehensive list directly.
    sample_data_for_tests = all_sample_footnotes

except ImportError:
    # Provide default empty lists if the file or variables are not found, so tests can be collected.
    # Tests relying on this data will likely be skipped or fail gracefully.
    print("Warning: Could not import all_sample_footnotes from tests.sample_footnote_data.py. Some tests may be skipped.")
    sample_data_for_tests = []


# Load test settings
TEST_SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'test_settings.yaml')
test_settings = load_settings(TEST_SETTINGS_FILE)
if not test_settings:
    print(f"Warning: Test settings file '{TEST_SETTINGS_FILE}' could not be loaded or is empty. Tests requiring settings will be skipped.")

# --- Test preprocess_footnote_for_parsing ---
# Basic cases
raw_data_simple = [[("Hello ", {}), ("World", {'italic': True})]]
expected_simple_preprocess = "Hello <i>World</i>"

raw_data_bold_underline = [[("Test ", {'bold': True}), ("example", {'underline': True})]]
expected_bold_underline_preprocess = "<b>Test </b><u>example</u>"

# Example with multiple text runs in one paragraph and multiple paragraphs
raw_data_multi_run_para = [
    [("Part1 ", {}), ("<i>italic</i> ", {'bold': True}), ("end.", {})], # pre-existing italic tag in text, then bolded
    [("Second para.", {})]
]
expected_multi_run_para_preprocess = "Part1 <b><i>italic</i> </b>end. Second para."

# From sample_footnote_data.py (footnote_preprocess_1_raw in previous versions, now check all_sample_footnotes)
# This specific case was: footnote_preprocess_1_raw = [[("Text1 ", {'bold': True}),("Text2", {'italic': True, 'bold': True}),(" Text3", {'underline': True})]]
# Expected: "<b>Text1 </b><b><i>Text2</i></b><u> Text3</u>"
# Find it in the sample_data_for_tests if it exists or add it explicitly.
# For now, adding explicitly as it was a specific preprocess test case.
raw_data_complex_styling = [[("Text1 ", {'bold': True}),("Text2", {'italic': True, 'bold': True}),(" Text3", {'underline': True})]]
expected_complex_styling_preprocess = "<b>Text1 </b><b><i>Text2</i></b><u> Text3</u>"


@pytest.mark.parametrize("raw_input, expected_output", [
    (raw_data_simple, expected_simple_preprocess),
    (raw_data_bold_underline, expected_bold_underline_preprocess),
    (raw_data_multi_run_para, expected_multi_run_para_preprocess),
    (raw_data_complex_styling, expected_complex_styling_preprocess)
])
def test_preprocess_footnote_for_parsing(raw_input, expected_output):
    assert preprocess_footnote_for_parsing(raw_input) == expected_output

# --- Test _parse_html_like_tags_to_format_list (internal helper) ---
@pytest.mark.parametrize("html_input, expected_segments", [
    ("Hello <i>World</i>", [("Hello ", {'italic': False, 'bold': False, 'underline': False}), ("World", {'italic': True, 'bold': False, 'underline': False})]),
    ("<b>Test</b> <u>Under</u>", [("Test", {'italic': False, 'bold': True, 'underline': False}), (" ", {'italic': False, 'bold': False, 'underline': False}), ("Under", {'italic': False, 'bold': False, 'underline': True})]),
    ("No tags", [("No tags", {'italic': False, 'bold': False, 'underline': False})]),
    ("<i>Nested <b>bold</b></i>", [("Nested ", {'italic': True, 'bold': False, 'underline': False}), ("bold", {'italic': True, 'bold': True, 'underline': False})]),
    ("<i>Sequential</i><b>Bold</b>", [("Sequential", {'italic': True, 'bold': False, 'underline': False}), ("Bold", {'italic': False, 'bold': True, 'underline': False})]),
    ("Text <html> <unsupported> tags.", [("Text <html> <unsupported> tags.", {'italic': False, 'bold': False, 'underline': False})]),
    (" leading space and <b>bold</b> trailing space ", [
        (" leading space and ", {'italic': False, 'bold': False, 'underline': False}),
        ("bold", {'italic': False, 'bold': True, 'underline': False}),
        (" trailing space ", {'italic': False, 'bold': False, 'underline': False}),
    ]),
    ("<i></i>", []), # Empty tag
    ("<i> </i>", [(" ", {'italic': True, 'bold': False, 'underline': False})]), # Tag with only space
    ("<b><i><u>All three</u></i></b>", [("All three", {'italic': True, 'bold': True, 'underline': True})]),
    ("Adjacent: <b>Bold</b><i>Italic</i>", [("Bold",{'italic': False, 'bold': True, 'underline': False}), ("Italic",{'italic': True, 'bold': False, 'underline': False})])
])
def test_parse_html_like_tags_to_format_list(html_input, expected_segments):
    assert _parse_html_like_tags_to_format_list(html_input) == expected_segments
    
# --- Test parse_and_match_footnote ---
param_parse_match = []
if sample_data_for_tests and test_settings:
    # Each item in sample_data_for_tests is a dictionary (expected_spec)
    param_parse_match = [(item['raw_data'], item) for item in sample_data_for_tests]
else:
    print("Warning: Skipping most parse_and_match_footnote tests due to missing data or settings.")

@pytest.mark.parametrize("raw_footnote_data, expected_spec", param_parse_match)
def test_parse_and_match_footnote(raw_footnote_data, expected_spec):
    if not test_settings: pytest.skip("Skipping test_parse_and_match_footnote due to missing test settings.")
    # It's possible for raw_footnote_data to be legitimately empty (e.g., representing an empty footnote)
    # So, we don't skip if raw_footnote_data is empty, but tests should handle it.
    # if not raw_footnote_data: pytest.skip("Skipping test_parse_and_match_footnote due to missing raw_footnote_data in spec.")


    result = parse_and_match_footnote(raw_footnote_data, test_settings)

    assert result['matched_type'] == expected_spec.get('expected_match_type')
    assert result['confidence'] == expected_spec.get('expected_confidence')
    
    # Check preprocessed_text consistency against the expected preprocessed text in the spec
    assert result['preprocessed_text'] == expected_spec.get('preprocessed_text')

    if result['matched_type'] is None:
        # For unmatched notes, check if preprocessed_text is present in parsed_fields
        assert 'preprocessed_text' in result['parsed_fields'], \
            f"parsed_fields should contain preprocessed_text for unmatched note: {expected_spec.get('name')}"
        assert result['parsed_fields']['preprocessed_text'] == result['preprocessed_text']
    else:
        # Compare key parsed fields.
        if 'expected_fields' in expected_spec:
            for field_name, expected_value in expected_spec['expected_fields'].items():
                assert result['parsed_fields'].get(field_name) == expected_value, \
                    f"Field '{field_name}' mismatch for {expected_spec.get('name')}"

# --- Test format_parsed_footnote ---
param_format_footnote = []
if sample_data_for_tests and test_settings:
    param_format_footnote = [(item['raw_data'], item) for item in sample_data_for_tests]
else:
    print("Warning: Skipping most format_parsed_footnote tests due to missing data or settings.")

@pytest.mark.parametrize("raw_footnote_data, expected_spec", param_format_footnote)
def test_format_parsed_footnote(raw_footnote_data, expected_spec):
    if not test_settings: pytest.skip("Skipping test_format_parsed_footnote due to missing test settings.")
    # if not raw_footnote_data: pytest.skip("Skipping test_format_parsed_footnote due to missing raw_footnote_data in spec.")

    parsed_output = parse_and_match_footnote(raw_footnote_data, test_settings)
    
    formatted_segments = format_parsed_footnote(
        parsed_output['matched_type'],
        parsed_output['parsed_fields'],
        test_settings
    )

    assert isinstance(formatted_segments, list)
    
    # Compare with expected_formatted_segments if available in the spec
    if 'expected_formatted_segments' in expected_spec:
        assert formatted_segments == expected_spec['expected_formatted_segments'], \
            f"Formatted segments mismatch for {expected_spec.get('name')}"
    elif parsed_output['matched_type'] is None:
        # If no specific expected format, for unmatched, compare with parsing preprocessed_text
        expected_unmatched_segments = _parse_html_like_tags_to_format_list(parsed_output['preprocessed_text'])
        assert formatted_segments == expected_unmatched_segments, \
            f"Formatted segments for unmatched note {expected_spec.get('name')} differ from parsed preprocessed text."
    else:
        # For matched notes, ensure non-empty if template and fields exist and input was not empty
        if parsed_output['preprocessed_text']: 
            is_special_classic_match = parsed_output['matched_type'] == 'special_classic' and \
                                       parsed_output['parsed_fields'].get('full_citation')
            
            ref_type_config = test_settings.get('reference_types', {}).get(parsed_output['matched_type'], {})
            is_ref_type_match = ref_type_config.get('template') and parsed_output['parsed_fields']
            
            if is_special_classic_match or is_ref_type_match:
                 assert len(formatted_segments) > 0, \
                    f"Formatted segments should not be empty for a matched type with content: {expected_spec.get('name')}."
        elif not parsed_output['preprocessed_text']: # an empty footnote initially
                 assert len(formatted_segments) == 0, \
                    f"Formatted segments should be empty for an initially empty footnote: {expected_spec.get('name')}."


# --- Test get_formatted_and_colored_footnote_segments ---
param_color_footnote = []
if sample_data_for_tests and test_settings:
    param_color_footnote = [(item['raw_data'], item) for item in sample_data_for_tests]
else:
    print("Warning: Skipping most get_formatted_and_colored_footnote_segments tests due to missing data or settings.")

@pytest.mark.parametrize("raw_footnote_data, expected_spec", param_color_footnote)
def test_get_formatted_and_colored_footnote_segments(raw_footnote_data, expected_spec):
    if not test_settings: pytest.skip("Skipping test_get_formatted_and_colored_footnote_segments due to missing test settings.")
    # if not raw_footnote_data: pytest.skip("Skipping test_get_formatted_and_colored_footnote_segments due to missing raw_footnote_data in spec.")

    parsed_output = parse_and_match_footnote(raw_footnote_data, test_settings)
    
    colored_segments = get_formatted_and_colored_footnote_segments(
        parsed_output['matched_type'],
        parsed_output['parsed_fields'],
        test_settings,
        parsed_output['confidence']
    )

    assert isinstance(colored_segments, list)
    
    if not parsed_output['preprocessed_text']: 
        assert not colored_segments, f"Colored segments should be empty if original text was empty: {expected_spec.get('name')}."
        return
    
    expected_plain_segments = format_parsed_footnote(
        parsed_output['matched_type'], 
        parsed_output['parsed_fields'], 
        test_settings
    )
    if not expected_plain_segments: 
        assert not colored_segments, f"Colored segments should be empty if formatting results in no segments: {expected_spec.get('name')}."
        return 

    assert len(colored_segments) > 0, f"Colored segments should not be empty if original text was present and formatting yields segments: {expected_spec.get('name')}."

    expected_color_val = None
    confidence = parsed_output['confidence']
    if confidence == 'green': expected_color_val = '#00AA00'
    elif confidence == 'yellow': expected_color_val = '#B8860B'
    elif confidence == 'red': expected_color_val = '#AA0000'

    for text, fmt_dict in colored_segments:
        assert fmt_dict.get('color') == expected_color_val, \
            f"Segment color mismatch for {expected_spec.get('name')}. Expected {expected_color_val} (confidence: {confidence}), got {fmt_dict.get('color')}"

```
