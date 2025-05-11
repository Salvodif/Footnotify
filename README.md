DOCX and ODT Footnote Extractor
This Python script extracts all footnotes from a Microsoft Word (.docx) or OpenDocument Text (.odt) file and lists them sequentially in a new .odt file.
It attempts to preserve basic text formatting (bold, italic, underline) and uses the rich library for an enhanced, interactive command-line experience.
Features
Extracts footnotes from both .docx and .odt files.
Preserves basic formatting: bold, italic, and <u>underline</u>.
Generates a new .odt file containing a sequential list of all extracted footnote contents.
Interactive CLI: Prompts the user for the file to process.
Readable terminal output with progress bars, using the Rich library.
Process multiple files in a single session.
Generated output files are named based on the input file (e.g., footnotes_da_original_name.odt) and placed in the output_footnotes/ directory.
Requirements
Python 3.x
Installation
Clone this repository or download the script.
(Optional, but Recommended) Create and activate a Python virtual environment:
python -m venv venv

# On Linux / macOS
source venv/bin/activate
 
# On Windows (Command Prompt / PowerShell)
.\venv\Scripts\activate
Use code with caution.
Bash
Install the required Python libraries:
pip install python-docx odfpy rich
Use code with caution.
Bash
Usage
Navigate to the script's directory in your terminal.
Run the script:
python your_script_name.py
Use code with caution.
Bash
(Replace your_script_name.py with the actual name of your Python file).
The script will prompt you to enter the path to the .docx or .odt file you wish to analyse.
Enter the full or relative path and press Enter.
The script will process the file and save the results to a new .odt file inside the output_footnotes/ sub-directory.
To stop the script, type esci at the prompt and press Enter.
(Note: The exit command is currently the Italian 'esci'. You can easily change this in the script's if __name__ == "__main__": block to 'quit' or 'exit' if preferred).
Limitations
Formatting: This script ONLY preserves basic bold, italic, and <u>underline</u> formatting.
It does NOT currently preserve other formatting such as:
Fonts, colours, or text sizes.
Lists (bulleted or numbered).
Tables.
Images.
Hyperlinks.
Paragraph alignment, indentation, or spacing.
Structure: The script generates a simple, sequential LIST of the footnote text in a new document. It does NOT replicate the footnote reference markers (¹, ², ³) within a copy of the main text, nor does it place the extracted notes into the page-footer layout of the output ODT.
Style Complexity: Complex or inherited styles, especially within ODT documents, may not be fully or correctly interpreted beyond the basic formatting checks implemented.
Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
License
MIT