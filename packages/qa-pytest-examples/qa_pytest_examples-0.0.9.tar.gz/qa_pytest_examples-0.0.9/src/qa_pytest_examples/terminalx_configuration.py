# SPDX-FileCopyrightText: 2025 Adrian Herscu
#
# SPDX-License-Identifier: Apache-2.0

from typing import List, final
from qa_pytest_examples.model.terminalx_credentials import TerminalXCredentials
from qa_pytest_examples.model.terminalx_user import TerminalXUser
from qa_pytest_webdriver.selenium_configuration import SeleniumConfiguration


class TerminalXConfiguration(SeleniumConfiguration):
    @property
    @final
    def users(self) -> List[TerminalXUser]:
        users_section = self.parser["users"]
        return [
            TerminalXUser(TerminalXCredentials.from_(username_password), name=key)
            for key, username_password in users_section.items()
        ]
