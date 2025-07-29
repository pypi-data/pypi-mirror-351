import unittest
from pathlib import Path

from PyJotformAJM.SectionsFieldDict import SectionFieldsDict
from PyJotformAJM.PyJotformAJM import JotForm

test_api_key_path = Path('../Misc_Project_Files/TestFormAPIKey.key').resolve()
if test_api_key_path.is_file():
    with open(test_api_key_path, 'r') as f:
        API_KEY = f.read()
else:
    raise EnvironmentError(f"API key file not found at {test_api_key_path}")


class TestingVersionJotform(JotForm):
    def _get_answers_dict(self, raw_answers: dict) -> dict:
        f_name = raw_answers['text']
        f_value = self._strip_answer(raw_answers.get('answer', None))

        if raw_answers['text'] == '' or not raw_answers['text']:
            f_name = raw_answers['name']

        ans_entry = {'field_name': f_name,
                     'uni_field_name': raw_answers['name'],
                     'field_type': raw_answers['type'],
                     'field_order': int(raw_answers['order']),
                     'value': f_value}
        return ans_entry


class TestSectionFieldsDict(unittest.TestCase):
    def setUp(self):
        self.testing_jf = TestingVersionJotform(api_key=API_KEY, form_id='242693235658062')
        self.test_jf_sfd = SectionFieldsDict(self.testing_jf)

    def test_get_current_section_index_start(self):
        self.assertIsInstance(self.test_jf_sfd.get_current_section_index_start('New Section')['section_index'], int)

    def test_get_next_section_index_start(self):
        try:
            self.assertIsInstance(self.test_jf_sfd.get_next_section_index_start('New Section')['section_index'], int)
        except KeyError:
            self.assertIsInstance(self.test_jf_sfd.get_next_section_index_start('New Section'), dict)
            self.assertEqual(len(self.test_jf_sfd.get_next_section_index_start('New Section').keys()), 0)

    def test_get_section_fields(self):
        fields = self.test_jf_sfd.get_section_fields('New Section')
        self.assertIsInstance(fields, list)
        self.assertGreater(len(fields), 0)

    def test_str(self):
        self.assertIsInstance(str(self.test_jf_sfd), str)


if __name__ == '__main__':
    unittest.main()
