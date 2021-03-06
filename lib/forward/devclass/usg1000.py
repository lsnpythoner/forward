# coding:utf-8
#
# This file is part of Forward.
#
# Forward is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Forward is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
-----Introduction-----
[Core][forward] Device class for USG1000.
"""
import re
from forward.devclass.baseVenustech import BASEVENUSTECH
from forward.utils.forwardError import ForwardError


class USG1000(BASEVENUSTECH):
    """This is a manufacturer of venustech, so it is integrated with BASEVENUSTECH library.
    """
    def showVlan(self):
        # No VLAN information for the model equipment.
        data = {"status": False,
                "content": [],
                "errLog": ""}
        data["status"] = True
        return data

    def _recv(self, _prompt):
        # Gets the return message after the command is executed.
        data = {"status": False,
                "content": "",
                "errLog": ""}
        # If the received message contains the host prompt, stop receiving.
        i = self.channel.expect([r"%s" % _prompt], timeout=self.timeout)
        try:
            if i[0] == -1:
                # The supplied host prompt is incorrect, resulting in the receive message timeout.
                raise ForwardError('Error: receive timeout')
            # Successed.
            data['status'] = True
            # Get result.
            data['content'] = i[-1]
        except ForwardError, e:
            data['errLog'] = str(e)
        return data

    def addUser(self, username, password, admin=False):
        """Create a user on the device.
        """
        # Set command.
        if admin:
            command = """user administrator {username} local {password} \
                       authorized-table admin\n""".format(username=username, password=password)
        else:
            command = """user administrator {username} local {password} \
                       authorized-table admsee\n""".format(username=username, password=password)
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            # parameters check.
            if not username or not password:
                # Spcify a user name and password parameters here.
                raise ForwardError('Please specify the username = your-username and password = your-password')
            # swith to config terminal mode.
            checkPermission = self._configMode()
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            if self.isConfigMode:
                # check terminal status
                self.channel.write(command)
                # adduser
                data = self._recv(self.prompt)
                # recv result
                if not data['status']:
                    # break
                    raise ForwardError(data['errLog'])
                result = data['content']
                if re.search('error|invalid|assword', result, flags=re.IGNORECASE):
                    # command failure
                    raise ForwardError(result)
                # set password is successed, save the configuration.
                data = self._commit()
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
            data['errLog'] = str(e)
            data['status'] = False
        return data

    def deleteUser(self, username):
        """Delete a user on the device
        """
        data = {"status": False,
                "content": "",
                "errLog": ""}
        try:
            # swith to config terminal mode.
            checkPermission = self._configMode()
            if not checkPermission['status']:
                raise ForwardError(checkPermission['errLog'])
            # Check config mode status.
            if self.isConfigMode:
                # check terminal status
                # deleteUser
                self.channel.write("""no user administrator {username}\n""".format(username=username))
                # recv result
                data = self._recv(self.prompt)
                if not data['status']:
                    # break
                    raise ForwardError(data['errLog'])
                # Get result.
                result = data['content']
                # Search for keywords to determine if the command execution is successful.
                if re.search('error|invalid|assword', result, flags=re.IGNORECASE):
                    # command failure
                    raise ForwardError(result)
                # delete user is successed, save the configuration.
                data = self._commit()
            else:
                raise ForwardError('Has yet to enter configuration mode')
        except ForwardError, e:
            data['errLog'] = str(e)
            data['status'] = False
        return data

    def changePassword(self, username, password):
        """Modify the password for the device account.
        Because the password command to modify the account on the device is consistent with the creation
        of the user's command, the interface to create the account is called.
        """
        return self.addUser(username=username, password=password)
