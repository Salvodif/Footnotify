import re

def preprocess_footnote_for_parsing(raw_footnote_data: list[list[tuple[str, dict[str, bool]]]]) -> str:
    """
    Converts raw footnote data (list of paragraphs, each a list of text runs)
    into a single string with simple HTML-like tags for formatting.

    Args:
        raw_footnote_data: A list of paragraphs. Each paragraph is a list of tuples,
                           where each tuple contains a text string and a dictionary
                           of formatting options (e.g., {'italic': True}).

    Returns:
        A single string with formatting tags (<i>, <b>, <u>) and normalized whitespace.
    """
    processed_parts = []
    for paragraph in raw_footnote_data:
        for text, formatting in paragraph:
            if not text: # Skip empty text runs
                continue
            
            current_text = text
            # Apply tags: order might matter if complex nesting is ever needed,
            # but for now, sequential is fine.
            if formatting.get('italic'):
                current_text = f"<i>{current_text}</i>"
            if formatting.get('bold'):
                current_text = f"<b>{current_text}</b>"
            if formatting.get('underline'): # Assuming 'underline' or 'underlined'
                current_text = f"<u>{current_text}</u>"
            processed_parts.append(current_text)
    
    # Join all parts, then normalize whitespace
    full_text = "".join(processed_parts)
    full_text = ' '.join(full_text.split()) # Replace multiple spaces with single, trim
    return full_text.strip()


def parse_and_match_footnote(
    raw_footnote_data: list[list[tuple[str, dict[str, bool]]]],
    settings: dict
) -> dict:
    """
    Parses a raw footnote, attempts to match it against special classics and
    defined reference types, and extracts fields.

    Args:
        raw_footnote_data: The raw footnote data from extract_notes.py.
        settings: The loaded settings from settings.yaml.

    Returns:
        A dictionary containing:
        - 'matched_type': The type of reference matched (str) or None.
        - 'parsed_fields': Extracted data from the footnote (dict).
        - 'preprocessed_text': The footnote text after preprocessing (str).
        - 'confidence': A string indicating match confidence ('high', 'medium', 'low').
    """
    preprocessed_text = preprocess_footnote_for_parsing(raw_footnote_data)

    # 1. Special Classics Matching
    if 'special_classics' in settings:
        for abbr, full_text_template in settings['special_classics'].items():
            # Simple check: does the preprocessed text start with the abbreviation?
            # This might need to be more flexible (e.g., allowing for surrounding punctuation)
            # For example, "STh." or "STh,"
            # A simple way is to check if preprocessed_text starts with abbr
            # or abbr followed by a common punctuation mark.
            # For now, a direct startswith or a pattern matching the abbreviation followed by common punctuation
            # like '.', ',', ' ', '(', etc.
            # A more robust way would be to use regex for the abbreviation itself if needed.
            # For example, if abbr is "STh", it might appear as "STh.", "STh,", "STh ", etc.
            
            # Let's try a slightly more robust check for abbreviation
            # We are looking for the abbreviation at the beginning of the text.
            # The abbreviation in special_classics is the key (e.g. "STh")
            # The preprocessed_text might be "STh. I-II, q. 1, a. 1." or "DS 123."
            # We check if preprocessed_text starts with the abbreviation.
            # We should also consider cases like "STh." (with a period) even if abbr is "STh"
            
            # Using a regex to check for the abbreviation at the beginning of the string,
            # possibly followed by non-alphanumeric characters.
            # Example: if abbr is "STh", this regex will match "STh.", "STh,", "STh ", "STh(", etc.
            # but not "SThompson"
            abbr_pattern = r"^{}(?=\W|$)".format(re.escape(abbr))
            if re.search(abbr_pattern, preprocessed_text, re.IGNORECASE): # Making it case-insensitive for abbreviation
                return {
                    'matched_type': 'special_classic',
                    'parsed_fields': {'abbreviation': abbr, 'full_citation': full_text_template},
                    'preprocessed_text': preprocessed_text,
                    'confidence': 'match' 
                }

    # 2. Reference Type Matching
    # Store potential matches and then decide the best one if multiple types match
    # For now, we take the first one that meets criteria.
    # This could be enhanced later to pick the "best" match if multiple types parse successfully.
    
    best_match_so_far = {
        'matched_type': None,
        # Ensure preprocessed_text is available in parsed_fields if no match, for format_parsed_footnote
        'parsed_fields': {'preprocessed_text': preprocessed_text} if True else {}, # Condition is a placeholder
        'preprocessed_text': preprocessed_text,
        'confidence': 'no_match' # Changed from 'red'
    }
    # Refined logic for initial best_match_so_far.parsed_fields:
    if best_match_so_far['matched_type'] is None:
        best_match_so_far['parsed_fields'] = {'preprocessed_text': preprocessed_text}


    if 'reference_types' in settings:
        for ref_type_name, ref_type_config in settings['reference_types'].items():
            extracted_data = {}
            
            defined_fields = ref_type_config.get('fields', {})
            if not isinstance(defined_fields, dict):
                continue # Skip if 'fields' is not a dict

            for field_name, field_regex in defined_fields.items():
                if not field_regex: 
                    continue
                try:
                    match = re.search(field_regex, preprocessed_text)
                    if match and field_name in match.groupdict():
                        value = match.group(field_name)
                        extracted_data[field_name] = value.strip() if value is not None else None
                except re.error:
                    pass # Ignore regex errors for now

            required_fields = ref_type_config.get('required_fields', [])
            all_required_found = True
            for req_field in required_fields:
                if req_field not in extracted_data or not extracted_data[req_field]:
                    all_required_found = False
                    break
            
            if all_required_found and (extracted_data or not required_fields): # Must find all required, and extract something if no required fields
                # First type that matches all its required fields is considered the match.
                best_match_so_far = {
                    'matched_type': ref_type_name,
                    'parsed_fields': extracted_data,
                    'preprocessed_text': preprocessed_text,
                    'confidence': 'match'
                }
                break # Exit loop once a match is found

    return best_match_so_far


