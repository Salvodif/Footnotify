# tests/sample_footnote_data.py
# This file contains sample raw footnote data for testing the footnote processor.
# Each variable is a list of paragraphs, where each paragraph is a list of (text_run, format_dict) tuples.

# Footnote 1: Matches testBook
footnote_book_1_raw = [
    [
        ("Doe, John", {}),
        (", ", {}),
        ("The Test Book", {'italic': True}),
        (" (Testville: Test Press, ", {}),
        ("2023", {}),
        (").", {})
    ]
]
footnote_book_1_preprocessed = "Doe, John, <i>The Test Book</i> (Testville: Test Press, 2023)."
footnote_book_1_expected_fields = {
    'Author': 'Doe, John',
    'Title': 'The Test Book',
    'Place': 'Testville',
    'Publisher': 'Test Press',
    'Year': '2023'
}
footnote_book_1_expected_formatted = [
    ("Doe, John, ", {'italic': False, 'bold': False, 'underline': False}),
    ("The Test Book", {'italic': True, 'bold': False, 'underline': False}),
    (" (Testville: Test Press, 2023).", {'italic': False, 'bold': False, 'underline': False})
]

# Footnote 2: Matches testJournalArticle
footnote_journal_1_raw = [
    [
        ("Smith, Jane", {}),
        (", ", {}),
        ("A Test Article", {}), # Note: Template expects quotes around title, regex captures it
        (", ", {}),
        ("Journal of Tests", {'italic': True}),
        (" Vol. ", {}),
        ("12", {}),
        (" (", {}),
        ("2024", {}),
        ("): ", {}),
        ("100-110", {}),
        (".", {})
    ]
]
# Correction: The template for testJournalArticle is: "Author, \"ArticleTitle,\" <i>JournalName</i> Vol. Volume (Year): Pages."
# The raw data needs to reflect the quotes for ArticleTitle for the regex '"(?P<ArticleTitle>.+?)"' to capture it correctly.
footnote_journal_1_raw_corrected = [
    [
        ("Smith, Jane", {}), (", ", {}),
        ("\"A Test Article,\"", {}), # ArticleTitle with quotes
        (" ", {}),
        ("Journal of Tests", {'italic': True}), # JournalName
        (" Vol. ", {}), ("12", {}), # Volume
        (" (", {}), ("2024", {}), # Year
        ("): ", {}), ("100-110", {}), (".", {}) # Pages
    ]
]
footnote_journal_1_preprocessed = 'Smith, Jane, "A Test Article," <i>Journal of Tests</i> Vol. 12 (2024): 100-110.'
footnote_journal_1_expected_fields = {
    'Author': 'Smith, Jane',
    'ArticleTitle': 'A Test Article,', # Comma included due to regex
    'JournalName': 'Journal of Tests',
    'Volume': '12',
    'Year': '2024',
    'Pages': '100-110'
}
footnote_journal_1_expected_formatted = [
    ("Smith, Jane, ", {'italic': False, 'bold': False, 'underline': False}),
    ("\"A Test Article,\" ", {'italic': False, 'bold': False, 'underline': False}),
    ("Journal of Tests", {'italic': True, 'bold': False, 'underline': False}),
    (" Vol. 12 (2024): 100-110.", {'italic': False, 'bold': False, 'underline': False})
]


# Footnote 3: Matches testWebPage (with optional Author present)
footnote_web_1_raw = [
    [
        ("Techie, Tom", {}), (", ", {}),
        ("\"My Test Page,\"", {}), (" ", {}),
        ("The Test Website", {'italic': True}), (", ", {}),
        ("https://example.com/testpage", {}), (", ", {}),
        ("(Accessed June 15, 2024)", {}) # Note: Template expects dot after parenthesis
    ]
]
footnote_web_1_raw_corrected = [ # Adding the final dot
    [
        ("Techie, Tom", {}), (", ", {}),
        ("\"My Test Page,\"", {}),(" ", {}),
        ("The Test Website", {'italic': True}), (", ", {}),
        ("https://example.com/testpage", {}), (", ", {}),
        ("(Accessed June 15, 2024)", {}), (".", {})
    ]
]
footnote_web_1_preprocessed = 'Techie, Tom, "My Test Page," <i>The Test Website</i>, https://example.com/testpage, (Accessed June 15, 2024).'
footnote_web_1_expected_fields = {
    'Author': 'Techie, Tom',
    'PageTitle': 'My Test Page,', # Comma included by regex
    'WebsiteName': 'The Test Website',
    'URL': 'https://example.com/testpage',
    'AccessedDate': 'June 15, 2024'
}

