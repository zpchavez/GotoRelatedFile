import sublime
import sublime_plugin
import os
import re
from glob import glob


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
        self.root = self._get_root_path()
        self.current_file = self.view.file_name()
        self.related_files = self._get_related_files()
        self.files_found = bool(self.related_files)

    def select(self, index):
        if index != -1:
            self.window.open_file(self.related_files[index][1])

    def get_items(self):
        return self.related_files

    def _get_root_path(self):
        """
            Search through the possible root directories until one is found that
            is included in the current file's path.  Return that directory, or None
            if not found.
        """
        possible_roots = self.settings.get('roots')
        current_file = self.view.file_name()
        for possible_root in possible_roots:
            search_string = os.sep + possible_root + os.sep
            match = re.search('^(.*?%s)' % re.escape(search_string), current_file)
            if match:
                return match.group(0)
        return None

    def _get_related_files(self):
        """
            Return a list of lists where element 0 is the file type
            and element 1 is the path.
        """
        if self.root is None or self.current_file is None:
            return None

        current_file_type = self._get_current_file_type()
        if current_file_type is None:
            return None

        related_files = []
        file_types = self.settings.get('file_types')
        for file_type, details in file_types.items():
            if current_file_type == file_type:
                continue

            related_file = self._get_related_file(
                self.current_file,
                current_file_type,
                file_type,
                details['paths']
            )

            if related_file:
                related_files.append([file_type, related_file])

        return related_files

    def _get_related_file(self, file_path, from_type, to_type, to_paths):
        """
            Get the full path to a file of type to_type give nthe path
            to a file of type from_type and possible target paths to_paths.
        """
        file_path_no_ext = os.path.splitext(file_path)[0]
        file_path_no_root = file_path_no_ext.replace(self.root, '', 1)
        filename = os.path.basename(file_path_no_ext)

        if from_type == 'test':
            file_path_no_root = self._remove_test_suffix(file_path_no_root)
            filename = self._remove_test_suffix(filename)

        for to_path in to_paths:
            if to_type == 'test':
                path_parts = [self.root, to_path, file_path_no_root]
            else:
                path_parts = [self.root, to_path, filename]
            pattern = os.path.realpath(os.sep.join(path_parts)) + '*'
            matches = glob(pattern)
            file_matches = [match for match in matches if os.path.isfile(match)]
            if file_matches:
                return file_matches[0]
        return None

    def _filter_out_base_path(self, file_type, filename):
        """Return filename without the root and file type path."""
        filtered_filename = filename.replace(self.root, '', 1)

        file_types = self.settings.get('file_types')
        for path in file_types[file_type]['paths']:
            if re.match('^%s' % re.escape(path), filtered_filename):
                filtered_filename = filtered_filename.replace(path, '', 1)
        return filtered_filename

    def _remove_test_suffix(self, filename):
        """Remove the test suffix from a base filename without the extension."""
        file_types = self.settings.get('file_types')
        for suffix in file_types['test']['suffixes']:
            pattern = re.escape(suffix) + '$'
            if re.search(pattern, filename):
                desuffixed_filename = re.sub(pattern, '', filename)
                return desuffixed_filename
        return filename

    def _get_current_file_type(self):
        """
            Get the current file type (as defined in settings), or None if it
            doesn't appear to match any of the file types.
        """
        if self.root is None or self.current_file is None:
            return None

        file_types = self.settings.get('file_types')

        for file_type, details in file_types.items():
            for path in details['paths']:
                search_string = self.root + path
                match = re.search('^%s' % search_string, self.current_file)
                if match:
                    return file_type
        return None
