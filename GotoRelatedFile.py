import sublime
import sublime_plugin
import os
import platform
import re
import glob
from string import Template


def insensitive_glob(pattern):
    """
        Case insensitive glob.
        From http://stackoverflow.com/questions/8151300/ignore-case-in-glob-on-linux.
    """
    if platform.system() == 'Windows':
        return glob.glob(pattern)

    def either(c):
        return '[%s%s]' % (c.lower(), c.upper()) if c.isalpha() else c
    return glob.glob(''.join(map(either, pattern)))


class GotoRelatedFileCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        window = sublime.active_window()

        selector = FileSelector(window)
        if selector.files_found:
            window.show_quick_panel(selector.get_items(), selector.select)
        else:
            sublime.status_message('No related files found.')


class FileSelector(object):

    def __init__(self, window):
        self.settings = sublime.load_settings('GotoRelatedFile.sublime-settings')
        self.window = window
        self.view = window.active_view()
        self.current_file = self.view.file_name()
        self.configuration = self._get_configuration()
        if self.configuration:
            self.related_files = self._get_related_files()
            self.files_found = bool(self.related_files)
        else:
            self.files_found = False

    def select(self, index):
        if index != -1:
            self.window.open_file(self.related_files[index][1])

    def get_items(self):
        return self.related_files

    def _get_configuration(self):
        """
            Search through the enabled configurations until one is found whose root
            directory is contained in the current file's path.  Return the details
            for that configuration, or None if no matches found.

            Also saves the full path to the app dir to self.app_path.
        """
        if not self.current_file:
            return None

        configs = self.settings.get('enabled_configurations', [])

        valid_configs = {}
        for config in configs:
            config_details = self.settings.get('configurations').get(config)
            if config_details:
                valid_configs[config] = config_details

        for config_key in valid_configs:
            possible_app_dir = valid_configs[config_key]['app_dir'].replace('/', os.sep)
            search_string = os.sep + possible_app_dir + os.sep
            match = re.search('^(.*?%s)' % re.escape(search_string), self.current_file)
            if match:
                self.app_path = match.group(0)
                return valid_configs[config_key]
        return None

    def _get_current_file_type(self):
        for file_type, details in self.configuration['file_types'].items():
            search_string = os.path.join(self.app_path, details['path']).replace('/', os.sep)
            match = re.search('^%s' % re.escape(search_string), self.current_file)
            if match:
                return file_type

    def _get_related_files(self):
        """
            Return list of lists with element 0 the file type
            and element 1 the path.
        """
        current_file_type = self._get_current_file_type()

        if current_file_type is None:
            return []

        current_file_type_details = self.configuration \
            .get('file_types', {}) \
            .get(current_file_type, {})
        current_file_type_path = current_file_type_details.get('path', '').replace('/', os.sep)
        suffix = current_file_type_details.get('suffix', '')

        current_file_no_ext = os.path.splitext(self.current_file)[0]
        current_file_no_suffix = re.sub('%s$' % re.escape(suffix), '', current_file_no_ext)
        current_file = re.sub('%s$' % re.escape(suffix), '', current_file_no_suffix)
        type_path = os.path.join(self.app_path, current_file_type_path)

        # Create template vars used in settings file.
        file_from_type_path = current_file.replace(type_path, '', 1)
        file_from_app_path = current_file.replace(self.app_path, '', 1)
        dir_from_type_path = os.path.dirname(file_from_type_path)

        patterns = self.configuration.get('file_types', {}) \
            .get(current_file_type, {}) \
            .get('rel_patterns', {})

        related_files = []
        for file_type, pattern in patterns.items():
            file_type_details = self.configuration \
                .get('file_types', {}) \
                .get(file_type, {})
            rel_file_type_path = file_type_details.get('path', '').replace('/', os.sep)

            template = Template(pattern.replace('/', os.sep))
            glob_pattern = template.safe_substitute(
                app_path=self.app_path,
                type_path=rel_file_type_path,
                file_from_type_path=file_from_type_path,
                file_from_app_path=file_from_app_path,
                dir_from_type_path=dir_from_type_path
            )
            matches = insensitive_glob(os.path.realpath(glob_pattern))
            file_matches = [
                ['%s (%s)' % (file_type, os.path.basename(match)), match]
                for match in matches
                if os.path.isfile(match)
            ]
            related_files += file_matches
        return related_files
