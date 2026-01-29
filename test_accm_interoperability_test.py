#!/bin/python3

import logging
import time
from datetime import date
from random import random

import pytest

from rpi_bench.libs.selenium_lib import lib_selenium
from rpi_bench.libs.appium.accessp_pages import CommandScreen, FabMenu
from rpi_bench.libs.appium.lib_appium import Phone
from rpi_bench.libs.lib_uart2 import UartInterface
from rpi_bench.libs.selenium_lib.lib_selenium import Actions
from rpi_bench.libs.selenium_lib.webpages import VehiclesPage, DashBoardPage
from rpi_bench.test_api.Webutility_AP.webuitlity import Utility, locators
from rpi_bench.test_api.access_plus_appium.key_operations_utils import vk_creation, vk_revoke
from rpi_bench.test_api.access_plus_appium.login_utils import login, logout
from rpi_bench.test_api.access_plus_appium.serial_utils import validating_uart_logs, Vehicle_LOCK, ACCM_UART_KEYWORDS, \
    get_com_port, Vehicle_UNLOCK
# from rpi_bench.test_api.customer_api.telemetry_utils import sms_api_post_template, sms_api_get_template
from rpi_bench.test_api.customer_api.vehicle_utils import vehicle_payload, vehicle_id_list, device_serial_list
from rpi_bench.test_api.tools import get_bench_configuration, get_environment_configuration
from rpi_bench.test_api.vk_tools import VkTools

bench_config = get_bench_configuration()
env_config = get_environment_configuration()
org_info = env_config.get("customer_api_org_preference")
testorg = env_config.get("org1.name")

test_bench_vehicle_id = env_config.get("test_bench_vehicle_id")
UART_KEYWORDS = bench_config.get(ACCM_UART_KEYWORDS)

logger = logging.getLogger("ACCM_campaign")
environment = env_config['environment']
super_admin_email = bench_config['ACCM_Login.Super_admin.email']
super_admin_password = bench_config['ACCM_Login.Super_admin.password']
vehicle_name = bench_config['MOBILE_AUTOMATION_DATA.Main_Page.vehicle_search_string']
VEHICLE_PAYLOAD = vehicle_payload

max_run = 1
UART_PORT = get_com_port()
logger.info(f"Uart Port : {UART_PORT}")
bc = get_bench_configuration()
vk_tools = VkTools(env_config)

url = bc['Signpage.web_url']
email = env_config.get("super_admin_login_payload.Email")
password = env_config.get("super_admin_login_payload.Password")
invalidpwd = bc['Signpage.invalidpwd']
superemail = bc['Signpage.superadmin']
superpwd = bc['Signpage.superpwd']
vehiclename = bc['Signpage.vhName']
useremailid = bc['Signpage.emailid']
user_mail = bc['Signpage.user_email']


