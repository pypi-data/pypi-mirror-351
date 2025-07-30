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

def write_file_if_different(path, new_content):
    if type(new_content) == str:
        new_content = bytes(new_content, encoding='utf-8')

    content_identical = False

    try:
        with open(path, 'rb') as f:
            old_content = f.read()
            content_identical = old_content == new_content
    except:
        pass

    if not content_identical:
        with open(path, 'wb') as f:
            f.write(new_content)
