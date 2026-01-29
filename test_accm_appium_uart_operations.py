import logging
import time

import pytest
from rpi_bench.libs.accm.accm_manager import get_accm_port

from rpi_bench.libs.appium.lib_appium import BaseTestClass
from rpi_bench.libs.lib_uart2 import UartInterface
from rpi_bench.test_api.access_plus_appium.serial_utils import get_com_port
from rpi_bench.test_api.tools import get_bench_configuration, get_environment_configuration
from rpi_bench.test_api.vk_tools import VkTools

logger = logging.getLogger("ACCM_campaign")
max_run = 1
bench_config = get_bench_configuration()
env_config = get_environment_configuration()
UART_PORT = get_com_port()
logger.info(f"Uart Port : {UART_PORT}")
vk_tools = VkTools(env_config)

test_vehicle_vin = bench_config['DATA.vehicle_vin']


@pytest.mark.usefixtures("update_results_to_jira")
class TestUartOperations(BaseTestClass):

    def setup_method(self):
        self.uart_i = UartInterface(UART_PORT)
        self.uart_i.start()

    def teardown_method(self):
        self.uart_i.stop()

    @pytest.mark.parametrize("run", list(range(0, max_run)))
    def test_uart_operations_010_target_firmware_version(self, run):
        """
        Getting the current firmware version of ACCM via UART
        """
        logger.info("Run {}/{}".format(run+1, max_run))
        logger.info("Current firmware version on target")
        self.uart_i.clear_buffer()
        response = self.uart_i.sendnoresponse('versions get rabbit')
        logger.info(self.uart_i.buffer)
        logger.info(response)

    def test_uart_operations_020_battery_voltage_check(self):
        """
        Verify the battery voltage via backend and ACCM
        """
        logger.info("verify battery voltage")
        self.uart_i.sendnoresponse('synthesis no')
        start_timestamp = (time.time()).__round__() - 80000
        resp = vk_tools.keycore_requests.get_vehicle_telemetry(vin=test_vehicle_vin,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'],
                                                               start_timestamp=start_timestamp)

        assert vk_tools.keycore_requests.cloud.response_code == 200
        battery = resp.get("telemetry")[0].get("battery").get("value")
        battery_resp = round(battery, 1)
        time.sleep(30)
        buffer_list = self.uart_i.buffer.split("\n")
        accm_resp = ""
        for line in buffer_list:
            if "battery_verifier:" in line:
                accm_resp = float(line.split(",")[1].split(":")[1][0:5])
                break
        try:
            assert accm_resp == battery_resp
        except AssertionError as assert_error:
            self.uart_i.save(clear_buffer=True)
            logger.info(self.uart_i.buffer)
            raise assert_error
        self.uart_i.clear_buffer()
