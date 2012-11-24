import sublime
import unittest
from GotoRelatedFile import FileSelector

import os


class TestFileSelector(unittest.TestCase):

    def setUp(self):
        base_path = os.sep.join([os.getcwd(), 'test_data', 'application'])
        self.controller_path = os.sep.join([base_path, 'controllers', 'foo.py'])
        self.view_path = os.sep.join([base_path, 'views', 'foo', 'bar.py'])
        self.template_path = os.sep.join([base_path, 'templates', 'foo', 'bar.html'])

    def testConfigurationSetToFirstMatchingAppPath(self):
        # Path matches config2 and config3, but 2 is first.
        file_selector = FileSelector(
            sublime.active_window(),
            'test_settings.sublime-settings',
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
            'test_settings2.sublime-settings',
            '/path/to/application/views/view.php'
        )

        self.assertEquals(
            file_selector.configuration,
            file_selector.settings.get('config3')
        )

    def testBasicRelPatternTemplateVars(self):
        # Test template vars app_path, type_path,
        # file_from_type_path, and dir_from_type_path
        file_selector = FileSelector(
            sublime.active_window(),
            'test_settings.sublime-settings',
            self.view_path
        )

        self.assertTrue(file_selector.files_found)

        related_files = file_selector.related_files
        self.assertEquals(len(related_files), 2)
        self.assertEquals(related_files[0][1], self.controller_path)
        self.assertEquals(related_files[1][1], self.template_path)

    def testRelPatternsCanContainAsteriskWildcardCharacter(self):
        file_selector = FileSelector(
            sublime.active_window(),
            'test_settings.sublime-settings',
            self.controller_path
        )

        self.assertTrue(file_selector.files_found)

        related_files = file_selector.related_files
        self.assertEquals(len(related_files), 2)
        self.assertEquals(related_files[0][1], self.template_path)
        self.assertEquals(related_files[1][1], self.view_path)

