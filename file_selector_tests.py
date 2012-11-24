import sublime
import unittest
from GotoRelatedFile import FileSelector

import os
import shutil


class TestFileSelector(unittest.TestCase):

    def setUp(self):
        self.test_data_path = os.sep.join([os.getcwd(), 'test_data'])
        self.settings_file = 'test_settings.sublime-settings'

        self.setUpDefaultSettings()

        self.deleteTempTestFiles()

    def tearDown(self):
        self.deleteTempTestFiles()

    def setUpDefaultSettings(self):
        settings = sublime.load_settings(self.settings_file)

        settings.erase('enabled_configurations')
        settings.erase('config1')
        settings.erase('config2')
        settings.erase('config3')

        settings.set('enabled_configurations', ['config1', 'config2', 'config3'])
        settings.set('config1', self.getJsConfig())
        settings.set('config2', self.getPyConfig())
        settings.set('config3', self.getPyConfigNoControllers())

    def deleteTempTestFiles(self):
        py_test_dir = os.sep.join([self.test_data_path, 'application'])
        js_test_dir = os.sep.join([self.test_data_path, 'js'])

        if os.path.isdir(py_test_dir):
            shutil.rmtree(py_test_dir)
        if os.path.isdir(js_test_dir):
            shutil.rmtree(js_test_dir)

    def createFile(self, path, content=''):
        file = open(path, 'w')
        if file:
            file.write(content)
            file.close()
        else:
            raise Exception('Could not create file "%s".' % path)

    def getJsConfig(self):
        return {
            "app_dir": "js/app",
            "file_types": {
                "controller": {
                    "path": "controllers",
                    "suffix": "_controller",
                    "rel_patterns": {
                        "view": "${app_path}/${type_path}/${file_from_type_path}/*",
                        "template": "${app_path}/${type_path}/${file_from_type_path}/*"
                    }
                },
                "template": {
                    "path": "templates",
                    "rel_patterns": {
                        "controller": "${app_path}/${type_path}/${dir_from_type_path}${suffix}.js",
                        "view": "${app_path}/${type_path}/${file_from_type_path}.js"
                    }
                },
                "view": {
                    "path": "views",
                    "rel_patterns": {
                        "controller": "${app_path}/${type_path}/${dir_from_type_path}${suffix}.js",
                        "template":   "${app_path}/${type_path}/${file_from_type_path}.hbs"
                    }
                }
            }
        }

    def getPyConfig(self):
        return {
            "app_dir": "application",
            "file_types": {
                "controller": {
                    "path": "controllers",
                    "rel_patterns": {
                        "view": "${app_path}/${type_path}/${file_from_type_path}/*",
                        "template": "${app_path}/${type_path}/${file_from_type_path}/*"
                    }
                },
                "template": {
                    "path": "templates",
                    "rel_patterns": {
                        "controller": "${app_path}/${type_path}/${dir_from_type_path}.py",
                        "view": "${app_path}/${type_path}/${file_from_type_path}.py"
                    }
                },
                "view": {
                    "path": "views",
                    "rel_patterns": {
                        "controller": "${app_path}/${type_path}/${dir_from_type_path}.py",
                        "template":   "${app_path}/${type_path}/${file_from_type_path}.html"
                    }
                }
            }
        }

    def getPyConfigNoControllers(self):
        pyConfig = self.getPyConfig()
        del pyConfig['file_types']['controller']
        return pyConfig

    def createSettingsWith1stPyConfigDisabled(self):
        settings = sublime.load_settings(self.settings_file)
        settings.set('enabled_configurations', ['config1', 'config3'])

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

        self.controller_path = os.sep.join([base_path, 'controllers', 'foo.py'])
        self.view_path = os.sep.join([base_path, 'views', 'foo', 'bar.py'])
        self.template_path = os.sep.join([base_path, 'templates', 'foo', 'bar.html'])

        self.createFile(self.controller_path)
        self.createFile(self.view_path)
        self.createFile(self.template_path)

    def setUpFooFilesForJsConfig(self):
        """
            Set up the following files:
            test_data/js/app/controllers/foo_controller.js
            test_data/js/app/views/foo/bar.js
            test_data/js/app/templates/foo/bar.hbs

            and save their paths to instance variables.
        """
        base_path = os.sep.join([self.test_data_path, 'js', 'app'])

        os.makedirs(os.sep.join([base_path, 'controllers']))
        os.makedirs(os.sep.join([base_path, 'views', 'foo']))
        os.makedirs(os.sep.join([base_path, 'templates', 'foo']))

        self.controller_path = os.sep.join([base_path, 'controllers', 'foo_controller.js'])
        self.view_path = os.sep.join([base_path, 'views', 'foo', 'bar.js'])
        self.template_path = os.sep.join([base_path, 'templates', 'foo', 'bar.hbs'])
        self.createFile(self.controller_path)
        self.createFile(self.view_path)
        self.createFile(self.template_path)

    def setUpBarFilesForJsConfig(self):
        """
            Set up the following files:
            test_data/js/app/views/bar/baz.js

            and save their paths to instance variables.

            Also set instance variable with path where
            controller should be created, and create
            the directory.
        """
        base_path = os.sep.join([self.test_data_path, 'js', 'app'])

        os.makedirs(os.sep.join([base_path, 'views', 'bar']))
        os.makedirs(os.sep.join([base_path, 'controllers']))

        self.view_path = os.sep.join([base_path, 'views', 'bar', 'baz.js'])
        self.controller_path = os.sep.join([base_path, 'controllers', 'bar_controller.js'])

        self.createFile(self.view_path)

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
        self.createSettingsWith1stPyConfigDisabled()
        file_selector = FileSelector(
            sublime.active_window(),
            self.settings_file,
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
            self.view_path
        )

        self.assertTrue(file_selector.files_found)

        related_files = file_selector.related_files
        self.assertEquals(len(related_files), 2)
        self.assertEquals(related_files[0][1], self.controller_path)
        self.assertEquals(related_files[0][0], 'Open controller (foo.py)')
        self.assertEquals(related_files[1][1], self.template_path)
        self.assertEquals(related_files[1][0], 'Open template (bar.html)')

    def testRelPatternsCanContainAsteriskWildcardCharacter(self):
        self.setUpFilesForPyConfig()

        file_selector = FileSelector(
            sublime.active_window(),
            self.settings_file,
            self.controller_path
        )

        self.assertTrue(file_selector.files_found)

        related_files = file_selector.related_files
        self.assertEquals(len(related_files), 2)
        self.assertEquals(related_files[0][1], self.template_path)
        self.assertEquals(related_files[1][1], self.view_path)

    def testSuffixTemplateVarReplacedWithSuffixOfTargetFile(self):
        self.setUpFooFilesForJsConfig()

        file_selector = FileSelector(
            sublime.active_window(),
            self.settings_file,
            self.view_path
        )

        self.assertTrue(file_selector.files_found)

        related_files = file_selector.related_files
        related_paths = [select_option[1] for select_option in related_files]
        self.assertTrue(self.controller_path in related_paths)

    def testSuffixRemovedFromValueOfFileFromTypePathTemplateVar(self):
        self.setUpFooFilesForJsConfig()

        file_selector = FileSelector(
            sublime.active_window(),
            self.settings_file,
            self.controller_path
        )

        self.assertTrue(file_selector.files_found)

        related_files = file_selector.related_files
        self.assertEquals(related_files[0][1], self.template_path)
        self.assertEquals(related_files[1][1], self.view_path)

    def testLabelSaysCreateIfMatchDoesNotExistButTargetDirDoes(self):
        self.setUpBarFilesForJsConfig()

        file_selector = FileSelector(
            sublime.active_window(),
            self.settings_file,
            self.view_path
        )

        self.assertTrue(file_selector.files_found)

        related_files = file_selector.related_files
        self.assertEquals(len(related_files), 1)
        self.assertEquals(related_files[0][1], self.controller_path)
        self.assertEquals(related_files[0][0], 'Create controller (bar_controller.js)')
        # No option to create template, since target directory does not exist.
