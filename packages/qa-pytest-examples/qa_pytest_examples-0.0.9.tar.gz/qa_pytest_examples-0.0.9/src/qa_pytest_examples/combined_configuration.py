# SPDX-FileCopyrightText: 2025 Adrian Herscu
#
# SPDX-License-Identifier: Apache-2.0


from qa_pytest_examples.swagger_petstore_configuration import SwaggerPetstoreConfiguration
from qa_pytest_examples.terminalx_configuration import TerminalXConfiguration


class CombinedConfiguration(
        SwaggerPetstoreConfiguration, TerminalXConfiguration):
    pass
