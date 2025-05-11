import os
from docx import Document as DocxDocument
from odf.opendocument import OpenDocumentText, load as odf_load
from odf.text import P as OdfP, Span as OdfSpan, Note as OdfNote, NoteBody as OdfNoteBody, LineBreak as OdfLineBreak
from odf.style import Style, TextProperties
from odf import teletype
from odf.element import Element 
from odf.namespaces import OFFICENS


# Importazioni Rich
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt # Per un input più carino con Rich
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.rule import Rule

# Inizializza la console Rich
console = Console()

# --- Funzioni Helper per Stili ODT --- (Identiche a prima)
def get_odt_style_name(fmt_dict):
    parts = []
    if fmt_dict.get('bold'): parts.append("bold")
    if fmt_dict.get('italic'): parts.append("italic")
    if fmt_dict.get('underline'): parts.append("underline")
    if not parts: return "default"
    return "ft_" + "_".join(parts)

def create_or_get_odt_style(doc_automatic_styles_container, fmt_dict):
    style_name = get_odt_style_name(fmt_dict)
    if style_name == "default": 
        return None

    if doc_automatic_styles_container:
        for s_element in doc_automatic_styles_container.getElementsByType(Style):
            if s_element.getAttribute("name") == style_name and s_element.getAttribute("family") == "text":
                return style_name
            
    style = Style(name=style_name, family="text")
    text_props = TextProperties()
    
    applied_prop = False
    if fmt_dict.get('bold'):
        text_props.setAttribute("fontweight", "bold")
        applied_prop = True
    if fmt_dict.get('italic'):
        text_props.setAttribute("fontstyle", "italic")
        applied_prop = True
    if fmt_dict.get('underline'):
        text_props.setAttribute("textunderlinetype", "single")
        text_props.setAttribute("textunderlinestyle", "solid")
        applied_prop = True

    if applied_prop:
        style.addElement(text_props)
        if doc_automatic_styles_container:
            doc_automatic_styles_container.addElement(style)
        else:
            console.print(f"[yellow]AVVISO:[/yellow] Contenitore stili automatici non valido per lo stile '{style_name}'.")
        return style_name
    return None

# --- Funzioni di Estrazione Footnote --- (Identiche a prima)
def extract_footnotes_from_docx(filepath):
    console.print(f"Estrazione footnotes da DOCX: [cyan]{filepath}[/cyan]")
    doc = DocxDocument(filepath)
    extracted_footnotes = []

    footnotes_part = None
    if hasattr(doc.part, 'document') and hasattr(doc.part.document, 'footnotes_part'):
        footnotes_part = doc.part.document.footnotes_part
    
    if not footnotes_part or not footnotes_part.footnotes:
        console.print("[yellow]Nessuna footnote trovata nel documento DOCX.[/yellow]")
        return []

    num_footnotes = len(footnotes_part.footnotes)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task(f"Elaborazione {num_footnotes} footnotes DOCX...", total=num_footnotes)
        for i, footnote in enumerate(footnotes_part.footnotes):
            footnote_paragraphs_data = []
            for paragraph in footnote.paragraphs:
                paragraph_runs_data = []
                for run in paragraph.runs:
                    fmt = {
                        'bold': run.bold if run.bold is not None else False,
                        'italic': run.italic if run.italic is not None else False,
                        'underline': run.underline if run.underline is not None else False,
                    }
                    paragraph_runs_data.append((run.text, fmt))
                footnote_paragraphs_data.append(paragraph_runs_data)
            extracted_footnotes.append(footnote_paragraphs_data)
            progress.update(task, advance=1)
    
    console.print(f"[green]Estratte {len(extracted_footnotes)} footnotes da DOCX.[/green]")
    return extracted_footnotes

