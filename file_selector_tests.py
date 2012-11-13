import sublime
import unittest
from GotoRelatedFile import FileSelector

class TestFileSelector(unittest.TestCase):

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
