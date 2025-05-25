# 📝 Footnotify - DOCX and ODT Footnote Extractor & Formatter
<div align="center">
  <img src="https://raw.githubusercontent.com/salvodif/Footnotify/main/assets/logo.png" width="300" alt="TomeTrove Logo" />

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/salvodif/footnotify?style=social)](https://github.com/salvodif/footnotify/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/salvodif/footnotify)](https://github.com/salvodif/footnotify/issues)
[![GitHub forks](https://img.shields.io/github/forks/salvodif/footnotify?style=social)](https://github.com/salvodif/footnotify/network/members)
</div>

This Python script extracts footnotes from Microsoft Word (`.docx`) or OpenDocument Text (`.odt`) files. Its primary purpose is to then parse these footnotes, attempt to identify their structure based on user-defined rules, and reformat them into a standardized citation style. The reformatted footnotes are saved in a new `.odt` file, with text color-coded to indicate the confidence of the parsing and formatting.

---

## 🚀 Features

*   Extracts footnotes from both `.docx` and `.odt` files.
*   **Customizable Parsing & Formatting**: Leverages a `settings.yaml` file where users define reference types (e.g., book, journal article), their desired output templates, and regex patterns to extract citation components.
*   **Special Classics Support**: Easily define standard citations for frequently referenced classic texts (e.g., "STh" for Thomas Aquinas' *Summa Theologiae*).
*   **Confidence-Based Color Coding**: Output footnotes in the generated `.odt` file are colored to indicate the system's confidence in the accuracy of the parsing and formatting:
    *   **Green**: High confidence (e.g., special classic match, or all required fields + a good number of optional fields found).
    *   **Dark Yellow**: Medium confidence (e.g., all required fields found, but some optional data might be missing).
    *   **Dark Red**: Low confidence (e.g., couldn't match a defined type, or critical information missing). The original (or preprocessed) text is usually shown.
*   Preserves basic formatting: **bold**, *italic*, and <u>underline</u> during both extraction and re-formatting based on templates.
*   💬 Interactive CLI: Prompts the user for the file to process and offers a test mode.
*   💅 Readable terminal output with progress bars, using the [Rich](https://github.com/Textualize/rich) library.
*   🔄 Process multiple files in a single session.
*   💾 Generated output files are named based on the input file (e.g., `footnotes_da_original_name.odt`) and placed in an `output_footnotes/` or `output_tests/` directory.

---

## 📦 Dependencies & Installation

The script requires the following Python libraries:
*   `python-docx`: For reading `.docx` files.
*   `odfpy`: For reading `.odt` files and creating the output `.odt` file.
*   `PyYAML`: For parsing the `settings.yaml` configuration file.
*   `rich`: For enhanced command-line interface text formatting and prompts.

**Installation Steps:**

1.  Clone this repository or download the script files.
2.  (Optional, but Recommended) Create and activate a Python virtual environment:
    ```bash
    python -m venv venv
    # On Linux / macOS
    source venv/bin/activate
    # On Windows (Command Prompt / PowerShell)
    .\venv\Scripts\activate
    ```
3.  Install the required libraries. You can do this by:
    *   Creating a `requirements.txt` file with the following content:
        ```
        python-docx
        odfpy
        PyYAML
        rich
        ```
        Then run:
        ```bash
        pip install -r requirements.txt
        ```
    *   Or, install them directly:
        ```bash
        pip install python-docx odfpy PyYAML rich
        ```

---

## 💻 Command Line Usage

1.  Navigate to the script's directory in your terminal (where `extract_notes.py`, `settings_parser.py`, `footnote_processor.py`, and `settings.yaml` are located).
2.  Run the script:
    ```bash
    python extract_notes.py
    ```
3.  The script will then guide you:
    *   It will prompt you to enter the path to the `.docx` or `.odt` file, type `test` to run the built-in test suite, or `esci` to exit.
        ```
        ───────────────────────────────────────────────────────────────────────────
        Inserisci il percorso del file .odt/.docx, 'test' per la modalità test, o 'esci' per terminare
        >
        ```
    *   **Normal Mode**: Enter the full or relative path to your document. The script will process it using `settings.yaml` and save results to `output_footnotes/`.
    *   **Test Mode**: Type `test`. The script will use predefined test documents (you'll need to create them in `test_data/`) and `test_data/test_settings.yaml`. Results are saved to `output_tests/`.

---

## ⚙️ Configuration (`settings.yaml`)

The `settings.yaml` file is crucial for the script's footnote parsing and formatting logic. By default, the script looks for `settings.yaml` in the same directory. For test mode, it uses `test_data/test_settings.yaml`.

The file has two main sections:

### `reference_types`

This section defines different types of references (e.g., book, journal article, web page) and how to parse and format them.

*   **Defining a Type**: Each type starts with a key (e.g., `book:`).
    ```yaml
    reference_types:
      book:
        template: "Author, <i>Title</i> (Place: Publisher, Date)."
        fields:
          Author: '(?P<Author>[A-Z][A-Za-z\s.,]+(?:et al\.)?),'
          Title: '<i>(?P<Title>[^<]+)</i>'
          Place: '\((?P<Place>[^:]+):'
          Publisher: ':\s*(?P<Publisher>[^,]+),'
          Date: ', (?P<Date>\d{4})\)\.'
        required_fields: ["Author", "Title", "Date"]
      # ... other types ...
    ```

*   **`template`**:
    *   A string defining the desired output format for this reference type.
    *   Placeholders (e.g., `Author`, `Title`) correspond to keys in the `fields` section.
    *   Use `<i>...</i>` for italics, `<b>...</b>` for bold, and `<u>...</u>` for underline in the template.
    *   Example: `template: "Author, <i>Title</i> (Place: Publisher, Date)."`

*   **`fields`**:
    *   A dictionary where each key is a placeholder name (e.g., `Author`, `Title`) used in the `template`.
    *   The value for each key is a **Python-compatible regular expression (regex)** string used to extract that piece of information from the raw footnote text.
    *   **Crucial**: These regexes must use named capture groups `(?P<FieldName>...)` where `FieldName` exactly matches the placeholder key.
    *   Example: `Title: '<i>(?P<Title>[^<]+)</i>'` will capture text within `<i>...</i>` tags as 'Title'.
    *   Getting these regexes right is key to accurate parsing and will likely require customization based on the footnote styles in your documents.

*   **`required_fields`**:
    *   A list of field names (from the `fields` section) that *must* be successfully extracted for a footnote to be considered a match for this reference type.
    *   If any of these fields are not found, the footnote will not be classified as this type (or may result in a 'red' low-confidence match).

*   **Optional Fields**:
    *   Any field defined in `fields` but not listed in `required_fields` is considered optional.
    *   Matching all required fields results in at least a 'yellow' (medium) confidence.
    *   Matching all required fields *and* more than half of the defined optional fields results in a 'green' (high) confidence score.

### `special_classics`

This section is for defining common abbreviations for well-known texts and their full, pre-formatted citation string. These matches are typically high-confidence ('green').

*   Each entry is a key-value pair: `ABBREVIATION: "Full Citation String"`
*   The "Full Citation String" can include `<i>`, `<b>`, `<u>` tags for formatting.
    ```yaml
    special_classics:
      STh: "Thomas Aquinas, <i>Summa Theologiae</i>"
      DS: "Henricus Denzinger, Peter Hünermann (eds.), <i>Enchiridion symbolorum...</i>"
    ```
    If the script encounters "STh. I, q.1, a.1", it will identify "STh" and use the predefined string.

**Customization Note**: Users are strongly encouraged to customize the regex patterns in `settings.yaml` to match the specific citation styles present in their documents. Online regex testers can be very helpful for this.

---

## 📊 Output Interpretation (Color Coding)

The script generates a new `.odt` file (e.g., `footnotes_da_my_document.odt`) in the `output_footnotes/` directory (or `output_tests/` if in test mode). The text within this file is color-coded:

*   <span style="color:#00AA00;">**Green Text**</span>: Indicates **high confidence**.
    *   This means the footnote was likely matched correctly as a `special_classic` or as a `reference_type` where all `required_fields` and a significant portion (>50%) of `optional_fields` were successfully extracted and formatted.
*   <span style="color:#B8860B;">**Dark Yellow Text**</span>: Indicates **medium confidence**.
    *   The footnote was matched to a `reference_type`, and all its `required_fields` were found, but fewer than half of the `optional_fields` were successfully extracted. The formatting is based on the template, but some parts might be missing.
*   <span style="color:#AA0000;">**Dark Red Text**</span>: Indicates **low confidence**.
    *   The script was unable to reliably match the footnote to any defined `reference_type` or `special_classic`.
    *   In this case, the output will typically be the preprocessed text of the footnote (original text with basic HTML-like tags for bold/italic/underline), colored red. This allows users to see the original content that failed to parse correctly.

---

## 🧪 Running Tests

The script includes a basic test mode to help verify its functionality with predefined data.

1.  **Prepare Test Files**:
    *   Ensure you have a `test_data/test_settings.yaml` file (as described in the Configuration section, tailored for the test documents).
    *   Manually create `test_data/test_document.docx` and `test_data/test_document.odt`. The script will print the expected content and formatting for these files if they are not found during test mode.
2.  **Run the Test Command**:
    *   Execute `python extract_notes.py` and type `test` at the prompt.
3.  **Review Output**:
    *   The script will process the test documents using `test_data/test_settings.yaml`.
    *   Output files will be generated in `output_tests/output_docx_test/` and `output_tests/output_odt_test/`.
    *   **Manual verification is required**: Open these generated `.odt` files and check if the footnotes are formatted and color-coded as expected based on the content of your test documents and `test_settings.yaml`.

---

## ⚠️ Limitations

*   **Formatting Preservation**: While the script aims to preserve bold, italic, and underline, and apply them based on templates, complex nested stylings or other formatting (fonts, sizes, lists, tables, images, hyperlinks, paragraph styles) are **not** preserved or supported.
*   **Regex Complexity**: The accuracy of footnote parsing is heavily dependent on the quality and specificity of the regex patterns defined in `settings.yaml`. Crafting robust regexes for diverse footnote styles can be challenging.
*   **Structural Output**: The output is a new ODT file containing a list of processed footnotes. It does not attempt to replicate the original document's main text or footnote markers.

---

## 🙌 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 📜 License

This project is licensed under the MIT License - see the `LICENSE` file (if one is provided in the repository) or assume standard MIT License terms.

---

## 🚀 Future Enhancements (TODO)

*   **Advanced Regex Management & GUI**:
    *   Develop a library for complex regex patterns within `settings.yaml` or a linked file.
    *   Create a UI (web or text-based) for testing regex patterns against sample footnotes.
*   **Improved Confidence Scoring & Ambiguity Handling**:
    *   Allow weighted fields for more nuanced confidence scores.
    *   Implement mechanisms to flag or manage ambiguous matches (e.g., when a footnote matches multiple types).
*   **Enhanced Output Options**:
    *   Add functionality to generate a bibliography from processed footnotes.
    *   Support output in other formats (e.g., plain text, Markdown).
    *   Allow user customization of confidence colors in `settings.yaml`.
*   **User Experience and Workflow**:
    *   Implement robust batch processing for multiple documents.
    *   Add a `requirements.txt` file for easier dependency management. (Note: This was mentioned in the installation section as a way to install, but an actual file in the repo could be added).
    *   Provide more detailed error reporting for settings and regex issues.
*   **Parsing Robustness**:
    *   Incorporate heuristics for correcting common OCR errors.
    *   Improve text normalization to handle variations in punctuation and spacing.
    *   Investigate support for legacy binary `.dot` files if required.
*   **Direct Document Modification (Advanced)**:
    *   Explore options for re-inserting formatted footnotes back into the source document (with caution due to complexity and risk).
