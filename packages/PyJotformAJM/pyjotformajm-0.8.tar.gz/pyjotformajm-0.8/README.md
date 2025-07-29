# PyJotformAJM

Welcome to the PyJotformAJM repository. This project encapsulates the functionality for interacting with JotForm submissions in a structured and organized manner.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Class and Methods](#class-and-methods)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Introduction

The PyJotformAJM provides a class to manage and interact with JotForm submissions. The aim is to provide a seamless integration with JotForm's API, facilitating various operations such as fetching new submissions, validating clients, and organizing submission answers.

## Features

- Fetch and handle new JotForm submissions
- Organize and validate submission data
- Ignore specific fields based on predefined settings
- Initialize and validate JotForm clients

## Installation

To use this project, you need to have Python 3.12.2 installed on your system. You can follow the steps below to set up the project locally.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/amcsparron2793-Water/jotform-python-wrapper.git
   cd jotform-python-wrapper
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

  - On Windows:
    ```bash
    venv\Scripts\activate
    ```

  - On macOS and Linux:
    ```bash
    source venv/bin/activate
    ```

4. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To use the JotForm class, simply import it and utilize its methods as needed. Below is an example script demonstrating basic usage:

```python
# File: main.py

from PyJotformAJM import JotForm

def main():
    # Create an instance of JotForm
    jot_form = JotForm()

    # Example methods usage
    if jot_form.has_new_entries():
        print(f"New entries total: {jot_form.new_entries_total()}")
        submissions = jot_form.get_new_submissions()
        for submission in submissions:
            answers = jot_form.get_answers_from_submission(submission)
            print(answers)

if __name__ == "__main__":
    main()
```

## Class and Methods

### Class: `JotForm`

#### Class Attributes

- `DEFAULT_FORM_ID`
- `ILLEGAL_STARTING_CHARACTERS`
- `IGNORED_FIELD_MESSAGE`
- `DATE_TODAY`
- `RAW_NEWEST_SUBMISSIONS_PATH`

#### Instance Attributes

- `_valid_submission_ids`
- `has_valid_client`
- `_section_fields_dict`
- `logger`
- `_last_submission_id`
- `_real_jf_field_names`
- `form_id`
- `_new_entries_total`
- `ignored_submission_fields`
- `_has_valid_client`
- `_organized_submission_answers`
- `client`
- `_form_section_headers`
- `_has_new_entries`
- `_submission`

#### Methods

- `__init__(self, form_id=None)`
- `real_jf_field_names(self)`
- `submission(self)`
- `section_fields_dict(self)`
- `form_section_headers(self)`
- `has_new_entries(self)`
- `new_entries_total(self)`
- `last_submission_id(self)`
- `_initialize_client(self)`
- `_validate_client(self)`
- `_get_last_submission_id(self)`
- `get_new_submissions(self)`
- `_strip_answer(self, answer)`
- `_get_answers_dict(self, submission)`
- `get_answers_from_submission(self, submission)`
- `is_illegal_field(self, field_name)`
- `_write_raw_newest_submissions(self)`

## Contributing

Contributions are welcome! Please follow these guidelines to contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature-name`.
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.txt) file for details.

## Contact

For any questions, please contact:
- GitHub: [amcsparron2793-Water](https://github.com/amcsparron2793-Water)