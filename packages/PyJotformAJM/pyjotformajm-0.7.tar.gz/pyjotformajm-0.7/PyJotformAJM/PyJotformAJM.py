"""
PyJotformAJM.py

"""
from json import dump, JSONDecodeError
from pathlib import Path

from datetime import datetime
from logging import getLogger
from typing import Union, Optional

from jotform import JotformAPIClient
from ApiKeyAJM.ApiKeyAJM import APIKeyFromFile

try:
    from .err import *
    from .SectionsFieldDict import SectionFieldsDict
    from .Submission import Submission
except ImportError:
    from err import *
    from SectionsFieldDict import SectionFieldsDict
    from Submission import Submission


class _JotFormClient(APIKeyFromFile):
    """
    JotFormClient is a class that extends APIKey and provides methods for initializing a client,
    validating the client, and handling authentication errors.
    The initializer sets up the client attribute and invokes the _initialize_client method.
    The _initialize_client method creates a JotformAPIClient instance based on the provided API key.
     If no key is provided, it attempts to fetch the key from the specified location.
     The _validate_client method checks the client by making a request to get_user
     and raises a JotFormAuthenticationError if an HTTPError occurs during the request.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """
        Initializes the client object by creating an instance of the
        JotformAPIClient class using the provided API key.
        If no API key is provided, it fetches the API key from the
        specified location before creating the client object.
        This method then validates the client to ensure it is ready for making API requests.
        """
        if self.api_key:
            self.client = JotformAPIClient(self.api_key)
        else:
            self.client = JotformAPIClient(self._fetch_api_key(self.api_key_location))
        self._validate_client()

    def _validate_client(self):
        """
        Validates the client by attempting to get a user.
        If an HTTPError occurs during the process,
        it raises a JotFormAuthenticationError with details from the error.
        """
        try:
            self.client.get_user()
        except HTTPError as e:
            raise JotFormAuthenticationError(
                url=e.url, code=e.code, msg=e.reason, hdrs=e.headers, fp=e.fp) from None


class JotForm(_JotFormClient):
    """
    This code defines a class `JotForm` that extends `_JotFormClient` class functionality
    and implements various properties and methods for interacting with JotForm submissions.

    Attributes:
    - `DEFAULT_FORM_ID`: Default form ID value set to `None`.
    - `ILLEGAL_STARTING_CHARACTERS`: List of illegal starting characters.
    - `IGNORED_FIELD_MESSAGE`: Message for ignored fields.
    - `DATE_TODAY`: Current date formatted as '%m%d%y'.
    - `RAW_NEWEST_SUBMISSIONS_PATH`: Path for storing newest submissions JSON file.
    - `FORM_ID_ERR_MSG`: Error message for missing form ID.

    Methods:
    - `__init__`: Class constructor to initialize instance attributes and validate form ID.
    - `real_jf_field_names`: Property to get real JotForm field names from submissions.
    - `submission`: Property to get submission object for the current instance.
    - `section_fields_dict`: Getter method for the `section_fields_dict` property.
    - `form_section_headers`: Property to retrieve section field headers from submissions.
    - `has_new_entries`: Property to check for new entries in the form.
    - `new_entries_total`: Property to get total count of new entries in the form.
    - `last_submission_id`: Property to retrieve the last submission ID for the specified form.
    - `has_valid_client`: Property to check for the validity of the JotForm client.
    - `_get_last_submission_id`: Internal method to get the last submission ID based on the provided datetime.
    - `get_new_submissions`: Method to return new submissions for a given form.
    """
    DEFAULT_FORM_ID = None
    ILLEGAL_STARTING_CHARACTERS = ['<']
    IGNORED_FIELD_MESSAGE = "ignored due to illegal starting character"
    # noinspection SpellCheckingInspection
    DATE_TODAY = datetime.now().date().strftime('%m%d%y')
    RAW_NEWEST_SUBMISSIONS_PATH = f'../Misc_Project_Files/newest_submissions_{DATE_TODAY}.json'
    FORM_ID_ERR_MSG = ("form_id not found, if form_id was not a keyword arg, "
                       "check that DEFAULT_FORM_ID is set in any subclasses.")

    def __init__(self, **kwargs):
        if hasattr(self, 'logger'):
            pass
        else:
            self.logger = kwargs.get('logger', getLogger('dummy_logger'))

        self._section_fields_dict = None
        self._valid_submission_ids = None
        self._submission = None
        self._organized_submission_answers = None

        self._has_valid_client = False
        self._has_new_entries = None
        self._new_entries_total = None
        self._last_submission_id = None
        self._real_jf_field_names = None
        self._form_section_headers = None

        self.ignored_submission_fields = kwargs.get('ignored_submission_fields', [])

        self.form_id = kwargs.get('form_id', JotForm.DEFAULT_FORM_ID)
        self._validate_form_id()

        super().__init__(**kwargs)

        if not self.has_valid_client:
            raise NoJotformClientError('no valid JotForm client object found.')
        self.logger.info(f"{self.__class__.__name__} Initialization complete.")

    def _validate_form_id(self):
        if not self.form_id and not JotForm.DEFAULT_FORM_ID:
            raise AttributeError(JotForm.FORM_ID_ERR_MSG)

    @property
    def real_jf_field_names(self):
        """
        This code defines a property called `real_jf_field_names` in a class.

        The property returns a list of field names extracted from the answers of a JotForm submission. The field
        names are retrieved using the `get_answers_from_submission` method and stored in the `_real_jf_field_names`
        variable before being returned.

        If the `_real_jf_field_names` variable is not set, the code executes the `get_answers_from_submission` method
        and retrieves the field names from the last submission ID in the `new_entries_total` attribute.

        The property is accessed using dot notation on an instance of the class.

        """
        if not self._real_jf_field_names:
            self._real_jf_field_names = [{'field_name': x['field_name'], 'uni_field_name': x['uni_field_name']}
                                         for x in self.get_answers_from_submission(self.last_submission_id)['answers']]
        return self._real_jf_field_names

    @property
    def submission(self):
        """
        Returns the submission object for the current instance.

        If the `_submission` attribute has not been set, it creates a new `Submission` object with the last submission ID
            and assigns it to the attribute. It then returns the `_submission` attribute.

        Returns:
            Submission: The submission object for the current instance.
        """
        if not self._submission:
            self._submission = Submission(self, self.last_submission_id)
        return self._submission

    @submission.setter
    def submission(self, sub_id: str):
        self._submission = Submission(self, sub_id)

    @property
    def section_fields_dict(self):
        """
        Getter method for the section_fields_dict property.

        Returns:
            The section_fields_dict property value. If it is not yet initialized, it initializes it using the SectionFieldsDict class.

        """
        if not self._section_fields_dict:
            self._section_fields_dict = SectionFieldsDict(self).section_fields_dict
        return self._section_fields_dict

    @property
    def form_section_headers(self):
        """
        This code defines a property method named 'form_section_headers'.

        When this property is accessed, it returns a list of field names from a submission's answers where the field
        type is 'control_head'. This property uses a lazy loading technique - it only retrieves the field names when
        the property is accessed for the first time and stores them in the '_form_section_headers' attribute for
        future use. If the '_form_section_headers' attribute is already populated, it simply returns its value
        without making additional database queries.

        """
        if not self._form_section_headers:
            self._form_section_headers = [x['field_name'] for x in
                                          self.get_answers_from_submission(
                                              self.last_submission_id)['answers']
                                          if x['field_type'] == 'control_head']
        return self._form_section_headers

    @property
    def has_new_entries(self):
        """
        This code defines a property called `has_new_entries` for a class.
        The property is used to determine whether there are new entries in a form.

        Attributes:
            - `client`: An object representing the client used to interact with forms.
            - `form_id`: The ID of the form to check for new entries.

        Returns:
            - `True` if there are new entries in the form.
            - `False` if there are no new entries in the form.

        Note:
        This property assumes that the `client` object has a method called `get_form` that returns information
        about the form specified by `form_id`. The information should include a field called 'new'
        representing the count of new entries.

        Usage:
        ```
        # Create an instance of the class
        client = Client()
        form_id = 123

        # Call the property to check for new entries
        is_new = client.has_new_entries
        ```
        """
        if int(self.client.get_form(self.form_id)['new']) > 0:
            self._has_new_entries = True
        else:
            self._has_new_entries = False
        return self._has_new_entries

    @property
    def new_entries_total(self):
        """
        @property
        def new_entries_total(self):
            """
        if self.has_new_entries:
            self._new_entries_total = {'total': int(self.client.get_form(self.form_id)['new']),
                                       'last_submission': self.client.get_form(self.form_id)['last_submission'],
                                       'last_submission_id': self.last_submission_id}
        else:
            self._new_entries_total = None
        return self._new_entries_total

    @property
    def last_submission_id(self):
        """
        Retrieves the last submission ID for the specified form.

        @return: The last submission ID as an integer.
        """
        self._last_submission_id = self._get_last_submission_id(self.client.get_form(self.form_id)['last_submission'])
        return self._last_submission_id

    @property
    def has_valid_client(self):
        """
        @property
        has_valid_client(self)

        Checks if the object has a valid client attribute and returns a boolean value indicating the validation result.
        """
        if hasattr(self, 'client'):
            self._has_valid_client = True
        else:
            self._has_valid_client = False
        return self._has_valid_client

    def _get_last_submission_id(self, last_sub_datetime: Union[datetime, str]):
        """
        This method is used to get the last submission ID of a form based on the provided last submission datetime.

        Parameters:
        - last_sub_datetime: The last submission datetime to search for. It can be provided as a datetime object or a string in ISO format.

        Returns:
        - The last submission ID as an integer if it exists.
        - None if there is no submission matching the provided datetime.

        Note:
        - This method relies on the 'client' attribute which should be an instance of a client object that has the 'get_form_submissions' method.
        - The 'client.get_form_submissions' method returns a list of submissions for the provided form ID.
        - The method iterates through each submission and checks if the 'created_at' datetime matches the provided last submission datetime.
        - If a matching submission is found, its ID is stored in the 'last_sub_id' list.
        - The method returns the first ID from the 'last_sub_id' list if it is not empty.
        - If there are no matching submissions, None is returned.
        """
        last_sub_id = [x['id'] for x in self.client.get_form_submissions(self.form_id)
                       if datetime.fromisoformat(x['created_at']) == datetime.fromisoformat(last_sub_datetime)][0]
        if last_sub_id:
            return last_sub_id

        return None

    def get_new_submissions(self):
        """
        Returns the new submissions for a given form.

        This method retrieves new form submissions from the client based on the specified form ID. It filters the submissions to only return those with the 'new' attribute set to '1'.

        Returns:
            list: A list of new submissions, each represented as a dictionary.

                The dictionary contains attributes and their corresponding values for each submission.

                Example:
                {'id': 1, 'name': 'John Doe', 'age': 25, 'new': '1'}

                If no new submissions are found, it returns None.

            None: If no new submissions are found.
        """
        new_submissions = [x for x in self.client.get_form_submissions(self.form_id) if x['new'] == '1']
        if new_submissions:
            return new_submissions
        return None

    @staticmethod
    def _strip_answer(answer: Optional[Union[str, dict]]):
        if isinstance(answer, str):
            answer = answer.strip()
        elif isinstance(answer, dict) and 'datetime' in answer.keys():
            answer = answer['datetime']
        return answer

    def _get_answers_dict(self, raw_answers: dict) -> dict:
        """f_name = raw_answers['text']
        f_value = self._strip_answer(raw_answers.get('answer', None))

        if raw_answers['text'] == '' or not raw_answers['text']:
            f_name = raw_answers['name']

        ans_entry = {'field_name': f_name,
                     'uni_field_name': raw_answers['name'],
                     'field_type': raw_answers['type'],
                     'field_order': int(raw_answers['order']),
                     'value': f_value}
        return ans_entry"""
        self.logger.warning("_get_answers_dict IS MEANT TO BE OVERWRITTEN IN A SUBCLASS!")
        return raw_answers

    # noinspection PyTypeChecker
    def get_answers_from_submission(self, submission_id: str):
        """
        Retrieves answers from a submission identified by a given submission ID.
        It parses the submission ID and retrieves the answers associated with it.
        The method iterates through the fields in the submission and constructs a
         dictionary of answers excluding the ignored submission fields.
         It logs warnings for illegal fields and missing values,
          then returns a dictionary containing the submission ID and answers obtained.
        """
        self.logger.info(f"parsing submission_id: {submission_id}")

        submission_answers = {'submission_id': submission_id, 'answers': []}
        submission_json = dict(self.client.get_submission(submission_id)['answers'].items())

        for field in submission_json.keys():
            if field not in self.ignored_submission_fields:
                field_text = submission_json[field]['text']
                try:
                    # these would be other internal/title fields that can be ignored
                    if not self.is_illegal_field(field_text):
                        submission_answers['answers'].append(self._get_answers_dict(submission_json[field]))
                    else:
                        self.logger.debug(f'field {field_text} (aka \'{field}\') {JotForm.IGNORED_FIELD_MESSAGE}')

                except KeyError:
                    self.logger.debug(f'no value found for: {field_text}')
                    submission_answers['answers'].append(self._get_answers_dict(submission_json[field]))

        return submission_answers

    @staticmethod
    def is_illegal_field(field_text: str) -> bool:
        """
        Check if the given field text starts with any illegal starting characters
        defined in the class attribute ILLEGAL_STARTING_CHARACTERS.

        :param field_text: A string representing the field text to be checked.
        :return: A boolean value indicating if the field text starts with any illegal starting characters.
        """
        return any([field_text.startswith(char) for char in JotForm.ILLEGAL_STARTING_CHARACTERS])

    def _write_raw_newest_submissions(self, **kwargs):
        save_location = Path(kwargs.get('save_location', JotForm.RAW_NEWEST_SUBMISSIONS_PATH))
        if save_location.suffix != '.json':
            try:
                raise AttributeError("save_location must be a json file")
            except AttributeError as e:
                self.logger.error(e, exc_info=True)
                raise e
        try:
            with open(save_location, 'w') as f:
                dump(self.get_new_submissions(), f, indent=4)
            self.logger.info(f"raw newest_submissions information written to file {save_location}")
        except (JSONDecodeError, IOError) as e:
            self.logger.error(e, exc_info=True)
            raise e