if __name__ == '__main__':
    print("Running example usage for footnote_processor.py...")

    # Dummy settings (simplified version of settings.yaml content)
    dummy_settings = {
        "reference_types": {
            "book": {
                "template": "Author, <i>Title</i> (Place: Publisher, Date).",
                "fields": {
                    "Author": r"^(?P<Author>[A-Za-z\s,.]+?),", # Simplified
                    "Title": r"<i>(?P<Title>.+?)</i>",
                    "Place": r"\((?P<Place>[^:]+):",
                    "Publisher": r":\s*(?P<Publisher>[^,]+),",
                    "Date": r",\s*(?P<Date>\d{4})\)\."
                },
                "required_fields": ["Author", "Title", "Date"]
            },
            "journalArticle": {
                "template": "Author, \"ArticleTitle,\" <i>JournalName</i> Volume, no. Issue (Date): Pages.",
                "fields": {
                    "Author": r"^(?P<Author>[A-Za-z\s,.]+?),",
                    "ArticleTitle": r"\"(?P<ArticleTitle>.+?)\"",
                    "JournalName": r"<i>(?P<JournalName>.+?)</i>",
                    "Volume": r"<i>[^<]+</i>\s+(?P<Volume>\d+),", # Assuming volume follows JournalName
                    "Date": r"\((?P<Date>\d{4})\)",
                    "Pages": r":\s*(?P<Pages>[\d\s-]+)\."
                },
                "required_fields": ["Author", "ArticleTitle", "JournalName", "Date"]
            },
             "webPage": {
                "template": "Author, \"PageTitle,\" <i>WebsiteName</i>, DatePublished, URL.",
                "fields": {
                    "Author": r"^(?P<Author>[A-Za-z\s,.]+?),?", # Optional author
                    "PageTitle": r"\"(?P<PageTitle>.+?)\"",
                    "WebsiteName": r"<i>(?P<WebsiteName>.+?)</i>",
                    "DatePublished": r"<i>[^<]+</i>,\s*(?P<DatePublished>\w+\s\d{1,2},\s\d{4}),",
                    "URL": r",\s*(?P<URL>https?://[^\s]+)\."
                },
                "required_fields": ["PageTitle", "WebsiteName", "URL"]
            }
        },
        "special_classics": {
            "STh": "Thomas Aquinas, <i>Summa Theologiae</i>",
            "DS": "Denzinger Schönmetzer, <i>Enchiridion Symbolorum</i>"
        }
    }

    # --- Test preprocess_footnote_for_parsing ---
    print("\n--- Testing preprocess_footnote_for_parsing ---")
    test_raw_1 = [[("Hello ", {'italic': False, 'bold': False}), ("World", {'italic': True, 'bold': False})]]
    print(f"Input: {test_raw_1}")
    print(f"Output: \"{preprocess_footnote_for_parsing(test_raw_1)}\" (Expected: \"Hello <i>World</i>\")")

    test_raw_2 = [[("Multi ", {}), ("<i>styling</i> ", {'bold': True}), ("here.", {'underline': True, 'italic':True})]]
    # Expected: "Multi <b>&lt;i&gt;styling&lt;/i&gt;</b> <i><u>here.</u></i>" (if tags don't strip existing ones)
    # Or "Multi <b>styling</b> <i><u>here.</u></i>" if tags are applied to original text.
    # Current logic: "Multi <b>&lt;i&gt;styling&lt;/i&gt;</b> <i><u>here.</u></i>" - No, it should be "Multi <b><i>styling</i></b> <i><u>here.</u></i>"
    # Let's re-verify the preprocess logic. It applies tags sequentially.
    # ('<i>styling</i> ', {'bold': True}) -> "<b><i>styling</i> </b>"
    # ('here.', {'underline': True, 'italic':True}) -> "<i><u>here.</u></i>"
    # Result: "Multi <b><i>styling</i> </b> <i><u>here.</u></i>" (with space normalization)
    print(f"Input: {test_raw_2}")
    print(f"Output: \"{preprocess_footnote_for_parsing(test_raw_2)}\" (Expected: \"Multi <b><i>styling</i></b> <i><u>here.</u></i>\")")
    
    test_raw_3 = [[("   Leading and trailing spaces   ", {})], [("Next para with  multiple   spaces.", {'italic':True})]]
    print(f"Input: {test_raw_3}")
    print(f"Output: \"{preprocess_footnote_for_parsing(test_raw_3)}\" (Expected: \"Leading and trailing spaces <i>Next para with multiple spaces.</i>\")")

    # --- Test parse_and_match_footnote ---
    print("\n--- Testing parse_and_match_footnote ---")

    # Test 1: Book
    footnote_book_raw = [
        [
            ("Doe, John", {'italic': False}), 
            (", ", {'italic': False}), 
            ("The Big Book of Examples", {'italic': True}),
            (" (Anytown: Big Publisher, ", {'italic': False}),
            ("2023", {'italic': False}),
            (").", {'italic': False})
        ]
    ]
    # Expected preprocessed: "Doe, John, <i>The Big Book of Examples</i> (Anytown: Big Publisher, 2023)."
    result_book = parse_and_match_footnote(footnote_book_raw, dummy_settings)
    print(f"\nInput (Book): {preprocess_footnote_for_parsing(footnote_book_raw)}")
    print(f"Match Result: {result_book['matched_type']}, Confidence: {result_book['confidence']}")
    print(f"Parsed Fields: {result_book['parsed_fields']}")
    assert result_book['matched_type'] == 'book'
    assert result_book['parsed_fields'].get('Author') == "Doe, John"
    assert result_book['parsed_fields'].get('Title') == "The Big Book of Examples"
    assert result_book['parsed_fields'].get('Date') == "2023"


    # Test 2: Special Classic (STh)
    footnote_sth_raw = [[("STh", {}), (". I, q. 1, a. 1.", {})]]
    # Expected preprocessed: "STh. I, q. 1, a. 1."
    result_sth = parse_and_match_footnote(footnote_sth_raw, dummy_settings)
    print(f"\nInput (STh): {preprocess_footnote_for_parsing(footnote_sth_raw)}")
    print(f"Match Result: {result_sth['matched_type']}, Confidence: {result_sth['confidence']}")
    print(f"Parsed Fields: {result_sth['parsed_fields']}")
    assert result_sth['matched_type'] == 'special_classic'
    assert result_sth['parsed_fields'].get('abbreviation') == 'STh'

    # Test 3: Special Classic (DS) - with more text
    footnote_ds_raw = [[("DS", {}), (" 123, an important point.", {})]]
    # Expected preprocessed: "DS 123, an important point."
    result_ds = parse_and_match_footnote(footnote_ds_raw, dummy_settings)
    print(f"\nInput (DS): {preprocess_footnote_for_parsing(footnote_ds_raw)}")
    print(f"Match Result: {result_ds['matched_type']}, Confidence: {result_ds['confidence']}")
    print(f"Parsed Fields: {result_ds['parsed_fields']}")
    assert result_ds['matched_type'] == 'special_classic'
    assert result_ds['parsed_fields'].get('abbreviation') == 'DS'
    
    # Test 4: Journal Article
    footnote_journal_raw = [
        [
            ("Smith, Jane", {}),
            (", ", {}),
            ("\"A Study of Patterns,\"", {}), # ArticleTitle
            (" ", {}),
            ("Journal of Obscure Studies", {'italic': True}), # JournalName
            (" ", {}),
            ("10", {}), # Volume
            (", no. 2 (", {}),
            ("2020", {}), # Date
            ("): ", {}),
            ("100-110", {}), # Pages
            (".", {})
        ]
    ]
    # Expected preprocessed: "Smith, Jane, "A Study of Patterns," <i>Journal of Obscure Studies</i> 10, no. 2 (2020): 100-110."
    # The regex for Volume in dummy_settings is: r"<i>[^<]+</i>\s+(?P<Volume>\d+),"
    # This expects JournalName, then space, then Volume, then comma.
    # Preprocessed text: "Smith, Jane, "A Study of Patterns," <i>Journal of Obscure Studies</i> 10, no. 2 (2020): 100-110."
    # Let's adjust raw data or regex to match. The current regex expects a comma after Volume.
    # "<i>Journal of Obscure Studies</i> 10,"
    # Corrected raw data for journal to ensure Volume regex matches:
    footnote_journal_raw_corrected = [
        [
            ("Smith, Jane", {}), (", ", {}),
            ("\"A Study of Patterns,\"", {}), (" ", {}), # ArticleTitle
            ("Journal of Obscure Studies", {'italic': True}), # JournalName
            (" ", {}), ("10", {}), (",", {}), # Volume followed by a comma
            (" no. 2 (", {}), ("2020", {}), # Date
            ("): ", {}), ("100-110", {}), (".", {}) # Pages
        ]
    ]
    result_journal = parse_and_match_footnote(footnote_journal_raw_corrected, dummy_settings)
    print(f"\nInput (Journal): {preprocess_footnote_for_parsing(footnote_journal_raw_corrected)}")
    print(f"Match Result: {result_journal['matched_type']}, Confidence: {result_journal['confidence']}")
    print(f"Parsed Fields: {result_journal['parsed_fields']}")
    assert result_journal['matched_type'] == 'journalArticle'
    assert result_journal['parsed_fields'].get('Author') == "Smith, Jane"
    assert result_journal['parsed_fields'].get('ArticleTitle') == "A Study of Patterns," # Note: comma included by regex
    assert result_journal['parsed_fields'].get('JournalName') == "Journal of Obscure Studies"
    assert result_journal['parsed_fields'].get('Volume') == "10"
    assert result_journal['parsed_fields'].get('Date') == "2020"


    # Test 5: Web Page
    footnote_web_raw = [
        [
            ("Techie, Tom", {}), (", ", {}),
            ("\"Latest Gadgets,\"", {}), (" ", {}),
            ("Gadget Review Site", {'italic': True}), (", ", {}), # WebsiteName
            ("October 26, 2023", {}), (", ", {}), # DatePublished
            ("https://example.com/gadgets", {}), (".", {}) # URL
        ]
    ]
    # The regex for DatePublished in dummy_settings is: r"<i>[^<]+</i>,\s*(?P<DatePublished>\w+\s\d{1,2},\s\d{4}),"
    # This expects WebsiteName in italics, then comma, then DatePublished, then comma.
    # Preprocessed: "Techie, Tom, "Latest Gadgets," <i>Gadget Review Site</i>, October 26, 2023, https://example.com/gadgets."
    result_web = parse_and_match_footnote(footnote_web_raw, dummy_settings)
    print(f"\nInput (Web): {preprocess_footnote_for_parsing(footnote_web_raw)}")
    print(f"Match Result: {result_web['matched_type']}, Confidence: {result_web['confidence']}")
    print(f"Parsed Fields: {result_web['parsed_fields']}")
    assert result_web['matched_type'] == 'webPage'
    assert result_web['parsed_fields'].get('PageTitle') == "Latest Gadgets,"
    assert result_web['parsed_fields'].get('WebsiteName') == "Gadget Review Site"
    assert result_web['parsed_fields'].get('DatePublished') == "October 26, 2023" # Comma is part of regex for DatePublished field
    assert result_web['parsed_fields'].get('URL') == "https://example.com/gadgets"

    # Test 6: No Match
    footnote_nomatch_raw = [[("Just some random text here.", {})]]
    result_nomatch = parse_and_match_footnote(footnote_nomatch_raw, dummy_settings)
    print(f"\nInput (No Match): {preprocess_footnote_for_parsing(footnote_nomatch_raw)}")
    print(f"Match Result: {result_nomatch['matched_type']}, Confidence: {result_nomatch['confidence']}")
    print(f"Parsed Fields: {result_nomatch['parsed_fields']}")
    assert result_nomatch['matched_type'] is None
    assert result_nomatch['confidence'] == 'low'

    # Test 7: Preprocessing - complex nesting and whitespace
    test_raw_complex = [
        [("  Start  ", {}), ("boldly", {'bold': True}), ("  and ", {}), ("<i>italicly</i>", {'italic': True, 'bold':True}), ("  end.  ", {})],
        [("  Second paragraph with  ", {}), ("<u>underline</u>", {'underline':True}), (" and ", {}), ("<b>bold</b>", {'bold':True}), (" and ", {}), ("<i>italic</i>", {'italic':True}), (" mix. ", {})]
    ]
    # Expected: "Start <b>boldly</b> and <b><i><i>italicly</i></i></b> end. Second paragraph with <u>underline</u> and <b>bold</b> and <i>italic</i> mix."
    # The `<i>italicly</i>` with bold:True and italic:True will become `<b><i><i>italicly</i></i></b>` if `<i>` is part of the text.
    # Let's assume the text itself doesn't contain tags, so it would be: `<b><i>italicly</i></b>`
    # preprocess_footnote_for_parsing logic:
    # 1. ('<i>italicly</i>', {'italic': True, 'bold':True})
    #    text = "<i>italicly</i>"
    #    italic: current_text = "<i><i>italicly</i></i>"
    #    bold: current_text = "<b><i><i>italicly</i></i></b>"
    # This is correct based on the current logic.
    processed_complex = preprocess_footnote_for_parsing(test_raw_complex)
    print(f"\nInput (Complex Preprocessing): {test_raw_complex}")
    print(f"Output: \"{processed_complex}\"")
    # Expected based on sequential application:
    # "Start <b>boldly</b> and <b><i>&lt;i&gt;italicly&lt;/i&gt;</i></b> end. Second paragraph with <u>underline</u> and <b>bold</b> and <i>italic</i> mix."
    # No, if the input text is "<i>italicly</i>", then italic:True makes it "<i><i>italicly</i></i>", then bold:True makes it "<b><i><i>italicly</i></i></b>".
    # This seems like a reasonable interpretation for now.
    # If input was ('italicly', {'italic': True, 'bold':True}), it would be "<b><i>italicly</i></b>".
    # Let's adjust test_raw_complex to not have tags in the text itself.
    test_raw_complex_clean = [
        [("  Start  ", {}), ("boldly", {'bold': True}), ("  and ", {}), ("italicly", {'italic': True, 'bold':True}), ("  end.  ", {})],
        [("  Second paragraph with  ", {}), ("underline", {'underline':True}), (" and ", {}), ("bold", {'bold':True}), (" and ", {}), ("italic", {'italic':True}), (" mix. ", {})]
    ]
    processed_complex_clean = preprocess_footnote_for_parsing(test_raw_complex_clean)
    print(f"Input (Complex Preprocessing - Clean Text): {test_raw_complex_clean}")
    print(f"Output (Clean Text): \"{processed_complex_clean}\"")
    expected_complex_clean = "Start <b>boldly</b> and <b><i>italicly</i></b> end. Second paragraph with <u>underline</u> and <b>bold</b> and <i>italic</i> mix."
    assert processed_complex_clean == expected_complex_clean
    print("\nExample usage completed.")

    # Test with a footnote that should match book but is missing a required field (Date)
    footnote_book_missing_req_raw = [
        [
            ("Doe, John", {'italic': False}), 
            (", ", {'italic': False}), 
            ("The Incomplete Book", {'italic': True}),
            (" (Anytown: Big Publisher).", {'italic': False}) # No date
        ]
    ]
    result_book_missing = parse_and_match_footnote(footnote_book_missing_req_raw, dummy_settings)
    print(f"\nInput (Book missing Date): {preprocess_footnote_for_parsing(footnote_book_missing_req_raw)}")
    print(f"Match Result: {result_book_missing['matched_type']}, Confidence: {result_book_missing['confidence']}")
    print(f"Parsed Fields: {result_book_missing['parsed_fields']}")
    assert result_book_missing['matched_type'] is None # Should be None as Date is required for book
    assert result_book_missing['confidence'] == 'low'
    
    print("\nAll assertions in example usage passed.")


