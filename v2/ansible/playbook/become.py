# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.playbook.attribute import Attribute, FieldAttribute
#from ansible.utils.display import deprecated

class Become:

    # Privlege escalation
    _become              = FieldAttribute(isa='bool', default=False)
    _become_method       = FieldAttribute(isa='string')
    _become_user         = FieldAttribute(isa='string')
    _become_pass         = FieldAttribute(isa='string')

    def __init__(self):
        return super(Become, self).__init__()

    def _detect_privilege_escalation_conflict(self, ds):

        # Fail out if user specifies conflicting privelege escalations
        has_become = 'become' in ds or 'become_user'in ds
        has_sudo   = 'sudo' in ds or 'sudo_user' in ds
        has_su     = 'su' in ds or 'su_user' in ds

        if has_become:
            msg = 'The become params ("become", "become_user") and'
            if has_sudo:
                raise errors.AnsibleParserError('%s sudo params ("sudo", "sudo_user") cannot be used together' % msg)
            elif has_su:
                raise errors.AnsibleParserError('%s su params ("su", "su_user") cannot be used together' % msg)
        elif has_sudo and has_su:
            raise errors.AnsibleParserError('sudo params ("sudo", "sudo_user") and su params ("su", "su_user") cannot be used together')

    def _munge_become(self, ds):

        self._detect_privilege_escalation_conflict(ds)

        # Setting user implies setting become/sudo/su to true
        if 'become_user' in ds and not ds.get('become', False):
            ds['become'] = True

        # Privilege escalation, backwards compatibility for sudo/su
        if 'sudo' in ds or 'sudo_user' in ds:
            ds['become_method'] = 'sudo'
            if 'sudo' in ds:
                ds['become'] = ds['sudo']
                del ds['sudo']
            else:
                ds['become'] = True
            if 'sudo_user' in ds:
                ds['become_user'] = ds['sudo_user']
                del ds['sudo_user']

            #deprecated("Instead of sudo/sudo_user, use become/become_user and set become_method to 'sudo' (default)")

        elif 'su' in ds or 'su_user' in ds:
            ds['become_method'] = 'su'
            if 'su' in ds:
                ds['become'] = ds['su']
                del ds['su']
            else:
                ds['become'] = True
            if 'su_user' in ds:
                ds['become_user'] = ds['su_user']
                del ds['su_user']

            #deprecated("Instead of su/su_user, use become/become_user and set become_method to 'su' (default is sudo)")

        return ds
