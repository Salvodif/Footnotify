<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DOCX and ODT Footnote Extractor</title>
    <style>
        body { font-family: sans-serif; line-height: 1.6; margin: 20px; max-width: 800px; margin-left: auto; margin-right: auto; }
        h1, h2, h3 { color: #333; }
        h1 { border-bottom: 2px solid #eee; padding-bottom: 10px; }
        h2 { border-bottom: 1px solid #eee; padding-bottom: 5px; }
        code { background-color: #f4f4f4; padding: 2px 6px; border-radius: 4px; font-family: monospace; }
        pre { background-color: #f4f4f4; padding: 15px; border-radius: 4px; overflow-x: auto; }
        ul { padding-left: 20px; }
        li { margin-bottom: 5px; }
        strong { font-weight: bold; }
        em { font-style: italic; }
        u { text-decoration: underline; }
        a { color: #0366d6; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .note { font-style: italic; color: #555; }
    </style>
</head>
<body>

    <h1>DOCX and ODT Footnote Extractor</h1>

    <p>This Python script extracts all footnotes from a Microsoft Word (<code>.docx</code>) or OpenDocument Text (<code>.odt</code>) file and lists them sequentially in a new <code>.odt</code> file.
    It attempts to preserve basic text formatting (bold, italic, underline) and uses the <code>rich</code> library for an enhanced, interactive command-line experience.</p>

    <h2>Features</h2>
    <ul>
        <li>Extracts footnotes from both <code>.docx</code> and <code>.odt</code> files.</li>
        <li>Preserves basic formatting: <strong>bold</strong>, <em>italic</em>, and <u>underline</u>.</li>
        <li>Generates a new <code>.odt</code> file containing a sequential list of all extracted footnote contents.</li>
        <li>Interactive CLI: Prompts the user for the file to process.</li>
        <li>Readable terminal output with progress bars, using the <a href="https://github.com/Textualize/rich">Rich</a> library.</li>
        <li>Process multiple files in a single session.</li>
        <li>Generated output files are named based on the input file (e.g., <code>footnotes_da_original_name.odt</code>) and placed in the <code>output_footnotes/</code> directory.</li>
    </ul>

    <h2>Requirements</h2>
    <ul>
        <li>Python 3.x</li>
    </ul>

    <h2>Installation</h2>
    <ol>
        <li>Clone this repository or download the script.</li>
        <li>(Optional, but Recommended) Create and activate a Python virtual environment:
            <pre><code>python -m venv venv

# On Linux / macOS
source venv/bin/activate
            
# On Windows (Command Prompt / PowerShell)
.\venv\Scripts\activate</code></pre>
        </li>
        <li>Install the required Python libraries:
            <pre><code>pip install python-docx odfpy rich</code></pre>
        </li>
    </ol>
    
    <h2>Usage</h2>
    <ol>
        <li>Navigate to the script's directory in your terminal.</li>
        <li>Run the script:
            <pre><code>python your_script_name.py</code></pre>
            (Replace <code>your_script_name.py</code> with the actual name of your Python file).
        </li>
        <li>The script will prompt you to enter the path to the <code>.docx</code> or <code>.odt</code> file you wish to analyse.</li>
        <li>Enter the full or relative path and press Enter.</li>
        <li>The script will process the file and save the results to a new <code>.odt</code> file inside the <code>output_footnotes/</code> sub-directory.</li>
        <li>To stop the script, type <code>esci</code> at the prompt and press Enter. <br>
            <span class="note">(Note: The exit command is currently the Italian 'esci'. You can easily change this in the script's <code>if __name__ == "__main__":</code> block to 'quit' or 'exit' if preferred).</span>
        </li>
    </ol>
 
    <h2>Limitations</h2>
    <ul>
        <li><strong>Formatting:</strong> This script ONLY preserves basic <strong>bold</strong>, <em>italic</em>, and <u>underline</u> formatting.
            It does <strong>NOT</strong> currently preserve other formatting such as:
            <ul>
                <li>Fonts, colours, or text sizes.</li>
                <li>Lists (bulleted or numbered).</li>
                <li>Tables.</li>
                <li>Images.</li>
                <li>Hyperlinks.</li>
                <li>Paragraph alignment, indentation, or spacing.</li>
            </ul>
        </li>
        <li><strong>Structure:</strong> The script generates a simple, sequential LIST of the footnote text in a new document. It does NOT replicate the footnote reference markers (¹, ², ³) within a copy of the main text, nor does it place the extracted notes into the page-footer layout of the output ODT.</li>
        <li><strong>Style Complexity:</strong> Complex or inherited styles, especially within ODT documents, may not be fully or correctly interpreted beyond the basic formatting checks implemented.</li>
    </ul>

    <h2>Contributing</h2>
    <p>Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.</p>

    <h2>License</h2>
    <p><a href="https://choosealicense.com/licenses/mit/">MIT</a> <br>
    <span class="note">(Suggestion: Add an MIT license file if you wish, or choose another)</span></p>

</body>
</html>