# Copyright 2014, Brian Coca <bcoca@ansible.com>
# Copyright 2017, Ken Celenza <ken@networktocode.com>
# Copyright 2017, Jason Edelman <jason@networktocode.com>
# Copyright 2017, Ansible Project
# Copyright 2020, Adanos
#
# This file is plugin for Ansible
#
# This plugin is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This plugin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with This plugin.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re

from ansible.errors import AnsibleFilterError
from ansible.utils.display import Display
from ansible.module_utils.six import iteritems

display = Display()

PARTED_SIZE_RANGES = {
    'Yi': 1 << 80,
    'Y': 10 ** 24,
    'Zi': 1 << 70,
    'Z': 10 ** 21,
    'Ei': 1 << 60,
    'E': 10 ** 18,
    'Pi': 1 << 50,
    'P': 10 ** 15,
    'Ti': 1 << 40,
    'T': 10 ** 12,
    'Gi': 1 << 30,
    'G': 10 ** 9,
    'Mi': 1 << 20,
    'M': 10 ** 6,
    'Ki': 1 << 10,
    'K': 10 ** 3,
    'B': 1,
}

def parted_human_to_bytes_convert(number, default_unit=None, isbits=False, iskibi=False):
    """Convert number in string format into bytes (ex: '2K' => 2048) or using unit argument.
    example: human_to_bytes('10M') <=> human_to_bytes(10, 'M')
    """
    regex_search_match = re.search(r'^\s*(\d*\.?\d*)\s*([A-Za-z]+)?', str(number), flags=re.IGNORECASE)

    if regex_search_match is None:
        raise ValueError("human_to_bytes() can't interpret following string: %s" % str(number))
    try:
        num = float(regex_search_match.group(1))
    except Exception:
        raise ValueError("human_to_bytes() can't interpret following number: %s (original input string: %s)" % (regex_search_match.group(1), number))

    unit = regex_search_match.group(2)
    if unit is None:
        unit = default_unit

    if unit is None:
        ''' No unit given, returning raw number '''
        return int(round(num))
    
    # Get unit for kilo or kibi
    if iskibi:
        range_key = unit[:2].capitalize()
    else:
        range_key = unit[0].capitalize()

    try:
        limit = PARTED_SIZE_RANGES[range_key]
    except Exception:
        # Get keys correspoinding to unit type (kilo or kibi)
        correct_units = []
        for KEY in PARTED_SIZE_RANGES:
            if len(KEY) == len(range_key):
                correct_units.append(KEY)
        raise ValueError("human_to_bytes() failed to convert %s (unit = %s). The suffix must be one of %s" % (number, unit, ", ".join(correct_units)))

    # default value
    unit_class = 'B'
    unit_class_name = 'byte'
    # handling bits case
    if isbits:
        unit_class = 'b'
        unit_class_name = 'bit'
    # check unit value if more than one character (KB, MB)
    if len(unit) > 1:
        expect_message = 'expect %s%s or %s' % (range_key, unit_class, range_key)
        if range_key == 'B':
            expect_message = 'expect %s or %s' % (unit_class, unit_class_name)

        if unit_class_name in unit.lower():
            pass
        elif (iskibi and unit[2] != unit_class) or (not iskibi and unit[1] != unit_class):
            raise ValueError("human_to_bytes() failed to convert %s. Value is not a valid string (%s)" % (number, expect_message))

    return int(round(num * limit))

def parted_human_to_bytes(size, default_unit=None, isbits=False, iskibi=False):
    ''' Return bytes count from a human readable string '''
    try:
        return parted_human_to_bytes_convert(size, default_unit, isbits, iskibi)
    except Exception:
        raise AnsibleFilterError("human_to_bytes() can't interpret following string: %s" % size)

def parted_bytes_to_human(size, isbits=False, unit=None, iskibi=False, spaceseparator=True):
    base = 'Bytes'
    if isbits:
        base = 'bits'
    suffix = ''

    separator = ''
    if spaceseparator:
        separator = ' '

    # Get only kilo or kibi units
    units = []
    for item in iteritems(PARTED_SIZE_RANGES):
        if (not iskibi and len(item[0]) == 1) or (iskibi and len(item[0]) == 2):
            units.append(item)

    for suffix, limit in sorted(units, key=lambda item: -item[1]):
        if iskibi:
            target_suffix = suffix[:2]
        else:
            target_suffix = suffix[0]
        if (unit is None and size >= limit) or unit is not None and unit.capitalize() == target_suffix:
            break

    if limit != 1:
        suffix += base[0]
    else:
        suffix = base

    return '%.2f%s%s' % (size / limit, separator, suffix)

def parted_human_readable(size, isbits=False, unit=None, iskibi=False, spaceseparator=True):
    ''' Return a human readable string '''
    try:
        return parted_bytes_to_human(size, isbits, unit, iskibi, spaceseparator)
    except Exception:
        raise AnsibleFilterError("human_readable() can't interpret following string: %s" % size)

class FilterModule(object):
    ''' Ansible size filters for Parted'''

    def filters(self):
        filters = {

            # computer theory
            'parted_human_readable': parted_human_readable,
            'parted_human_to_bytes': parted_human_to_bytes

        }

        return filters
