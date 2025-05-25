# 📝 Footnotify - DOCX and ODT Footnote Extractor
<div align="center">
  <img src="https://raw.githubusercontent.com/salvodif/Footnotify/main/assets/logo.png" width="300" alt="TomeTrove Logo" />
</div>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads/)
<!-- Per aggiungere altri badge una volta che il repo è attivo:
[![GitHub stars](https://img.shields.io/github/stars/TUO_USERNAME/NOME_TUO_REPO?style=social)](https://github.com/TUO_USERNAME/NOME_TUO_REPO/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/TUO_USERNAME/NOME_TUO_REPO)](https://github.com/TUO_USERNAME/NOME_TUO_REPO/issues)
[![GitHub forks](https://img.shields.io/github/forks/TUO_USERNAME/NOME_TUO_REPO?style=social)](https://github.com/TUO_USERNAME/NOME_TUO_REPO/network/members)
-->

This Python script extracts all footnotes from a Microsoft Word (`.docx`) or OpenDocument Text (`.odt`) file and lists them sequentially in a new `.odt` file.
It attempts to preserve basic text formatting (bold, italic, underline) and uses the [Rich](https://github.com/Textualize/rich) library for an enhanced, interactive command-line experience.

---

## 🚀 Features

*   Extracts footnotes from both `.docx` and `.odt` files.
*   Preserves basic formatting: **bold**, *italic*, and <u>underline</u>.
*   Generates a new `.odt` file containing a sequential list of all extracted footnote contents.
*   💬 Interactive CLI: Prompts the user for the file to process.
*   💅 Readable terminal output with progress bars, using the [Rich](https://github.com/Textualize/rich) library.
*   🔄 Process multiple files in a single session.
*   💾 Generated output files are named based on the input file (e.g., `footnotes_da_original_name.odt`) and placed in the `output_footnotes/` directory.

---

## 📦 Installation

1.  Clone this repository or download the script.
2.  (Optional, but Recommended) Create and activate a Python virtual environment:
    ```bash
    python -m venv venv
    
    # On Linux / macOS
    source venv/bin/activate
     
    # On Windows (Command Prompt / PowerShell)
    .\venv\Scripts\activate 
    ```
3.  Install the required Python libraries:
    ```bash
    pip install python-docx odfpy rich
    ```

---

## 💻 Command Line Usage

1.  Navigate to the script's directory in your terminal.
2.  Run the script:
    ```bash
    python your_script_name.py 
    ```
    *(Replace `your_script_name.py` with the actual name of your Python file, e.g., `extract_notes.py`)*

3.  The script will then guide you through an interactive session:
    *   It will prompt you to enter the path to the `.docx` or `.odt` file you wish to analyse.
        ```
        ┌────────────────────────────────────────────────────────────────────┐
        │ Inserisci il percorso del file .odt o .docx da analizzare (o 'esci' │
        │ per terminare)                                                     │
        └────────────────────────────────────────────────────────────────────┘
        > your_document.odt
        ```
    *   Enter the full or relative path and press Enter.
    *   The script will process the file and save the results to a new `.odt` file inside the `output_footnotes/` sub-directory.
    *   To stop the script and exit, type `esci` (or `exit`/`quit` if you modify the script) at the prompt and press Enter.

---

## ⚠️ Limitations

*   **Formatting:** This script ONLY preserves basic **bold**, *italic*, and <u>underline</u> formatting.
    It does **NOT** currently preserve other formatting such as:
    *   Fonts, colours, or text sizes.
    *   Lists (bulleted or numbered).
    *   Tables.
    *   Images.
    *   Hyperlinks.
    *   Paragraph alignment, indentation, or spacing.
*   **Structure**: The script generates a simple, sequential LIST of the footnote text in a new document. It does NOT replicate the footnote reference markers (¹, ², ³) within a copy of the main text, nor does it place the extracted notes into the page-footer layout of the output ODT.
*   **Style Complexity**: Complex or inherited styles, especially within ODT documents, may not be fully or correctly interpreted beyond the basic formatting checks implemented.

---

## 🙌 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