def parse_odt_style_attributes(doc_odt, style_name_to_find):
    fmt = {'bold': False, 'italic': False, 'underline': False}
    if not style_name_to_find:
        return fmt

    style_element = None
    style_sources = []
    if hasattr(doc_odt, 'automaticstyles') and doc_odt.automaticstyles:
        style_sources.append(doc_odt.automaticstyles)
    if hasattr(doc_odt, 'styles') and doc_odt.styles:
        style_sources.append(doc_odt.styles)
    
    MODEL_STYLE_QNAME = Style(name="temp-qname-style", family="text").qname

    for source_container in style_sources:
        for s_candidate in source_container.childNodes:
            if hasattr(s_candidate, 'qname') and s_candidate.qname == MODEL_STYLE_QNAME:
                 if s_candidate.getAttribute("name") == style_name_to_find and \
                    s_candidate.getAttribute("family") == "text":
                    style_element = s_candidate
                    break
            if style_element: break
        if style_element: break
    
    if style_element:
        text_props_list = style_element.getElementsByType(TextProperties)
        if text_props_list:
            text_props = text_props_list[0]
            if text_props.getAttribute("fontweight") == "bold":
                fmt['bold'] = True
            if text_props.getAttribute("fontstyle") == "italic":
                fmt['italic'] = True
            if text_props.getAttribute("textunderlinetype") and \
               text_props.getAttribute("textunderlinetype") != "none":
                fmt['underline'] = True
    return fmt


def extract_footnotes_from_odt(filepath):
    console.print(f"Estrazione footnotes da ODT: [cyan]{filepath}[/cyan]")
    doc = odf_load(filepath)
    extracted_footnotes = []

    notes_found = doc.getElementsByType(OdfNote)
    
    MODEL_NOTE_QNAME = OdfNote(noteclass="footnote", id="temp-qname").qname
    MODEL_NOTE_BODY_QNAME = OdfNoteBody().qname
    MODEL_P_QNAME = OdfP().qname
    MODEL_SPAN_QNAME = OdfSpan().qname
    MODEL_LINEBREAK_QNAME = OdfLineBreak().qname

    footnote_elements = []
    for n in notes_found:
        if hasattr(n, 'qname') and n.qname == MODEL_NOTE_QNAME: # Confronto qname
            if n.getAttribute("noteclass") == "footnote": # Poi attributo
                footnote_elements.append(n)

    if not footnote_elements:
        console.print("[yellow]Nessuna footnote trovata nel documento ODT.[/yellow]")
        return []

    num_footnotes = len(footnote_elements)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task(f"Elaborazione {num_footnotes} footnotes ODT...", total=num_footnotes)
        for i, note_element in enumerate(footnote_elements):
            note_body = None
            for child in note_element.childNodes:
                if hasattr(child, 'qname') and child.qname == MODEL_NOTE_BODY_QNAME:
                    note_body = child
                    break
            
            if not note_body:
                progress.update(task, advance=1)
                continue
            
            footnote_paragraphs_data = []
            for p_element_candidate in note_body.childNodes:
                if not (hasattr(p_element_candidate, 'qname') and p_element_candidate.qname == MODEL_P_QNAME):
                    continue

                p_element = p_element_candidate
                paragraph_runs_data = []
                
                base_fmt = {} 
                # parent_p_style_name = p_element.getAttribute("stylename")
                # if parent_p_style_name:
                #     base_fmt = parse_odt_style_attributes(doc, parent_p_style_name)


                for child_node in p_element.childNodes:
                    text_content = "" 
                    fmt = base_fmt.copy() 

                    if child_node.nodeType == child_node.TEXT_NODE:
                        text_content = child_node.data
                    elif hasattr(child_node, 'qname'):
                        if child_node.qname == MODEL_SPAN_QNAME:
                            span_element = child_node
                            text_content = teletype.extractText(span_element)
                            style_name = span_element.getAttribute("stylename")
                            if style_name:
                                span_fmt = parse_odt_style_attributes(doc, style_name)
                                fmt.update(span_fmt)
                        elif child_node.qname == MODEL_LINEBREAK_QNAME:
                            text_content = "\n"
                    
                    if text_content.strip() or text_content == "\n":
                        paragraph_runs_data.append((text_content, fmt))
                
                if paragraph_runs_data:
                     footnote_paragraphs_data.append(paragraph_runs_data)
            extracted_footnotes.append(footnote_paragraphs_data)
            progress.update(task, advance=1)

    console.print(f"[green]Estratte {len(extracted_footnotes)} footnotes da ODT.[/green]")
    return extracted_footnotes


