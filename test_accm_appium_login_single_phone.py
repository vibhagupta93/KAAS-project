""" Campaign to test login
"""
import logging
import pytest

from rpi_bench.libs.appium.accessp_pages import LoginPage, MainPage
from rpi_bench.libs.appium.lib_appium import Phone, BaseTestClass
from rpi_bench.test_api.access_plus_appium.login_utils import login, logout
from rpi_bench.test_api.tools import get_bench_configuration, get_environment_configuration

bc = get_bench_configuration()
env = get_environment_configuration()

logger = logging.getLogger("ACCM_campaign")

environment = env['environment']
super_admin_email = bc['ACCM_Login.Super_admin.email']
super_admin_password = bc['ACCM_Login.Super_admin.password']

password_validation_user_email = bc['ACCM_Login.User_password_validation.email']
password_validation_user_password = bc['ACCM_Login.User_password_validation.password']


@pytest.mark.usefixtures("update_results_to_jira")
class TestACCMLogin(BaseTestClass):
    """ Campaign to test login  """
    @classmethod
    def setup_class(cls):
        """Setup phone before testing
        """
        cls.phone1 = Phone(bc['AppiumConfig.Phone1'])

    @classmethod
    def teardown_class(cls):
        """Kill phone after testing
        """
        try:
            cls.phone1.stop_driver()
        except Exception as excep: #pylint: disable=W0718
            logger.info("Couldn't stop the driver properly")
            logger.error(excep)

    def test_login_single_phone_010_check_login(self):
        """
        Login and Check if the elements defined in the model are present on the page
        """

        logger.info("Login user")
        login(self.phone1, super_admin_email, super_admin_password, environment)
        assert self.phone1.check_elements(MainPage.element_list)
        assert self.phone1.check_text_in_elements("Vehicle list", MainPage.vehicle_list_title)

        logger.info("Logout user")
        logout(self.phone1)
        assert self.phone1.check_elements(LoginPage.element_list)

    @pytest.mark.parametrize("password", [password_validation_user_password.upper(),
                                          ''.join(filter(str.isalnum, password_validation_user_password)),
                                          password_validation_user_password.lower(),
                                          ""],
                                          ids=["_password_with_all_uppercase_letters",
                                               "_password_after_removing_special_characters",
                                               "_password_with_all_lowercase_letters",
                                               "_giving_empty_password"])
    def test_login_single_phone_020_password_validations(self, password):
        """
        Password validation checks
        Scenario1: Checking the validation by giving password with all uppercase letters
        Scenario2: Checking the validation by giving password after removing special characters
        Scenario3: Checking the validation by giving password with all lowercase letters
        Scenario4: Checking the validation by giving empty password
        Implementing test case id: C20605417 (Check login with wrong password)
        """
        logger.info("Password validation")

        login(self.phone1, password_validation_user_email, password, environment,
              handle_location_permission=False, handle_relative_position_permission=False, handle_notification_permission=False)
        assert self.phone1.check_elements(LoginPage.element_list)
