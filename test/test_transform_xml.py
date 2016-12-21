import os
import unittest
import xml.etree.ElementTree as eT
from src.transform_xml import TransformXML
from src.transform_xml import update_criteria_file
from src.transform_xml import requirements_met
from test_get_xml import clear_old_test_data


def clear_test_criteria():
    """Remove all the test criteria files from the previous test run
    """
    folder = '{}{}'.format(os.getcwd(), '/config_TEST/')
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


class NonBlankFileTransform(unittest.TestCase):
    """Class to make the setup for test cases with different contexts
    to be logically separated.

    This class sets the context for the test cases that are run when
    there is no valid criteria file or it is blank
    """

    def setUp(self):
        clear_old_test_data()
        # Writing a timestamp to a new test criteria file
        test_cf = '{cwd}{file}'.format(cwd=os.getcwd(),
                                       file='/config_TEST'
                                            '/test_transform.criteria')
        with open(test_cf, 'wt') as cf:
            # Using a low number as the timestamp to keep testing easy
            cf.write('10')

        self.t_xml = TransformXML()
        self.t_xml.criteria = '/config_TEST/test_transform.criteria'
        self.t_xml.data_dir = '/data_TEST/'


class TestTransformXMLWithCF(NonBlankFileTransform):
    """Test cases for when the criteria file has a valid timestamp
    """

    def test_get_new_input(self):
        expected_files = ['10_transform_test.xml',
                          '20_transform_test.xml']
        obtained_files = self.t_xml.get_new_input()
        for ef in expected_files:
            self.assertTrue(ef in obtained_files)

    def test_criteria_file_updated(self):
        with open('{}{}'.format(os.getcwd(), self.t_xml.criteria),
                  'rt') as cf:
            criteria_file = '{}{}'.format(os.getcwd(),
                                          self.t_xml.criteria)
            data_files = os.listdir('{}{}'.format(os.getcwd(),
                                                  self.t_xml.data_dir))
            update_criteria_file(criteria_file, data_files)
            '''Assert that the criteria file has a timestamp of at
            least 20.  The oldest file used for this test will be 20
            ms or the timestamp of one of the files created from the
            GetXML test suite.
            '''
            self.assertTrue(cf.readline() >= 20)

    def test_reduce_xml(self):
        pass

    def test_write_csv(self):
        pass


class BlankTransformFile(unittest.TestCase):
    """Class to make the setup for test cases with different contexts
    to be logically separated.

    This class sets the context for the test cases that are run when
    there is a valid criteria file that is not blank
    """

    def setUp(self):
        clear_test_criteria()
        self.t_xml = TransformXML()
        self.t_xml.criteria = '/config_TEST/test_transform.criteria'
        self.t_xml.data_dir = '/data_TEST/'


class TestTransformXMLNoDate(BlankTransformFile):
    """Test cases when the criteria file is blank
    """

    def test_get_new_input(self):
        """Expecting all 3 files to be returned in the list from
        function
        """
        expected_files = ['1_transform_test.xml',
                          '10_transform_test.xml',
                          '20_transform_test.xml']
        obtained_files = self.t_xml.get_new_input()
        for ef in expected_files:
            self.assertTrue(ef in obtained_files)

    def test_requirements_met(self):
        good_xml = '<Description>please and thank you</Description>'
        good_member = eT.fromstring(good_xml)
        self.assertTrue(requirements_met(good_member))

        non_matching_val_xml = '<Description>or</Description>'
        non_matching_val_member = eT.fromstring(non_matching_val_xml)
        self.assertFalse(requirements_met(non_matching_val_member))

        bad_tag_xml = '<NotATag>gonna be ignored</NotATag>'
        bad_tag_member = eT.fromstring(bad_tag_xml)
        self.assertFalse(requirements_met(bad_tag_member))
