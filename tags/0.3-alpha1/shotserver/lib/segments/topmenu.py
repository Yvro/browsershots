# Copyright (C) 2006 Johann C. Rocholl <johann@browsershots.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Display top menu bar.
"""

__revision__ = '$Rev$'
__date__ = '$Date$'
__author__ = '$Author$'

from shotserver03.interface import xhtml, menu

def write():
    """
    Write XHTML top menu bar.
    """
    xhtml.write_open_tag_line('div', _class="menu lightgray", _id="topmenu")

    menu.write('float-left', (
        "Screenshots=/screenshots/",
        "Queue=/queue/",
        "Factories=/factories/"))

    menu.write('float-right mockup', (
        "Technology Preview=http://browsershots.org/blog/2006/06/12/technology-preview/", ))

    xhtml.write_tag_line('div', '', _class="clear")
    xhtml.write_close_tag_line('div') # id="topmenu"