# Footnote 4: Matches TestSTh (special classic)
footnote_classic_1_raw = [[("TestSTh", {}), (". I, q. 1, a. 1.", {})]]
footnote_classic_1_preprocessed = "TestSTh. I, q. 1, a. 1."
footnote_classic_1_expected_fields = {
    'abbreviation': 'TestSTh',
    'full_citation': "Test Thomas, <i>Test Summa</i>"
}
footnote_classic_1_expected_formatted = [
    ("Test Thomas, ", {'italic': False, 'bold': False, 'underline': False}),
    ("Test Summa", {'italic': True, 'bold': False, 'underline': False}),
]


# Footnote 5: No match, should return preprocessed text for formatting
footnote_nomatch_1_raw = [
    [("This is some ", {}), ("random text ", {'italic': True}), ("that won't match.", {})]
]
footnote_nomatch_1_preprocessed = "This is some <i>random text</i> that won't match."
# Expected behavior: matched_type is None, format_parsed_footnote uses preprocessed_text
footnote_nomatch_1_expected_formatted = [
    ("This is some ", {'italic': False, 'bold': False, 'underline': False}),
    ("random text", {'italic': True, 'bold': False, 'underline': False}),
    (" that won't match.", {'italic': False, 'bold': False, 'underline': False}),
]

# Footnote 6: Matches testOnlyRequired
footnote_onlyreq_1_raw = [[("Key1: ValueAlpha, Key2: ValueBeta.", {})]]
footnote_onlyreq_1_preprocessed = "Key1: ValueAlpha, Key2: ValueBeta."
footnote_onlyreq_1_expected_fields = {'Value1': 'ValueAlpha', 'Value2': 'ValueBeta'}

# Footnote 7: Matches TestDS (special classic with formatting tags)
footnote_classic_ds_raw = [[("TestDS", {}), (" 123.", {})]]
footnote_classic_ds_preprocessed = "TestDS 123."
footnote_classic_ds_expected_fields = {
    'abbreviation': 'TestDS',
    'full_citation': "Test Denzinger, <i>Test Enchiridion</i>. With <b>bold tag</b> and <u>underline tag</u>."
}
footnote_classic_ds_expected_formatted = [
    ("Test Denzinger, ", {'italic': False, 'bold': False, 'underline': False}),
    ("Test Enchiridion", {'italic': True, 'bold': False, 'underline': False}),
    (". With ", {'italic': False, 'bold': False, 'underline': False}),
    ("bold tag", {'italic': False, 'bold': True, 'underline': False}),
    (" and ", {'italic': False, 'bold': False, 'underline': False}),
    ("underline tag", {'italic': False, 'bold': False, 'underline': True}),
    (".", {'italic': False, 'bold': False, 'underline': False}),
]

# Footnote 8: Preprocessing test with multiple styles
footnote_preprocess_1_raw = [
    [
        ("Text1 ", {'bold': True}),
        ("Text2", {'italic': True, 'bold': True}),
        (" Text3", {'underline': True})
    ]
]
footnote_preprocess_1_preprocessed = "<b>Text1</b> <b><i>Text2</i></b> <u>Text3</u>"


# Footnote 9: For testBookChapter
footnote_bookchapter_1_raw = [
    [
        ("ChapterAuthor, Name", {}), (", ", {}),
        ("“<i>The Best Chapter Ever</i>”", {}), (", ", {}),
        ("in A Great Book Title", {}), (", ", {}),
        ("ed. Editor, Famous", {}), (", ", {}),
        ("(New Place: Good Publisher, ", {}),
        ("2025", {}), ("), ", {}),
        ("pp. ", {}), ("10-20", {}), (".", {})
    ]
]
footnote_bookchapter_1_preprocessed = "ChapterAuthor, Name, “<i>The Best Chapter Ever</i>”, in A Great Book Title, ed. Editor, Famous, (New Place: Good Publisher, 2025), pp. 10-20."
footnote_bookchapter_1_expected_fields = {
    'ChapterAuthor': 'ChapterAuthor, Name',
    'ChapterTitle': 'The Best Chapter Ever',
    'BookTitle': 'A Great Book Title',
    'Editor': 'Editor, Famous',
    'Place': 'New Place',
    'Publisher': 'Good Publisher',
    'Year': '2025',
    'Pages': '10-20'
}

