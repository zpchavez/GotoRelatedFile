GotoRelatedFile
===============
GotoRelatedFile is a Sublime plugin that allows easy navigation to files that
are related to the current one, e.g. the views related to a controller.

Installation
============
GotoRelatedFile is not in package control at this time.  You can add it manually
by selecting "Package Control: Add Repository" from the Command Palette.

Configuration
=============
GotoRelatedFile is customizable to different project directory structures.
See the default settings file to see how it works.

The placeholders used in the rel_patterns strings are:

   * app_path  - The absolute path to the application directory.
   * type_path - The path to where files of the target type are found, relative to the app path.
   * suffix - The suffix of the target file type, if one is defined.
   * file_from_type_path - The path to the starting file, minus the extension and suffix, relative to the type_path
   * file_from_app_path - The path to the starting file, minus the extension and suffix, relative to the app_path.
   * dir_from_type_path - The path to the starting file's directory relative to the type_path

GotoRelatedFile will go through the enabled_configurations and use the first one whose
app_dir is found in the path of the current file.

Usage
=====
The default key binding to bring up the list of related files is ctrl+shift+r on Windows
and Linux and cmd+shift+r on OSX.

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
