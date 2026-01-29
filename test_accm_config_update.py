import logging
import time

import pytest

from rpi_bench.libs.appium.accessp_pages import CommandScreen, FabMenu
from rpi_bench.libs.appium.lib_appium import Phone
from rpi_bench.libs.selenium_lib.lib_selenium import BaseTestClass
from rpi_bench.libs.selenium_lib.webpages import VehiclesPage
from rpi_bench.test_api.Webutility_AP.webuitlity import Utility, wait_time
from rpi_bench.test_api.tools import get_bench_configuration, get_environment_configuration, get_env_organisation_item
from rpi_bench.test_api.access_plus_appium.key_operations_utils import vk_creation
from rpi_bench.test_api.access_plus_appium.login_utils import login

bc = get_bench_configuration()
locators = BaseTestClass.load_pages()

logger = logging.getLogger("ACCM_campaign")

env = get_environment_configuration()
url = env.get("base_url")
email = env.get("login_mail")
password = env.get("login_pass")
invalidpwd = bc['Signpage.invalidpwd']
superemail = bc['Signpage.superadmin']
superpwd = bc['Signpage.superpwd']
vehiclename = bc['Signpage.vhName']
offtime = 30
readytime = bc['Signpage.readytime']
chargingtime = bc['Signpage.chargingtime']
startedtime = bc['Signpage.startedtime']
drivingtime = bc['Signpage.drivingtime']

#UART_PORT = bc['UART_CONFIG.Uart_Port.port_number']
super_admin_email = bc['ACCM_Login.Super_admin.email']
super_admin_password = bc['ACCM_Login.Super_admin.password']
vehicle_name = bc['MOBILE_AUTOMATION_DATA.Main_Page.vehicle_search_string']
environment = env.get("environment")  # while login to mobile app
org_name = get_env_organisation_item("name")  # while logging into keycore2


class TestConfigUpdate:

    def setup_method(self):
        self.driver = BaseTestClass.set_up(self)
        self.wb = Utility(self.driver)
        self.phone1 = Phone(bc['AppiumConfig.Phone1'])

    def teardown_method(self):
        BaseTestClass.teardown(self)
        self.phone1.stop_driver()

    def test_set_precondition_for_private_mode(self):
        """ KAAS-20533
        Apply the pre condition: disable private mode if it is enabled alreayd
        """
        self.wb.test_login(url, email, password)
        self.wb.verify_login()
        self.wb.select_environment(org_name)
        self.wb.verify_env_selection(org_name)
        self.wb.searchVehicle(vehiclename)
        logger.info("Vehicle: " + vehiclename.upper() + "  is found in the search")
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        logger.info("Navigated to Vehicle details section")
        if self.wb.verify_private_mode_in_config_page("off"):
            logger.info("Private mode is disabled already to this vehicle")
        else:
            self.wb.disable_privatemode()
            self.wb.verify_private_mode_in_config_page("off")
            self.wb.navigate_to_event_log()
            # added below assertions to confirm the 'disable private mode' config completion
            assert self.wb.verify_event_log("Device Global Config", "Global Config Created",
                                            60), "Device Global Config event is not created"
            assert self.wb.verify_event_log("Device Config Manifest", "Config Manifest Requested by device", 180), \
                "Config manifest is not requested by device even after 3 minutes since the update is triggered in " \
                "configuration page "
            assert self.wb.verify_event_log("Device Config Manifest", "SUCCESS", 600), \
                "Configuration manifest is not completed even after almost 5 minutes since " \
                "the update is triggered in configuration tab "
            self.wb.navigate_back_to_device_details()

    @pytest.mark.depends(on=['test_set_precondition_for_private_mode'])
    def test_remove_existing_vk(self):
        """ KAAS-20533
        Apply the pre condition: remove the existing vk
        """
        status = self.wb.revoke_vk_on_FE(bc['Signpage.client_device'])
        if status:
            assert status is True, "Revoke Vk failed"
        else:
            logging.info("No Active Vk to revoke, create Vk and try again")

    @pytest.mark.depends(on=['test_remove_existing_vk'])
    def test_set_private_mode(self):
        """ KAAS-20533
        Set the private mode to ON for 'GNSS_POSITION'
        Check if the event logs are updated for the config update performed
        """
        self.wb.navigate_to_configuration_tab()
        self.wb.apply_private_mode(bc["private_mode_list"])
        self.wb.verify_private_mode_in_config_page("on")
        time.sleep(10)
        self.wb.navigate_to_event_log()
        assert self.wb.verify_event_log("Device Global Config", "Global Config Created",
                                        60), "Device Global Config event is not created"
        assert self.wb.verify_event_log("Device Config Manifest", "Config Manifest Requested by device", 180), \
            "Config manifest is not requested by device even after 3 minutes since the update is triggered in " \
            "configuration page "
        assert self.wb.verify_event_log("Device Config Manifest", "SUCCESS", 600), \
            "Configuration manifest is not completed even after 5 minutes since the update is triggered in " \
            "configuration tab "
        self.wb.navigate_back_to_device_details()

    @pytest.mark.depends(on=['test_set_private_mode'])
    def test_create_vk_in_access_plus(self):
        """ KAAS-20533
        Send the unlock/lock message from access+ mobile app and check the events for the same
        """
        login(self.phone1, super_admin_email, super_admin_password, environment)
        vk_creation(self.phone1, vehicle_name)
        time.sleep(10)
        self.phone1.tap(CommandScreen.unlock_button)
        assert self.phone1.get_text(CommandScreen.state_tab) == "Unlocking doors…"
        wait_time(offtime)
        time.sleep(self.phone1.default_timing)
        wait_time(offtime)
        self.wb.navigate_to_vehicle_data()
        self.wb.verify_private_mode_indicator("on")
        self.wb.verify_location_indicator("on")
        # Verifying if the 'Event' is coming in the vehicle data post enabling private mode
        self.wb.select_item("Event Name")
        self.wb.verify_event_telemetry_in_pvt_mode()

    @pytest.mark.depends(on=['test_set_private_mode'])
    def test_reset_configuration(self):
        """ KAAS-20533
        Disable the private mode
        Reset the timings to 1800s
        """
        self.wb.disable_privatemode()
        assert self.wb.set_config_time_interval("1800", readytime, chargingtime, startedtime, drivingtime)
        self.wb.logout()
