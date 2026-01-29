import datetime
import time

import pytest
import logging
import os

from rpi_bench.libs.appium.accessp_pages import CommandScreen, MainPage
from rpi_bench.libs.appium.lib_appium import Phone, BaseTestClass
from rpi_bench.libs.lib_uart2 import UartInterface
from rpi_bench.test_api.access_plus_appium.key_operations_utils import vk_creation, vk_revoke
from rpi_bench.test_api.access_plus_appium.serial_utils import validating_uart_logs, ACCM_UART_KEYWORDS, get_com_port, \
    TLS_Error
from rpi_bench.test_api.access_plus_appium.vehicle_search_utils import search_vehicle
from rpi_bench.test_api.tools import get_bench_configuration, get_environment_configuration
from rpi_bench.test_api.access_plus_appium.login_utils import login
from rpi_bench.test_collections.accm.test_accm_appium_car_operations import UART_KEYWORDS
from rpi_bench.libs.lib_bugfender import BugFenderAPI
from rpi_bench.test_api.extract_logs_accessPlus import analyze_file

bench_config = get_bench_configuration()
env_config = get_environment_configuration()
logger = logging.getLogger("ACCM_Time_Connection")

environment = env_config['environment']
super_admin_email = bench_config['ACCM_Login.Super_admin.email']
super_admin_password = bench_config['ACCM_Login.Super_admin.password']
vehicle_name = bench_config['MOBILE_AUTOMATION_DATA.Main_Page.vehicle_search_string']
UART_PORT = get_com_port()
UART_KEYWORDS = bench_config.get(ACCM_UART_KEYWORDS)
logger.info(f"Uart Port : {UART_PORT}")
Run = env_config['No_Of_Run']

max_run = 1

bugfender_start_time = None
bugfender_end_time = None


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
    def test_10_multiple_times_VK_creation_and_revocation(self, run):
        """Login and perform multiple times VK creation and revocation"""
        logger.info("Run {}/{}".format(run + 1, max_run))
        logger.info("VK create/revoke")
        global bugfender_start_time
        bugfender_start_time = (datetime.datetime.utcnow()).isoformat() + "Z"
        login(self.phone1, super_admin_email, super_admin_password, environment)
        start_time = datetime.datetime.now()
        for run in range(Run):
            vk_creation(self.phone1, vehicle_name)
            time.sleep(self.phone1.default_timing)
            assert self.phone1.check_elements(CommandScreen.element_list, timeout=60)
            self.phone1.tap(CommandScreen.lock_button)
            vk_revoke(self.phone1, vehicle_name)
            assert self.phone1.check_elements(MainPage.element_list)
            logger.info("Run " + str(run + 1) + " is complete " + "-" * 25)
            response = validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[TLS_Error])
            if response:
                print(self.uart_i.buffer)
                self.uart_i.save(clear_buffer=True)
            self.uart_i.clear_buffer()
        print("Time Taken in complete test case execution:", datetime.datetime.now() - start_time)

    def test_20_multiple_times_VK_disconnection_and_reconnection(self):
        """Perform multiple times VK disconnection and reconnection"""
        logger.info("VK disconnection/connection")
        vk_creation(self.phone1, vehicle_name)
        time.sleep(5)
        start_time = datetime.datetime.now()
        for run in range(Run):
            self.phone1.tap(CommandScreen.back_button)
            self.phone1.tap(MainPage.clear_button)
            self.phone1.tap(MainPage.clear_button)
            assert self.phone1.check_elements(MainPage.element_list)
            search_vehicle(self.phone1, vehicle_name)
            assert self.phone1.check_elements(CommandScreen.element_list, timeout=60)
            self.phone1.tap(CommandScreen.lock_button)
            logger.info("Run " + str(run + 1) + " is complete " + "-" * 25)
            if validating_uart_logs(self.uart_i.buffer, UART_KEYWORDS[TLS_Error]) is True:
                print(self.uart_i.buffer)
                self.uart_i.save(clear_buffer=True)
                self.uart_i.clear_buffer()
            print("Time Taken in complete test case execution:", datetime.datetime.now() - start_time)
        time.sleep(150)

    def test_30_restart_app(self):
        """Restart the application and perform some activity"""
        self.phone1.close_app()
        self.phone1.launch_app()
        search_vehicle(self.phone1, vehicle_name)
        time.sleep(150)
        global bugfender_end_time
        bugfender_end_time = (datetime.datetime.utcnow()).isoformat() + "Z"
        print(bugfender_end_time)

    def test_40_download_bugfender_logs(self):
        """Download the bugfender logs and analyze the logs using time connection scripts"""
        bugfender_obj = BugFenderAPI(env_config['Platform'])
        log_filepath = f"./../../reports/downloaded_logs_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        log_filepath = os.path.abspath(log_filepath)
        bugfender_obj.download_app_logs(bugfender_start_time, bugfender_end_time, filepath=log_filepath)
        analyze_file(log_filepath, env_config['Platform'])








