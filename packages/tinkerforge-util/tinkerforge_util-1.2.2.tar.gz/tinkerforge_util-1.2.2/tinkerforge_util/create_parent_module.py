#
# Tinkerforge Util
# Copyright (C) 2024 Matthias Bolte <matthias@tinkerforge.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
#

import sys
import pathlib
import importlib.util
import importlib.machinery


def create_parent_module(path, module_name):
    if module_name in sys.modules:
        return

    module_path = pathlib.Path(path).absolute()

    while len(module_path.name) > 0 and module_path.name != module_name:
        module_path = module_path.parent

    if module_path.name != module_name:
        raise Exception(f'Module {module_name} not found in path {path}')

    if sys.hexversion < 0x3050000:
        module = importlib.machinery.SourceFileLoader(module_name, module_path / '__init__.py').load_module()
    else:
        spec = importlib.util.spec_from_file_location(module_name, module_path / '__init__.py')
        module = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(module)

    sys.modules[module_name] = module