# --- HTML-like tag parsing helper ---
def _parse_html_like_tags_to_format_list(text_with_tags: str) -> list[tuple[str, dict[str, bool]]]:
    """
    Parses a string containing simple HTML-like tags (<i>, <b>, <u>)
    into a list of (text_segment, format_dict) tuples.

    Args:
        text_with_tags: The string to parse.

    Returns:
        A list of tuples, where each tuple is (text_segment, format_dict).
        format_dict contains {'italic': bool, 'bold': bool, 'underline': bool}.
    """
    # Supported tags and their corresponding format key
    supported_tags = {
        'i': 'italic',
        'b': 'bold',
        'u': 'underline' # Corrected typo here
    }
    
    # Regex to find tags or text segments
    # It matches either an opening/closing tag or a sequence of non-< characters.
    # Tags: <(/?) (i|b|u) >
    # Text: [^<]+
    segment_regex = re.compile(r"(<(/?)(" + "|".join(supported_tags.keys()) + r")>|[^<]+)")

    result = []
    current_text_parts = []
    
    # Current formatting state
    # Initialize all to False
    active_formats = {key: False for key in supported_tags.values()}

    for match in segment_regex.finditer(text_with_tags):
        token = match.group(0)
        
        if token.startswith("<"): # It's a tag
            is_closing_tag = token.startswith("</")
            tag_name = token[2 if is_closing_tag else 1 : -1].lower()

            if tag_name in supported_tags:
                format_key = supported_tags[tag_name]
                
                # If there's accumulated text, add it to results with current formatting
                if current_text_parts:
                    result.append(("".join(current_text_parts), active_formats.copy()))
                    current_text_parts = []
                
                # Update active_formats
                active_formats[format_key] = not is_closing_tag
            else: # Not a supported tag, treat as text
                current_text_parts.append(token)
        else: # It's a text segment
            current_text_parts.append(token)

    # Add any remaining text after the last tag
    if current_text_parts:
        result.append(("".join(current_text_parts), active_formats.copy()))
        
    # Filter out empty text segments that might arise from adjacent tags
    return [(text, fmt) for text, fmt in result if text]