@pytest.mark.usefixtures("update_results_to_jira")
class TestACCMCarOperations:

    @classmethod
    def setup_class(cls):
        cls.phone1 = Phone(bench_config['AppiumConfig.Phone1'])

    @classmethod
    def teardown_class(cls):
        try:
            cls.phone1.stop_driver()
        except:
            logger.error("Couldn't stop the driver properly")

    def setup_method(self):
        self.driver = lib_selenium.BaseTestClass.set_up(self)
        self.wb = Utility(self.driver)
        self._bt = Actions(self.driver)
        self.uart_i = UartInterface(UART_PORT)
        self.uart_i.start()
        self.video = self.phone1.start_screen_video()

    def teardown_method(self):
        lib_selenium.BaseTestClass.teardown(self)
        self.uart_i.stop()

    @pytest.mark.parametrize("run", list(range(0, max_run)))
    def test_kaas34139_createvk_evenlogs_01_api_revoke(self, run):
        """
                create virtual key from mobile, verify the vk status from keycore
                portal also extract the Vk id and revoke the vk through api call   """
        # login to access+ and create a virtual key and logut from the application
        logger.info("Run {}/{}".format(run + 1, max_run))
        logger.info("Login user and creating virtual key through mobile")
        login(self.phone1, super_admin_email, super_admin_password, environment)
        vk_creation(self.phone1, vehicle_name)
        time.sleep(10)
        self.phone1.tap(CommandScreen.fab_menu)
        assert self.phone1.check_elements(FabMenu.element_list, timeout=120)
        self.phone1.tap(CommandScreen.fab_menu)
        logger.info("Virtual key created.")
        """performing unlock operation """
        self.phone1.tap(CommandScreen.unlock_button)

        # Login and Check if vk is created and check for vk Id from keycore web
        logger.info("Login user from keycore portal, verify if the vk is created and extract the vk ID")
        self.wb.test_login(url, email, password)
        self.wb.select_environment(bc['Signpage.orgqa'])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        vk_id = self.wb.check_for_vk_active_status()
        logger.info("the virtual key id is" + vk_id)

        # Api Automation to revoke the Virtual key
        logger.info("revoke the created vk from mobile through api call")
        resp = vk_tools.keycore_requests.revoke_vk(vk_id)
        assert vk_tools.keycore_requests.cloud.response_code == 200, "response code not equals to 200"
        self.phone1.click_back(timeout=120)
        logout(self.phone1)

    def test_remote_assiatance_02_uart_api_status(self):
        """
          through the keycore perform lock operation from remote assistance page and verify the toast message,
          verify lock event generated from event log and fetch the sms id and sms status.
          checking the lock action from UART and verifying the lock sms status through api
               """
        # launch keycore and perform lock operation from remote assistance
        logger.info("launching the keycore and selecting the vehicle")
        self.wb.test_login(url, email, password)
        self.wb.select_environment(bc['Signpage.orgqa'])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        logger.info("obtaining the SMS_request_id and sms_request_status")
        msg = self.wb.backend_vehicle_remote_assistance(locators[DashBoardPage.door_lock_button])
        assert msg == bc['Signpage.lock_succesful'], "lock unsuccessful"
        self.wb.navigate_to_event_log()
        assert self.wb.verify_event_log("Vehicle Control", "Eculock command requested by " + email,
                                        60), "lock sms command unsuccessful "
        smsid, smsstatus, clientid = self.wb.get_sms_request_id()
        logger.info("sms request id" + smsid)
        logger.info("sms request status" + smsstatus)

        # Validating UART LOGS generated for lock operation performed from the remote assistance
        logger.info("checking for UART-LOGS for lock action performed from keycore on the device")
        try:
            assert validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[Vehicle_LOCK])
        except AssertionError as assert_error:
            self.uart_i.save(clear_buffer=True)
            logger.info(self.uart_i.buffer)
            raise assert_error
        self.uart_i.clear_buffer()

        # Verifying the STATUS of the LOCK operation sms through API
        logger.info(" verifying the status of lock sms operation through API")
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=smsid,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp1.get("remoteOperation").get("status") == smsstatus, "sms status not Delivered"

    @pytest.mark.parametrize("run", list(range(0, max_run)))
    def test_kaas34141_createvk_03_evenlogs_webrevoke(self, run):
        """
                create virtual key from mobile, verify the vk status from keycore
                portal also extract the client id and revoke the vk through web keycore poratl   """

        logger.info("Run {}/{}".format(run + 1, max_run))
        logger.info("Login user and creating virtual key through mobile")
        login(self.phone1, super_admin_email, super_admin_password, environment)
        vk_creation(self.phone1, vehicle_name)
        time.sleep(10)
        self.phone1.tap(CommandScreen.fab_menu)
        assert self.phone1.check_elements(FabMenu.element_list, timeout=120)
        self.phone1.tap(CommandScreen.fab_menu)
        logger.info("Virtual key created.")

        # launch keycore and check for the events log for the vk creation , also revoke the VK and verify the eventlog.
        logger.info("launching the keycore and selecting the vehicle")
        self.wb.test_login(url, email, password)
        self.wb.select_environment("kaas user testQa")
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        self.wb.navigate_to_event_log()
        logger.info("checking for the events Virtual Key Created and acknowledged. from the events log ")
        assert self.wb.verify_event_log("Virtual Key", "Virtual Key Created and acknowledged.",
                                        60), "virtual key not created "
        smsid, smsstatus, clientId = self.wb.get_sms_request_id()
        logger.info("the cleint id is" + clientId)
        self.wb.navigate_back_to_device_details()
        logger.info("revoking the vk through keycore poratal.")
        status = self.wb.revoke_vk_on_FE(clientId)
        if status:
            assert status is True, "Revoke Vk failed"
        else:
            logging.info("No Active Vk to revoke, create Vk and try again")
        self.phone1.click_back(timeout=120)
        logout(self.phone1)

    @pytest.mark.parametrize("run", list(range(0, max_run)))
    def test_kaas34137_createvk_04_evenlogss_webrevoke(self, run):
        """
        create virtual key from mobile, perform lock operation through mobile, verify the VEHILE_LOCKED event is
        present in  vehicle data page of BE, on the event logs as along with UART validation """

        logger.info("Run {}/{}".format(run + 1, max_run))
        logger.info("Login user and creating virtual key through mobile")
        login(self.phone1, super_admin_email, super_admin_password, environment)
        vk_creation(self.phone1, vehicle_name)
        time.sleep(10)
        self.phone1.tap(CommandScreen.fab_menu)
        assert self.phone1.check_elements(FabMenu.element_list, timeout=120), "all elements are not visible"
        self.phone1.tap(CommandScreen.fab_menu)
        logger.info("Virtual key created.")
        """performing lock operation """
        self.phone1.tap(CommandScreen.lock_button)

        # launch keycore and check for the events log for the vk creation , also revoke the VK and verify the eventlog.
        logger.info("launching the keycore and selecting the vehicle")
        self.wb.test_login(url, email, password)
        self.wb.select_environment("kaas user testQa")
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        logger.info("Validating VEHICLE_LOCKED event is generated in the vehicle data.")
        self.wb.select_item("Event Name")
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.eventName_val])
        assert element is True, "Event data not found"
        logging.info("the event generated is " + element_data)
        self.wb.navigate_to_event_log()
        logger.info("checking for the events Virtual Key Created and acknowledged. from the events log ")
        assert self.wb.verify_event_log("Virtual Key", "Virtual Key Created and acknowledged.",
                                        60), "virtual key not created "

        # Validating UART LOGS generated for lock operation performed from the remote assistance
        logger.info("checking for UART-LOGS for lock action performed from keycore on the device")
        try:
            assert validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[Vehicle_LOCK])
        except AssertionError as assert_error:
            self.uart_i.save(clear_buffer=True)
            logger.info(self.uart_i.buffer)
            raise assert_error
        self.uart_i.clear_buffer()

    def test_unlock_KAAS34143_keycore_05_apistatus(self):
        """
        This test case performs unlock operation from back end - keycore portal.
        verifies the unlock event generated from the vehicles page, verifies UART logs for unlock
        checks the status of the sms through API.
        """
        # Login to web portal and perform Unlock operation from remote assistance
        self.wb.test_login(url, email, password)
        self.wb.select_environment(bc['Signpage.orgqa'])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        msg = self.wb.backend_vehicle_remote_assistance(locators[DashBoardPage.door_unlock_button])
        assert msg == bc['Signpage.unlock_succesful'], "unlock unsuccessful"

        # checking for events from the vehicle page.
        logger.info("navigating to vehicle page to check the generated event")
        self.wb.select_item("Event Name")
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.eventName_val])
        assert element is True, "Event data not found"
        logging.info(element_data)
        time.sleep(3)
        self.wb.navigate_to_event_log()
        logger.info("navigating to events logs to check the event generated.")
        assert self.wb.verify_event_log("Vehicle Control", "Ecuunlock command requested by " + email,
                                        60), "unlock sms command unsuccessful "
        smsid, smsstatus, clientid = self.wb.get_sms_request_id()
        logger.info("sms request id" + smsid)
        logger.info("sms request status" + smsstatus)

        # verifying the event UNLOCK generated at event data
        logger.info("checking for the UART-LOGS for the unlock operation")
        try:
            assert validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[Vehicle_UNLOCK])
        except AssertionError as assert_error:
            self.uart_i.save(clear_buffer=True)
            logger.info(self.uart_i.buffer)
            raise assert_error
        self.uart_i.clear_buffer()

        # Verifying the STATUS of the LOCK operation sms through API
        logger.info(" verifying the status of unlock sms operation through API")
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=smsid,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp1.get("remoteOperation").get("status") == smsstatus

    def test_KAAS34146_sms_id_lock_06_web_eventdata(self):
        """
        this test case performs lock operation through sms api ,generated VEHICLE_LOCKED
        event is Validated  through the web portal
        """
        logger.info("performing lock operation through SMS api")
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["LOCK"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        # vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        # vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED", "the status of the lock operation is not " \
                                                                          "delivered "

        # login to keycore and select the vehicle
        self.wb.test_login(url, email, password)
        self.wb.select_environment(bc['Signpage.orgqa'])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])

        # checking for events from the vehicle page- VEHICLE_LOCKED.
        logger.info("navigating to vehicle page to check the generated event")
        self.wb.select_item("Event Name")
        element, element_data = self.wb.telemetric_data(locators[DashBoardPage.eventName_val])
        assert element is True, "Event data not found"
        logging.info("event data is" + element_data)

    def test_07_KAAS34144_create_vehicle_web_check(self):
        """
        This test case creates new vehicle through the APi and verifies that the created vehicle is appearing on the keycore.
        """
        logger.info("creating vehicle through api")
        vk_tools.keycore_requests.authenticate()
        vk_tools.keycore_requests.create_module_and_device_rabbit()

        VEHICLE_PAYLOAD["device"]["serialNumber"] = "{}".format(vk_tools.keycore_requests.kc_info['module_serial'])
        payload = VEHICLE_PAYLOAD.copy()

        resp = vk_tools.keycore_requests.create_vehicle_rabbit_device(payload=payload, version=2)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        logger.info(
            "New vehicle has be created. VIN : {}, vehicle id : {}, device_serial number : {}".format(resp.get("vin"),
                                                                                                      resp.get("id"),
                                                                                                      resp.get(
                                                                                                          "device")))
        vehicle_vin = format(resp.get("vin"))
        logger.info("VIn number is" + vehicle_vin)
        vk_tools.keycore_requests.vehicle.id = resp.get("id")
        vehicle_id_list.append(resp.get("id"))
        device_serial_list.append(resp.get("device").get("serialNumber"))

        # login to keycore and select the vehicle
        logger.info("Login through the keycore and check the vehicle is avaible in the vehicle list.")
        logger.info("selecting the vehicle from the Keycore")
        self.wb.test_login(url, email, password)
        self.wb.select_environment(bc['Signpage.orgqa'])
        self.wb.searchVehicle(vehiclename)
