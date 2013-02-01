GotoRelatedFile
===============
GotoRelatedFile is a Sublime plugin that allows easy navigation to files that
are related to the current one, e.g. the views related to a controller.

Installation
============
GotoRelatedFile is not in package control at this time. You can add it manually
by first adding the repository by selecting "Package Control: Add Repository"
from the Command Palette and typing in the repo's URL (without the .git), and then
selecting "Package Control: Install Package" and selecting GotoRelatedFile.

Usage
=====
The default key binding to bring up the list of related files is ctrl+shift+r on Windows
and Linux and cmd+shift+r on OSX.

Configuration
=============
GotoRelatedFile is customizable to different project directory structures.
See the default settings file to see how it works.

To determine which configuration to use, GotoRelatedFile will go through the
enabled_configurations and use the first one whose app_dir is found in the
path of the current file.

Placeholders
------------

The placeholders used in the rel_patterns strings are:

   * app_path  - The absolute path to the application directory.
   * type_path - The path to where files of the target type are found, relative to the app path.
   * full_type_path - (Somewhat) shorter alias for app_path/type_path.
   * base_filename - The filename without the path or extension.
   * file_from_type_path - The path to the starting file, minus the extension, relative to the type_path.
   * file_from_app_path - The path to the starting file, minus the extension, relative to the app_path.
   * dir_from_type_path - The path to the starting file's directory relative to the type_path.

Suffixes and Prefixes
---------------------

You can define a suffix or prefix for any file type.  The fix will be removed or added as needed
when searching for related files.

Modules
-------

You may use the string {%} in an app_dir or path value to represent a directory
that separates the app into a module.  For example, if your project has:

js/modules/public
js/modules/admin

You can either define your type paths like so:

modules/{%}/controllers
modules/{%}/views

Or, if no part of your application exists outside of a module, you can
define your app_dir as:

js/modules/{%}

When searching for related files, GotoRelatedFile will replace the {%} in the
target path with whatever was contained in the {%} for the current file.

Project Settings
----------------

You can specify which configurations to use per project by adding a
"settings" dict to the .sublime-project file and defining "enabled_configurations"
there.

Tests
=====

GotoRelatedFile has tests.  To run them, assign a key binding to
the command show_goto_related_file_test_suites.

License
=======
GotoRelatedFile is licensed under a modified BSD license.

Copyright (c) 2012, Zachary Chavez
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
   * Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.
   * Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.
   * Neither the name of the copyright holder nor the name of any of the
     software's contributors may be used to endorse or promote products
     derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
