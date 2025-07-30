from qa_pytest_examples.combined_configuration import CombinedConfiguration
from qa_pytest_examples.swagger_petstore_steps import SwaggerPetstoreSteps
from qa_pytest_examples.terminalx_steps import TerminalXSteps


class CombinedSteps(
        SwaggerPetstoreSteps[CombinedConfiguration],
        TerminalXSteps[CombinedConfiguration]):
    pass
