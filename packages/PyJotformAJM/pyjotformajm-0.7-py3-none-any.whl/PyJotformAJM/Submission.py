from datetime import datetime
from sys import modules
try:
    from .err import *
    from .LinkRequester import LinkRequester
except ImportError:
    from err import *
    try:
        # noinspection PyUnresolvedReferences
        from LinkRequester import LinkRequester
    except ImportError:
        print("LinkRequester could not be imported!")


class Submission:
    """
    This code defines a class called Submission representing a Jotform submission.

    Constructor:
    - __init__(self, jf, submission_id): Initializes an instance of Submission with the given parameters.
      - Parameters:
        - jf: An instance of a Jotform object.
        - submission_id: The ID of the submission.

    Properties:
    - valid_submission_ids: Represents a list of valid submission IDs.
      - Returns: A list of valid submission IDs.

    - active_submission_id: Represents the ID of the active submission.
      - Returns: The ID of the active submission.
      - Setter: Sets the ID of the active submission if it is valid.
        - Parameters:
          - value: The value to set as the active submission ID.

    - active_submission_edit_or_submit_date: Represents the date and time when the active submission was edited or submitted.
      - Returns: The date and time of the active submission edit or submit.

    - active_submission_non_null_answers: Represents the non-null answers of the active submission.
      - Returns: A dictionary of field names and their corresponding non-null values.

    - active_submission_all_answers: Represents all the answers of the active submission.
      - Returns: All the answers of the active submission.

    - organized_submission_answers: Represents the organized answers of the active submission.
      - Returns: A dictionary containing the section, uni_field_name, and submitted answer for each field in the active submission.

    Methods:
    - GetSubmissionAllAnswers(cls, submission_id, jf, **kwargs): Gets all the answers of the given submission ID.
      - Parameters:
        - submission_id: The ID of the submission.
        - jf: An instance of a Jotform object.
        - **kwargs: Additional optional arguments.
      - Returns: All the answers of the given submission ID.

    """

    # TODO: TESTS!!!!!
    def __init__(self, jf, submission_id, get_links=False):
        self.jf = jf
        self.logger = jf.logger
        self.form_id = jf.form_id
        self.client = jf.client

        self.get_links = get_links
        self._initialize_get_links()

        self.last_submission_id = jf.last_submission_id
        self._valid_submission_ids = None
        self._previous_submission_id = None
        self._active_submission_id = None
        self.active_submission_id = submission_id

        self._active_submission_all_answers = None
        self._active_submission_non_null_answers = None
        self._organized_submission_answers = {}

    def _initialize_get_links(self):
        if self.get_links and 'LinkRequester' not in modules.keys():
            self.logger.warning("LinkRequester could not be imported, setting self.get_links to False!")
            self.get_links = False

    @classmethod
    def GetSubmissionAllAnswers(cls, submission_id, jf):
        """
        This method is a class method that retrieves all the answers associated with a submission.

        Parameters:
        - submission_id: The ID of the submission for which the answers need to be retrieved.
        - jf: The JSON format in which the answers are stored.
        - **kwargs: Additional keyword arguments that can be passed to the method.

        Returns:
        - A list of all the answers associated with the submission.

        Note:
        - This method should be called on the class itself, rather than on an instance of the class.

        """
        return cls(jf, submission_id).active_submission_all_answers

    @property
    def valid_submission_ids(self):
        """
        Gets the valid submission IDs for a form.

        This property returns a list of valid submission IDs for a form. If the list is empty, it queries the client to fetch the submissions and then retrieves the IDs.

        Returns:
            list: A list of valid submission IDs for the form.

        Note:
            This property caches the submission IDs to avoid repeated queries to the client.

        Example:
            form = Form(form_id)
            submissions = form.valid_submission_ids
            for submission_id in submissions:
                print(submission_id)
        """
        if not self._valid_submission_ids:
            self._valid_submission_ids = [x['id'] for x in self.jf.client.get_form_submissions(self.form_id)]
        return self._valid_submission_ids

    @property
    def active_submission_id(self):
        """
        This method is a property that retrieves the active submission ID. If the _active_submission_id attribute is None, it is assigned the value of the last_submission_id attribute. It then returns the value of the _active_submission_id attribute.

        Parameters:
            None

        Returns:
            int: The active submission ID.

        """
        if not self._active_submission_id:
            self._active_submission_id = self.last_submission_id
        return self._active_submission_id

    @active_submission_id.setter
    def active_submission_id(self, value):
        """
        Sets the active submission ID.

        Args:
            value: The new active submission ID.

        Raises:
            InvalidJotformSubmissionID: If the provided value is not a valid submission ID.

        Returns:
            None
        """
        if value in self.valid_submission_ids:
            self._previous_submission_id = self.active_submission_id
            self._active_submission_id = value
        else:
            try:
                raise InvalidJotformSubmissionID(f'invalid submission_id - {value}')
            except InvalidJotformSubmissionID as e:
                self.logger.error(e, exc_info=True)
                raise e

    @property
    def active_submission_edit_or_submit_date(self):
        """
        This method retrieves the active submission's edit or submit date for a specific form.

        Returns:
            datetime: The edit or submit date of the active submission.

        Raises:
            IndexError: If the active submission ID does not exist in the form submissions.
        """
        info = [{'created_at': x['created_at'], 'updated_at': x['updated_at']} for x in
                self.jf.client.get_form_submissions(self.form_id) if x['id'] == self.active_submission_id][0]
        if info['updated_at'] is None:
            return datetime.fromisoformat(info['created_at'])
        return datetime.fromisoformat(info['updated_at'])

    @property
    def active_submission_non_null_answers(self):
        """
        This code defines a property named "active_submission_non_null_answers" in a class.
        The property is defined using the @property decorator.

        The property computes a dictionary of non-null answers from the "active_submission_all_answers"
        attribute of the class. The dictionary is computed using a dictionary comprehension
        that filters out answers with a value that is not None.

        The computed dictionary is stored in the instance variable "_active_submission_non_null_answers",
         which is then returned by the property.

        This property allows access to the non-null answers of the active submission."""
        self._active_submission_non_null_answers = {x['field_name']: x['value'] for x in
                                                    self.active_submission_all_answers['answers']
                                                    if x['value'] is not None}
        return self._active_submission_non_null_answers

    @property
    def active_submission_all_answers(self):
        """
        Creates and returns a property `active_submission_all_answers`.

        This property retrieves the answers associated with the active submission.
        It uses `jf.get_answers_from_submission` method to fetch the answers based on the active submission ID.
        The retrieved answers are cached for subsequent calls, but if the active submission ID changes,
         the answers are fetched again.

        Returns:
            The answers associated with the active submission.

        Note:
            This property is lazy-loaded and will only fetch the answers when requested.

        """
        if not self._active_submission_all_answers:
            self._active_submission_all_answers = self.jf.get_answers_from_submission(self.active_submission_id)
        elif self.active_submission_id != self.last_submission_id:
            self._active_submission_all_answers = self.jf.get_answers_from_submission(self.active_submission_id)
        return self._active_submission_all_answers

    @property
    def organized_submission_answers(self):
        """
        This method returns a dictionary of organized submission answers.
        It first checks if the active submission ID exists in the `_organized_submission_answers` dictionary.
        If not, it creates a new dictionary `answers_section_field_dict` and populates it
        with the section, uni_field_name, and an empty string for the submitted answer for each field in
        `self.jf.section_fields_dict` that is not a string.

        Then, it retrieves the uni_field_name and value from `self.active_submission_all_answers['answers']`
        and iterates through the `answers_section_field_dict` to match and update the submitted answer
        based on the uni_field_name. If the uni_field_name is 'phoneNumber', it sets the submitted answer
        as the full value. If it is 'PassFailTest', it sets the submitted answer as either "1" or "2" depending
        on the value. If the value is a string that starts with 'http', it sets the submitted answer as
        the value and tries to download the signature file using `LinkRequester.GetWriteFile`.
        If there is an error downloading the file, a warning message is logged.
        For any other value, it sets the submitted answer as the value.

        Finally, it adds the active_submission_id as a key to the
        `_organized_submission_answers` dictionary and returns it.

        @return dictionary of organized submission answers
        """
        if not self._organized_submission_answers.get(self.active_submission_id, None):
            answers_section_field_dict = []
            for x in self.jf.section_fields_dict:
                answers_section_field_dict.extend([{'section': x, 'uni_field_name': y['uni_field_name'],
                                                    'submitted_answer': ''} for y in self.jf.section_fields_dict[x]
                                                   if not isinstance(y, str)])
            # print(answers_section_field_dict)
            uni_field_name_values = [(x['uni_field_name'], x['value']) for x
                                     in self.active_submission_all_answers['answers']]
            for x in answers_section_field_dict:
                for y in uni_field_name_values:
                    if x['uni_field_name'] == y[0]:
                        if x['uni_field_name'] == 'phoneNumber':
                            x['submitted_answer'] = y[1]['full']
                        elif x['uni_field_name'] == 'PassFailTest':
                            x['submitted_answer'] = y[1].get("1", y[1].get("2"))
                        elif isinstance(y[1], str) and y[1].startswith('http'):
                            x['submitted_answer'] = y[1]

                            if self.get_links:
                                try:
                                    LinkRequester.GetWriteFile(url_str=y[1], api_key=self.jf.api_key,
                                                               logger=self.logger)
                                except SignatureFileError as e:
                                    self.logger.warning(f"Could not download signature file(s) due to {e}")
                                    continue

                        else:
                            x['submitted_answer'] = y[1]
            # add the active_submission_id on as a key to the new list_dict
            self._organized_submission_answers = {self.active_submission_id: answers_section_field_dict}
        return self._organized_submission_answers