def format_parsed_footnote(matched_type: str, parsed_fields: dict, settings: dict) -> list[tuple[str, dict[str, bool]]]:
    """
    Formats the parsed footnote data back into a list of (text_segment, format_dict)
    tuples based on the matched type and its template.

    Args:
        matched_type: The type of reference matched (e.g., 'book', 'special_classic').
        parsed_fields: Extracted data from the footnote.
        settings: The loaded settings from settings.yaml.

    Returns:
        A list of (text_segment, format_dict) tuples.
    """
    if not matched_type:
        # If matched_type is None, try to format preprocessed_text if available
        if parsed_fields and 'preprocessed_text' in parsed_fields:
            preprocessed_text = parsed_fields['preprocessed_text']
            if preprocessed_text and isinstance(preprocessed_text, str): # Ensure it's a non-empty string
                return _parse_html_like_tags_to_format_list(preprocessed_text)
        return [] # Fallback for no matched_type and no valid preprocessed_text

    if matched_type == 'special_classic':
        full_citation = parsed_fields.get('full_citation', '')
        # The full_citation might contain <i>, <b>, <u> tags.
        return _parse_html_like_tags_to_format_list(full_citation)
    
    if 'reference_types' in settings and matched_type in settings['reference_types']:
        ref_config = settings['reference_types'][matched_type]
        template = ref_config.get('template', '')

        # Replace placeholders in the template
        # Placeholders are field names like "Author", "Title"
        # We need to be careful not to replace parts of HTML tags if field names are generic.
        # A simple string.replace loop should be okay if field names are distinct enough.
        # For "<i>Title</i>", the field name is "Title".
        # The replacement should happen for "Title" resulting in "<i>Value of Title</i>".

        # Create a sorted list of field names by length (descending)
        # to avoid issues where one field name is a substring of another
        # e.g., "Page" and "Pages". Replace "Pages" before "Page".
        sorted_field_names = sorted(parsed_fields.keys(), key=len, reverse=True)

        formatted_string = template
        for field_name in sorted_field_names:
            field_value = parsed_fields.get(field_name, "")
            # Ensure placeholder is not part of an HTML tag.
            # This simple replace might still be problematic if field_name is like 'i' or 'b'.
            # Assuming field names are actual words like "Author", "Title".
            formatted_string = formatted_string.replace(field_name, str(field_value))
            
        # Replace any remaining (unfilled) placeholders with empty strings
        # This uses the 'fields' definition from settings to find all possible placeholders
        if 'fields' in ref_config:
            for field_name in ref_config['fields'].keys():
                # Check if placeholder still exists (e.g. if it wasn't in parsed_fields)
                if field_name in formatted_string: # This check is a bit naive.
                                                 # A more robust way is to use regex for placeholders,
                                                 # e.g. {FieldName} but current template is "FieldName"
                    formatted_string = formatted_string.replace(field_name, "")
        
        # Clean up common issues:
        # - Multiple spaces:
        formatted_string = re.sub(r'\s+', ' ', formatted_string).strip()
        # - Space before comma/period:
        formatted_string = re.sub(r'\s([,.])', r'\1', formatted_string)
        # - Empty parentheses or brackets if fields inside were empty:
        formatted_string = re.sub(r'\(\s*\)', '', formatted_string)
        formatted_string = re.sub(r'\[\s*\]', '', formatted_string)
        # - Dangling commas or other punctuation if fields are missing
        #   e.g. "Author, , Title" -> "Author, Title" (harder to generalize)
        #   e.g. ", Title" -> "Title" (if author was empty)
        formatted_string = re.sub(r'^,\s*', '', formatted_string) # Leading comma
        formatted_string = re.sub(r',\s*,\s*', ', ', formatted_string) # Double comma
        formatted_string = re.sub(r',\s*\.', '.', formatted_string) # Comma before period

        return _parse_html_like_tags_to_format_list(formatted_string)

    return [] # Should not be reached if matched_type is valid


# Placeholder for more sophisticated functions if needed later
# e.g., for confidence scoring, advanced text cleaning, etc.
# def calculate_confidence_score(parsed_fields, required_fields, preprocessed_text):
#     # TODO: Implement more advanced matching confidence logic
#     # - How many optional fields were matched?
#     # - How much of the preprocessed_text remains unexplained after parsing?
#     # - Specificity of regex matches (e.g., did a date regex match a full date or just a year?)
#     return "medium" # Placeholder


