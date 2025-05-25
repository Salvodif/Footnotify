import yaml

def load_settings(filepath: str) -> dict:
    """
    Parses a YAML file and returns its content as a Python dictionary.

    Args:
        filepath: The path to the YAML file.

    Returns:
        A dictionary representing the YAML content, or an empty dictionary
        if an error occurs.
    """
    try:
        with open(filepath, 'r') as file:
            settings = yaml.safe_load(file)
            return settings if settings else {}
    except FileNotFoundError:
        print(f"Error: Settings file not found at '{filepath}'.")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file '{filepath}': {e}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred while loading settings from '{filepath}': {e}")
        return {}

if __name__ == '__main__':
    # Example usage:
    # Create a dummy settings.yaml for testing if it doesn't exist
    # (though it should have been created by the previous step)
    dummy_yaml_content = """
reference_types:
  book:
    template: "Author, <i>Title</i> (Place: Publisher, Date)."
    fields:
      Author: '(?P<Author>[A-Z][A-Za-z\\s.,]+(?:et al\\.)?),'
      Title: '<i>(?P<Title>[^<]+)</i>'
      Place: '\\((?P<Place>[^:]+):'
      Publisher: ':\\s*(?P<Publisher>[^,]+),'
      Date: ', (?P<Date>\\d{4})\\)\\.'
    required_fields: ["Author", "Title", "Publisher", "Date"]
special_classics:
  STh: "Thomas Aquinas, <i>Summa Theologiae</i>"
"""
    dummy_filepath = "dummy_settings_for_test.yaml"
    try:
        with open(dummy_filepath, 'w') as f:
            f.write(dummy_yaml_content)

        print(f"Attempting to load settings from '{dummy_filepath}'...")
        settings_data = load_settings(dummy_filepath)

        if settings_data:
            print("\nSettings loaded successfully:")
            # Print a part of the loaded data for verification
            if "reference_types" in settings_data and "book" in settings_data["reference_types"]:
                print("Book template:", settings_data["reference_types"]["book"]["template"])
            if "special_classics" in settings_data:
                print("STh:", settings_data["special_classics"].get("STh"))
        else:
            print("\nFailed to load settings or settings file was empty.")

        print(f"\nAttempting to load settings from 'non_existent_settings.yaml' (testing FileNotFoundError)...")
        load_settings("non_existent_settings.yaml")

        # Create an invalid YAML file for testing YAMLError
        invalid_yaml_filepath = "invalid_settings.yaml"
        with open(invalid_yaml_filepath, 'w') as f:
            f.write("reference_types: [unclosed_bracket\n  book: another_value")
        print(f"\nAttempting to load settings from '{invalid_yaml_filepath}' (testing YAMLError)...")
        load_settings(invalid_yaml_filepath)

    finally:
        # Clean up dummy files
        import os
        if os.path.exists(dummy_filepath):
            os.remove(dummy_filepath)
        if os.path.exists(invalid_yaml_filepath):
            os.remove(invalid_yaml_filepath)
        print("\nCleaned up dummy test files.")