# --- Funzione di Creazione ODT con Footnotes --- (Identica a prima)
def create_odt_with_footnotes(footnotes_data, output_filepath):
    console.print(f"Creazione file ODT di output: [cyan]{output_filepath}[/cyan]")
    new_doc = OpenDocumentText()

    if not hasattr(new_doc, 'automaticstyles') or new_doc.automaticstyles is None:
        console.print("[yellow]INFO:[/yellow] [cyan]new_doc.automaticstyles[/cyan] non inizializzato. Tentativo di creazione manuale.")
        auto_styles_element = Element(qname=(OFFICENS, 'automatic-styles'))
        if hasattr(new_doc, 'document') and new_doc.document is not None:
            target_parent = new_doc.document
            reference_node = None
            if hasattr(new_doc, 'body') and new_doc.body is not None:
                reference_node = new_doc.body
            if reference_node:
                target_parent.insertBefore(auto_styles_element, reference_node)
            else:
                if target_parent.hasChildNodes():
                    target_parent.insertBefore(auto_styles_element, target_parent.firstChild)
                else:
                    target_parent.addElement(auto_styles_element)
            new_doc.automaticstyles = auto_styles_element
            console.print("[green]INFO:[/green] Creato e inserito [cyan]<office:automatic-styles>[/cyan] manualmente.")
        else:
            console.print("[bold red]ERRORE:[/bold red] Impossibile trovare [cyan]new_doc.document[/cyan] per inserire [cyan]automatic-styles[/cyan].")

    num_footnotes_to_write = len(footnotes_data)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        task_write = progress.add_task(f"Scrittura {num_footnotes_to_write} footnotes...", total=num_footnotes_to_write)
        for i, footnote_content_paragraphs in enumerate(footnotes_data):
            heading_p = OdfP()
            heading_span = OdfSpan(text=f"--- Nota a piè di pagina {i+1} ---")
            heading_p.addElement(heading_span)
            new_doc.text.addElement(heading_p)

            for paragraph_runs in footnote_content_paragraphs:
                if not paragraph_runs:
                    new_doc.text.addElement(OdfP())
                    continue
                odt_paragraph = OdfP()
                for text_content, fmt_dict in paragraph_runs:
                    if not text_content: continue
                    if "\n" in text_content:
                        parts = text_content.split('\n')
                        first_part = True
                        for part_text in parts:
                            if not first_part and odt_paragraph.hasChildNodes():
                                odt_paragraph.addElement(OdfLineBreak())
                            if part_text:
                                span = OdfSpan(text=part_text)
                                style_name = create_or_get_odt_style(new_doc.automaticstyles, fmt_dict)
                                if style_name:
                                    span.setAttribute("stylename", style_name)
                                odt_paragraph.addElement(span)
                            first_part = False
                    else:
                        span = OdfSpan(text=text_content)
                        style_name = create_or_get_odt_style(new_doc.automaticstyles, fmt_dict)
                        if style_name:
                            span.setAttribute("stylename", style_name)
                        odt_paragraph.addElement(span)
                if odt_paragraph.hasChildNodes():
                    new_doc.text.addElement(odt_paragraph)
            new_doc.text.addElement(OdfP())
            progress.update(task_write, advance=1)
    try:
        new_doc.save(output_filepath)
        console.print(f"[green]File '{output_filepath}' creato con successo con {num_footnotes_to_write} footnotes.[/green]")
    except Exception as e:
        console.print(f"[bold red]Errore durante il salvataggio del file ODT:[/bold red] {e}")
        # (gestione errore directory omessa per brevità, ma era corretta prima)