if __name__ == '__main__':
    # ... (previous __main__ content remains here)
    # We will append new tests to the existing __main__
    print("Running example usage for footnote_processor.py...")

    # Dummy settings for testing - adjusted for required/optional field testing
    # Note: 'fields' contains regex patterns for parsing.
    # 'required_fields' lists fields essential for a match.
    # Optional fields are those in 'fields' but not in 'required_fields'.
    dummy_settings = {
        "reference_types": {
            "book": { # For testing green vs yellow based on optional fields
                "template": "Author, <i>Title</i> (Place: Publisher, Date, Edition).",
                "fields": { 
                    "Author": r"^(?P<Author>[A-Za-z\s,.]+?),", 
                    "Title": r"<i>(?P<Title>.+?)</i>",
                    "Place": r"\((?P<Place>[^:]+):", # Optional
                    "Publisher": r":\s*(?P<Publisher>[^,]+),", # Optional
                    "Date": r",\s*(?P<Date>\d{4})", # Optional (made optional for testing)
                    "Edition": r",\s*(?P<Edition>\d(?:st|nd|rd|th)\s*ed\.)" # Optional
                },
                # Required: Author, Title. Optional: Place, Publisher, Date, Edition (4 optional)
                # Green: Author, Title + >2 optional (i.e., 3 or 4 optional)
                # Yellow: Author, Title + 0, 1, or 2 optional
                "required_fields": ["Author", "Title"] 
            },
            "journalArticle": {
                "template": "Author, \"ArticleTitle,\" <i>JournalName</i> Volume, no. Issue (Date): Pages.",
                "fields": {
                    "Author": r"^(?P<Author>[A-Za-z\s,.]+?),",
                    "ArticleTitle": r"\"(?P<ArticleTitle>.+?)\"",
                    "JournalName": r"<i>(?P<JournalName>.+?)</i>",
                    "Volume": r"<i>[^<]+</i>\s+(?P<Volume>\d+),", 
                    "Date": r"\((?P<Date>\d{4})\)", # Required
                    "Pages": r":\s*(?P<Pages>[\d\s-]+)\." # Optional for this test config
                },
                "required_fields": ["Author", "ArticleTitle", "JournalName", "Date"] # Pages is optional
            },
             "webPage": { # All fields required for simplicity in this test type
                "template": "Author, \"PageTitle,\" <i>WebsiteName</i>, DatePublished, URL.",
                "fields": {
                    "Author": r"^(?P<Author>[A-Za-z\s,.]+?),?", 
                    "PageTitle": r"\"(?P<PageTitle>.+?)\"",
                    "WebsiteName": r"<i>(?P<WebsiteName>.+?)</i>",
                    "DatePublished": r"<i>[^<]+</i>,\s*(?P<DatePublished>\w+\s\d{1,2},\s\d{4}),",
                    "URL": r",\s*(?P<URL>https?://[^\s]+)\."
                },
                "required_fields": ["PageTitle", "WebsiteName", "URL"] # Author is effectively optional due to regex
            },
            "customType": { 
                "template": "<b>Name</b>: <i>Details</i>. [ExtraInfo] Section: <u>Underlined</u>.",
                "fields": {"Name": "", "Details": "", "ExtraInfo": "", "Underlined": ""},
                "required_fields": ["Name", "Details"] # Example required fields
            },
            "onlyRequiredType": {
                "template": "FieldA: ValueA, FieldB: ValueB.",
                "fields": {"ValueA": r"ValueA:\s*(?P<ValueA>[^,]+),", "ValueB": r"ValueB:\s*(?P<ValueB>.+)\."},
                "required_fields": ["ValueA", "ValueB"] # No optional fields
            }
        },
        "special_classics": {
            "STh": "Thomas Aquinas, <i>Summa Theologiae</i>",
            "DS": "Denzinger Schönmetzer, <i>Enchiridion Symbolorum</i>. With <b>bold</b> and <u>underline</u>."
        }
    }

    # --- Test preprocess_footnote_for_parsing ---
    print("\n--- Testing preprocess_footnote_for_parsing ---")
    test_raw_1 = [[("Hello ", {'italic': False, 'bold': False}), ("World", {'italic': True, 'bold': False})]]
    print(f"Input: {test_raw_1}")
    print(f"Output: \"{preprocess_footnote_for_parsing(test_raw_1)}\" (Expected: \"Hello <i>World</i>\")")
    assert preprocess_footnote_for_parsing(test_raw_1) == "Hello <i>World</i>"

    test_raw_2 = [[("Multi ", {}), ("styling", {'bold': True, 'italic': True}), (" here.", {'underline': True})]]
    # Expected: "Multi <b><i>styling</i></b> <u>here.</u>"
    print(f"Input: {test_raw_2}")
    processed_test_raw_2 = preprocess_footnote_for_parsing(test_raw_2)
    print(f"Output: \"{processed_test_raw_2}\" (Expected: \"Multi <b><i>styling</i></b> <u>here.</u>\")")
    assert processed_test_raw_2 == "Multi <b><i>styling</i></b> <u>here.</u>"
    
    test_raw_3 = [[("   Leading and trailing spaces   ", {})], [("Next para with  multiple   spaces.", {'italic':True})]]
    print(f"Input: {test_raw_3}")
    processed_test_raw_3 = preprocess_footnote_for_parsing(test_raw_3)
    print(f"Output: \"{processed_test_raw_3}\" (Expected: \"Leading and trailing spaces <i>Next para with multiple spaces.</i>\")")
    assert processed_test_raw_3 == "Leading and trailing spaces <i>Next para with multiple spaces.</i>"

    # --- Test parse_and_match_footnote ---
    print("\n--- Testing parse_and_match_footnote ---")

    # Test 1: Book
    footnote_book_raw = [
        [
            ("Doe, John", {'italic': False}), 
            (", ", {'italic': False}), 
            ("The Big Book of Examples", {'italic': True}),
            (" (Anytown: Big Publisher, ", {'italic': False}),
            ("2023", {'italic': False}),
            (").", {'italic': False})
        ]
    ]
    result_book = parse_and_match_footnote(footnote_book_raw, dummy_settings)
    print(f"\nInput (Book): {preprocess_footnote_for_parsing(footnote_book_raw)}")
    print(f"Match Result: {result_book['matched_type']}, Confidence: {result_book['confidence']}")
    print(f"Parsed Fields: {result_book['parsed_fields']}")
    # This book example has Author, Title (required) and Date (optional, 1 of 4).
    # Expected: Yellow (1/4 optional = 25% <= 50%)
    assert result_book['matched_type'] == 'book'
    assert result_book['parsed_fields'].get('Author') == "Doe, John"
    assert result_book['parsed_fields'].get('Title') == "The Big Book of Examples"
    assert result_book['parsed_fields'].get('Date') == "2023" # This is now an optional field
    assert result_book['confidence'] == 'yellow'


    # Test 1b: Book - Green (All required + >50% optional)
    # Required: Author, Title. Optional: Place, Publisher, Date, Edition (4 optional)
    # Need Author, Title + 3 or 4 optional.
    footnote_book_green_raw = [
        [
            ("Doe, Jane", {}), (", ", {}), 
            ("The Greener Book", {'italic': True}), # Title
            (" (Greentown: Green Pub, ", {}), # Place, Publisher
            ("2024", {}), # Date
            (", 2nd ed.", {}), # Edition
            ("). Other text.", {})
        ]
    ]
    # Preprocessed: "Doe, Jane, <i>The Greener Book</i> (Greentown: Green Pub, 2024, 2nd ed.). Other text."
    # Fields: Author, Title, Place, Publisher, Date, Edition (all 4 optional matched)
    result_book_green = parse_and_match_footnote(footnote_book_green_raw, dummy_settings)
    print(f"\nInput (Book Green): {preprocess_footnote_for_parsing(footnote_book_green_raw)}")
    print(f"Match Result: {result_book_green['matched_type']}, Confidence: {result_book_green['confidence']}")
    print(f"Parsed Fields: {result_book_green['parsed_fields']}")
    assert result_book_green['matched_type'] == 'book'
    assert result_book_green['parsed_fields'].get('Author') == "Doe, Jane"
    assert result_book_green['parsed_fields'].get('Title') == "The Greener Book"
    assert result_book_green['parsed_fields'].get('Place') == "Greentown"
    assert result_book_green['parsed_fields'].get('Publisher') == "Green Pub"
    assert result_book_green['parsed_fields'].get('Date') == "2024"
    assert result_book_green['parsed_fields'].get('Edition') == "2nd ed."
    assert result_book_green['confidence'] == 'green' # All 4 optional fields matched > 50%

    # Test 1c: Book - Yellow (All required + exactly 50% optional)
    # Need Author, Title + 2 optional (Place, Publisher). Date, Edition are not matched.
    footnote_book_yellow_half_raw = [
        [
            ("Doe, Half", {}), (", ", {}),
            ("The Halfway Book", {'italic': True}), # Title
            (" (Halfplace: HalfPub, ", {}), # Place, Publisher
            # No Date, No Edition here in the text
            ("). Some other details.", {})
        ]
    ]
    # Regex for Date: r",\s*(?P<Date>\d{4})"
    # Regex for Edition: r",\s*(?P<Edition>\d(?:st|nd|rd|th)\s*ed\.)"
    # Preprocessed: "Doe, Half, <i>The Halfway Book</i> (Halfplace: HalfPub, ). Some other details."
    # Matched: Author, Title, Place, Publisher (2 of 4 optional = 50%)
    result_book_yellow_half = parse_and_match_footnote(footnote_book_yellow_half_raw, dummy_settings)
    print(f"\nInput (Book Yellow Half): {preprocess_footnote_for_parsing(footnote_book_yellow_half_raw)}")
    print(f"Match Result: {result_book_yellow_half['matched_type']}, Confidence: {result_book_yellow_half['confidence']}")
    print(f"Parsed Fields: {result_book_yellow_half['parsed_fields']}")
    assert result_book_yellow_half['matched_type'] == 'book'
    assert result_book_yellow_half['parsed_fields'].get('Author') == "Doe, Half"
    assert result_book_yellow_half['parsed_fields'].get('Title') == "The Halfway Book"
    assert result_book_yellow_half['parsed_fields'].get('Place') == "Halfplace"
    assert result_book_yellow_half['parsed_fields'].get('Publisher') == "HalfPub"
    assert result_book_yellow_half['confidence'] == 'yellow' # 2/4 = 50%, not > 50%


    # Test 2: Special Classic (STh) - Should be Green
    footnote_sth_raw = [[("STh", {}), (". I, q. 1, a. 1.", {})]]
    result_sth = parse_and_match_footnote(footnote_sth_raw, dummy_settings)
    print(f"\nInput (STh): {preprocess_footnote_for_parsing(footnote_sth_raw)}")
    print(f"Match Result: {result_sth['matched_type']}, Confidence: {result_sth['confidence']}")
    print(f"Parsed Fields: {result_sth['parsed_fields']}")
    assert result_sth['matched_type'] == 'special_classic'
    assert result_sth['parsed_fields'].get('abbreviation') == 'STh'
    assert result_sth['confidence'] == 'green'

    # Test 3: Special Classic (DS) - Should be Green
    footnote_ds_raw = [[("DS", {}), (" 123, an important point.", {})]]
    result_ds = parse_and_match_footnote(footnote_ds_raw, dummy_settings)
    print(f"\nInput (DS): {preprocess_footnote_for_parsing(footnote_ds_raw)}")
    print(f"Match Result: {result_ds['matched_type']}, Confidence: {result_ds['confidence']}")
    print(f"Parsed Fields: {result_ds['parsed_fields']}")
    assert result_ds['matched_type'] == 'special_classic'
    assert result_ds['parsed_fields'].get('abbreviation') == 'DS'
    assert result_ds['confidence'] == 'green'
    
    # Test 4: Journal Article - All required, 0 optional (Pages is optional) -> Yellow
    # Required: Author, ArticleTitle, JournalName, Date. Optional: Pages.
    footnote_journal_raw_no_opt = [
        [
            ("Smith, Jane", {}), (", ", {}),
            ("\"A Study of Patterns,\"", {}), (" ", {}), 
            ("Journal of Obscure Studies", {'italic': True}), 
            (" ", {}), ("10", {}), (",", {}), # Volume
            (" no. 2 (", {}), ("2020", {}), # Date
            # ("): ", {}), ("100-110", {}), (".", {}) # Pages (optional) are missing
            (").", {})
        ]
    ]
    # Preprocessed: "Smith, Jane, "A Study of Patterns," <i>Journal of Obscure Studies</i> 10, no. 2 (2020)."
    # Matched: Author, ArticleTitle, JournalName, Volume, Date. Pages (optional) is not matched.
    # Volume regex: r"<i>[^<]+</i>\s+(?P<Volume>\d+)," -- this will match "10,"
    # Date regex: r"\((?P<Date>\d{4})\)" -- this will match "(2020)"
    # Pages regex: r":\s*(?P<Pages>[\d\s-]+)\." -- this will not match.
    # So, 0 out of 1 optional fields matched. Expected: Yellow.
    result_journal_no_opt = parse_and_match_footnote(footnote_journal_raw_no_opt, dummy_settings)
    print(f"\nInput (Journal Yellow - no optional): {preprocess_footnote_for_parsing(footnote_journal_raw_no_opt)}")
    print(f"Match Result: {result_journal_no_opt['matched_type']}, Confidence: {result_journal_no_opt['confidence']}")
    print(f"Parsed Fields: {result_journal_no_opt['parsed_fields']}")
    assert result_journal_no_opt['matched_type'] == 'journalArticle'
    assert result_journal_no_opt['parsed_fields'].get('Author') == "Smith, Jane"
    # ... check other required fields if necessary ...
    assert result_journal_no_opt['confidence'] == 'yellow' # 0/1 optional fields

    # Test 4b: Journal Article - All required, AND optional (Pages) -> Green
    # Required: Author, ArticleTitle, JournalName, Date. Optional: Pages.
    # Preprocessed: "Smith, Jane, "A Study of Patterns," <i>Journal of Obscure Studies</i> 10, no. 2 (2020): 100-110."
    # Matched: All required + Pages (1 of 1 optional). >50% (100%) optional matched. Expected: Green.
    result_journal_with_opt = parse_and_match_footnote(footnote_journal_raw_corrected, dummy_settings) # footnote_journal_raw_corrected has pages
    print(f"\nInput (Journal Green - with optional): {preprocess_footnote_for_parsing(footnote_journal_raw_corrected)}")
    print(f"Match Result: {result_journal_with_opt['matched_type']}, Confidence: {result_journal_with_opt['confidence']}")
    print(f"Parsed Fields: {result_journal_with_opt['parsed_fields']}")
    assert result_journal_with_opt['matched_type'] == 'journalArticle'
    assert result_journal_with_opt['confidence'] == 'green'


    # Test 5: Web Page - All required fields present -> Yellow (Author is optional-like due to regex `?`)
    # Required: PageTitle, WebsiteName, URL.
    # Fields: Author, PageTitle, WebsiteName, DatePublished, URL.
    # Optional: Author, DatePublished (Author regex allows it to be missing)
    # If Author and DatePublished are present, it's Green. Otherwise Yellow.
    # The footnote_web_raw has DatePublished, so 1 of 2 optional. (50% -> Yellow)
    # If Author is also present, it becomes Green.
    # Let's re-verify Author regex: r"^(?P<Author>[A-Za-z\s,.]+?),?" - the final comma is also optional.
    # If Author is "Techie, Tom", it matches.
    # So, Author, PageTitle, WebsiteName, DatePublished, URL are all present.
    # Optional fields: Author, DatePublished. Both are matched. (2/2 = 100% > 50%) -> Green
    result_web = parse_and_match_footnote(footnote_web_raw, dummy_settings)
    print(f"\nInput (Web): {preprocess_footnote_for_parsing(footnote_web_raw)}")
    print(f"Match Result: {result_web['matched_type']}, Confidence: {result_web['confidence']}")
    print(f"Parsed Fields: {result_web['parsed_fields']}")
    assert result_web['matched_type'] == 'webPage'
    assert result_web['parsed_fields'].get('Author') == "Techie, Tom" # Matched
    assert result_web['parsed_fields'].get('DatePublished') == "October 26, 2023" # Matched
    assert result_web['confidence'] == 'green' 

    # Test 6: No Match - Should be Red
    footnote_nomatch_raw = [[("Just some random text here.", {})]]
    result_nomatch = parse_and_match_footnote(footnote_nomatch_raw, dummy_settings)
    print(f"\nInput (No Match): {preprocess_footnote_for_parsing(footnote_nomatch_raw)}")
    print(f"Match Result: {result_nomatch['matched_type']}, Confidence: {result_nomatch['confidence']}")
    print(f"Parsed Fields: {result_nomatch['parsed_fields']}")
    assert result_nomatch['matched_type'] is None
    assert result_nomatch['confidence'] == 'red'

    test_raw_complex_clean = [
        [("  Start  ", {}), ("boldly", {'bold': True}), ("  and ", {}), ("italicly", {'italic': True, 'bold':True}), ("  end.  ", {})],
        [("  Second paragraph with  ", {}), ("underline", {'underline':True}), (" and ", {}), ("bold", {'bold':True}), (" and ", {}), ("italic", {'italic':True}), (" mix. ", {})]
    ]
    processed_complex_clean = preprocess_footnote_for_parsing(test_raw_complex_clean)
    print(f"\nInput (Complex Preprocessing - Clean Text): {test_raw_complex_clean}")
    print(f"Output (Clean Text): \"{processed_complex_clean}\"")
    expected_complex_clean = "Start <b>boldly</b> and <b><i>italicly</i></b> end. Second paragraph with <u>underline</u> and <b>bold</b> and <i>italic</i> mix."
    assert processed_complex_clean == expected_complex_clean
    
    footnote_book_missing_req_raw = [
        [
            # ("Doe, John", {'italic': False}), # Author is missing (required)
            (", ", {'italic': False}), 
            ("The Incomplete Book", {'italic': True}),
            (" (Anytown: Big Publisher, 2022).", {'italic': False}) 
        ]
    ]
    # Preprocessed: ", <i>The Incomplete Book</i> (Anytown: Big Publisher, 2022)."
    # Author is required for 'book' and is missing.
    result_book_missing = parse_and_match_footnote(footnote_book_missing_req_raw, dummy_settings)
    print(f"\nInput (Book missing Required): {preprocess_footnote_for_parsing(footnote_book_missing_req_raw)}")
    print(f"Match Result: {result_book_missing['matched_type']}, Confidence: {result_book_missing['confidence']}")
    print(f"Parsed Fields: {result_book_missing['parsed_fields']}")
    assert result_book_missing['matched_type'] is None 
    assert result_book_missing['confidence'] == 'red' # Missing required field -> Red

    # Test for "onlyRequiredType" - should be green if both ValueA and ValueB are found
    footnote_only_req_raw = [[("ValueA: TestA, ValueB: TestB.", {})]]
    # Preprocessed: "ValueA: TestA, ValueB: TestB."
    result_only_req = parse_and_match_footnote(footnote_only_req_raw, dummy_settings)
    print(f"\nInput (Only Required Type - Green): {preprocess_footnote_for_parsing(footnote_only_req_raw)}")
    print(f"Match Result: {result_only_req['matched_type']}, Confidence: {result_only_req['confidence']}")
    print(f"Parsed Fields: {result_only_req['parsed_fields']}")
    assert result_only_req['matched_type'] == 'onlyRequiredType'
    assert result_only_req['parsed_fields'].get('ValueA') == 'TestA'
    assert result_only_req['parsed_fields'].get('ValueB') == 'TestB'
    assert result_only_req['confidence'] == 'green' # All required met, no optional fields.

    # Test for "onlyRequiredType" - missing one required field -> red
    footnote_only_req_missing_raw = [[("ValueA: TestA, ValueB: .", {})]] # Missing ValueB content
    result_only_req_missing = parse_and_match_footnote(footnote_only_req_missing_raw, dummy_settings)
    print(f"\nInput (Only Required Type - Red): {preprocess_footnote_for_parsing(footnote_only_req_missing_raw)}")
    print(f"Match Result: {result_only_req_missing['matched_type']}, Confidence: {result_only_req_missing['confidence']}")
    print(f"Parsed Fields: {result_only_req_missing['parsed_fields']}")
    assert result_only_req_missing['matched_type'] is None # No type should fully match
    assert result_only_req_missing['confidence'] == 'red' # because ValueB content is missing.
    
    print("\n--- Testing _parse_html_like_tags_to_format_list ---")
    test_html_1 = "Hello <i>World</i>"
    expected_1 = [("Hello ", {'italic': False, 'bold': False, 'underline': False}), ("World", {'italic': True, 'bold': False, 'underline': False})]
    assert _parse_html_like_tags_to_format_list(test_html_1) == expected_1
    print(f"Parsed '{test_html_1}': {_parse_html_like_tags_to_format_list(test_html_1)}")

    test_html_2 = "<b>Bold</b> and <i>Italic</i> and <u>Underline</u>."
    expected_2 = [
        ("Bold", {'italic': False, 'bold': True, 'underline': False}),
        (" and ", {'italic': False, 'bold': False, 'underline': False}),
        ("Italic", {'italic': True, 'bold': False, 'underline': False}),
        (" and ", {'italic': False, 'bold': False, 'underline': False}),
        ("Underline", {'italic': False, 'bold': False, 'underline': True}),
        (".", {'italic': False, 'bold': False, 'underline': False})
    ]
    assert _parse_html_like_tags_to_format_list(test_html_2) == expected_2
    print(f"Parsed '{test_html_2}': {_parse_html_like_tags_to_format_list(test_html_2)}")

    test_html_3 = "Sequential: <i>Italic</i><b>Bold</b><u>Under</u>."
    expected_3 = [
        ("Italic", {'italic': True, 'bold': False, 'underline': False}),
        ("Bold", {'italic': False, 'bold': True, 'underline': False}),
        ("Under", {'italic': False, 'bold': False, 'underline': True}),
        (".", {'italic': False, 'bold': False, 'underline': False}) # Assuming tag closes implicitly or by next tag
    ]
    # The helper function should correctly handle transitions.
    # "<i>Italic</i><b>Bold</b>" means "Italic" is italic, "Bold" is bold.
    # The state resets/changes when a new tag starts or an old one ends.
    # My current helper logic might need adjustment for implicit closing by new tag.
    # Let's re-evaluate the helper logic:
    # "<i>Italic</i>" -> active_formats['italic'] = True. Text "Italic" added.
    # "<b>" -> active_formats['italic'] = False (if not nested), active_formats['bold'] = True.
    # This needs to handle nesting or sequential states correctly.
    # The regex splits by tags, so "<i>", "Italic", "</i>", "<b>", "Bold", "</b>".
    # "<i>": active_formats['italic'] = True
    # "Italic": add ("Italic", {'italic':True,...})
    # "</i>": active_formats['italic'] = False
    # "<b>": active_formats['bold'] = True
    # "Bold": add ("Bold", {'italic':False, 'bold':True,...})
    # "</b>": active_formats['bold'] = False
    # This seems correct for sequential.

    actual_html_3 = _parse_html_like_tags_to_format_list(test_html_3)
    print(f"Parsed '{test_html_3}': {actual_html_3}")
    assert actual_html_3 == expected_3


    test_html_4 = "Nested: <b>Bold<i>Italic</i>Bold</b>Normal."
    # Expected: [('Bold', b), ('Italic', b+i), ('Bold', b), ('Normal.', normal)]
    expected_4 = [
        ("Bold", {'italic': False, 'bold': True, 'underline': False}),
        ("Italic", {'italic': True, 'bold': True, 'underline': False}),
        ("Bold", {'italic': False, 'bold': True, 'underline': False}), # After </i>, italic becomes false, bold remains true
        ("Normal.", {'italic': False, 'bold': False, 'underline': False})
    ]
    actual_html_4 = _parse_html_like_tags_to_format_list(test_html_4)
    print(f"Parsed '{test_html_4}': {actual_html_4}")
    assert actual_html_4 == expected_4
    
    test_html_5 = "Text with <html> <unsupported> tags."
    expected_5 = [("Text with <html> <unsupported> tags.", {'italic': False, 'bold': False, 'underline': False})]
    actual_html_5 = _parse_html_like_tags_to_format_list(test_html_5)
    print(f"Parsed '{test_html_5}': {actual_html_5}")
    assert actual_html_5 == expected_5

    test_html_6 = "<i></i>Empty italic" # Edge case: empty tag
    expected_6 = [("Empty italic", {'italic': False, 'bold': False, 'underline': False})] # Empty tags should ideally be ignored or result in empty string
    actual_html_6 = _parse_html_like_tags_to_format_list(test_html_6)
    print(f"Parsed '{test_html_6}': {actual_html_6}")
    # Current logic will create ('', {'italic':True...}) then ('Empty italic', {'italic':False...})
    # The filter `if text` at the end removes the empty segment. This is good.
    assert actual_html_6 == expected_6


    print("\n--- Testing format_parsed_footnote ---")
    # Test 1: Book type
    parsed_book_fields = result_book['parsed_fields'] # From previous test
    # Reminder: dummy_settings.reference_types.book.template = "Author, <i>Title</i> (Place: Publisher, Date)."
    # Parsed: {'Author': 'Doe, John', 'Title': 'The Big Book of Examples', 'Place': 'Anytown', 'Publisher': 'Big Publisher', 'Date': '2023'}
    # (Need to ensure parse_and_match_footnote returns all these fields from its regex)
    # For now, let's manually construct parsed_fields for format_parsed_footnote tests for clarity
    
    book_fields_for_format = {
        'Author': 'Doe, John', 
        'Title': 'The Big Book of Examples', 
        'Place': 'Anytown', 
        'Publisher': 'Big Publishing Co', 
        'Date': '2023'
    }
    formatted_book = format_parsed_footnote('book', book_fields_for_format, dummy_settings)
    expected_formatted_book = [
        ("Doe, John, ", {'italic': False, 'bold': False, 'underline': False}),
        ("The Big Book of Examples", {'italic': True, 'bold': False, 'underline': False}),
        (" (Anytown: Big Publishing Co, 2023).", {'italic': False, 'bold': False, 'underline': False})
    ]
    print(f"Formatted Book: {formatted_book}")
    assert formatted_book == expected_formatted_book

    # Test 2: Special Classic
    # dummy_settings.special_classics.STh = "Thomas Aquinas, <i>Summa Theologiae</i>"
    sth_fields_for_format = {'abbreviation': 'STh', 'full_citation': dummy_settings['special_classics']['STh']}
    formatted_sth = format_parsed_footnote('special_classic', sth_fields_for_format, dummy_settings)
    expected_formatted_sth = [
        ("Thomas Aquinas, ", {'italic': False, 'bold': False, 'underline': False}),
        ("Summa Theologiae", {'italic': True, 'bold': False, 'underline': False})
    ]
    print(f"Formatted STh: {formatted_sth}")
    assert formatted_sth == expected_formatted_sth

    # Test 3: Special Classic with multiple formats
    # dummy_settings.special_classics.DS = "Denzinger Schönmetzer, <i>Enchiridion Symbolorum</i>. With <b>bold</b> and <u>underline</u>."
    ds_fields_for_format = {'abbreviation': 'DS', 'full_citation': dummy_settings['special_classics']['DS']}
    formatted_ds = format_parsed_footnote('special_classic', ds_fields_for_format, dummy_settings)
    expected_formatted_ds = [
        ("Denzinger Schönmetzer, ", {'italic': False, 'bold': False, 'underline': False}),
        ("Enchiridion Symbolorum", {'italic': True, 'bold': False, 'underline': False}),
        (". With ", {'italic': False, 'bold': False, 'underline': False}),
        ("bold", {'italic': False, 'bold': True, 'underline': False}),
        (" and ", {'italic': False, 'bold': False, 'underline': False}),
        ("underline", {'italic': False, 'bold': False, 'underline': True}),
        (".", {'italic': False, 'bold': False, 'underline': False})
    ]
    print(f"Formatted DS: {formatted_ds}")
    assert formatted_ds == expected_formatted_ds
    
    # Test 4: Custom type with mixed plain/tagged and all formats
    # template: "<b>Name</b>: <i>Details</i>. [ExtraInfo] Section: <u>Underlined</u>."
    custom_fields = {
        'Name': 'Test Name', 
        'Details': 'Some details here', 
        'ExtraInfo': 'Optional Info', 
        'Underlined': 'Important Text'
    }
    formatted_custom = format_parsed_footnote('customType', custom_fields, dummy_settings)
    expected_formatted_custom = [
        ("Test Name", {'italic': False, 'bold': True, 'underline': False}),
        (": ", {'italic': False, 'bold': False, 'underline': False}),
        ("Some details here", {'italic': True, 'bold': False, 'underline': False}),
        (". [Optional Info] Section: ", {'italic': False, 'bold': False, 'underline': False}),
        ("Important Text", {'italic': False, 'bold': False, 'underline': True}),
        (".", {'italic': False, 'bold': False, 'underline': False})
    ]
    print(f"Formatted Custom: {formatted_custom}")
    assert formatted_custom == expected_formatted_custom

    # Test 5: Book type with a missing optional field (Place)
    # Template: "Author, <i>Title</i> (Place: Publisher, Date)."
    # If Place is missing, it might become "( Publisher, Date)" or "(: Publisher, Date)"
    # Current replacement logic will make it "Author, <i>Title</i> (: Publisher, Date)."
    # The cleanup regex `\(\s*:\s*` or similar might be needed if we want to remove dangling punctuation from empty fields.
    # Current cleanup: `\(\s*\)` and `\[\s*\]` and `\s([,.])`.
    # `formatted_string = formatted_string.replace(field_name, "")` for missing fields.
    # So, "Author, <i>Title</i> (: Publisher, Date)." -> after cleanup: "Author, <i>Title</i> (:Publisher, Date)."
    # Let's test this specific case.
    book_missing_place = {
        'Author': 'Doe, Jane', 
        'Title': 'A Book', 
        # 'Place': 'NoPlace', # Place is missing
        'Publisher': 'PubCo', 
        'Date': '2024'
    }
    # Template: "Author, <i>Title</i> (Place: Publisher, Date)."
    # After field replacement: "Doe, Jane, <i>A Book</i> (: PubCo, 2024)." (Place becomes empty string)
    # Cleanups:
    # \s+ -> no change
    # \s([,.]) -> no change
    # \(\s*\) -> no change
    # ^,\s* -> no change
    # ,,\s* -> no change
    # ,\s*\. -> no change
    # So expected is "Doe, Jane, <i>A Book</i> (: PubCo, 2024)." which then parses.
    formatted_book_missing_place = format_parsed_footnote('book', book_missing_place, dummy_settings)
    expected_formatted_book_missing_place = [
        ("Doe, Jane, ", {'italic': False, 'bold': False, 'underline': False}),
        ("A Book", {'italic': True, 'bold': False, 'underline': False}),
        # (" (: PubCo, 2024).", {'italic': False, 'bold': False, 'underline': False})
        # The space before (: will be there.
        (" (: PubCo, 2024).", {'italic': False, 'bold': False, 'underline': False})
    ]
    print(f"Formatted Book (Missing Place): {formatted_book_missing_place}")
    assert formatted_book_missing_place == expected_formatted_book_missing_place

    # Test 6: Template where a field (not tagged) is missing, leaving punctuation
    # (Using the corrected dummy_settings_journal_fix from previous step for this test)
    dummy_settings_journal_fix = dummy_settings.copy()
    dummy_settings_journal_fix["reference_types"]["journalArticle"]["fields"]["Issue"] = r"no\.\s*(?P<Issue>\d+)" 
    journal_missing_volume = {
        'Author': 'Reviewer, A.', 'ArticleTitle': 'Some Thoughts', 'JournalName': 'Critical Reviews',
        'Issue': '3', 'Date': '2021', 'Pages': '1-2'
    } # Volume is missing
    formatted_journal_missing_vol = format_parsed_footnote(
        'journalArticle', journal_missing_volume, dummy_settings_journal_fix
    )
    expected_formatted_journal_missing_vol = [
        ("Reviewer, A., \"Some Thoughts,\" ", {'italic': False, 'bold': False, 'underline': False}),
        ("Critical Reviews", {'italic': True, 'bold': False, 'underline': False}),
        (", no. 3 (2021): 1-2.", {'italic': False, 'bold': False, 'underline': False})
    ]
    print(f"Formatted Journal (Missing Volume): {formatted_journal_missing_vol}")
    assert formatted_journal_missing_vol == expected_formatted_journal_missing_vol
    
    # Test 7: All fields missing from a complex template to test cleanup
    empty_fields_custom = {}
    # Template: "<b>Name</b>: <i>Details</i>. [ExtraInfo] Section: <u>Underlined</u>."
    # Fields for customType: "Name", "Details", "ExtraInfo", "Underlined"
    # All will be replaced by ""
    # Result: "<b></b>: <i></i>. [] Section: <u></u>."
    # Cleanups:
    # \s([,.]) -> "<b></b>:<i></i>. [] Section:<u></u>."
    # \[\s*\] -> "<b></b>:<i></i>. Section:<u></u>."
    # _parse_html_like_tags_to_format_list will then produce:
    # [(":", normal), (".", normal), (" Section:", normal), (".", normal)]
    formatted_empty_custom = format_parsed_footnote('customType', empty_fields_custom, dummy_settings)
    expected_empty_custom = [
        (":", {'italic': False, 'bold': False, 'underline': False}),
        (".", {'italic': False, 'bold': False, 'underline': False}),
        (" Section:", {'italic': False, 'bold': False, 'underline': False}),
        (".", {'italic': False, 'bold': False, 'underline': False})
    ]
    print(f"Formatted Custom (Empty Fields): {formatted_empty_custom}")
    assert formatted_empty_custom == expected_empty_custom


    print("\nAll assertions (including new ones) in example usage passed.")


