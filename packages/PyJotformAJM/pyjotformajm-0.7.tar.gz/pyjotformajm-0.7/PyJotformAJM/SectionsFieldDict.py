from typing import List, Optional, Dict, Tuple


class SectionFieldsDict:
    """
    The SectionFieldsDict class represents a dictionary of all the fields organized by form section.
    It provides methods to fetch the indexes and names of all the fields in a given section.

    __init__(self, jf):
       Constructor method that initializes the SectionFieldsDict object.
       Parameters:
           - jf: JotForm object

    __str__(self):
       Returns a string representation of the SectionFieldsDict object.

    get_field_index(field, answers):
       Static method that returns the index of a given field in a list of answers.
       Parameters:
           - field: a dictionary representing a field.
           - answers: a list of dictionaries representing the answers.

    _get_all_field_indexes(self, **kwargs):
       Private method that returns a list of dictionaries containing the name and index of all the fields in the form.
       Parameters:
           - kwargs: optional keyword arguments.

    _get_all_section_indexes(self, **kwargs):
       Private method that returns a list of dictionaries containing the name and index of all the sections in the form.
       Parameters:
           - kwargs: optional keyword arguments.

    get_current_section_index_start(self, current_section_name):
       Returns the start index of a given section.
       Parameters:
           - current_section_name: the name of the section or a dictionary representing the section.

    get_next_section_index_start(self, current_section_name):
       Returns the start index of the next section after the given section.
       Parameters:
           - current_section_name: the name of the section or a dictionary representing the section.

    _get_section_start_end_int(self, section_name):
       Private method that returns the start and end indexes of a given section.
       Parameters:
           - section_name: the name of the section.

    get_section_fields(self, section_name):
       Returns a list of field names in a given section.
       Parameters:
           - section_name: the name of the section.

    _build_section_fields_dict(self):
       Private method that builds and returns a dictionary of all the fields in each section of the form.
    """
    # WHENEVER ANYTHING CHANGES ORDER, NEW HEADER, ETC THESE WILL MOST LIKELY CHANGE!!
    # EX. adding "Administrative Information" header caused a shift in multiple categories
    SPECIAL_SECTIONS: Dict[str, Tuple[int, int]] = {}

    def __init__(self, jf: 'JotForm'):
        self.jf = jf
        self.logger = jf.logger
        self.last_submission_id = jf.last_submission_id
        self.all_section_indexes: List[dict] = self._get_all_section_indexes()
        self.all_field_indexes: List[dict] = self._get_all_field_indexes()
        self.section_fields_dict = self._build_section_fields_dict()

    def __str__(self):
        """
        Represents a SectionFieldsDict class built based on a submission_id.

        This class is used to create an object that contains section fields data specific to a particular submission_id.

        Methods:
        - __str__(self): Returns a string representation of the SectionFieldsDict object.
        """
        return f"SectionFieldsDict based on submission_id {self.last_submission_id}"

    @staticmethod
    def get_field_index(field, answers):
        """
        A static method that returns the index of a given field in a list of answers.

        Parameters:
        - field: A dictionary representing a field. Must contain 'field_name' and 'uni_field_name'.
        - answers: A list of dictionaries representing answers. Each dictionary must contain 'field_name', 'uni_field_name', and 'field_order'.

        Returns:
        An integer representing the index of the field in the answers list, or None if the field is not found.

        Example:
        field = {'field_name': 'name', 'uni_field_name': 'Name'}
        answers = [{'field_name': 'name', 'uni_field_name': 'Name', 'field_order': 0},
                   {'field_name': 'occupation', 'uni_field_name': 'Occupation', 'field_order': 1}]
        index = get_field_index(field, answers)
        # index = 0
        """
        required_keys = {'field_name', 'uni_field_name'}
        if not required_keys.issubset(field):
            raise ValueError(f"The field dictionary is missing one of the required keys: {required_keys}")

        for answer in answers:
            if not required_keys.issubset(answer) or 'field_order' not in answer:
                raise ValueError(
                    "Each answer dictionary must contain 'field_name', 'uni_field_name', and 'field_order' keys.")

            if answer['field_name'] == field['field_name'] and answer['uni_field_name'] == field['uni_field_name']:
                return answer.get('field_order', None)

        return None

    def _get_all_field_indexes(self):
        """
        This method retrieves the field indexes for all the fields in the form.

        :param **kwargs: Additional keyword arguments that may be used by the method.
        :return: A list of dictionaries containing the field name and the field index.
        """
        answers = self.jf.get_answers_from_submission(self.jf.submission.active_submission_id)['answers']
        fi: List[dict] = []
        for field in self.jf.real_jf_field_names:
            if field not in self.jf.form_section_headers:
                field_index = self.get_field_index(field, answers)
                fi.append({'field_name': field, 'field_index': field_index})
        return fi

    def _get_all_section_indexes(self):
        """
        Gets the indexes of all sections in the form.

        :param **kwargs: Optional keyword arguments.
        :return: A list of dictionaries, each containing the name and index of a section.
        """
        answers = self.jf.get_answers_from_submission(self.jf.submission.active_submission_id)['answers']
        si: List[dict] = []
        for field in self.jf.real_jf_field_names:
            if field['field_name'] in self.jf.form_section_headers:
                section_index = self.get_field_index(field, answers)
                si.append({'section_name': field,
                           'section_index': section_index})
        return si

    def get_current_section_index_start(self, current_section_name) -> Optional[dict]:
        """
        Get the starting index of the current section in the list of all section indexes.

        :param current_section_name: The name of the current section.
        :type current_section_name: dict or str
        :return: The starting index of the current section, or None if no match is found.
        :rtype: int or None
        """
        if isinstance(current_section_name, dict):
            current_section_name = current_section_name['field_name']

        sec_ind_start = [x for x in self.all_section_indexes
                         if x['section_name']['field_name'].lower() == current_section_name.lower()][0]
        if sec_ind_start:
            return sec_ind_start
        self.logger.warning(f"no match found for section name: {current_section_name}")
        return None

    def get_next_section_index_start(self, current_section_name):
        """
        This function is used to retrieve the index of the next section in a given list of section indexes.

        The function takes two parameters:

        - self: The instance of the class calling the function.
        - current_section_name: The name of the current section to find the next index for.

        The function iterates over the list of all section indexes and checks if the 'section_name'
            field of each section matches the provided 'current_section_name' parameter, ignoring case.
            If a match is found, the function returns the index of the next section in the list.
            If no match is found, a warning message is logged and None is returned.

        Example usage:
            section_index = obj.get_next_section_index_start('Section1')

        Parameters:
            - current_section_name: The name of the current section to find the next index for.

        Returns:
            - The index of the next section in the list of section indexes, or None if no match is found.
        """
        it = iter(self.all_section_indexes)
        for section in it:
            if section['section_name']['field_name'].lower() == current_section_name.lower():  #['field_name'].lower():
                return next(it, {})
        self.logger.warning(f"no match found for section name: {current_section_name}")
        return None

    def _get_section_start_end_int(self, section_name):
        """
        This method is used to retrieve the start and end index of a specific section in the current object.

        :param section_name: The name of the section to retrieve the start and end index for.
        :return: A tuple containing the start index, end index, and section name.

        The start index is calculated by adding 1 to the current section's start index retrieved using the
            'get_current_section_index_start' method.

        The end index is determined by calling the 'get_next_section_index_start' method to get the
            start index of the next section. If no next section is found, the end index is set to None.

        If the section name is found in the 'SPECIAL_SECTIONS' attribute,
            the start and end index are retrieved from this attribute instead.

        Note: This method assumes that the 'SPECIAL_SECTIONS' attribute is defined and contains
            the special sections' start and end indexes.

        Example usage:
            section_start, section_end, section_name = _get_section_start_end_int("section_name")
        """
        section_name = self.get_current_section_index_start(section_name)['section_name']['field_name']
        section_start = self.get_current_section_index_start(section_name)['section_index'] + 1
        section_end = self.get_next_section_index_start(section_name).get('section_index', None)

        # special sections have concrete start and end points
        if section_name in self.SPECIAL_SECTIONS:
            section_start, section_end = self.SPECIAL_SECTIONS[section_name]
        # TODO: add to JotFormForCatalog?
        # this case is probably the end of the form
        if section_end is None:
            section_end = self.all_field_indexes[-1]['field_index']
            # this is probably a section with only one entry
            if section_end == section_start:
                section_end += 1
            # this is a 'normal' entry
            else:
                section_end -= 1

        return section_start, section_end, section_name

    def get_section_fields(self, section_name):
        """
        This method returns a list of field names for a given section in the current object.

        Parameters:
        - section_name: The name of the section for which to retrieve the field names.

        Returns:
        - field_names: A list of field names belonging to the specified section.

        Raises:
        - TypeError: If section_start or section_end is not an integer.

        Example usage:
        ```python
        obj = SomeClass()
        fields = obj.get_section_fields('SectionName')
        print(fields)
        ```
        """
        field_names = []
        section_start, section_end, section_name = self._get_section_start_end_int(section_name)
        # TODO: this if chunk might be redundant
        if section_end < section_start:
            if section_end + 1 == section_start:
                section_start -= 1
                print(f'section start adjusted to {section_start}')
            else:
                raise TypeError(f"section_end ({section_end}) cannot be less than section_start ({section_start})")
        try:
            for i in range(section_start, section_end):
                try:
                    # this makes the entries in field_name have both the 'field_name' and the 'uni_field_name' key/value
                    field_name = [x for x in self.all_field_indexes
                                  if x['field_index'] == i][0]['field_name']  #['field_name']
                    field_names.append(field_name)
                except IndexError as e:
                    print(e)
                    self.logger.warning(e)
                    continue
        except TypeError as e:
            self.logger.error(e, exc_info=True)
            raise e
        return field_names

    def _build_section_fields_dict(self):
        """
        This method is responsible for building a dictionary called section_fields_dict.
            The dictionary stores section names as keys and their corresponding field names as values.
            The method iterates over all section indexes and checks if the section name's field name is
            'Secondary Device Test'. If it is, the method adds an additional field called
            'Final Test Date' with the universal field name 'finalTest' to the section.
            Otherwise, it retrieves the section's fields using the get_section_fields method
            and assigns them to the section_fields_dict.

        Note that the logger is used to log informational and debugging messages.
            The logger.info method is called to log the message "building section_fields_dict"
            at the beginning of the method, and "finished building section_fields_dict" at the end of the method.

        The method returns the section_fields_dict after it has been built.
        """
        self.logger.info("building section_fields_dict")
        section_fields_dict = {}
        for section in self.all_section_indexes:
            section_fields_dict[section['section_name']['field_name']] = self.get_section_fields(
                section['section_name']['field_name'])

        # print(dumps(section_fields_dict, indent=4))
        self.logger.info("finished building section_fields_dict")
        return section_fields_dict
