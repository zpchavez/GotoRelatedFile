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

        selector = FileSelector(
            window,
            'GotoRelatedFile.sublime-settings',
            window.active_view().file_name()
        )

        if selector.files_found:
            window.show_quick_panel(selector.get_items(), selector.select)
        else:
            sublime.status_message('No related files found.')


class FileSelector(object):

    def __init__(self, window, config_file, current_file):
        self.settings = sublime.load_settings(config_file)
        self.window = window
        self.view = window.active_view()
        self.wildcard_vals_in_type_path = []
        self.current_file = current_file
        self.configuration = self._get_configuration()
        if self.configuration:
            self.related_files = self._get_related_files()
            self.files_found = bool(self.related_files)
        else:
            self.files_found = False

    def select(self, index):
        if index != -1:
            selected_file = self.related_files[index][1]
            if not os.path.isdir(os.path.dirname(selected_file)):
                os.makedirs(os.path.dirname(selected_file))
            self.window.open_file(selected_file)

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

        # If project-specific enabled_configurations exist, use those.
        if self.view.settings().get('enabled_configurations'):
            configs = self.view.settings().get('enabled_configurations')
        else:
            configs = self.settings.get('enabled_configurations', [])

        valid_configs = {}
        for config in configs:
            config_details = self.settings.get(config)
            if config_details:
                valid_configs[config] = config_details

        paths = self._get_possible_paths(valid_configs)

        for config_key, path_dict in paths.items():
            app_path = path_dict['app_path']
            for path in path_dict['paths']:

                search_string = os.sep + path + os.sep

                # Module wildcard {%} can match anything except directory separators.
                search_string = re.escape(search_string) \
                    .replace(
                        re.escape('{%}'),
                        '(?P<module>[^' + re.escape(os.sep) + ']+)'
                    )

                match = re.search(
                    '^(.*?%s)' % search_string,
                    self.current_file
                )
                if match:
                    if 'module' in match.groupdict():
                        app_path = app_path.replace('{%}', match.group('module'))
                        path = path.replace('{%}', match.group('module'))

                    path_before_app_path = match.group(0).rstrip(os.sep).replace(path, '')
                    self.app_path = path_before_app_path + app_path

                    return valid_configs[config_key]

        return None

    def _get_possible_paths(self, configs):
        """
        Get a dict where keys are configuration names and values are dicts
        with keys 'app_path' and 'paths'.

        'paths' will include the app_path, as well as any other possible paths
        for that configuration which are implied by directory traversals in
        type paths.

        :Args:
            - configs: a dict of config settings

        """
        possible_paths_for_app_path = {}

        for config_key in sorted(configs):
            app_dir = configs[config_key]['app_dir'].replace('/', os.sep)
            paths = [app_dir]

            possible_paths_for_app_path[config_key] = {'app_path': app_dir}

            for file_type, file_type_details in configs[config_key]['file_types'].items():
                type_path = file_type_details['path']
                if '..' in type_path:
                    path_outside_of_app_path = os.path.realpath(
                            app_dir + os.sep + type_path
                        ).replace(os.path.realpath('.') + os.sep, '')

                    paths.append(path_outside_of_app_path)

            possible_paths_for_app_path[config_key]['paths'] = paths

        return possible_paths_for_app_path

    def _get_current_file_type(self):
        for file_type, details in self.configuration['file_types'].items():
            type_path = self._get_file_type_path(
                details['path'].replace('/', os.sep),
                self.current_file
            )

            if not type_path:
                continue

            search_string = os.path.realpath(
                os.path.join(
                    self.app_path,
                    type_path
                ).replace('/', os.sep)
            )

            match = re.search(
                '^%s' % re.escape(search_string),
                self.current_file
            )

            if match:
                return file_type

    def _get_file_type_path(self, path_pattern, file_path):
        """
        Get the file type path given the path pattern and the path of
        a file of that type.  Paths with a {%} wildcard will be replaced
        with the actual value used in the file path.

        """
        if '{%}' not in path_pattern:
            return path_pattern

        pattern = re.escape(path_pattern) \
            .replace(re.escape('{%}'), '([^' + re.escape(os.sep) + ']+)')

        match = re.search(
            pattern,
            file_path
        )
        if match:
            self.wildcard_vals_in_type_path = match.groups()
            return match.group(0)

    def _get_template_var_values(self):
        """
            Get a dictionary mapping the supported template variables and their
            values for the active file.
        """
        current_file_type_details = self._get_file_type_details(self._get_current_file_type())

        current_file_type_path = self._get_file_type_path(
            current_file_type_details.get('path', '').replace('/', os.sep),
            self.current_file
        )

        current_suffix = current_file_type_details.get('suffix', '')
        current_prefix = current_file_type_details.get('prefix', '')

        current_file_no_ext = os.path.splitext(self.current_file)[0]
        current_file_no_suffix = re.sub('%s$' % re.escape(current_suffix), '', current_file_no_ext)
        current_file_no_fixes = re.sub(
            '%s([^%s]+)$' % (re.escape(current_prefix), re.escape(os.sep)),
            '\g<1>',
            current_file_no_suffix
        )
        current_file = current_file_no_fixes

        current_file_type_path = os.path.realpath(
            os.path.join(self.app_path, current_file_type_path)
        )

        file_from_type_path = current_file.replace(current_file_type_path, '', 1).strip(os.sep)
        file_from_app_path = current_file.replace(self.app_path, '', 1).strip(os.sep)
        dir_from_type_path = os.path.dirname(file_from_type_path).strip(os.sep)

        return {
            'base_filename': os.path.basename(current_file),
            'file_from_type_path': file_from_type_path,
            'file_from_app_path': file_from_app_path,
            'dir_from_type_path': dir_from_type_path
        }

    def _get_file_type_details(self, file_type):
        file_type_details = self.configuration \
            .get('file_types', {}) \
            .get(file_type, {})

        return file_type_details

    def _is_creatable_file(self, glob_pattern):
        return '*' not in glob_pattern

    def _get_related_files(self):
        """
            Return list of lists with element 0 the file description
            and element 1 the path.
        """
        current_file_type = self._get_current_file_type()

        if current_file_type is None:
            return

        current_file_type_details = self._get_file_type_details(
            current_file_type
        )

        if not current_file_type_details:
            return

        template_vars = self._get_template_var_values()

        patterns = current_file_type_details.get('rel_patterns', {})

        related_files = []
        for file_type, pattern in patterns.items():

            target_file_type_details = self._get_file_type_details(file_type)
            target_suffix = target_file_type_details.get('suffix', '')
            target_prefix = target_file_type_details.get('prefix', '')

            target_file_type_path = target_file_type_details.get('path', '').replace('/', os.sep)

            for val in self.wildcard_vals_in_type_path:
                target_file_type_path = target_file_type_path.replace('{%}', val, 1)

            template = Template(pattern.replace('/', os.sep))
            glob_pattern = template.safe_substitute(
                app_path=self.app_path,
                type_path=target_file_type_path,
                base_filename=template_vars['base_filename'],
                file_from_type_path=template_vars['file_from_type_path'],
                file_from_app_path=template_vars['file_from_app_path'],
                dir_from_type_path=template_vars['dir_from_type_path'],
                suffix=''  # For backward compatability
            )

            # Add prefix and suffix to glob_pattern
            glob_pattern = re.sub(
                '(.+?)([^%s]+)\.([^.]+)$' % re.escape(os.sep),
                '\g<1>%s\g<2>%s.\g<3>' % (target_prefix, target_suffix),
                glob_pattern
            )

            # Collect matches
            matches = insensitive_glob(os.path.realpath(glob_pattern))

            related_files += [
                ['Open %s (%s)' % (file_type, os.path.basename(match)), match]
                for match in matches
                if os.path.isfile(match)
            ]

            if (not matches and self._is_creatable_file(glob_pattern)):
                creatable_file_path = os.path.realpath(glob_pattern)
                related_files.append(
                    [
                        'Create %s (%s)' % (
                            file_type,
                            os.path.basename(creatable_file_path)
                        ),
                        creatable_file_path
                    ]
                )

        return related_files