# --- Color Formatting Function ---
def get_formatted_and_colored_footnote_segments(
    matched_type: str, 
    parsed_fields: dict, 
    settings: dict, 
    confidence_level: str
) -> list[tuple[str, dict]]:
    """
    Formats a parsed footnote and applies a color to each segment based on confidence.

    Args:
        matched_type: The type of reference matched.
        parsed_fields: Extracted data from the footnote.
        settings: The loaded settings.
        confidence_level: The confidence of the match ('green', 'yellow', 'red').

    Returns:
        A list of (text_segment, format_dict_with_color) tuples.
    """
    formatted_segments = format_parsed_footnote(matched_type, parsed_fields, settings)
    
    red_color = '#AA0000'

    colored_segments = []
    for text_segment, base_format_dict in formatted_segments:
        new_fmt = base_format_dict.copy()
        if confidence_level == 'no_match':
            new_fmt['color'] = red_color
        # No specific color is applied for 'match', it will use default document text color.
        colored_segments.append((text_segment, new_fmt))
        
    return colored_segments

    
# Placeholder for more sophisticated functions if needed later
# e.g., for confidence scoring, advanced text cleaning, etc.
# def calculate_confidence_score(parsed_fields, required_fields, preprocessed_text):
#     # TODO: Implement more advanced matching confidence logic
#     # - How many optional fields were matched?
#     # - How much of the preprocessed_text remains unexplained after parsing?
#     # - Specificity of regex matches (e.g., did a date regex match a full date or just a year?)
#     return "medium" # Placeholder
