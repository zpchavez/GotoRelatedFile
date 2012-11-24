import sublime
import unittest
from GotoRelatedFile import FileSelector

import os
import shutil


class TestFileSelector(unittest.TestCase):

    def setUp(self):
        self.test_data_path = os.sep.join([os.getcwd(), 'test_data'])
        self.settings_file = 'test_settings.sublime-settings'
        self.settings_file_alt = 'test_settings_alt.sublime-settings'

    def tearDown(self):
        py_test_dir = os.sep.join([self.test_data_path, 'application'])
        js_test_dir = os.sep.join([self.test_data_path, 'js'])
        if os.path.isdir(py_test_dir):
            shutil.rmtree(py_test_dir)
        if os.path.isdir(js_test_dir):
            shutil.rmtree(js_test_dir)

    def createFile(self, path):
        file = open(path, 'w')
        if file:
            file.close()
        else:
            raise Exception('Could not create file "%s".' % path)

    def setUpFilesForPyConfig(self):
        """
            Set up the following files:
            test_data/application/controllers/foo.py
            test_data/application/views/foo/bar.py
            test_data/application/templates/foo/bar.html

            and save their paths to instance variables.
        """
        base_path = os.sep.join([self.test_data_path, 'application'])

        os.makedirs(os.sep.join([base_path, 'controllers']))
        os.makedirs(os.sep.join([base_path, 'views', 'foo']))
        os.makedirs(os.sep.join([base_path, 'templates', 'foo']))

        self.py_controller_path = os.sep.join([base_path, 'controllers', 'foo.py'])
        self.py_view_path = os.sep.join([base_path, 'views', 'foo', 'bar.py'])
        self.py_template_path = os.sep.join([base_path, 'templates', 'foo', 'bar.html'])

        self.createFile(self.py_controller_path)
        self.createFile(self.py_view_path)
        self.createFile(self.py_template_path)

    def setUpFooFilesForJsConfig(self):
        pass

    def setUpBarFilesForJsConfig(self):
        pass

    def testConfigurationSetToFirstMatchingAppPath(self):
        # Path matches config2 and config3, but 2 is first.
        file_selector = FileSelector(
            sublime.active_window(),
            self.settings_file,
            '/path/to/application/views/view.php'
        )

        self.assertEquals(
            file_selector.configuration,
            file_selector.settings.get('config2')
        )

    def testConfigsNotEnabledAreNotConsidered(self):
        # Path matches config2 and config3, but config2 is not enabled.
        file_selector = FileSelector(
            sublime.active_window(),
            self.settings_file_alt,
            '/path/to/application/views/view.php'
        )

        self.assertEquals(
            file_selector.configuration,
            file_selector.settings.get('config3')
        )

    def testBasicRelPatternTemplateVars(self):
        # Test template vars app_path, type_path,
        # file_from_type_path, and dir_from_type_path
        self.setUpFilesForPyConfig()

        file_selector = FileSelector(
            sublime.active_window(),
            self.settings_file,
            self.py_view_path
        )

        self.assertTrue(file_selector.files_found)

        related_files = file_selector.related_files
        self.assertEquals(len(related_files), 2)
        self.assertEquals(related_files[0][1], self.py_controller_path)
        self.assertEquals(related_files[0][0], 'Open controller (foo.py)')
        self.assertEquals(related_files[1][1], self.py_template_path)
        self.assertEquals(related_files[1][0], 'Open template (bar.html)')

    def testRelPatternsCanContainAsteriskWildcardCharacter(self):
        self.setUpFilesForPyConfig()

        file_selector = FileSelector(
            sublime.active_window(),
            self.settings_file,
            self.py_controller_path
        )

        self.assertTrue(file_selector.files_found)

        related_files = file_selector.related_files
        self.assertEquals(len(related_files), 2)
        self.assertEquals(related_files[0][1], self.py_template_path)
        self.assertEquals(related_files[1][1], self.py_view_path)

    def testSuffixTemplateVarReplacedWithSuffixOfTargetFile(self):
        self.fail()

    def testSuffixRemovedFromValueOfFileFromTypePathTemplateVar(self):
        self.fail()

    def testLabelSaysCreateIfMatchDoesNotExistButTargetDirDoes(self):
        self.fail()

    def testNoMatchIfTargetDirDoesNotExist(self):
        self.fail()
