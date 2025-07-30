import random

import pytest

from hamcrest import is_  # type: ignore

from qa_pytest_examples.combined_configuration import CombinedConfiguration
from qa_pytest_examples.combined_steps import CombinedSteps
from qa_pytest_examples.model.swagger_petstore_pet import SwaggerPetstorePet
from qa_pytest_rest.rest_tests import RestTests
from qa_pytest_webdriver.selenium_tests import SeleniumTests
from qa_testing_utils.matchers import yields_item, traced


@pytest.mark.external
@pytest.mark.selenium
class CombinedTests(
        RestTests[CombinedSteps, CombinedConfiguration],
        SeleniumTests[CombinedSteps, CombinedConfiguration]):
    _steps_type = CombinedSteps
    _configuration = CombinedConfiguration()

    def should_run_combined_tests(self):
        random_pet = SwaggerPetstorePet.random()
        random_user = random.choice(self._configuration.users)

        (self.steps
            .given.swagger_petstore(self._rest_session)
            .when.adding(random_pet)
            .then.the_available_pets(yields_item(traced(is_(random_pet))))
            .given.terminalx(self._web_driver)
            .when.logging_in_with(random_user.credentials)
            .then.the_user_logged_in(is_(random_user.name)))
