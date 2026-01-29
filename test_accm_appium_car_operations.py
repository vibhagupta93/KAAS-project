#!/bin/python3

import logging
import time
import pytest
from rpi_bench.libs.accm.accm_manager import get_accm_port

from rpi_bench.libs.appium.accessp_pages import MainPage, KeyCreation, CommandScreen, FabMenu
from rpi_bench.libs.appium.lib_appium import Phone, BaseTestClass
from rpi_bench.libs.lib_uart2 import UartInterface
from rpi_bench.test_api.access_plus_appium.key_operations_utils import vk_creation, vk_revoke
from rpi_bench.test_api.access_plus_appium.login_utils import login
from rpi_bench.test_api.access_plus_appium.vehicle_search_utils import search_vehicle
from rpi_bench.test_api.access_plus_appium.serial_utils import validating_uart_logs, VK_CREATE, VK_REVOKE, \
    Vehicle_Flash_Light, Vehicle_Open_Trunk, Vehicle_LOCK, Vehicle_UNLOCK, Vehicle_Enable_Engine_Start, \
    Vehicle_Disable_Engine_Start, ACCM_UART_KEYWORDS, get_com_port
from rpi_bench.test_api.tools import get_bench_configuration, get_environment_configuration
from rpi_bench.test_api.vk_tools import VkTools
from rpi_bench.test_api.customer_api.vehicle_utils import test_bench_vehicle_id

bench_config = get_bench_configuration()
env_config = get_environment_configuration()

UART_KEYWORDS = bench_config.get(ACCM_UART_KEYWORDS)

logger = logging.getLogger("ACCM_campaign")

environment = env_config['environment']
super_admin_email = bench_config['ACCM_Login.Super_admin.email']
super_admin_password = bench_config['ACCM_Login.Super_admin.password']
vehicle_name = bench_config['MOBILE_AUTOMATION_DATA.Main_Page.vehicle_search_string']

max_run = 1
UART_PORT = get_com_port()
logger.info(f"Uart Port : {UART_PORT}")

vk_tools = VkTools(env_config)