# --- Funzione Principale Modificata ---
def run_footnote_extraction(input_filepath, output_filepath_base="output_footnotes"):
    """
    Funzione principale che orchestra l'estrazione e la creazione del file di output.
    """
    if not os.path.exists(input_filepath):
        console.print(f"[bold red]Errore:[/bold red] File di input '[cyan]{input_filepath}[/cyan]' non trovato.")
        return

    # Crea la directory di output se non esiste
    if not os.path.exists(output_filepath_base):
        try:
            os.makedirs(output_filepath_base)
            console.print(f"Creata directory di output: [cyan]{output_filepath_base}[/cyan]")
        except OSError as e:
            console.print(f"[bold red]Errore creando directory di output {output_filepath_base}:[/bold red] {e}")
            return # Non possiamo procedere senza directory di output

    base_filename, ext = os.path.splitext(os.path.basename(input_filepath))
    ext = ext.lower() # Estensione in minuscolo

    # Costruisci il nome del file di output
    output_filename = f"footnotes_da_{base_filename.replace(' ', '_')}.odt"
    output_filepath_full = os.path.join(output_filepath_base, output_filename)
    
    console.print(Rule(f"Inizio elaborazione: [b cyan]{os.path.basename(input_filepath)}[/b cyan]"))
    
    footnotes_data = []
    if ext == ".docx":
        try:
            # Controllo preliminare (opzionale ma buono)
            doc_for_check = DocxDocument(input_filepath)
            fp = None
            if hasattr(doc_for_check.part, 'document') and hasattr(doc_for_check.part.document, 'footnotes_part'):
                 fp = doc_for_check.part.document.footnotes_part
            
            if fp and fp.footnotes:
                 footnotes_data = extract_footnotes_from_docx(input_filepath)
            else:
                console.print("[yellow]Nessuna footnote trovata nel documento DOCX (controllo preliminare).[/yellow]")
        except Exception as e:
            console.print(f"[bold red]Errore durante il caricamento o controllo preliminare del DOCX:[/bold red] {e}")
            return

    elif ext == ".odt":
        footnotes_data = extract_footnotes_from_odt(input_filepath)
    else:
        console.print(f"[bold red]Errore:[/bold red] Formato file '[yellow]{ext}[/yellow]' non supportato. Usare .docx o .odt.")
        return

    if footnotes_data:
        create_odt_with_footnotes(footnotes_data, output_filepath_full)
    else:
        console.print("[yellow]Nessuna footnote da scrivere nel file di output.[/yellow]")
    console.print(Rule(f"Fine elaborazione: [b cyan]{os.path.basename(input_filepath)}[/b cyan]"))


# --- Esecuzione Script ---
if __name__ == "__main__":
    console.print(Panel.fit("📝 Estrattore di Footnote Interattivo 📝", style="bold blue on white", border_style="blue"))
    
    while True:
        input_file = Prompt.ask(
            "Inserisci il percorso del file .odt o .docx da analizzare (o 'esci' per terminare)"
        ).strip()

        if not input_file: # Se l'utente preme Invio senza scrivere nulla
            console.print("[yellow]Nessun file specificato. Riprova o digita 'esci'.[/yellow]")
            continue

        if input_file.lower() == 'esci':
            console.print("[bold blue]Arrivederci![/bold blue]")
            break

        if not os.path.exists(input_file):
            console.print(f"[bold red]Errore:[/bold red] Il file '[cyan]{input_file}[/cyan]' non esiste. Controlla il percorso e riprova.")
            continue

        # Verifica estensione prima di chiamare run_footnote_extraction
        _, ext_check = os.path.splitext(input_file.lower())
        if ext_check not in [".odt", ".docx"]:
            console.print(f"[bold red]Errore:[/bold red] Estensione file '[yellow]{ext_check}[/yellow]' non supportata. Sono accettati solo .odt e .docx.")
            continue
            
        # Esegui l'elaborazione
        run_footnote_extraction(input_file, output_filepath_base="output_footnotes")
        console.print("\nElaborazione completata per questo file.\n")

    console.print("[bold green]Programma terminato.[/bold green]")