# List of all sample footnotes for easy iteration in tests
all_sample_footnotes = [
    {
        "name": "Book1",
        "raw_data": footnote_book_1_raw,
        "preprocessed_text": footnote_book_1_preprocessed,
        "expected_match_type": "testBook",
        "expected_fields": footnote_book_1_expected_fields,
        "expected_formatted_segments": footnote_book_1_expected_formatted,
        "expected_confidence": "green" # Assuming all required fields match and some optional might too
    },
    {
        "name": "Journal1_Corrected",
        "raw_data": footnote_journal_1_raw_corrected,
        "preprocessed_text": footnote_journal_1_preprocessed,
        "expected_match_type": "testJournalArticle",
        "expected_fields": footnote_journal_1_expected_fields,
        "expected_formatted_segments": footnote_journal_1_expected_formatted,
        "expected_confidence": "green"
    },
    {
        "name": "Web1_Corrected",
        "raw_data": footnote_web_1_raw_corrected,
        "preprocessed_text": footnote_web_1_preprocessed,
        "expected_match_type": "testWebPage",
        "expected_fields": footnote_web_1_expected_fields,
        # expected_formatted_segments for web can be derived similarly if needed for direct comparison
        "expected_confidence": "green" # Author is optional, but if present, contributes
    },
    {
        "name": "ClassicSTh1",
        "raw_data": footnote_classic_1_raw,
        "preprocessed_text": footnote_classic_1_preprocessed,
        "expected_match_type": "special_classic",
        "expected_fields": footnote_classic_1_expected_fields,
        "expected_formatted_segments": footnote_classic_1_expected_formatted,
        "expected_confidence": "green"
    },
    {
        "name": "NoMatch1",
        "raw_data": footnote_nomatch_1_raw,
        "preprocessed_text": footnote_nomatch_1_preprocessed,
        "expected_match_type": None, # Expect no specific type match
        "expected_fields": {'preprocessed_text': footnote_nomatch_1_preprocessed}, # Should contain preprocessed_text
        "expected_formatted_segments": footnote_nomatch_1_expected_formatted,
        "expected_confidence": "red" # Or 'low' depending on implementation details in parse_and_match
    },
    {
        "name": "OnlyRequired1",
        "raw_data": footnote_onlyreq_1_raw,
        "preprocessed_text": footnote_onlyreq_1_preprocessed,
        "expected_match_type": "testOnlyRequired",
        "expected_fields": footnote_onlyreq_1_expected_fields,
        "expected_confidence": "green" # All required, no optional defined
    },
    {
        "name": "ClassicDS1",
        "raw_data": footnote_classic_ds_raw,
        "preprocessed_text": footnote_classic_ds_preprocessed,
        "expected_match_type": "special_classic",
        "expected_fields": footnote_classic_ds_expected_fields,
        "expected_formatted_segments": footnote_classic_ds_expected_formatted,
        "expected_confidence": "green"
    },
    {
        "name": "BookChapter1",
        "raw_data": footnote_bookchapter_1_raw,
        "preprocessed_text": footnote_bookchapter_1_preprocessed,
        "expected_match_type": "testBookChapter",
        "expected_fields": footnote_bookchapter_1_expected_fields,
        "expected_confidence": "green" # All required fields are present
    }
]

# This list is expected by test_footnote_processor.py for some parametrized tests.
# It should be updated to reflect new confidence values: 'match' or 'no_match'.
expected_processed_footnotes = [
    { # Footnote 1 (Original: Green)
        "matched_type": "book",
        "confidence": "match",
        "parsed_fields": {"Author": "Test Author", "Title": "Sample Book Title", "PublicationInfoRaw": "SamplePlace: SamplePublisher, 2023", "Pages": "10-20"}
    },
    { # Footnote 2 (Original: Yellow)
        "matched_type": "bookChapter",
        "confidence": "match", # Yellow becomes Match if required fields were met
        "parsed_fields": {"Author": "Chapter Author", "ChapterTitle": "Sample Chapter", "BookTitle": "Main Book Title", "Date": "2023"}
    },
    { # Footnote 3 (Original: Red)
        "matched_type": None,
        "confidence": "no_match",
        "preprocessed_text": "This is a random footnote."
    },
    { # Footnote 4 (Original: Green)
        "matched_type": "dictionaryEntry",
        "confidence": "match",
        "parsed_fields": {"Author": "Dictionary Author", "Term": "Sample Term,", "DictionaryTitle": "Sample Dictionary", "Place": "SamplePlace", "Publisher": "SamplePublisher", "Date": "2024"}
    },
    { # Footnote 5 (Original: Yellow)
        "matched_type": "webPage",
        "confidence": "match", # Yellow becomes Match if required fields were met
        "parsed_fields": {"Author": "Web Author", "PageTitle": "Some Page", "WebsiteName": "SomeSite", "URL": "https://example.com/somepage."}
    },
    { # Footnote 6 (Original: Red)
        "matched_type": None,
        "confidence": "no_match",
        "preprocessed_text": "Unmatchable reference content."
    },
    { # Footnote 7 (Original: Green)
        "matched_type": "special_classic",
        "confidence": "match",
        "parsed_fields": {"abbreviation": "SThTest", "full_citation": "Test Aquinas, <i>Summa Testologiae</i>"}
    }
]