@pytest.mark.usefixtures("update_results_to_jira")
class TestACCMCarOperations(BaseTestClass):

    @classmethod
    def setup_class(cls):
        cls.phone1 = Phone(bench_config['AppiumConfig.Phone1'])

    @classmethod
    def teardown_class(cls):
        try:
            cls.phone1.stop_driver()
        except:
            logger.info("Couldn't stop the driver properly")

    def setup_method(self):
        self.uart_i = UartInterface(UART_PORT)
        self.uart_i.start()
        self.video = self.phone1.start_screen_video()

    def teardown_method(self):
        self.uart_i.stop()

    @pytest.mark.parametrize("run", list(range(0, max_run)))
    def test_car_operations_010_check_login(self, run):
        """Login and Check if the elements defined in the model are present on the page"""
        logger.info("Run {}/{}".format(run + 1, max_run))
        logger.info("Login user")
        login(self.phone1, super_admin_email, super_admin_password, environment)
        assert self.phone1.check_elements(MainPage.element_list)

    def test_car_operations_020_search_vehicle_and_click(self):
        """Searching the vehicle and verifying the elements on the key creation screen"""
        logger.info("Search Vehicle")
        search_vehicle(self.phone1, vehicle_name)
        assert self.phone1.check_elements(KeyCreation.element_list, timeout=60)
        self.phone1.tap(KeyCreation.back_button)
        self.phone1.tap(MainPage.clear_button)
        self.phone1.tap(MainPage.clear_button)

    def test_car_operations_030_key_creation_and_revocation(self):
        """Creating and Revoking the virtual key.
           Implementing test case id: C20442947 (Create VK with phone)"""
        logger.info("virtual key creation and revocation")
        vk_creation(self.phone1, vehicle_name)
        assert self.phone1.check_elements(CommandScreen.element_list, timeout=60)
        assert vehicle_name in self.phone1.get_text(CommandScreen.vehicle_title)
        vk_revoke(self.phone1, vehicle_name)
        assert self.phone1.check_elements(MainPage.element_list)
        time.sleep(15)
        try:
            assert validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[VK_CREATE])
            assert validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[VK_REVOKE])
        except AssertionError as assert_error:
            self.uart_i.save(clear_buffer=True)
            logger.info(self.uart_i.buffer)
            raise assert_error
        self.uart_i.clear_buffer()

    def test_car_operations_040_vk_create_revoke_5_times(self):
        """Creating and Revoking the virtual key 5 times.
           Implementing test case id: C20605399 (Create/revoked VK with phone 5 times with android)"""
        logger.info("virtual key creation and revocation 5 times")
        for run in range(5):
            self.test_car_operations_030_key_creation_and_revocation()
            logger.info("Run " + str(run + 1) + " is complete " + "-" * 25)

    def test_car_operations_050_vk_creation(self):
        """Creating the virtual key.
                   Implementing test case id: C20404647 (Set default State)"""
        vk_creation(self.phone1, vehicle_name)
        time.sleep(10)
        self.phone1.tap(CommandScreen.fab_menu)
        assert self.phone1.check_elements(FabMenu.element_list, timeout=120)
        self.phone1.tap(CommandScreen.fab_menu)

    def test_car_operations_060_lock(self):
        """Creating virtual key and locking the car. Implementing test case id: C20398383 (Vehicle Lock)"""
        logger.info("vehicle lock")
        self.phone1.tap(CommandScreen.lock_button)
        time.sleep(self.phone1.default_timing)
        try:
            assert validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[Vehicle_LOCK])
        except AssertionError as assert_error:
            self.uart_i.save(clear_buffer=True)
            logger.info(self.uart_i.buffer)
            raise assert_error
        self.uart_i.clear_buffer()

    def test_car_operations_070_unlock(self):
        """Unlocking the car. Implementing test case id: C20398382 (Vehicle Unlock)"""
        logger.info("vehicle unlock")
        self.phone1.tap(CommandScreen.unlock_button)
        time.sleep(self.phone1.default_timing)
        try:
            assert validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[Vehicle_UNLOCK])
        except AssertionError as assert_error:
            self.uart_i.save(clear_buffer=True)
            logger.info(self.uart_i.buffer)
            raise assert_error
        self.uart_i.clear_buffer()

    def test_car_operations_080_open_trunk(self):
        """Open the trunk of the car. Implementing test case id: C20398385 (Vehicle Trunk)"""
        logger.info("Trunk Open")
        self.phone1.tap(CommandScreen.trunk_icon)
        time.sleep(self.phone1.default_timing)
        try:
            assert validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[Vehicle_Open_Trunk])
        except AssertionError as assert_error:
            self.uart_i.save(clear_buffer=True)
            logger.info(self.uart_i.buffer)
            raise assert_error

    def test_car_operations_090_flash_light(self):
        """Flashing the light of the car. Implementing test case id: C21073899 (Vehicle Flash Lights)"""
        logger.info("Flash Light")
        self.phone1.tap(CommandScreen.fab_menu)
        self.phone1.tap(FabMenu.flash_lights_button)
        time.sleep(self.phone1.default_timing)
        try:
            assert validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[Vehicle_Flash_Light])
        except AssertionError as assert_error:
            self.uart_i.save(clear_buffer=True)
            logger.info(self.uart_i.buffer)
            raise assert_error

    def test_car_operations_100_auth_start_enable(self):
        """Enable Auth Start of the car. Implementing test case id: C20398387 (Enable Engine Start)"""
        logger.info("Enable Engine Start")
        self.phone1.tap(CommandScreen.auth_start_icon)
        time.sleep(self.phone1.default_timing)
        try:
            assert validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[Vehicle_Enable_Engine_Start])
        except AssertionError as assert_error:
            self.uart_i.save(clear_buffer=True)
            logger.info(self.uart_i.buffer)
            raise assert_error
        self.uart_i.clear_buffer()

    def test_car_operations_110_auth_start_disable(self):
        """Disable Auth Start of the car. Implementing test case id: C20398388 (Disable Engine Start)"""
        logger.info("Disable Engine Start")
        self.phone1.tap(CommandScreen.auth_start_icon)
        time.sleep(self.phone1.default_timing)
        try:
            assert validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[Vehicle_Disable_Engine_Start])
        except AssertionError as assert_error:
            self.uart_i.save(clear_buffer=True)
            logger.info(self.uart_i.buffer)
            raise assert_error
        self.uart_i.clear_buffer()

    def test_car_operations_120_lock_5_times(self):
        """Locking the car for 5 times. Implementing test case id: C20605394 (Vehicle Lock with android 5 times without failed)"""
        logger.info("Locking doors 5 times")
        for run in range(5):
            self.test_car_operations_060_lock()
            logger.info("Run " + str(run + 1) + " is complete " + "-" * 25)

    def test_car_operations_130_unlock_5_times(self):
        """Unlocking the car for 5 times. Implementing test case id: C20605393 (Vehicle Unlock with android 5 times without failed)"""
        logger.info("unlocking doors 5 times")
        for run in range(5):
            self.test_car_operations_070_unlock()
            logger.info("Run " + str(run + 1) + " is complete " + "-" * 25)

    def test_car_operations_140_enable_and_disable_engine_start_5_times(self):
        """Enabling and disabling the engine of the car for 5 times. Implementing test case id: C20605418 and C20605419"""
        logger.info("Engine start and stop 5 times")
        for run in range(5):
            self.test_car_operations_100_auth_start_enable()
            self.test_car_operations_110_auth_start_disable()
            logger.info("Run " + str(run + 1) + " is complete " + "-" * 25)

    def test_car_operations_150_sms_api_remote_assistance_lock_command(self):
        """Locking the car from backend. Implementing test case id: C20605405 (Backend vehicle lock (SMS))"""
        logger.info("Vehicle lock via SMS")
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["LOCK"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(self.phone1.default_timing)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"
        time.sleep(self.phone1.default_timing)
        try:
            assert validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[Vehicle_LOCK])
        except AssertionError as assert_error:
            self.uart_i.save(clear_buffer=True)
            logger.info(self.uart_i.buffer)
            raise assert_error

    def test_car_operations_160_sms_api_remote_assistance_unlock_command(self):
        """Unlocking the car from backend. Implementing test case id: C20605404 (Backend vehicle unlock (SMS))"""
        logger.info("Vehicle unlock via SMS")
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["UNLOCK"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(self.phone1.default_timing)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"
        time.sleep(self.phone1.default_timing)
        try:
            assert validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[Vehicle_UNLOCK])
        except AssertionError as assert_error:
            self.uart_i.save(clear_buffer=True)
            logger.info(self.uart_i.buffer)
            raise assert_error

    def test_car_operations_170_sms_api_remote_assistance_trunk_command(self):
        """Releasing the trunk from backend. Implementing test case id: C20398495 (Backend vehicle trunk release)"""
        logger.info("Trunk release via SMS")
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["TRUNK_ACTION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(self.phone1.default_timing)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"
        time.sleep(self.phone1.default_timing)
        try:
            assert validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[Vehicle_Open_Trunk])
        except AssertionError as assert_error:
            self.uart_i.save(clear_buffer=True)
            logger.info(self.uart_i.buffer)
            raise assert_error

    def test_car_operations_180_sms_api_remote_assistance_engine_enable_command(self):
        """Unlocking the car from backend. Implementing test case id: C20398496 (Backend vehicle auth start enable)"""
        logger.info("Engine start enable via SMS")
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["ENABLE_IGNITION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(self.phone1.default_timing)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"
        time.sleep(self.phone1.default_timing)
        try:
            assert validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[Vehicle_Enable_Engine_Start])
        except AssertionError as assert_error:
            self.uart_i.save(clear_buffer=True)
            logger.info(self.uart_i.buffer)
            raise assert_error

    def test_car_operations_190_sms_api_remote_assistance_engine_disable_command(self):
        """Unlocking the car from backend. Implementing test case id: C21077999 (Backend vehicle auth start disable)"""
        logger.info("Engine start disable via SMS")
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["DISABLE_IGNITION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(self.phone1.default_timing)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"
        time.sleep(self.phone1.default_timing)
        try:
            assert validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[Vehicle_Disable_Engine_Start])
        except AssertionError as assert_error:
            self.uart_i.save(clear_buffer=True)
            logger.info(self.uart_i.buffer)
            raise assert_error

    def test_car_operations_200_sms_api_remote_assistance_Unlock_engine_enable_command(self):
        """Unlocking the car from backend and enabling the engine start. Implementing test case id: C20398497 (Backend vehicle unlock and enable)"""
        logger.info("Unlock the vehicle and engine start enable via SMS")
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["UNLOCK", "ENABLE_IGNITION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(self.phone1.default_timing)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"
        time.sleep(self.phone1.default_timing)
        try:
            assert validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[Vehicle_UNLOCK])
            assert validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[Vehicle_Enable_Engine_Start])
        except AssertionError as assert_error:
            self.uart_i.save(clear_buffer=True)
            logger.info(self.uart_i.buffer)
            raise assert_error

    def test_car_operations_210_vk_revoke(self):
        """Revoking the virtual key.
                   Implementing test case id: C20398333 (Revoke VK from backend)"""
        vk_revoke(self.phone1, vehicle_name)

    def test_car_operations_220_vk_creation_without_open_door(self):
        """Creating the virtual key without open door option.
                   Implementing test case id: C20398328 (Create VK without open door option)"""
        search_vehicle(self.phone1, vehicle_name)
        time.sleep(5)
        self.phone1.tap(KeyCreation.unlock_icon)
        self.phone1.tap(KeyCreation.create_key)
        time.sleep(self.phone1.default_timing)
        try:
            assert not self.phone1.tap(CommandScreen.unlock_button)
        except AssertionError as assert_error:
            raise assert_error
        finally:
            self.test_car_operations_210_vk_revoke()

    def test_car_operations_230_vk_creation_without_closed_door(self):
        """Creating the virtual key without close door option.
                   Implementing test case id: C20398329 (Create VK without close door option)"""
        search_vehicle(self.phone1, vehicle_name)
        time.sleep(5)
        self.phone1.tap(KeyCreation.lock_icon)
        self.phone1.tap(KeyCreation.create_key)
        time.sleep(self.phone1.default_timing)
        try:
            assert not self.phone1.tap(CommandScreen.lock_button)
        except AssertionError as assert_error:
            raise assert_error
        finally:
            self.test_car_operations_210_vk_revoke()

    def test_car_operations_240_vk_creation_without_open_trunk_door(self):
        """Creating the virtual key without open trunk option.
                   Implementing test case id: C20398330 (Create VK without open trunk option)"""
        search_vehicle(self.phone1, vehicle_name)
        self.phone1.tap(KeyCreation.trunk_icon)
        self.phone1.tap(KeyCreation.create_key)
        time.sleep(self.phone1.default_timing)
        try:
            assert not self.phone1.tap(CommandScreen.trunk_icon)
        except AssertionError as assert_error:
            raise assert_error
        finally:
            self.test_car_operations_210_vk_revoke()

    def test_car_operations_250_vk_creation_without_start_engine(self):
        """Creating the virtual key without start engine option.
                   Implementing test case id: C20398331 (Create VK without start option)"""
        search_vehicle(self.phone1, vehicle_name)
        self.phone1.tap(KeyCreation.auth_start_icon)
        self.phone1.tap(KeyCreation.create_key)
        time.sleep(self.phone1.default_timing)
        try:
            time.sleep(self.phone1.default_timing)
            assert not self.phone1.tap(CommandScreen.auth_start_icon)
        except AssertionError as assert_error:
            raise assert_error
        finally:
            self.test_car_operations_210_vk_revoke()

    def test_car_operations_260_vk_creation_without_flash_light(self):
        """Creating the virtual key without flash light option.
                   Implementing test case id: C21078000 (Create VK without flash light option)"""
        search_vehicle(self.phone1, vehicle_name)
        self.phone1.tap(KeyCreation.flash_lights_icon)
        self.phone1.tap(KeyCreation.create_key)
        time.sleep(self.phone1.default_timing)
        try:
            self.phone1.tap(CommandScreen.fab_menu)
            assert not self.phone1.tap(FabMenu.flash_lights_button)
        except AssertionError as assert_error:
            raise assert_error
        finally:
            self.test_car_operations_210_vk_revoke()
