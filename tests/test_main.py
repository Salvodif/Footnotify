# tests/test_main.py
import unittest.mock as mock
import os
import pytest

# Assuming main.py is in the parent directory or PYTHONPATH is set up
# For imports to work correctly, ensure the project root is in PYTHONPATH when running pytest
import main
import footnote_processor
import settings_parser

# Import sample data from the file created by the previous step
from tests.sample_footnote_data import sample_raw_footnotes # Using the name I specified

@pytest.fixture
def mock_main_dependencies(mocker):
    """Mocks dependencies for testing run_footnote_extraction in main.py."""
    # Mock file extraction to return our sample raw data
    mocker.patch('main.extract_footnotes_from_docx', return_value=sample_raw_footnotes)
    mocker.patch('main.extract_footnotes_from_odt', return_value=sample_raw_footnotes)
    
    # Load test settings from tests/test_settings.yaml
    test_settings_path = os.path.join(os.path.dirname(__file__), 'test_settings.yaml')
    # Ensure test_settings.yaml was created in the previous step by the worker
    # For the purpose of this test setup, we assume it exists or load_settings handles its absence
    test_settings = settings_parser.load_settings(test_settings_path) 
    mocker.patch('main.settings_parser.load_settings', return_value=test_settings)
    
    # Mock the output creation function
    mocker.patch('main.create_odt_with_footnotes')

def test_run_footnote_extraction_docx_flow(mock_main_dependencies, tmp_path, capsys):
    """
    Test the overall flow of run_footnote_extraction for a DOCX file.
    Focuses on orchestration and ensures create_odt_with_footnotes is called.
    """
    # Create a dummy input file so os.path.exists(input_filepath) passes in main.py
    # This is needed because run_footnote_extraction checks for file existence early.
    input_file_path = tmp_path / "dummy_input.docx"
    input_file_path.write_text("dummy docx content")
    
    output_base_path = tmp_path / "output_test_docx"

    # Path to the test settings file created in the 'develop test data' step
    settings_file_path = os.path.join(os.path.dirname(__file__), 'test_settings.yaml')

    main.run_footnote_extraction(str(input_file_path), str(output_base_path), settings_filepath=settings_file_path)

    # Assert that create_odt_with_footnotes was called (basic check)
    main.create_odt_with_footnotes.assert_called_once()
    
    # To check arguments passed to create_odt_with_footnotes:
    # args, kwargs = main.create_odt_with_footnotes.call_args
    # processed_footnotes_for_odt = args[0]
    # assert len(processed_footnotes_for_odt) == len(sample_raw_footnotes)
    # You could add more detailed assertions here about the content of processed_footnotes_for_odt
    # This would involve re-running parts of footnote_processor logic or having expected processed data.

def test_run_footnote_extraction_odt_flow(mock_main_dependencies, tmp_path, capsys):
    """
    Test the overall flow of run_footnote_extraction for an ODT file.
    """
    input_file_path = tmp_path / "dummy_input.odt"
    input_file_path.write_text("dummy odt content")
    
    output_base_path = tmp_path / "output_test_odt"
    settings_file_path = os.path.join(os.path.dirname(__file__), 'test_settings.yaml')

    main.run_footnote_extraction(str(input_file_path), str(output_base_path), settings_filepath=settings_file_path)
    
    main.create_odt_with_footnotes.assert_called_once()

def test_run_footnote_extraction_no_input_file(capsys, tmp_path):
    """Test how run_footnote_extraction handles a non-existent input file."""
    output_base_path = tmp_path / "output_no_file"
    settings_file_path = os.path.join(os.path.dirname(__file__), 'test_settings.yaml')

    # We need to mock create_odt_with_footnotes here because it's not covered by mock_main_dependencies
    # and this test function doesn't use mock_main_dependencies.
    with mock.patch('main.create_odt_with_footnotes') as mock_create_odt:
        main.run_footnote_extraction("non_existent_file.docx", str(output_base_path), settings_filepath=settings_file_path)
    
    captured = capsys.readouterr()
    assert "File di input 'non_existent_file.docx' non trovato" in captured.out # Or captured.err depending on print
    mock_create_odt.assert_not_called() # Ensure output creation was not attempted

def test_run_footnote_extraction_no_settings_file(tmp_path, capsys):
    """Test how run_footnote_extraction handles a non-existent settings file."""
    input_file_path = tmp_path / "dummy_input_for_settings_test.docx"
    input_file_path.write_text("dummy content")
    output_base_path = tmp_path / "output_no_settings"

    # Temporarily mock load_settings to simulate it returning {} or raising error for this specific test
    # Also mock create_odt_with_footnotes for this specific test scope
    with mock.patch('main.settings_parser.load_settings', return_value={}) as mock_load_settings, \
         mock.patch('main.create_odt_with_footnotes') as mock_create_odt:
        main.run_footnote_extraction(str(input_file_path), str(output_base_path), settings_filepath="non_existent_settings.yaml")
    
    captured = capsys.readouterr()
    # Check for the specific error message printed by main.py when settings are not loaded
    assert "Impossibile caricare il file delle impostazioni" in captured.out 
    mock_create_odt.assert_not_called()

# Additional test: What if settings file is found but is empty or invalid?
def test_run_footnote_extraction_invalid_settings_content(tmp_path, capsys):
    """Test how run_footnote_extraction handles an invalid/empty settings file."""
    input_file_path = tmp_path / "dummy_input_for_invalid_settings.docx"
    input_file_path.write_text("dummy content")
    output_base_path = tmp_path / "output_invalid_settings"
    
    invalid_settings_file = tmp_path / "invalid_settings.yaml"
    invalid_settings_file.write_text("this is not valid yaml content: {") # Malformed YAML

    with mock.patch('main.create_odt_with_footnotes') as mock_create_odt:
        main.run_footnote_extraction(str(input_file_path), str(output_base_path), settings_filepath=str(invalid_settings_file))

    captured = capsys.readouterr()
    assert "Impossibile caricare il file delle impostazioni da " + str(invalid_settings_file) in captured.out
    mock_create_odt.assert_not_called()
