"""
requirements :
=============
    * bench os : (ios / windows)
    *
    *

other infos :
=============


"""

import logging
import os
import random
from copy import deepcopy
from threading import Thread
import pytest
import time

from rpi_bench.test_api.customer_api.client_device_utils import pagination_info, device_template, \
    device_creation_template, nfc_device_creation_template, nfc_device_template
from rpi_bench.test_api.customer_api.vehicle_utils import vehicle_payload, electric_vehicle_payload, vehicle_id_list, \
    device_serial_list, journal_api_max_limit, max_limit_cd_veh_vk, test_bench_vehicle_id, \
    vehicles_get_template, vehicle_vin, vehicle_payload_with_no_device, device_info_payload
from rpi_bench.test_api.customer_api.vk_utils import vk_creation_template, \
    vk_get_template, vk_update_template
from rpi_bench.test_api.vk_tools import VkTools
from rpi_bench.test_api.tools import get_environment_configuration, get_env_organisation_item

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
env_config = get_environment_configuration()
org_info = env_config.get("customer_api_org_preference")
vk_tools = VkTools(env_config, org_info)
os.environ["VK_CALL_FILE_NAME"] = os.path.basename(__file__)

from rpi_bench.test_api.customer_api.telemetry_utils import send_telemetry_ecu_custom, sms_api_post_template, \
    sms_api_get_template, ev_telemetry_template, telemetry_template, send_telemetry_data_logger_ecu

custom_api_key = get_env_organisation_item("apikey", "org1")
custom_secret_key = get_env_organisation_item("secretkey", "org1")


# for skip wrong tests with specific env
def is_us_preprod():
    return env_config["TEST_ENVIRONMENT"] == "us_preprod-dev"


def is_keycore_dev():
    return env_config["TEST_ENVIRONMENT"] == "us_keycore-dev"


def is_debug2():
    return env_config["TEST_ENVIRONMENT"] == "debug2"


result_to_jira = get_environment_configuration().get("NEED_RESULTS_IN_JIRA", default=False)

VK_ALREADY_CREATED = False
DEMO_MODE = False
VEHICLE_PAYLOAD = vehicle_payload
VEHICLE_PAYLOAD_WITH_NO_DEVICE = vehicle_payload_with_no_device
ELECTRIC_VEHICLE_PAYLOAD = electric_vehicle_payload

vk_tools.keycore_requests.kc_info['new_cd_id'] = "a" + str(random.randint(1000000, 9999999))


@pytest.mark.usefixtures("update_results_to_jira")
class TestACCMCustomerAPI:

    def test_create_client_device_010_wrong_authentication(self):
        """
        Check that the API returns the correct errors when authentication is incorrect
        """
        payload = {
            "dummy": "dummy"
        }
        vk_tools.check_authentication_errors(method="POST", endpoint="clientdevices", body=payload)

    def test_get_client_device_020_wrong_authentication(self):
        """
        Check that the API returns the correct errors when authentication is incorrect
        """
        vk_tools.check_authentication_errors(method="GET", endpoint="clientdevices")

    def test_create_vehicle_030_wrong_authentication(self):
        """
        Check that the API returns the correct errors when authentication is incorrect
        """
        payload = {
            "dummy": "dummy"
        }
        vk_tools.check_authentication_errors(method="POST", endpoint="vehicles", body=payload)

    def test_get_list_vehicles_040_wrong_authentication(self):
        """
        Check that the API returns the correct errors when authentication is incorrect
        """
        vk_tools.check_authentication_errors(method="GET", endpoint="vehicles")

    def test_create_vk_050_wrong_authentication(self):
        """
        Check that the API returns the correct errors when authentication is incorrect
        """
        payload = {
            "dummy": "dummy"
        }
        vk_tools.check_authentication_errors(method="POST", endpoint="virtualkeys", body=payload)

    def test_get_vk_060_wrong_authentication(self):
        """
        Check that the API returns the correct errors when authentication is incorrect
        """
        vk_tools.check_authentication_errors(method="GET", endpoint="virtualkeys")

    def test_update_vk_070_wrong_authentication(self):
        """
        Check that the API returns the correct errors when authentication is incorrect
        """
        payload = {
            "dummy": "dummy"
        }
        vk_tools.check_authentication_errors(method="PUT", endpoint="virtualkeys/fakeid", body=payload)

    def test_get_telemetry_journal_080_wrong_authentication(self):
        """
        Check that the API returns the correct errors when authentication is incorrect
        KAAS-19293 - as per this bug there is mismatch in error id & error messages. Since kaas is in maintenance,
        no fix is planned so will be updating the script with current behavior
        """
        vk_tools.check_authentication_errors(method="GET", endpoint="vehicles/all/telemetry/journal")

    def test_get_telemetry_merged_090_wrong_authentication(self):
        """
        Check that the API returns the correct errors when authentication is incorrect
        KAAS-19293 - as per this bug there is mismatch in error id & error messages. Since kaas is in maintenance,
        no fix is planned so will be updating the script with current behavior
        """
        timestamp = (time.time()).__round__() - 290
        vk_tools.check_authentication_errors(method="GET", endpoint="vehicles/all/telemetry/merged",
                                             params="?startTimestamp={}".format(timestamp))

    def test_unlink_vehicle_with_vin_100_wrong_authentication(self):
        """
        Check that the API returns the correct errors when authentication is incorrect
        """
        vk_tools.check_authentication_errors(method="DELETE", endpoint="vehicles/fakeid/devices/fakeserial")

    def test_unlink_vehicle_with_id_110_wrong_authentication(self):
        """
        Check that the API returns the correct errors when authentication is incorrect
        """
        vk_tools.check_authentication_errors(method="DELETE", endpoint="vehicles/vin/fakevin/devices/fakeserial")

    def test_disable_vehicle_120_wrong_authentication(self):
        """
        Check that the API returns the correct errors when authentication is incorrect
        """
        payload = {
            "dummy": "dummy"
        }
        vk_tools.check_authentication_errors(method="POST", endpoint="vehicles/fakeid/disable", body=payload)

    def test_disable_client_device_130_wrong_authentication(self):
        """
        Check that the API returns the correct errors when authentication is incorrect
        """
        payload = {
            "dummy": "dummy"
        }
        vk_tools.check_authentication_errors(method="POST", endpoint="clientdevices/fakeserial/disable", body=payload)

    def test_create_nfc_140_wrong_authentication_nfc(self):
        """
        Check that the API returns the correct errors when authentication is incorrect
        """
        payload = {
            "dummy": "dummy"
        }
        vk_tools.check_authentication_errors(method="POST", endpoint="clientdevices/nfc", body=payload)

    def test_create_nfc_150_wrong_authentication_nfc_bulk(self):
        """
        Check that the API returns the correct errors when authentication is incorrect
        """
        random_string = "a" + str(random.randint(1000000, 9999999))
        vk_tools.keycore_requests.kc_info['nfc_tag_ids_list'].append(random_string)
        payload = {
            "nfcTagIds": [random_string]
        }
        vk_tools.check_authentication_errors(method="POST", endpoint="clientdevices/nfc/bulk", body=payload)

    def test_client_device_010_create_client_device(self):
        """
        Create a client device and check that the response contains the correct fields
        """
        new_cd_id = vk_tools.keycore_requests.kc_info['new_cd_id']
        payload = {
            "id": new_cd_id,
            "enabled": True,
            "label": "new_cd_label",
        }
        resp = vk_tools.keycore_requests.create_client_device(payload=payload, save_response_data=True)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(device_creation_template, True)

        assert resp.get("id") == new_cd_id
        assert resp.get("enabled") is True
        assert resp.get("label") == "new_cd_label"

    def test_client_device_011_create_client_device_nfc(self):
        """
        Create a client device and check that the response contains the correct fields
        """
        random_string = "a" + str(random.randint(1000000, 9999999))
        vk_tools.keycore_requests.kc_info['nfc_tag_id'] = random_string
        payload = {
            "NFCTagId": vk_tools.keycore_requests.kc_info['nfc_tag_id'],
            "NFCAlgorithm": "0",
            "NFCPage": 0,
            "NFCBlock": 1,
            "enabled": True
        }
        resp = vk_tools.keycore_requests.create_nfc_client_device(payload=payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.keycore_requests.kc_info['nfc_client_device_id'] = resp.get("id")
        vk_tools.assert_correct_field(nfc_device_creation_template, True)
        assert resp.get("NFC_tag_id") == random_string
        assert resp.get("enabled") is True

    def test_client_device_012_create_nfc_tag_id_missing(self):
        """
        Create a client device without nfc tag id or empty tag id and check that the response contains the correct fields
        """
        payload = {
            "NFCTagId": "",
            "NFCAlgorithm": "0",
            "NFCPage": 0,
            "NFCBlock": 1,
            "enabled": True
        }
        resp = vk_tools.keycore_requests.create_nfc_client_device(payload=payload)
        logger.info(vk_tools.keycore_requests.cloud.response_body)
        assert vk_tools.keycore_requests.cloud.response_code == 400
        assert resp.get("errorId") == 1101
        assert resp.get("message") == "Required field NFC Tag ID is missing."

    def test_client_device_013_create_nfc_tag_id_invalid(self):
        """
        Create a client device with invalid nfc tag id and check that the response contains the correct fields
        """
        payload = {
            "NFCTagId": 100,
            "NFCAlgorithm": "0",
            "NFCPage": 0,
            "NFCBlock": 1,
            "enabled": True
        }
        resp = vk_tools.keycore_requests.create_nfc_client_device(payload=payload)
        assert vk_tools.keycore_requests.cloud.response_code == 400
        assert resp.get("errorId") == 1102
        assert resp.get("message") == "Field is invalid"

    def test_client_device_014_create_nfc_already_exist(self):
        """
        Create a client device with already existing nfc tag id and check that the response contains the correct fields
        """
        payload = {
            "NFCTagId": vk_tools.keycore_requests.kc_info['nfc_tag_id'],
            "NFCAlgorithm": "0",
            "NFCPage": 0,
            "NFCBlock": 1,
            "enabled": True
        }
        resp = vk_tools.keycore_requests.create_nfc_client_device(payload=payload)
        assert vk_tools.keycore_requests.cloud.response_code == 409
        assert resp.get("errorId") == 1104
        assert resp.get("message") == "Cannot create resource. ID already exists"

    def test_client_device_015_create_client_device_nfc_bulk(self):
        """
        Create a nfc client devices in bulk and check that the response contains the correct fields
        """
        for i in range(3):
            random_string = "a" + str(random.randint(1000000, 9999999))
            vk_tools.keycore_requests.kc_info['nfc_tag_ids_list'].append(random_string)
        print(vk_tools.keycore_requests.kc_info['nfc_tag_ids_list'])
        payload = {
            "nfcTagIds": vk_tools.keycore_requests.kc_info['nfc_tag_ids_list']
        }
        resp = vk_tools.keycore_requests.create_nfc_client_device_bulk(payload=payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert vk_tools.keycore_requests.kc_info['nfc_tag_ids_list'] == resp.get("nfcTagIdsAdded")
        assert len(resp.get("errors")) == 0

    def test_client_device_016_bulk_nfc_tag_id_missing(self):
        """
        Create a client device and check that the response contains the correct fields
        """
        payload = {
            "nfcTagIds": ["", ""]
        }
        resp = vk_tools.keycore_requests.create_nfc_client_device_bulk(payload=payload)
        logger.info(vk_tools.keycore_requests.cloud.response_body)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("nfcTagIdsAdded") == []
        assert resp.get("errors") == ["Bad format: ", "Bad format: "]

    def test_client_device_017_bulk_nfc_tag_id_invalid(self):
        """
        Create a client device nfc in bulk with invalid tag ids and check that the response contains the correct fields
        """
        payload = {
            "nfcTagIds": ["100aaaaaaabbbbbbbbbbccccccccccd", "101aaaaaaabbbbbbbbbbccccccccccd"]
        }
        resp = vk_tools.keycore_requests.create_nfc_client_device_bulk(payload=payload)
        logger.info(vk_tools.keycore_requests.cloud.response_body)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("nfcTagIdsAdded") == []
        assert "Bad format" in resp.get("errors")[0]

    def test_client_device_018_temp_disable_client_device_nfc(self):
        """
        Temp disable the nfc and check the response
        """
        nfc_client_device_id = vk_tools.keycore_requests.kc_info['nfc_client_device_id']
        resp = vk_tools.keycore_requests.nfc_temp_disable_enable_client_device(state="disable",
                                                                               client_device_id=nfc_client_device_id)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("id") == vk_tools.keycore_requests.kc_info['nfc_client_device_id']

    def test_client_device_019_temp_enable_client_device_nfc(self):
        """
        Temp enable the nfc and check the response
        """
        nfc_client_device_id = vk_tools.keycore_requests.kc_info['nfc_client_device_id']
        resp = vk_tools.keycore_requests.nfc_temp_disable_enable_client_device(state="enable",
                                                                               client_device_id=nfc_client_device_id)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("id") == vk_tools.keycore_requests.kc_info['nfc_client_device_id']

    def test_client_device_020_get_client_device(self):
        """
        Get a client device and check that the response body contains the correct fields
        """
        vk_tools.keycore_requests.get_client_device()
        assert vk_tools.keycore_requests.cloud.response_code == 200

        vk_tools.assert_correct_field(device_template, True)

    def test_client_device_021_get_client_device_mobile_v2(self):
        """
        Get a client device and check that the response body contains the correct fields
        """
        vk_tools.keycore_requests.get_client_device_mobile_v2(limit=4)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(device_template, True)

    def test_client_device_021_get_client_device_nfc_v2(self):
        """
        Get a client device and check that the response body contains the correct fields
        """
        vk_tools.keycore_requests.get_client_device_nfc_v2(limit=50, offset=10)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(nfc_device_template, True)

    def test_client_device_022_get_client_device_mobile_v2_status(self):
        """
        Get a client device with query paramter and check that the response body contains the correct fields
        """

        vk_tools.keycore_requests.get_client_device_mobile_v2(status="disabled",
                                                              custom_apikey=custom_api_key,
                                                              custom_secretkey=custom_secret_key)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(device_template, True)
        resp = vk_tools.keycore_requests.get_client_device_mobile_v2(status="enabled",
                                                                     custom_apikey=custom_api_key,
                                                                     custom_secretkey=custom_secret_key)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("clientdevices")[0].get("enabled") is True

    def test_client_device_030_get_client_device_inputs(self):
        """
        Get a client device with inputs parameters set, and check that they are effective
        """
        resp = vk_tools.keycore_requests.get_client_device(limit=3)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("clientdevices")) == 3
        assert resp.get("paginationInfo").get("limit") == 3
        assert resp.get("paginationInfo").get("offset") == 0
        id3 = resp.get("clientdevices")[2].get("id")

        resp = vk_tools.keycore_requests.get_client_device(limit=2, offset=2)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("clientdevices")) == 2
        assert resp.get("paginationInfo").get("limit") == 2
        assert resp.get("paginationInfo").get("offset") == 2
        assert id3 == resp.get("clientdevices")[0].get("id")

    def test_client_device_040_get_client_device_with_max_limit(self):
        """
        KAAS-15121 based on this bug
        Get a client device with max limit input parameter and validate the response
        """
        # Validating with Max limit
        resp = vk_tools.keycore_requests.get_client_device(limit=max_limit_cd_veh_vk)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("clientdevices")) == max_limit_cd_veh_vk
        assert resp.get("paginationInfo").get("limit") == max_limit_cd_veh_vk
        assert resp.get("paginationInfo").get("offset") == 0

    def test_client_device_050_get_client_device_with_max_limit_exceed(self):
        """
        KAAS-15121 based on this bug
        Get a client device with max limit exceed input parameter and validate the response
        """
        # Validating with Max limit exceed
        resp = vk_tools.keycore_requests.get_client_device(limit=max_limit_cd_veh_vk + 1)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("clientdevices")) == max_limit_cd_veh_vk
        assert resp.get("paginationInfo").get("limit") == max_limit_cd_veh_vk
        assert resp.get("paginationInfo").get("offset") == 0

    def test_client_device_060_get_client_device_with_negative_limit_offset(self):
        """
        KAAS-15121 based on this bug
        Get a client device with negative input and offset and validate the response
        """
        # Validating with negative limit and offset values
        resp = vk_tools.keycore_requests.get_client_device(limit=-10, offset=-10)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("clientdevices")) == 25
        assert resp.get("paginationInfo").get("limit") == 25
        assert resp.get("paginationInfo").get("offset") == 0

    def test_client_device_070_get_client_device_with_limit_equals_zero(self):
        """
        KAAS-15121 based on this bug
        Get a client device with limit=0 and validate the response
        """
        # Validating with limit=0
        resp = vk_tools.keycore_requests.get_client_device(limit=0)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("clientdevices")) == 25
        assert resp.get("paginationInfo").get("limit") == 25
        assert resp.get("paginationInfo").get("offset") == 0

    def test_client_device_080_get_client_device_with_pagination_info(self):
        """
        KAAS-15121 based on this bug
        Get a client device and validate pagination info
        """
        # Validating with max limit, offset=20 and checking pagination info details
        resp = vk_tools.keycore_requests.get_client_device(limit=max_limit_cd_veh_vk, offset=20)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("clientdevices")) == max_limit_cd_veh_vk
        assert resp.get("paginationInfo").get("limit") == max_limit_cd_veh_vk
        assert resp.get("paginationInfo").get("offset") == 20
        current_page_api_data = resp.get("paginationInfo").get("currentPage")
        next_page_api_data = resp.get("paginationInfo").get("nextPage")
        previous_page_api_data = resp.get("paginationInfo").get("previousPage")
        current_page = "/1/clientdevices?limit={}".format(max_limit_cd_veh_vk) + "\u0026offset=20"
        next_page = "/1/clientdevices?limit={}".format(max_limit_cd_veh_vk) + "\u0026offset={}".format(
            max_limit_cd_veh_vk + 20)
        previous_page = "/1/clientdevices?limit={}".format(max_limit_cd_veh_vk) + "\u0026offset=0"
        assert current_page_api_data == current_page
        assert next_page_api_data == next_page
        assert previous_page_api_data == previous_page

    def test_client_device_090_client_device_invalid_push_provider_id(self):
        """
        Validate error id and message for create client device with invalid push provider id
        """
        payload = {
            "id": "dummy_id",
            "enabled": True,
            "label": "new_cd_label",
            "pushProviderId": "dummy"
        }
        resp = vk_tools.keycore_requests.create_client_device(payload=payload, save_response_data=False)
        assert vk_tools.keycore_requests.cloud.response_code == 400
        assert resp.get("errorId") == 10010002
        assert resp.get("message") == "PushProviderId is not valid"

    def test_vehicle_010_create_vehicle(self):
        """
        Create a vehicle and check that the response body contains the correct fields
        Stores the vehicle id for next tests
        """
        vk_tools.keycore_requests.authenticate()
        vk_tools.keycore_requests.create_module_and_device_rabbit()

        VEHICLE_PAYLOAD["device"]["serialNumber"] = "{}".format(vk_tools.keycore_requests.kc_info['module_serial'])
        payload = VEHICLE_PAYLOAD.copy()

        resp = vk_tools.keycore_requests.create_vehicle_rabbit_device(payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.keycore_requests.vehicle.id = resp.get("id")
        vehicle_id_list.append(resp.get("id"))
        device_serial_list.append(resp.get("device").get("serialNumber"))
        assert resp.get("enabled") == VEHICLE_PAYLOAD["enabled"]
        assert resp.get("device").get("type") == VEHICLE_PAYLOAD["device"]["type"]
        assert resp.get("device").get("serialNumber") == VEHICLE_PAYLOAD["device"]["serialNumber"]
        assert resp.get("vin") == VEHICLE_PAYLOAD["vin"]
        assert resp.get("make") == VEHICLE_PAYLOAD["make"]
        assert resp.get("model") == VEHICLE_PAYLOAD["model"]
        assert resp.get("year") == int(VEHICLE_PAYLOAD["year"])
        assert resp.get("licensePlate") == VEHICLE_PAYLOAD["licensePlate"]
        assert resp.get("color") == VEHICLE_PAYLOAD["color"]
        assert resp.get("tank_capacity") == VEHICLE_PAYLOAD["tank_capacity"]
        assert resp.get("generation") == VEHICLE_PAYLOAD["generation"]
        assert resp.get("transmissionType") == VEHICLE_PAYLOAD["transmissionType"]
        assert resp.get("regionOfSale") == VEHICLE_PAYLOAD["regionOfSale"]
        assert resp.get("engineType") == VEHICLE_PAYLOAD["engineType"]
        assert resp.get("engineSize") == VEHICLE_PAYLOAD["engineSize"]
        assert resp.get("protocol") == VEHICLE_PAYLOAD["protocol"]

    def test_vehicle_020_create_vehicle_mandatory_fields_missing(self):
        """
        Create a vehicle without mandatory fields and check that an applicative error is returned
        """
        mandatory_fields = ["vin", "make", "model", "year", "engineType", "generation", "transmissionType"]
        for field in mandatory_fields:
            logger.info("testing mandatory field:" + field)
            payload = VEHICLE_PAYLOAD.copy()
            del payload[field]  # Removing the field from the payload
            resp = vk_tools.keycore_requests.create_vehicle_rabbit_device(payload)
            assert vk_tools.keycore_requests.cloud.response_code == 400
            assert resp.get("errorId") == 1103

    def test_vehicle_030_get_vehicle_by_id(self):
        """
        Get the vehicle created by test_create_vehicle and check that the response contains the correct fields
        """
        resp = vk_tools.keycore_requests.get_vehicle_by_id()
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("vehicles")) == 1
        vehicle = resp.get("vehicles")[0]
        assert vehicle.get("enabled") == VEHICLE_PAYLOAD["enabled"]
        assert vehicle.get("device").get("type") == VEHICLE_PAYLOAD["device"]["type"]
        assert vehicle.get("device").get("serialNumber") == VEHICLE_PAYLOAD["device"]["serialNumber"]
        assert vehicle.get("vin") == VEHICLE_PAYLOAD["vin"]
        assert vehicle.get("make") == VEHICLE_PAYLOAD["make"]
        assert vehicle.get("model") == VEHICLE_PAYLOAD["model"]
        assert vehicle.get("year") == VEHICLE_PAYLOAD["year"]
        assert vehicle.get("licensePlate") == VEHICLE_PAYLOAD["licensePlate"]
        assert vehicle.get("color") == VEHICLE_PAYLOAD["color"]
        assert vehicle.get("tank_capacity") == VEHICLE_PAYLOAD["tank_capacity"]
        assert vehicle.get("generation") == VEHICLE_PAYLOAD["generation"]
        assert vehicle.get("transmissionType") == VEHICLE_PAYLOAD["transmissionType"]
        assert vehicle.get("regionOfSale") == VEHICLE_PAYLOAD["regionOfSale"]
        assert vehicle.get("engineType") == VEHICLE_PAYLOAD["engineType"]
        assert vehicle.get("engineSize") == VEHICLE_PAYLOAD["engineSize"]
        assert vehicle.get("protocol") == VEHICLE_PAYLOAD["protocol"]

    def test_vehicle_040_get_list_vehicles(self):
        """
        Get the list of vehicles and check that the response code is 200
        """
        vk_tools.keycore_requests.get_vehicle_list()
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vehicles_get_template, True)

    def test_vehicle_050_get_list_vehicles_pagination(self):
        """
        Get the list of vehicles and check that the pagination is working properly
        """
        # First request with limit = 4:
        # {v1, v2, v3, v4}
        resp = vk_tools.keycore_requests.get_vehicle_list(limit=4)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("paginationInfo").get("limit") == 4
        assert resp.get("paginationInfo").get("offset") == 0
        v3 = resp.get("vehicles")[2].get("id")
        v4 = resp.get("vehicles")[3].get("id")

        # Second request with offset = 2 and limit = 2:
        # {v3, v4}
        resp = vk_tools.keycore_requests.get_vehicle_list(limit=2, offset=2)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("vehicles")) == 2
        assert resp.get("paginationInfo").get("limit") == 2
        assert resp.get("paginationInfo").get("offset") == 2
        assert resp.get("vehicles")[0].get("id") == v3
        assert resp.get("vehicles")[1].get("id") == v4

    def test_vehicle_060_get_list_vehicles_with_max_limit(self):
        """
        KAAS-15121 based on this bug
        Get vehicles with max limit input parameter and validate the response
        """
        # Validating with Max limit
        resp = vk_tools.keycore_requests.get_vehicle_list(limit=max_limit_cd_veh_vk)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        if resp.get("paginationInfo").get("total") > max_limit_cd_veh_vk:
            assert len(resp.get("vehicles")) == max_limit_cd_veh_vk
        else:
            assert len(resp.get("vehicles")) == resp.get("paginationInfo").get("total")
        assert resp.get("paginationInfo").get("limit") == max_limit_cd_veh_vk
        assert resp.get("paginationInfo").get("offset") == 0

    def test_vehicle_070_get_list_vehicles_with_max_limit_exceed(self):
        """
        KAAS-15121 based on this bug
        Get vehicles with with max limit exceed input parameter and validate the response
        """
        # Validating with Max limit exceed
        resp = vk_tools.keycore_requests.get_vehicle_list(limit=max_limit_cd_veh_vk + 1)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        if resp.get("paginationInfo").get("total") > max_limit_cd_veh_vk:
            assert len(resp.get("vehicles")) == max_limit_cd_veh_vk
        else:
            assert len(resp.get("vehicles")) == resp.get("paginationInfo").get("total")
        assert resp.get("paginationInfo").get("limit") == max_limit_cd_veh_vk
        assert resp.get("paginationInfo").get("offset") == 0

    def test_vehicle_080_get_list_vehicles_with_negative_limit_offset(self):
        """
        KAAS-15121 based on this bug
        Get vehicles with negative input and offset and validate the response
        """
        # Validating with negative limit and offset values
        resp = vk_tools.keycore_requests.get_vehicle_list(limit=-10, offset=-10)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("vehicles")) == 25
        assert resp.get("paginationInfo").get("limit") == 25
        assert resp.get("paginationInfo").get("offset") == 0

    def test_vehicle_090_get_list_vehicles_with_limit_equals_zero(self):
        """
        KAAS-15121 based on this bug
        Get vehicles with limit=0 and validate the response
        """
        # Validating with limit=0
        resp = vk_tools.keycore_requests.get_vehicle_list(limit=0)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("vehicles")) == 25
        assert resp.get("paginationInfo").get("limit") == 25
        assert resp.get("paginationInfo").get("offset") == 0

    def test_vehicle_100_get_list_vehicles_with_pagination_info(self):
        """
        KAAS-15121 based on this bug
        Get vehicles and validate pagination info
        """
        # Validating with max limit, offset=20 and checking pagination info details
        resp = vk_tools.keycore_requests.get_vehicle_list(limit=max_limit_cd_veh_vk, offset=20)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        if resp.get("paginationInfo").get("total") > (max_limit_cd_veh_vk + 20):
            assert len(resp.get("vehicles")) == max_limit_cd_veh_vk
        else:
            assert len(resp.get("vehicles")) == resp.get("paginationInfo").get("size")
        assert resp.get("paginationInfo").get("limit") == max_limit_cd_veh_vk
        assert resp.get("paginationInfo").get("offset") == 20
        current_page_api_data = resp.get("paginationInfo").get("currentPage")
        next_page_api_data = resp.get("paginationInfo").get("nextPage")
        previous_page_api_data = resp.get("paginationInfo").get("previousPage")
        current_page = "/1/vehicles?limit={}".format(max_limit_cd_veh_vk) + "\u0026offset=20"
        if resp.get("paginationInfo").get("total") > (max_limit_cd_veh_vk + 20):
            next_page = "/1/vehicles?limit={}".format(max_limit_cd_veh_vk) + "\u0026offset={}".format(
                max_limit_cd_veh_vk + 20)
        else:
            next_page = "/1/vehicles?limit={}".format(max_limit_cd_veh_vk) + "\u0026offset={}".format(
                resp.get("paginationInfo").get("size"))
        previous_page = "/1/vehicles?limit={}".format(max_limit_cd_veh_vk) + "\u0026offset=0"
        assert current_page_api_data == current_page
        assert next_page_api_data == next_page
        assert previous_page_api_data == previous_page

    def test_vehicle_110_get_list_vehicles_filter_vin(self):
        """
        Get the list of vehicles filter by the vin, and check that the vehicle just created is returned
        """
        resp = vk_tools.keycore_requests.get_vehicle_list(vin=VEHICLE_PAYLOAD["vin"])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vehicle_found = False
        for vehicle in resp.get("vehicles"):
            if vehicle["id"] == vk_tools.keycore_requests.vehicle.id:
                assert vehicle["vin"] == VEHICLE_PAYLOAD["vin"]
                assert vehicle["enabled"] == VEHICLE_PAYLOAD["enabled"]
                assert vehicle["device"].get("type") == VEHICLE_PAYLOAD["device"]["type"]
                assert vehicle["device"].get("serialNumber") == VEHICLE_PAYLOAD["device"]["serialNumber"]
                assert vehicle["vin"] == VEHICLE_PAYLOAD["vin"]
                assert vehicle["make"] == VEHICLE_PAYLOAD["make"]
                assert vehicle["model"] == VEHICLE_PAYLOAD["model"]
                assert vehicle["year"] == VEHICLE_PAYLOAD["year"]
                assert vehicle["licensePlate"] == VEHICLE_PAYLOAD["licensePlate"]
                assert vehicle["color"] == VEHICLE_PAYLOAD["color"]
                assert vehicle["protocol"] == VEHICLE_PAYLOAD["protocol"]
                vehicle_found = True
        assert vehicle_found

    def test_vehicle_111_update_vehicle(self):
        """
        update the vehicle by vehicle id and  check that the vehicle updated is returned
        """
        payload = {
            "licensePlate": "TESTING"
        }
        vk_tools.keycore_requests.update_vehicle(payload=payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200

    def test_vehicle_112_get_updated_vehicle_by_id(self):
        """
        Get the updated vehicle and check that the response code is 200 and the updated item is displaying in the response
        """
        payload = {
            "licensePlate": "TESTING"
        }
        vk_tools.keycore_requests.update_vehicle(payload=payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        resp = vk_tools.keycore_requests.get_vehicle_by_id()
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vehicles_get_template, True)
        vehicle = resp.get("vehicles")[0]
        assert vehicle.get("licensePlate") == "TESTING"

    def test_vehicle_113_update_vehicle_with_license_plate_empty(self):
        """
        update the vehicle by empty license plate and check that the vehicle updated is returned
        """
        payload = {
            "licensePlate": ""
        }
        vk_tools.keycore_requests.update_vehicle(payload=payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        resp = vk_tools.keycore_requests.get_vehicle_by_id()
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vehicles_get_template, True)
        vehicle = resp.get("vehicles")[0]
        assert vehicle.get("licensePlate") == ""

    def test_vehicle_114_update_vehicle_odometer_offset(self):
        """
        update the vehicle by license plate and customerOdometerOffset, check that the vehicle updated is returned
        """
        payload = {
            "licensePlate": "TESTING",
            "customerOdometerOffset": 100.12345
        }
        vk_tools.keycore_requests.update_vehicle(payload=payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        resp = vk_tools.keycore_requests.get_vehicle_by_id()
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vehicles_get_template, True)
        vehicle = resp.get("vehicles")[0]
        assert vehicle.get("licensePlate") == "TESTING"
        assert vehicle.get("customerOdometerOffset") == 100.12345

    def test_vehicle_115_update_vehicle_odometer_offset(self):
        """
        update the vehicle by customerOdometerOffset with int, check that the vehicle updated is returned
        """
        payload = {
            "customerOdometerOffset": 50
        }
        vk_tools.keycore_requests.update_vehicle(payload=payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        resp = vk_tools.keycore_requests.get_vehicle_by_id()
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vehicles_get_template, True)
        vehicle = resp.get("vehicles")[0]
        assert vehicle.get("customerOdometerOffset") == 50

    def test_vehicle_116_update_vehicle_odometer_offset(self):
        """
        update the vehicle by customerOdometerOffset with negative value, check that the vehicle updated is returned
        """
        payload = {
            "customerOdometerOffset": -35.123
        }
        vk_tools.keycore_requests.update_vehicle(payload=payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        resp = vk_tools.keycore_requests.get_vehicle_by_id()
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vehicles_get_template, True)
        vehicle = resp.get("vehicles")[0]
        assert vehicle.get("customerOdometerOffset") == -35.123

    def test_vehicle_117_update_vehicle_reset_odometer_offset(self):
        """
        update the vehicle by resetting customerOdometerOffset to 0, check that the vehicle updated is returned
        """
        payload = {
            "customerOdometerOffset": 0
        }
        vk_tools.keycore_requests.update_vehicle(payload=payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        resp = vk_tools.keycore_requests.get_vehicle_by_id()
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vehicles_get_template, True)
        vehicle = resp.get("vehicles")[0]
        assert vehicle.get("customerOdometerOffset") == 0

    def test_vk_010_nfc_create_vk(self):
        """
        Create a virtual key with nfc for the vehicle created by test_create_vehicle
        Check that the response contains the correct fields
        """
        start_date = int(time.time())
        end_date = start_date + 10 * 60
        payload = {
            "vehicleId": vk_tools.keycore_requests.vehicle.id,
            "clientDeviceId": vk_tools.keycore_requests.kc_info['nfc_client_device_id'],
            "validityStartDate": start_date,
            "validityEndDate": end_date,
            "clientDeviceNumberOfActionsAllowed": vk_tools.data['clientDeviceNumberOfActionsAllowed'],
            "clientDeviceActionsAllowedBitfield": vk_tools.data['clientDeviceActionsAllowedBitfield'],
            "userAuthentication": False,
            "label": "testing"
        }
        resp = vk_tools.keycore_requests.create_vk(payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_creation_template, True)
        vk = resp.get("virtualkey")
        vk_tools.keycore_requests.kc_info['nfc_vk_id'] = vk.get("id")
        assert vk.get("clientDeviceId") == payload["clientDeviceId"]
        assert vk.get("vehicleId") == payload["vehicleId"]
        assert vk.get("validityStartDate") == str(payload["validityStartDate"])
        assert vk.get("validityEndDate") == str(payload["validityEndDate"])
        assert vk.get("clientDeviceActionsAllowed") == []
        assert vk.get("clientDeviceActionsAllowedBitfield") == payload["clientDeviceActionsAllowedBitfield"]
        assert vk.get("clientDeviceNumberOfActionsAllowed") == payload["clientDeviceNumberOfActionsAllowed"]
        assert vk.get("label") == "testing"

    def test_vk_011_create_vk(self):
        """
        Create a virtual key for the vehicle created by test_create_vehicle
        Check that the response contains the correct fields
        """
        start_date = int(time.time())
        end_date = start_date + 10 * 60
        global vk_id
        vk_id = "create_vk_test_" + str(random.randint(1, 99999999999999999999))
        payload = {
            "id": vk_id,
            "vehicleId": vk_tools.keycore_requests.vehicle.id,
            "clientDeviceId": vk_tools.keycore_requests.kc_info['new_cd_id'],
            "validityStartDate": start_date,
            "validityEndDate": end_date,
            "clientDeviceNumberOfActionsAllowed": vk_tools.data['clientDeviceNumberOfActionsAllowed'],
            "clientDeviceActionsAllowedBitfield": vk_tools.data['clientDeviceActionsAllowedBitfield'],
            "userAuthentication": False,
            "generationInterval": 3600,
            "label": "testing"
        }
        resp = vk_tools.keycore_requests.create_vk(payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        vk_tools.assert_correct_field(vk_creation_template, True)
        vk = resp.get("virtualkey")
        assert vk.get("id") == payload["id"]
        assert vk.get("clientDeviceId") == payload["clientDeviceId"]
        assert vk.get("vehicleId") == payload["vehicleId"]
        assert vk.get("validityStartDate") == str(payload["validityStartDate"])
        assert vk.get("validityEndDate") == str(payload["validityEndDate"])
        assert vk.get("clientDeviceActionsAllowed") == []
        assert vk.get("clientDeviceActionsAllowedBitfield") == payload["clientDeviceActionsAllowedBitfield"]
        assert vk.get("clientDeviceNumberOfActionsAllowed") == payload["clientDeviceNumberOfActionsAllowed"]
        assert vk.get("userAuthentication") == payload["userAuthentication"]
        assert vk.get("generationInterval") == str(payload["generationInterval"])
        assert vk.get("label") == "testing"

    def test_vk_020_get_new_vks_with_id_filter(self):
        """
        Get the list of virtual keys filtered by VK ID and check that the response contains the correct fields
        """
        resp = vk_tools.keycore_requests.get_vk_ivkapi(id=vk_id)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)
        assert resp.get("virtualKeys")[0].get("id") == vk_id

    def test_vk_030_get_new_vks_with_status_created_filter(self):
        """
        Get the list of virtual keys with VK status as CREATED and check that the response contains the correct fields
        """
        resp = vk_tools.keycore_requests.get_vk_ivkapi(vk_status="CREATED")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)
        assert resp.get("virtualKeys")[0].get("status") == "CREATED"

    def test_vk_040_create_vk_mandatory_fields(self):
        """
        Create a virtual key without mandatory fields and check that an applicative error is returned
        """
        start_date = int(time.time())
        end_date = start_date + 10 * 60

        payload = {
            "vehicleId": vk_tools.keycore_requests.vehicle.id,
            "clientDeviceId": vk_tools.keycore_requests.client_device.id,
            "validityStartDate": start_date,
            "validityEndDate": end_date,
            # "clientDeviceNumberOfActionsAllowed": vk_tools.data['clientDeviceNumberOfActionsAllowed'], # should be required
            # "userAuthentication": False, # should be required
            "clientDeviceActionsAllowedBitfield": vk_tools.data['clientDeviceActionsAllowedBitfield']
        }
        custom_error = {
            "clientDeviceActionsAllowedBitfield": "Required field clientDeviceActionsAllowedBitfield or "
                                                  "clientDeviceActionsAllowed is missing."
        }
        vk_tools.check_mandatory_fields(payload, method="POST", endpoint='virtualkeys',
                                        custom_error_messages=custom_error)

    def test_vk_050_create_vk_errors(self):
        """
        Call the API with wrong inputs and check that errors are triggered
        """
        # Testing with an invalid generationInterval
        start_date = int(time.time())
        end_date = start_date + 10 * 60
        id = "create_vk_test_" + str(random.randint(1, 99999999999999999999))
        payload = {
            "id": id,
            "vehicleId": vk_tools.keycore_requests.vehicle.id,
            "clientDeviceId": vk_tools.keycore_requests.kc_info['new_cd_id'],
            "validityStartDate": start_date,
            "validityEndDate": end_date,
            "clientDeviceNumberOfActionsAllowed": vk_tools.data['clientDeviceNumberOfActionsAllowed'],
            "clientDeviceActionsAllowedBitfield": vk_tools.data['clientDeviceActionsAllowedBitfield'],
            "userAuthentication": False,
            "generationInterval": 14 * 60
        }
        resp = vk_tools.keycore_requests.create_vk(payload)
        assert vk_tools.keycore_requests.cloud.response_code == 400
        assert resp.get("errorId") == 10020001
        assert resp.get("message") == "Field generationInterval is invalid."

        # Testing with both clientDeviceActionsAllowed and clientDeviceActionsAllowedBitfield in the same request
        payload["generationInterval"] = 3600
        payload["clientDeviceActionsAllowed"] = ["LOCK"]
        resp = vk_tools.keycore_requests.create_vk(payload)
        assert vk_tools.keycore_requests.cloud.response_code == 400
        assert resp.get("errorId") == 10020002
        assert resp.get("message") == "Field is invalid"

    def test_vk_060_get_vks(self):
        """
        Get the list of virtual keys and check that the response contains the correct fields
        """
        resp = vk_tools.keycore_requests.get_vk_ivkapi(sort="-validityStartDate")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        logger.info(vk_tools.keycore_requests.cloud.response_body)
        vk_tools.assert_correct_field(vk_get_template, True)
        assert resp.get("virtualKeys")[0].get("type") == "MOBILE" or resp.get("virtualKeys")[0].get("type") == "CARD"
        assert type(resp.get("virtualKeys")[0].get("label")) == str

    def test_vk_070_get_vks_main(self):
        """
        Get the list of virtual keys with version 1 main API and check that the response contains the correct fields
        """
        vk_tools.keycore_requests.get_vk_ivkapi(v1_main=True, version="1")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)

    def test_vk_080_get_new_vks_with_start_date_sorting(self):
        """
        Get the list of virtual keys with validityStartDate sorting and check that the response contains the correct fields
        KAAS-19949 - Issue is closed as kaas in in maintenance and will not be fixed.
        So adding N/A value in the assertion
        """
        resp = vk_tools.keycore_requests.get_vk_ivkapi(sort="-validityStartDate")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)
        assert resp.get("virtualKeys")[0].get("type") == "MOBILE" or resp.get("virtualKeys")[0].get("type") == "CARD" or \
               resp.get("virtualKeys")[0].get("type") == "N/A"
        assert int(resp.get("virtualKeys")[1].get("validityStartDate")) > int(
            resp.get("virtualKeys")[2].get("validityStartDate"))

    def test_vk_090_get_new_vks_with_start_date_asc_sorting(self):
        """
        Get the list of virtual keys with ascending validityStartDate sorting and check that the response contains
        the correct fields
        KAAS-19949 - Issue is closed as kaas in in maintenance and will not be fixed.
        So adding N/A value in the assertion
        """
        resp = vk_tools.keycore_requests.get_vk_ivkapi(sort="validityStartDate")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)
        assert resp.get("virtualKeys")[0].get("type") == "MOBILE" or resp.get("virtualKeys")[0].get("type") == "CARD" or \
               resp.get("virtualKeys")[0].get("type") == "N/A"
        assert int(resp.get("virtualKeys")[0].get("validityStartDate")) < int(
            resp.get("virtualKeys")[1].get("validityStartDate"))

    def test_vk_100_get_new_vks_with_end_date_sorting(self):
        """
        Get the list of virtual keys with validityEndDate sorting and check that the response contains the correct fields
        KAAS-19949 - Issue is closed as kaas in in maintenance and will not be fixed.
        So adding N/A value in the assertion
        """
        resp = vk_tools.keycore_requests.get_vk_ivkapi(sort="-validityEndDate")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)
        assert resp.get("virtualKeys")[0].get("type") == "MOBILE" or resp.get("virtualKeys")[0].get("type") == "CARD" or \
               resp.get("virtualKeys")[0].get("type") == "N/A"
        assert int(resp.get("virtualKeys")[0].get("validityEndDate")) > int(
            resp.get("virtualKeys")[1].get("validityEndDate"))

    def test_vk_110_get_new_vks_with_end_date_asc_sorting(self):
        """
        Get the list of virtual keys with ascending validityEndDate sorting and check that the response
        contains the correct fields
        KAAS-19949 - Issue is closed as kaas in in maintenance and will not be fixed.
        So adding N/A value in the assertion
        """
        resp = vk_tools.keycore_requests.get_vk_ivkapi(sort="validityEndDate")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)
        assert resp.get("virtualKeys")[0].get("type") == "MOBILE" or resp.get("virtualKeys")[0].get("type") == "CARD" or \
               resp.get("virtualKeys")[0].get("type") == "N/A"
        assert int(resp.get("virtualKeys")[0].get("validityEndDate")) < int(
            resp.get("virtualKeys")[1].get("validityEndDate"))

    def test_vk_120_get_new_vks_with_status_active_filter(self):
        """
        Get the list of virtual keys with VK status as ACTIVE and check that the response contains the correct fields
        """
        vk_tools.keycore_requests.get_vk_ivkapi(vk_status="ACTIVE")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)

    def test_vk_130_get_new_vks_with_status_revoke_pending_filter(self):
        """
        Get the list of virtual keys with VK status as REVOKE_PENDING and check that the response
        contains the correct fields
        """
        vk_tools.keycore_requests.get_vk_ivkapi(vk_status="REVOKE_PENDING")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)

    def test_vk_140_get_new_vks_with_vehicle_id_filter(self):
        """
        Get the list of virtual keys with vehicle id filtering and check that the response contains the correct fields
        """
        resp = vk_tools.keycore_requests.get_vk_ivkapi(vehicle_id=vehicle_id_list[0])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)
        assert resp.get("virtualKeys")[0].get("vehicleId") == vehicle_id_list[0]
        assert resp.get("paginationInfo").get("total") != 0

    def test_vk_150_get_new_vks_with_clientdevice_id_filter(self):
        """
        Get the list of virtual keys with client device id filtering and check that the response contains the correct fields
        """
        new_cd_id = vk_tools.keycore_requests.kc_info['new_cd_id']
        resp = vk_tools.keycore_requests.get_vk_ivkapi(client_device_id=new_cd_id)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)
        assert resp.get("virtualKeys")[0].get("clientDeviceId") == new_cd_id

    def test_vk_160_get_new_vks_with_input_filter(self):
        """
        Get the list of virtual keys with various filters and check that the response contains the correct fields
        """
        new_cd_id = vk_tools.keycore_requests.kc_info['new_cd_id']

        resp = vk_tools.keycore_requests.get_vk_ivkapi(client_device_id=new_cd_id, vehicle_id=vehicle_id_list[0],
                                                       sort="-validityStartDate")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)
        assert resp.get("virtualKeys")[0].get("clientDeviceId") == new_cd_id
        assert resp.get("virtualKeys")[0].get("vehicleId") == vehicle_id_list[0]

    def test_vk_170_get_vks_pagination(self):
        """
        Get the list of virtual keys by setting pagination parameters and check that the parameters are effective
        """
        # First request with limit = 4:
        # {vk1, vk2, vk3, vk4}
        resp = vk_tools.keycore_requests.get_vk_ivkapi(limit=4, offset=0, sort="-validityStartDate")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)
        assert resp.get("paginationInfo").get("limit") == 4
        assert resp.get("paginationInfo").get("offset") == 0
        vk3 = resp.get("virtualKeys")[2].get("id")
        vk4 = resp.get("virtualKeys")[3].get("id")

        # Second request with offset = 2 and limit = 2:
        # {vk3, vk4}
        resp = vk_tools.keycore_requests.get_vk_ivkapi(limit=2, offset=2,
                                                       sort="-validityStartDate")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("virtualKeys")) == 2
        assert resp.get("paginationInfo").get("limit") == 2
        assert resp.get("paginationInfo").get("offset") == 2
        assert resp.get("virtualKeys")[0].get("id") == vk3
        assert resp.get("virtualKeys")[1].get("id") == vk4

    def test_vk_180_get_vks_pagination_with_page_navigation(self):
        """
        Get the list of virtual keys by setting pagination parameters navigating to next page and coming back to
        previous page, Vk list should be same
        """
        vk_list_pagination = []
        # First request with limit = 10:
        # {vk1, vk2, vk3, vk4...vk10}
        # Copy each vk id in a list vk_list_pagination
        resp = vk_tools.keycore_requests.get_vk_ivkapi(limit=10,
                                                       sort="-validityStartDate")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)
        assert resp.get("paginationInfo").get("limit") == 10
        assert resp.get("paginationInfo").get("offset") == 0
        for index in range(resp.get("paginationInfo").get("limit")):
            vk_list_pagination.append(resp.get("virtualKeys")[index].get("id"))

        # moving to next page
        # Second request with limit = 10 and offset = 10
        resp = vk_tools.keycore_requests.get_vk_ivkapi(limit=10, offset=10,
                                                       sort="-validityStartDate")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)
        assert resp.get("paginationInfo").get("limit") == 10
        assert resp.get("paginationInfo").get("offset") == 10

        # moving to previous page
        # Third request again coming back to previous page with limit = 10
        # Compare each vk ids with vk_list_pagination list
        resp = vk_tools.keycore_requests.get_vk_ivkapi(limit=10,
                                                       sort="-validityStartDate")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)
        assert resp.get("paginationInfo").get("limit") == 10
        assert resp.get("paginationInfo").get("offset") == 0
        for index in range(resp.get("paginationInfo").get("limit")):
            assert vk_list_pagination[index] == resp.get("virtualKeys")[index].get("id")

    def test_vk_190_get_list_vks_with_max_limit(self):
        """
        KAAS-15121 based on this bug
        Get virtual keys with max limit input parameter and validate the response
        """
        # Validating with Max limit
        resp = vk_tools.keycore_requests.get_vk_ivkapi(limit=max_limit_cd_veh_vk,
                                                       sort="-validityStartDate")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        if resp.get("paginationInfo").get("total") > max_limit_cd_veh_vk:
            assert len(resp.get("virtualKeys")) == max_limit_cd_veh_vk
        else:
            assert len(resp.get("virtualKeys")) == resp.get("paginationInfo").get("size")
        assert resp.get("paginationInfo").get("limit") == max_limit_cd_veh_vk
        assert resp.get("paginationInfo").get("offset") == 0

    def test_vk_120_get_list_vks_with_max_limit_exceed(self):
        """
        KAAS-15121 based on this bug
        Get virtual keys with with max limit exceed input parameter and validate the response
        """
        # Validating with Max limit exceed
        resp = vk_tools.keycore_requests.get_vk_ivkapi(limit=max_limit_cd_veh_vk + 1,
                                                       sort="-validityStartDate")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        if resp.get("paginationInfo").get("total") > max_limit_cd_veh_vk:
            assert len(resp.get("virtualKeys")) == max_limit_cd_veh_vk
        else:
            assert len(resp.get("virtualKeys")) == resp.get("paginationInfo").get("size")
        assert resp.get("paginationInfo").get("limit") == max_limit_cd_veh_vk
        assert resp.get("paginationInfo").get("offset") == 0

    def test_vk_130_get_list_vks_with_negative_limit_offset(self):
        """
        KAAS-15121 based on this bug
        Get virtual keys with negative input and offset and validate the response
        """
        # Validating with negative limit and offset values
        resp = vk_tools.keycore_requests.get_vk_ivkapi(limit=-10, offset=-10,
                                                       sort="-validityStartDate")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("virtualKeys")) == 25
        assert resp.get("paginationInfo").get("limit") == 25
        assert resp.get("paginationInfo").get("offset") == 0

    def test_vk_140_get_list_vks_with_limit_equals_zero(self):
        """
        KAAS-15121 based on this bug
        Get virtual keys with limit=0 and validate the response
        """
        # Validating with limit=0
        resp = vk_tools.keycore_requests.get_vk_ivkapi(limit=0, sort="-validityStartDate")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("virtualKeys")) == 25
        assert resp.get("paginationInfo").get("limit") == 25
        assert resp.get("paginationInfo").get("offset") == 0

    def test_vk_150_get_list_vks_with_pagination_info(self):
        """
        KAAS-15121 based on this bug
        Get virtual keys and validate pagination info
        """
        # Validating with max limit, offset=20 and checking pagination info details
        resp = vk_tools.keycore_requests.get_vk_ivkapi(limit=max_limit_cd_veh_vk, offset=20,
                                                       sort="-validityStartDate")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        if resp.get("paginationInfo").get("size") > max_limit_cd_veh_vk:
            assert len(resp.get("virtualKeys")) == max_limit_cd_veh_vk
        else:
            assert len(resp.get("virtualKeys")) == resp.get("paginationInfo").get("size")
        assert resp.get("paginationInfo").get("limit") == max_limit_cd_veh_vk
        assert resp.get("paginationInfo").get("offset") == 20
        current_page_api_data = resp.get("paginationInfo").get("currentPage")
        next_page_api_data = resp.get("paginationInfo").get("nextPage")
        previous_page_api_data = resp.get("paginationInfo").get("previousPage")
        current_page = "/2/virtualkeys?sort=-validityStartDate\u0026limit={}".format(
            max_limit_cd_veh_vk) + "\u0026offset=20"
        if resp.get("paginationInfo").get("total") > max_limit_cd_veh_vk + 20:
            next_page = "/2/virtualkeys?sort=-validityStartDate\u0026limit={}".format(
                max_limit_cd_veh_vk) + "\u0026offset={}".format(max_limit_cd_veh_vk + 20)
        else:
            next_page = "/2/virtualkeys?sort=-validityStartDate\u0026limit={}".format(
                max_limit_cd_veh_vk) + "\u0026offset={}".format(resp.get("paginationInfo").get("total"))
        previous_page = "/2/virtualkeys?sort=-validityStartDate\u0026limit={}".format(
            max_limit_cd_veh_vk) + "\u0026offset=0"
        assert current_page_api_data == current_page
        assert next_page_api_data == next_page
        assert previous_page_api_data == previous_page

    def test_vk_151_get_vks_filtered(self):
        """
        Get the list of virtual keys by setting filters parameters and check that the parameters are effective
        """
        resp = vk_tools.keycore_requests.get_vk_ivkapi(client_device_id=vk_tools.keycore_requests.kc_info['new_cd_id'],
                                                       sort="-validityStartDate")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)
        for vk in resp.get("virtualKeys"):
            assert vk.get("clientDeviceId") == vk_tools.keycore_requests.kc_info['new_cd_id']

        resp = vk_tools.keycore_requests.get_vk_ivkapi(vehicle_id=vk_tools.keycore_requests.vehicle.id,
                                                       sort="-validityStartDate")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)
        for vk in resp.get("virtualKeys"):
            assert vk.get("vehicleId") == vk_tools.keycore_requests.vehicle.id

    def test_vk_170_update_vk(self):
        """
        Create virtual key, then call the API to update it. Check that the response contains the correct fields
        """
        start_date = int(time.time()) + 120
        end_date = start_date + 10 * 60

        payload = {
            "vehicleId": vk_tools.keycore_requests.vehicle.id,
            "clientDeviceId": vk_tools.keycore_requests.client_device.id,
            "validityStartDate": start_date,
            "validityEndDate": end_date,
            "clientDeviceNumberOfActionsAllowed": vk_tools.data['clientDeviceNumberOfActionsAllowed'],
            "clientDeviceActionsAllowedBitfield": vk_tools.data['clientDeviceActionsAllowedBitfield'],
            "userAuthentication": False,
            "generationInterval": 3600
        }
        vk_tools.keycore_requests.create_vk(payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        new_validity_start_date = start_date + 30
        new_validity_end_date = end_date + 30
        new_generation_interval = 20 * 60
        resp = vk_tools.keycore_requests.update_vk(new_validityenddate=new_validity_end_date,
                                                   new_validitystartdate=new_validity_start_date,
                                                   new_generationinterval=new_generation_interval)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_update_template, True)
        assert resp.get("validityStartDate") == str(new_validity_start_date)
        assert resp.get("validityEndDate") == str(new_validity_end_date)
        assert resp.get("generationInterval") == str(new_generation_interval)

    def test_vk_180_update_vk_start_time(self):
        """
        Create virtual key, then call the API to update it with same start time which was given at the time of creation.
        Check that the response contains the correct fields
        """
        start_date = int(time.time()) + 120
        end_date = start_date + 10 * 60

        payload = {
            "vehicleId": vk_tools.keycore_requests.vehicle.id,
            "clientDeviceId": vk_tools.keycore_requests.client_device.id,
            "validityStartDate": start_date,
            "validityEndDate": end_date,
            "clientDeviceNumberOfActionsAllowed": vk_tools.data['clientDeviceNumberOfActionsAllowed'],
            "clientDeviceActionsAllowedBitfield": vk_tools.data['clientDeviceActionsAllowedBitfield'],
            "userAuthentication": False,
            "generationInterval": 3600
        }
        vk_tools.keycore_requests.create_vk(payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        new_validity_start_date = start_date
        new_validity_end_date = end_date
        new_generation_interval = 20 * 60
        resp = vk_tools.keycore_requests.update_vk(new_validityenddate=new_validity_end_date,
                                                   new_validitystartdate=new_validity_start_date,
                                                   new_generationinterval=new_generation_interval)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_update_template, True)
        assert resp.get("validityStartDate") != "0"
        assert resp.get("validityStartDate") == str(start_date)
        assert resp.get("validityEndDate") == str(end_date)
        assert resp.get("generationInterval") == str(new_generation_interval)

    def test_vk_190_update_vk_errors(self):
        """
        Create virtual key, then call the API to update it with wrong inputs. Check that errors are triggered
        """
        # Calling with an invalid generationInterval
        start_date = int(time.time()) + 120
        end_date = start_date + 3 * 60

        payload = {
            "vehicleId": vk_tools.keycore_requests.vehicle.id,
            "clientDeviceId": vk_tools.keycore_requests.client_device.id,
            "validityStartDate": start_date,
            "validityEndDate": end_date,
            "clientDeviceNumberOfActionsAllowed": vk_tools.data['clientDeviceNumberOfActionsAllowed'],
            "clientDeviceActionsAllowedBitfield": vk_tools.data['clientDeviceActionsAllowedBitfield'],
            "userAuthentication": False,
            "generationInterval": 3600
        }
        vk_tools.keycore_requests.create_vk(payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        new_validity_start_date = start_date + 30
        new_validity_end_date = end_date + 30
        new_generation_interval = 3 * 60  # 3 minutes
        resp = vk_tools.keycore_requests.update_vk(new_validityenddate=new_validity_end_date,
                                                   new_validitystartdate=new_validity_start_date,
                                                   new_generationinterval=new_generation_interval)
        assert vk_tools.keycore_requests.cloud.response_code == 400
        assert resp.get("errorId") == 10020001
        assert resp.get("message") == "Field generationInterval is invalid."

        # Trying to update validityStartDate whereas the VK has already begun
        payload["validityStartDate"] = int(time.time())
        vk_tools.keycore_requests.create_vk(payload)
        time.sleep(5)
        new_validity_start_date = int(time.time()) + 30
        new_generation_interval = 20 * 60
        resp = vk_tools.keycore_requests.update_vk(new_validityenddate=new_validity_end_date,
                                                   new_validitystartdate=new_validity_start_date,
                                                   new_generationinterval=new_generation_interval)
        assert vk_tools.keycore_requests.cloud.response_code == 400
        assert resp.get("errorId") == 1102  # TBC
        assert resp.get("message") == "Field validityStartDate is invalid."

    def test_vk_200_revoke_vk(self):
        """
        Revoke the virtual key created in test_create_vk and check that the response code is 200
        """
        global vk_id
        resp = vk_tools.keycore_requests.revoke_vk(vk_id)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("id") == vk_id

    def test_vk_201_nfc_revoke_vk(self):
        """
        Revoke the virtual key created by nfc create vk test and check that the response code is 200
        """
        resp = vk_tools.keycore_requests.revoke_vk(vk_tools.keycore_requests.kc_info['nfc_vk_id'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("id") == vk_tools.keycore_requests.kc_info['nfc_vk_id']

    def test_vk_210_get_new_vks_with_status_revoked_filter(self):
        """
        Get the list of virtual keys with VK status as REVOKED and check that the response contains the correct fields
        """
        resp = vk_tools.keycore_requests.get_vk_ivkapi(vk_status="REVOKED")
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)
        assert resp.get("virtualKeys")[0].get("status") == "REVOKED"

    def test_sms_010_sms_api_provider_id_lock_command(self):
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["LOCK"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_020_sms_api_provider_id_unlock_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["UNLOCK"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_030_sms_api_provider_id_trunk_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["TRUNK_ACTION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_040_sms_api_provider_id_engine_enable_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["ENABLE_IGNITION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_050_sms_api_provider_id_unlock_eng_enable_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["UNLOCK", "ENABLE_IGNITION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_060_sms_api_provider_id_engine_disable_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["DISABLE_IGNITION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_070_sms_api_end_date_validation(self):
        timestamp = (time.time()).__round__() + 100000
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               expiration_date=timestamp,
                                                               operations=["LOCK"])
        assert vk_tools.keycore_requests.cloud.response_code == 400
        assert resp.get("message") == "Expiration date must be between 0 and 1 day after request"

    def test_sms_080_sms_api_unrecognized_operation(self):
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id, operations=["LOCK1"])
        assert vk_tools.keycore_requests.cloud.response_code == 400
        assert resp.get("message") == "Unrecognized operation : LOCK1"

    def test_sms_090_sms_api_invalid_combination_of_operations(self):
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["LOCK", "UNLOCK"])
        assert vk_tools.keycore_requests.cloud.response_code == 400
        assert resp.get("message") == "Invalid combination of operations"

    def test_telemetry_010_get_telemetry_journal(self):
        """
        Call the telemetry journal API and check that the response contains the correct fields
        """
        output_template = {
            "firstTelemetryId": str,
            "lastTelemetryId": str,
            "nextTelemetryId": str,
            "telemetry": ev_telemetry_template
        }
        start_timestamp = (time.time()).__round__() - 86400
        vk_tools.keycore_requests.get_telemetry_journal(start_timestamp=start_timestamp)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        vk_tools.assert_correct_field(output_template, is_template_mandatory=False)

    def test_telemetry_020_get_telemetry_journal_input(self):
        """
        Call the telemetry journal API with pagination parameters and check that they are effective
        """
        # First call limit=3
        # output expected : firstTelemetryId = id1 ; lastTelemetryId = id3 ; nextTelemetryId = id4
        # telemetry = [{id1...},{id2...},{id3...}]
        resp = vk_tools.keycore_requests.get_telemetry_journal(limit=3)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("telemetry")) == 3
        assert resp.get("firstTelemetryId") == resp.get("telemetry")[0].get("telemetryId")
        id3 = resp.get("lastTelemetryId")
        assert id3 == resp.get("telemetry")[2].get("telemetryId")
        id4 = resp.get("nextTelemetryId")

        # Second call with start_telemetry_id = id3 ; limit=2
        # output expected : firstTelemetryId = id3 ; lastTelemetryId = id4 ;
        # telemetry = [{id3...},{id4...}]
        resp = vk_tools.keycore_requests.get_telemetry_journal(limit=2, start_telemetry_id=id3)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("telemetry")) == 2
        assert resp.get("firstTelemetryId") == id3 == resp.get("telemetry")[0].get("telemetryId")
        assert resp.get("lastTelemetryId") == id4 == resp.get("telemetry")[1].get("telemetryId")

    def test_telemetry_030_get_telemetry_journal_input_max_limit(self):
        """
        Call the telemetry journal API with pagination parameters with Max limit value and check that they are effective
        """
        # First call limit=500
        # output expected : firstTelemetryId = id1 ; lastTelemetryId = last_telemetry_data ; nextTelemetryId = next_data
        # telemetry = [{id1...},{id2...},{id3...}]
        resp = vk_tools.keycore_requests.get_telemetry_journal(limit=journal_api_max_limit)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("telemetry")) == journal_api_max_limit
        assert resp.get("firstTelemetryId") == resp.get("telemetry")[0].get("telemetryId")
        next_data = resp.get("nextTelemetryId")
        last_data = resp.get("lastTelemetryId")
        assert last_data == resp.get("telemetry")[journal_api_max_limit - 1].get("telemetryId")

        # Second call with start_telemetry_id = last_data ; limit=2
        # output expected : firstTelemetryId = last_data ; lastTelemetryId = next_data ;
        resp = vk_tools.keycore_requests.get_telemetry_journal(limit=2, start_telemetry_id=last_data)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("telemetry")) == 2
        assert next_data == resp.get("telemetry")[1].get("telemetryId")

    def test_telemetry_040_get_telemetry_journal_input_wrong_max_limit(self):
        """
            Check that the API returns the correct errors when there is max limit exceeding for telemetry data
        """
        resp = vk_tools.keycore_requests.get_telemetry_journal(limit=journal_api_max_limit + 1)
        assert vk_tools.keycore_requests.cloud.response_code == 400
        assert resp.get("message") == "Limit must not be greater than " + str(journal_api_max_limit)

    def test_telemetry_050_get_telemetry_journal_full(self):
        """
        Send a ecu message to insert a full telemetry.
        Then call the telemetry journal API and check that the response contains the correct fields and that all the
        values inserted are returned by the API
        """

        # Sending a telemetry to the BE prior to the test
        start_timestamp = (time.time()).__round__() - 30
        resp, cbor_default = send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                                       vin=VEHICLE_PAYLOAD["vin"], cbor_type="all")

        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        template_to_use = (deepcopy(telemetry_template))
        template_to_use[0]["keyInfo"] = {"serialNumber": int}
        output_template = {
            "firstTelemetryId": str,
            "lastTelemetryId": str,
            "nextTelemetryId": str,
            "telemetry": deepcopy(template_to_use)
        }
        # The field correctedFuelLevelSmooth is deprecated and cannot be returned for new telemetry, so we remove it
        del output_template.get("telemetry")[0]["correctedFuelLevelSmooth"]
        resp = vk_tools.keycore_requests.get_telemetry_journal(start_timestamp=start_timestamp)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        # Remove all the telemetries from the response, except the one sent in the current test
        telemetries = resp.get("telemetry").copy()
        odometer = cbor_default["odometer"]
        logger.info("========= Odometer value:: " + str(odometer))
        for telemetry in telemetries:
            if not telemetry.get("odometer") or telemetry.get("odometer").get("value") != odometer:
                resp.get("telemetry").remove(telemetry)
        assert len(resp.get("telemetry")) == 1, "Output should contain one and only one telemetry at this point"

        vk_tools.assert_correct_field(output_template, is_template_mandatory=True)

    def test_telemetry_060_get_telemetry_merged_full(self):
        """
        Send a ecu message to insert a full telemetry.
        Then call the telemetry merged API and check that the response contains the correct fields and that all the values
        inserted are returned by the API
        """
        # Sending a telemetry to the BE prior to the test
        start_timestamp = (time.time()).__round__() - 30
        resp, cbor_default = send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                                       vin=VEHICLE_PAYLOAD["vin"], cbor_type="all")
        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        output_template = {
            "paginationInfo": pagination_info,
            "transactionId": str,
            "lastTimestamp": int,
            "telemetry": deepcopy(telemetry_template)
        }
        resp = vk_tools.keycore_requests.get_telemetry_merged(start_timestamp=start_timestamp)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        # Remove all the telemetries from the response, except the one sent in the current test
        odometer = cbor_default["odometer"]
        logger.info("========= Odometer value:: " + str(odometer))
        telemetries = resp.get("telemetry").copy()
        for telemetry in telemetries:
            if not telemetry.get("odometer") or telemetry.get("odometer").get("value") != odometer:
                resp.get("telemetry").remove(telemetry)
        assert len(resp.get("telemetry")) == 1, "Output should contain one and only one telemetry at this point"

        # TODO delete these lines when KAAS-9333 is fixed
        del output_template.get("telemetry")[0]["correctedFuelLevelSmooth"]
        del output_template.get("telemetry")[0]["event"]

        vk_tools.assert_correct_field(output_template, is_template_mandatory=True)

    def test_telemetry_070_get_telemetry_merged(self):
        """
        Call the telemetry merged API and check that the response contains the correct fields
        """
        output_template = {
            "paginationInfo": pagination_info,
            "transactionId": str,
            "lastTimestamp": int,
            "telemetry": telemetry_template
        }
        timestamp = (time.time()).__round__() - 290
        resp = vk_tools.keycore_requests.get_telemetry_merged(start_timestamp=timestamp)

        assert vk_tools.keycore_requests.cloud.response_code == 200

        if len(resp.get("telemetry")) == 0:
            pytest.skip("Not enough telemetry data to run the test")

        vk_tools.assert_correct_field(output_template, is_template_mandatory=False)

    def test_telemetry_071_get_vehicle_telemetry(self):
        """
        Call the telemetry API for specific vehicle with vin and check that the response contains the correct fields
        """
        start_timestamp = (time.time()).__round__() - 80000
        end_timestamp = (time.time()).__round__() - 50000
        vk_tools.keycore_requests.get_vehicle_telemetry(vin=vehicle_vin,
                                                        custom_apikey=custom_api_key,
                                                        custom_secretkey=custom_secret_key,
                                                        start_timestamp=start_timestamp,
                                                        end_timestamp=end_timestamp,
                                                        )

        assert vk_tools.keycore_requests.cloud.response_code == 200
        # More Assertions are added once this bug KAAS-20834 is fixed

    def test_telemetry_072_get_vehicle_telemetry_inputs(self):
        """
        Call the telemetry API for specific vehicle with vin and check with different query parameters
        """
        start_timestamp = (time.time()).__round__() - 80000
        resp = vk_tools.keycore_requests.get_vehicle_telemetry(vin=vehicle_vin,
                                                               custom_apikey=custom_api_key,
                                                               custom_secretkey=custom_secret_key,
                                                               start_timestamp=start_timestamp, limit=10)

        assert vk_tools.keycore_requests.cloud.response_code == 200
        if len(resp.get("telemetry")) == 0:
            logger.warning("Get telemetry request is successful but No telemetries available")
            return
        assert len(resp.get("telemetry")) == 10
        id1 = resp.get("telemetry")[0].get("telemetryId")
        resp = vk_tools.keycore_requests.get_vehicle_telemetry(vin=vehicle_vin,
                                                               custom_apikey=custom_api_key,
                                                               custom_secretkey=custom_secret_key,
                                                               start_timestamp=start_timestamp, limit=10,
                                                               offset=2, paginated=True)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("telemetry")) == 10
        assert id1 != resp.get("telemetry")[0].get("telemetryId")

    def test_telemetry_080_get_telemetry_merged_error(self):
        """
        Call the telemetry merged API with a wrong timestamp and check that an error is triggered
        """
        output_template = {
            "paginationInfo": pagination_info,
            "transactionId": str,
            "lastTimestamp": int,
            "telemetry": telemetry_template
        }
        timestamp = (time.time()).__round__() - 400
        resp = vk_tools.keycore_requests.get_telemetry_merged(start_timestamp=timestamp)
        assert vk_tools.keycore_requests.cloud.response_code == 400
        # assert resp.get("errorId") == 10030002
        assert resp.get("message") == "StartTimestamp must be less than 5 mins before current time"

    def test_telemetry_090_get_telemetry_merged_inputs(self):
        """
        Call the telemetry merged API with various parameters and check that they are effective
        Also check that errors are correctly raised when the input parameters are incorrect
        """
        # Testing limit parameter
        timestamp = (time.time()).__round__() - 290
        resp = vk_tools.keycore_requests.get_telemetry_merged(start_timestamp=timestamp, limit=2)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("telemetry")) <= 2

        # Testing with no input
        resp = vk_tools.keycore_requests.get_telemetry_merged()
        assert vk_tools.keycore_requests.cloud.response_code == 400
        # assert resp.get("errorId") == 10030002
        assert resp.get(
            "message") == "One of either startTimestamp or transactionId must be specified. Neither were given"

        # Testing offset without transaction_id
        timestamp = (time.time()).__round__() - 290
        resp = vk_tools.keycore_requests.get_telemetry_merged(start_timestamp=timestamp, offset=2)
        assert vk_tools.keycore_requests.cloud.response_code == 400
        # assert resp.get("errorId") == 10030002
        assert resp.get("message") == "TransactionId must be provided"

    def test_telemetry_100_get_telemetry_merged_negative_time_60sec(self):
        """
        Send a ecu message to insert a full telemetry.
        Call the telemetry merged API with a -ve timestamp (-60) and check the response
        """
        # Sending a telemetry to the BE prior to the test
        resp, cbor_default = send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                                       vin=VEHICLE_PAYLOAD["vin"], cbor_type="all")
        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        output_template = {
            "paginationInfo": pagination_info,
            "transactionId": str,
            "lastTimestamp": int,
            "telemetry": deepcopy(telemetry_template)
        }

        timestamp = -60
        resp = vk_tools.keycore_requests.get_telemetry_merged(start_timestamp=timestamp)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("paginationInfo").get("offset") == 0
        assert resp.get("paginationInfo").get("limit") == 100
        flag = False
        for value in resp.get("telemetry"):
            if value["vin"] == VEHICLE_PAYLOAD["vin"]:
                flag = True
                break
        assert flag is True, "No telemetry for the vehicle VIN {}".format(VEHICLE_PAYLOAD["vin"])

        # Remove all the telemetries from the response, except the one sent in the current test
        telemetries = resp.get("telemetry").copy()
        odometer = cbor_default["odometer"]
        logger.info("========= Odometer value:: " + str(odometer))
        for telemetry in telemetries:
            if not telemetry.get("odometer") or telemetry.get("odometer").get("value") != odometer:
                resp.get("telemetry").remove(telemetry)
        assert len(resp.get("telemetry")) == 1, "Output should contain one and only one telemetry at this point"

        # TODO delete these lines when KAAS-9333 is fixed
        del output_template.get("telemetry")[0]["correctedFuelLevelSmooth"]
        del output_template.get("telemetry")[0]["event"]

        vk_tools.assert_correct_field(output_template, is_template_mandatory=True)

    def test_telemetry_110_get_telemetry_merged_negative_time_120sec(self):
        """
        Send a ecu message to insert a full telemetry.
        Call the telemetry merged API with a -ve timestamp (-120) and check the response
        """
        # Sending a telemetry to the BE prior to the test
        resp, cbor_default = send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                                       vin=VEHICLE_PAYLOAD["vin"], cbor_type="all")
        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        output_template = {
            "paginationInfo": pagination_info,
            "transactionId": str,
            "lastTimestamp": int,
            "telemetry": deepcopy(telemetry_template)
        }

        timestamp = -120
        resp = vk_tools.keycore_requests.get_telemetry_merged(start_timestamp=timestamp)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("paginationInfo").get("offset") == 0
        assert resp.get("paginationInfo").get("limit") == 100
        flag = False
        for value in resp.get("telemetry"):
            if value["vin"] == VEHICLE_PAYLOAD["vin"]:
                flag = True
                break
        assert flag is True, "No telemetry for the vehicle VIN {}".format(VEHICLE_PAYLOAD["vin"])

        # Remove all the telemetries from the response, except the one sent in the current test
        odometer = cbor_default["odometer"]
        logger.info("========= Odometer value:: " + str(odometer))
        telemetries = resp.get("telemetry").copy()
        for telemetry in telemetries:
            if not telemetry.get("odometer") or telemetry.get("odometer").get("value") != odometer:
                resp.get("telemetry").remove(telemetry)
        assert len(resp.get("telemetry")) == 1, "Output should contain one and only one telemetry at this point"

        # TODO delete these lines when KAAS-9333 is fixed
        del output_template.get("telemetry")[0]["correctedFuelLevelSmooth"]
        del output_template.get("telemetry")[0]["event"]

        vk_tools.assert_correct_field(output_template, is_template_mandatory=True)

    def test_telemetry_120_get_telemetry_merged_negative_time_200sec(self):
        """
        Send a ecu message to insert a full telemetry.
        Call the telemetry merged API with a -ve timestamp (-200) and check the response
        """
        # Sending a telemetry to the BE prior to the test
        send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                  vin=VEHICLE_PAYLOAD["vin"],
                                  cbor_type="all")
        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        timestamp = -200
        resp = vk_tools.keycore_requests.get_telemetry_merged(start_timestamp=timestamp)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("paginationInfo").get("offset") == 0
        assert resp.get("paginationInfo").get("limit") == 100
        flag = False
        for value in resp.get("telemetry"):
            if value["vin"] == VEHICLE_PAYLOAD["vin"]:
                flag = True
                break
        assert flag is True, "No telemetry for the vehicle VIN {}".format(VEHICLE_PAYLOAD["vin"])

    def test_telemetry_130_get_telemetry_merged_negative_time_301sec(self):
        """
        Call the telemetry merged API with a -ve timestamp (-301) and check that an error is triggered
        """
        timestamp = -301
        resp = vk_tools.keycore_requests.get_telemetry_merged(start_timestamp=timestamp)
        assert vk_tools.keycore_requests.cloud.response_code == 400
        assert resp.get("message") == "StartTimestamp must be less than 5 mins before current time"

    def test_telemetry_131_get_telemetry_door_status_event(self):
        """
        Send a ecu message to insert a full telemetry with door status event.
        Then call the telemetry journal API and check that the response contains the correct fields and that all the values
        inserted are returned by the API
        """
        # Sending a telemetry to the BE prior to the test

        start_timestamp = (time.time()).__round__() - 30
        params = {
            "event": random.choice([16, 17]),
        }
        send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                  vin=VEHICLE_PAYLOAD["vin"], cbor_type="custom_value", param_list=params)
        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        resp = vk_tools.keycore_requests.get_telemetry_journal(start_timestamp=start_timestamp)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        telemetry_length = len(resp.get("telemetry"))
        if params["event"] == 16:
            assert resp.get("telemetry")[telemetry_length - 1].get("event") == "ALL_DOORS_LOCKED"
        else:
            assert resp.get("telemetry")[telemetry_length - 1].get("event") == "ALL_DOORS_CLOSED"

    def test_telemetry_132_get_telemetry_engine_start_stop_event(self):
        """
        Send a ecu message to insert a full telemetry with Engine start/stop event.
        Then call the telemetry journal API and check that the response contains the correct fields and that all the values
        inserted are returned by the API
        """
        # Sending a telemetry to the BE prior to the test

        start_timestamp = (time.time()).__round__() - 30
        params = {
            "event": random.choice([2, 3]),
        }
        send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                  vin=VEHICLE_PAYLOAD["vin"], cbor_type="custom_value", param_list=params)
        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        resp = vk_tools.keycore_requests.get_telemetry_journal(start_timestamp=start_timestamp)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        telemetry_length = len(resp.get("telemetry"))
        if params["event"] == 2:
            assert resp.get("telemetry")[telemetry_length - 1].get("event") == "ENGINE_START"
        else:
            assert resp.get("telemetry")[telemetry_length - 1].get("event") == "ENGINE_STOP"

    def test_telemetry_133_get_telemetry_vehicle_locked_unlocked_event(self):
        """
        Send a ecu message to insert a full telemetry with vehicle locked/unlocked event.
        Then call the telemetry journal API and check that the response contains the correct fields and that all the values
        inserted are returned by the API
        """
        # Sending a telemetry to the BE prior to the test

        start_timestamp = (time.time()).__round__() - 30
        params = {
            "event": random.choice([4, 5]),
        }
        send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                  vin=VEHICLE_PAYLOAD["vin"], cbor_type="custom_value", param_list=params)
        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        resp = vk_tools.keycore_requests.get_telemetry_journal(start_timestamp=start_timestamp)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        telemetry_length = len(resp.get("telemetry"))
        if params["event"] == 4:
            assert resp.get("telemetry")[telemetry_length - 1].get("event") == "VEHICLE_UNLOCKED"
        else:
            assert resp.get("telemetry")[telemetry_length - 1].get("event") == "VEHICLE_LOCKED"

    def test_telemetry_134_get_telemetry_towing_detection_event(self):
        """
        Send a ecu message to insert a full telemetry with towing detection event.
        Then call the telemetry journal API and check that the response contains the correct fields and that all the values
        inserted are returned by the API
        """
        # Sending a telemetry to the BE prior to the test

        start_timestamp = (time.time()).__round__() - 30
        params = {
            "event": 11
        }
        send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                  vin=VEHICLE_PAYLOAD["vin"], cbor_type="custom_value", param_list=params)
        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        resp = vk_tools.keycore_requests.get_telemetry_journal(start_timestamp=start_timestamp)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        telemetry_length = len(resp.get("telemetry"))
        assert resp.get("telemetry")[telemetry_length - 1].get("event") == "TOWING_DETECTION"

    def test_telemetry_135_get_telemetry_card_holder_event(self):
        """
        Send a ecu message to insert a full telemetry with card holder event.
        Then call the telemetry journal API and check that the response contains the correct fields and that all the values
        inserted are returned by the API
        """
        # Sending a telemetry to the BE prior to the test

        start_timestamp = (time.time()).__round__() - 30
        params = {
            "event": 12
        }
        send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                  vin=VEHICLE_PAYLOAD["vin"], cbor_type="custom_value", param_list=params)
        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        resp = vk_tools.keycore_requests.get_telemetry_journal(start_timestamp=start_timestamp)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        telemetry_length = len(resp.get("telemetry"))
        assert resp.get("telemetry")[telemetry_length - 1].get("event") == "CARD_HOLDER"

    def test_telemetry_136_nan_value_in_telemetry(self):
        """
        Send a ecu message to insert a full telemetry with NaN value for fuel level.
        Then call the telemetry journal API and check that the response contains the correct fields and that all the values
        inserted are returned by the API
        """

        # Sending a telemetry to the BE prior to the test
        start_timestamp = (time.time()).__round__() - 30

        nan_list = ["fuel_smooth", "odometer", "fuel_level"]
        send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                  vin=VEHICLE_PAYLOAD["vin"],
                                  cbor_type="custom_nan",
                                  nan_list=nan_list)

        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        output_template = {
            "firstTelemetryId": str,
            "lastTelemetryId": str,
            "nextTelemetryId": str,
            "telemetry": deepcopy(telemetry_template)
        }
        # The field correctedFuelLevelSmooth is deprecated and cannot be returned for new telemetry, so we remove it
        del output_template.get("telemetry")[0]["correctedFuelLevelSmooth"]
        del output_template.get("telemetry")[0]["fuelLevel"]
        resp = vk_tools.keycore_requests.get_telemetry_journal(start_timestamp=start_timestamp)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        # Remove all the telemetries from the response, except the one sent in the current test
        telemetries = resp.get("telemetry").copy()
        expected_telemetry = telemetries[len(telemetries) - 1]
        for value in nan_list:
            assert (value in expected_telemetry) is False, "NAN value is not set for the parameter: " + value
            logger.info("NAN value is set for the parameter: " + value)

    def test_telemetry_137_all_nan_values_in_telemetry(self):
        """
        Send a ecu message to insert a full telemetry with NaN values for all telemetry items.
        Then call the telemetry journal API and check that the response contains the correct fields and that all the values
        inserted are returned by the API
        """

        # Sending a telemetry to the BE prior to the test
        start_timestamp = (time.time()).__round__() - 30
        send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                  vin=VEHICLE_PAYLOAD["vin"],
                                  cbor_type="nan")
        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        output_template = {
            "firstTelemetryId": str,
            "lastTelemetryId": str,
            "nextTelemetryId": str,
            "telemetry": deepcopy(telemetry_template)
        }
        # The field correctedFuelLevelSmooth is deprecated and cannot be returned for new telemetry, so we remove it
        del output_template.get("telemetry")[0]["correctedFuelLevelSmooth"]
        del output_template.get("telemetry")[0]["fuelLevel"]
        resp = vk_tools.keycore_requests.get_telemetry_journal(start_timestamp=start_timestamp)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        # Remove all the telemetries from the response, except the one sent in the current test
        telemetries = resp.get("telemetry").copy()
        for telemetry in telemetries:
            if not telemetry.get("odometer") or telemetry.get("odometer").get("value") != "nan":
                resp.get("telemetry").remove(telemetry)

        assert len(resp.get("telemetry")) == 0
        logger.info("No telemetry entry available when all values are nan")

        vk_tools.assert_correct_field(output_template, is_template_mandatory=True)

    def test_telemetry_131a_get_telemetry_harsh_braking_high(self):
        """
        Send a ecu message to insert a full telemetry with HARSH_BRAKING_HIGH event.
        Then call the telemetry journal API and check that the response contains the correct fields and that all the values
        inserted are returned by the API
        """
        # Sending a telemetry to the BE prior to the test

        start_timestamp = (time.time()).__round__() - 30
        params = {
            "event": 20,
        }
        send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                  vin=VEHICLE_PAYLOAD["vin"], cbor_type="custom_value", param_list=params)
        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        resp = vk_tools.keycore_requests.get_telemetry_journal(start_timestamp=start_timestamp)
        print(resp)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        telemetry_length = len(resp.get("telemetry"))
        assert resp.get("telemetry")[telemetry_length - 1].get("event") == "HARSH_BRAKING_HIGH"

    def test_telemetry_131b_get_telemetry_harsh_braking_med(self):
        """
        Send a ecu message to insert a full telemetry with HARSH_BRAKING_MED event.
        Then call the telemetry journal API and check that the response contains the correct fields and that all the values
        inserted are returned by the API
        """
        # Sending a telemetry to the BE prior to the test

        start_timestamp = (time.time()).__round__() - 30
        params = {
            "event": 21,
        }
        send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                  vin=VEHICLE_PAYLOAD["vin"], cbor_type="custom_value", param_list=params)
        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        resp = vk_tools.keycore_requests.get_telemetry_journal(start_timestamp=start_timestamp)
        print(resp)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        telemetry_length = len(resp.get("telemetry"))
        assert resp.get("telemetry")[telemetry_length - 1].get("event") == "HARSH_BRAKING_MED"

    def test_telemetry_131c_get_telemetry_harsh_accer(self):
        """
        Send a ecu message to insert a full telemetry with HARSH_ACCELERATION event.
        Then call the telemetry journal API and check that the response contains the correct fields and that all the values
        inserted are returned by the API
        """
        # Sending a telemetry to the BE prior to the test

        start_timestamp = (time.time()).__round__() - 30
        params = {
            "event": 22,
        }
        send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                  vin=VEHICLE_PAYLOAD["vin"], cbor_type="custom_value", param_list=params)
        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        resp = vk_tools.keycore_requests.get_telemetry_journal(start_timestamp=start_timestamp)
        print(resp)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        telemetry_length = len(resp.get("telemetry"))
        assert resp.get("telemetry")[telemetry_length - 1].get("event") == "HARSH_ACCELERATION"

    def test_telemetry_131d_get_telemetry_harsh_cornering(self):
        """
        Send a ecu message to insert a full telemetry with HARSH_CORNERING event.
        Then call the telemetry journal API and check that the response contains the correct fields and that all the values
        inserted are returned by the API
        """
        # Sending a telemetry to the BE prior to the test

        start_timestamp = (time.time()).__round__() - 30
        params = {
            "event": 23,
        }
        send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                  vin=VEHICLE_PAYLOAD["vin"], cbor_type="custom_value", param_list=params)
        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        resp = vk_tools.keycore_requests.get_telemetry_journal(start_timestamp=start_timestamp)
        print(resp)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        telemetry_length = len(resp.get("telemetry"))
        assert resp.get("telemetry")[telemetry_length - 1].get("event") == "HARSH_CORNERING"

    def test_telemetry_131e_get_telemetry_harsh_acc_activity(self):
        """
        Send a ecu message to insert a full telemetry with ACCELEROMETER_ACTIVITY event.
        Then call the telemetry journal API and check that the response contains the correct fields and that all the values
        inserted are returned by the API
        """
        # Sending a telemetry to the BE prior to the test

        start_timestamp = (time.time()).__round__() - 30
        params = {
            "event": 24,
        }
        send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                  vin=VEHICLE_PAYLOAD["vin"], cbor_type="custom_value", param_list=params)
        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        resp = vk_tools.keycore_requests.get_telemetry_journal(start_timestamp=start_timestamp)
        print(resp)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        telemetry_length = len(resp.get("telemetry"))
        assert resp.get("telemetry")[telemetry_length - 1].get("event") == "ACCELEROMETER_ACTIVITY"

    def test_telemetry_140_get_telemetry_merged_negative_time_2sec(self):
        """
        Call the telemetry merged API with a -ve timestamp (-2) and check the response
        """
        time.sleep(2)
        timestamp = -2
        resp = vk_tools.keycore_requests.get_telemetry_merged(start_timestamp=timestamp)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("paginationInfo").get("offset") == 0
        assert resp.get("paginationInfo").get("limit") == 100
        assert resp.get("paginationInfo").get("size") == 0
        assert resp.get("paginationInfo").get("total") == 0

    def test_telemetry_150_get_telemetry_merged_error_future_time(self):
        """
        Call the telemetry merged API with a -ve timestamp (-5) and check the response
        """
        timestamp = 100
        resp = vk_tools.keycore_requests.get_telemetry_merged(start_timestamp=timestamp)
        assert vk_tools.keycore_requests.cloud.response_code == 400
        assert resp.get("message") == "StartTimestamp must be less than 5 mins before current time"
        timestamp = (time.time()).__round__() + 50
        resp = vk_tools.keycore_requests.get_telemetry_merged(start_timestamp=timestamp)
        assert vk_tools.keycore_requests.cloud.response_code == 400
        assert resp.get("message") == "StartTimestamp must be before current time"

    @pytest.mark.skipif(is_keycore_dev(), reason="keycore-dev : 403 forbidden error")
    def test_telemetry_160_open_telemetry_stream(self):
        """
        Test the web socket for getting telemetries:
        - Connect to the websocket
        - Send a telemetry a few seconds later
        - Check that the telemetry was pushed through the websocket
        """

        def run():
            time.sleep(5)
            send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                      vin=VEHICLE_PAYLOAD["vin"], cbor_type="all")

        # Launching the thread that will send a telemetry in 5 seconds
        thread = Thread(target=run)
        thread.start()
        # Connecting with the websocket to receive telemetries
        list_telemetries = vk_tools.receive_telemetry_web_socket()
        assert len(list_telemetries) > 0
        telemetry_found = False
        for telemetry in list_telemetries:
            if telemetry["vin"] == VEHICLE_PAYLOAD["vin"]:
                telemetry_found = True
        assert telemetry_found

    def test_client_device_200_temp_disable_client_device_nfc_vk_check(self):
        """
        Temp disable nfc and try to create vk and check the response.
        """
        nfc_client_device_id = vk_tools.keycore_requests.kc_info['nfc_client_device_id']
        resp = vk_tools.keycore_requests.nfc_temp_disable_enable_client_device(state="disable",
                                                                               client_device_id=nfc_client_device_id)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("id") == vk_tools.keycore_requests.kc_info['nfc_client_device_id']

        # check nfc vk creation
        start_date = int(time.time())
        end_date = start_date + 10 * 60
        payload = {
            "vehicleId": vk_tools.keycore_requests.vehicle.id,
            "clientDeviceId": vk_tools.keycore_requests.kc_info['nfc_client_device_id'],
            "validityStartDate": start_date,
            "validityEndDate": end_date,
            "clientDeviceNumberOfActionsAllowed": vk_tools.data['clientDeviceNumberOfActionsAllowed'],
            "clientDeviceActionsAllowedBitfield": vk_tools.data['clientDeviceActionsAllowedBitfield'],
            "userAuthentication": False,
            "label": "testing"
        }
        vk_tools.keycore_requests.create_vk(payload)
        assert vk_tools.keycore_requests.cloud.response_code == 404

    def test_client_device_210_temp_enable_client_device_nfc_vk_check(self):
        """
        Temp enable nfc and try to create vk and check the response.
        """
        nfc_client_device_id = vk_tools.keycore_requests.kc_info['nfc_client_device_id']
        resp = vk_tools.keycore_requests.nfc_temp_disable_enable_client_device(state="enable",
                                                                               client_device_id=nfc_client_device_id)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("id") == vk_tools.keycore_requests.kc_info['nfc_client_device_id']

        # nfc vk creation
        start_date = int(time.time())
        end_date = start_date + 10 * 60
        payload = {
            "vehicleId": vk_tools.keycore_requests.vehicle.id,
            "clientDeviceId": vk_tools.keycore_requests.kc_info['nfc_client_device_id'],
            "validityStartDate": start_date,
            "validityEndDate": end_date,
            "clientDeviceNumberOfActionsAllowed": vk_tools.data['clientDeviceNumberOfActionsAllowed'],
            "clientDeviceActionsAllowedBitfield": vk_tools.data['clientDeviceActionsAllowedBitfield'],
            "userAuthentication": False,
            "label": "testing"
        }
        resp = vk_tools.keycore_requests.create_vk(payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_creation_template, True)
        vk = resp.get("virtualkey")
        vk_tools.keycore_requests.kc_info['nfc_vk_id'] = vk.get("id")
        assert vk.get("clientDeviceId") == payload["clientDeviceId"]
        assert vk.get("vehicleId") == payload["vehicleId"]
        assert vk.get("validityStartDate") == str(payload["validityStartDate"])
        assert vk.get("validityEndDate") == str(payload["validityEndDate"])
        assert vk.get("clientDeviceActionsAllowed") == []
        assert vk.get("clientDeviceActionsAllowedBitfield") == payload["clientDeviceActionsAllowedBitfield"]
        assert vk.get("clientDeviceNumberOfActionsAllowed") == payload["clientDeviceNumberOfActionsAllowed"]
        assert vk.get("label") == "testing"

    def test_vehicle_120_unlink_vehicle_from_device_with_id(self):
        """
        Unlink the vehicle from the device using the id and check that vehicle is correctly unlinked and VK revoked
        """
        # Need to create a vk in order to check that the vk is revoked after the unlink
        vk_tools.create_vk()
        assert vk_tools.keycore_requests.cloud.response_code == 200

        # Unlink the vehicle/device
        vk_tools.keycore_requests.unlink_vehicle_from_device_with_id()
        assert vk_tools.keycore_requests.cloud.response_code == 200
        time.sleep(10)
        # Get the vehicle to check that it is now unlinked
        resp = vk_tools.keycore_requests.get_vehicle_by_id()
        vehicle = resp.get("vehicles")[0]
        assert vehicle.get("device").get("serialNumber") == ""

        # Check that all the vehicle VK are revoked
        resp = vk_tools.keycore_requests.get_vk_ivkapi(vehicle_id=vk_tools.keycore_requests.vehicle.id)
        for vk in resp.get("virtualKeys"):
            assert vk.get("status") == "REVOKED" or vk.get("status") == "REVOKE_PENDING"
            logger.info("All the VKs are revoked when device is unlinked")

    def test_vehicle_130_disable_vehicle(self):
        """
        Disable the vehicle created in test_create_vehicle and check that the response code is 200
        """
        resp = vk_tools.keycore_requests.disable_vehicle()
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("id") == vk_tools.keycore_requests.vehicle.id

    def test_vehicle_140_disable_already_disabled_vehicle(self):
        """
        Try disabling already disabled vehicle and check for the response and status code
        """
        resp = vk_tools.keycore_requests.disable_vehicle()
        assert vk_tools.keycore_requests.cloud.response_code == 404
        assert resp.get("errorId") == 404
        assert resp.get("message") == "Unable to find resource"

    def test_vehicle_141_update_already_disabled_vehicle(self):
        """
        update the vehicle with already disabled vehicle id and check the response code is 404
        """
        payload = {
            "licensePlate": "TESTING"
        }
        vk_tools.keycore_requests.update_vehicle(payload=payload)
        assert vk_tools.keycore_requests.cloud.response_code == 404

    def test_vehicle_150_unlink_with_invalid_vin(self):
        """
        Try unlink vehicle from invalid vin number and verify error message
        """
        resp = vk_tools.keycore_requests.unlink_vehicle_from_device_with_vin("invalid_vin")
        assert vk_tools.keycore_requests.cloud.response_code == 404
        assert resp.get("message") == "Error getting vehicle by VIN"

    def test_vehicle_160_unlink_vehicle_from_device_with_vin(self):
        """
        Unlink the vehicle from the device using the vin and check that vehicle is correctly unlinked and VK revoked
        """
        # This test needs to create a new vehicle because the 1st one has been disable in previous test
        VEHICLE_PAYLOAD["device"]["serialNumber"] = "{}".format(vk_tools.keycore_requests.kc_info['module_serial'])
        VEHICLE_PAYLOAD["vin"] = str(random.randint(10000000000000000, 99999999999999999))
        payload = VEHICLE_PAYLOAD.copy()
        resp = vk_tools.keycore_requests.create_vehicle_rabbit_device(payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.keycore_requests.vehicle.id = resp.get("id")
        vehicle_id_list.append(resp.get("id"))
        device_serial_list.append(resp.get("device").get("serialNumber"))
        # Need to create a vk in order to check that the vk is revoked after the unlink
        vk_tools.create_vk()
        assert vk_tools.keycore_requests.cloud.response_code == 200

        # unlink vehicle from device
        vk_tools.keycore_requests.unlink_vehicle_from_device_with_vin(VEHICLE_PAYLOAD["vin"])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        # get the vehicle and check that no device is linked to the vehicle anymore
        resp = vk_tools.keycore_requests.get_vehicle_by_id()
        vehicle = resp.get("vehicles")[0]
        assert vehicle.get("device").get("serialNumber") == ""

        # Check that all the vehicle VK are revoked
        resp = vk_tools.keycore_requests.get_vk_ivkapi(vehicle_id=vk_tools.keycore_requests.vehicle.id)
        for vk in resp.get("virtualKeys"):
            assert vk.get("status") == "REVOKED" or vk.get("status") == "REVOKE_PENDING"

    def test_telemetry_170_get_telemetry_merged_negative_time_300sec(self):
        """
        Create 2 vehicles.
        Send a ecu message to insert a full telemetry in both the vehicles.
        Then call the telemetry merged API with negative timestamp of -300 and verify response
        """
        for x in range(2):
            # This test needs to create a new vehicle because the 1st one has been disable in previous test
            VEHICLE_PAYLOAD["device"]["serialNumber"] = "{}".format(vk_tools.keycore_requests.kc_info['module_serial'])
            VEHICLE_PAYLOAD["vin"] = str(random.randint(10000000000000000, 99999999999999999))
            payload = VEHICLE_PAYLOAD.copy()
            resp = vk_tools.keycore_requests.create_vehicle_rabbit_device(payload)
            assert vk_tools.keycore_requests.cloud.response_code == 200
            vk_tools.keycore_requests.vehicle.id = resp.get("id")
            vehicle_id_list.append(resp.get("id"))
            device_serial_list.append(resp.get("device").get("serialNumber"))
            # Need to create a vk in order to check that the vk is revoked after the unlink
            vk_tools.create_vk()
            assert vk_tools.keycore_requests.cloud.response_code == 200

            # Sending a telemetry to the BE prior to the test
            vin_num = VEHICLE_PAYLOAD["vin"]
            device_serial = str(random.randint(10000000000000000, 99999999999999999))
            send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                      vin=vin_num, cbor_type="all")
            time.sleep(3)
            assert vk_tools.keycore_requests.cloud.response_code == 200

            # unlink vehicle from device
            vk_tools.keycore_requests.unlink_vehicle_from_device_with_vin(VEHICLE_PAYLOAD["vin"])
            assert vk_tools.keycore_requests.cloud.response_code == 200
            # get the vehicle and check that no device is linked to the vehicle anymore
            resp = vk_tools.keycore_requests.get_vehicle_by_id()
            vehicle = resp.get("vehicles")[0]
            assert vehicle.get("device").get("serialNumber") == ""
            time.sleep(3)

        timestamp = -300
        resp = vk_tools.keycore_requests.get_telemetry_merged(start_timestamp=timestamp, limit=2)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("paginationInfo").get("limit") == 2
        assert resp.get("paginationInfo").get("size") == 2
        assert resp.get("paginationInfo").get("total") >= 2
        assert resp.get("transactionId") != ""
        assert resp.get("lastTimestamp") != ""
        telemetry_id = resp.get("telemetry")[1].get("telemetryId")
        telemetry_transaction_id = resp.get("transactionId")
        resp = vk_tools.keycore_requests.get_telemetry_merged(transaction_id=telemetry_transaction_id, offset=1)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert telemetry_id == resp.get("telemetry")[0].get("telemetryId")
        assert resp.get("paginationInfo").get("offset") == 1
        current_page_api_data = resp.get("paginationInfo").get("currentPage")
        next_page_api_data = resp.get("paginationInfo").get("nextPage")
        previous_page_api_data = resp.get("paginationInfo").get("previousPage")
        current_page = "/1/vehicles/all/telemetry/merged?transactionId={}".format(
            telemetry_transaction_id) + "\u0026limit=100\u0026offset=1"
        next_page = ""
        previous_page = "/1/vehicles/all/telemetry/merged?transactionId={}".format(
            telemetry_transaction_id) + "\u0026limit=1\u0026offset=0"
        assert current_page_api_data == current_page
        assert next_page_api_data == next_page
        assert previous_page_api_data == previous_page

        # Testing transactionId and offset parameters
        resp = vk_tools.keycore_requests.get_telemetry_merged(transaction_id=telemetry_transaction_id, offset=1)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("telemetry")[0].get("telemetryId") == telemetry_id

        # Testing start_timestamp and transaction_id at the same time
        timestamp = (time.time()).__round__() - 290
        resp = vk_tools.keycore_requests.get_telemetry_merged(start_timestamp=timestamp,
                                                              transaction_id=telemetry_transaction_id)

        assert vk_tools.keycore_requests.cloud.response_code == 400
        # assert resp.get("errorId") == 10030002
        assert resp.get("message") == "One of either startTimestamp or transactionId must be specified. Both were given"

    def test_vehicle_180_link_vehicle_with_device_using_vehicle_id(self):
        """
        Link vehicle with device using vehicle id
        """
        logger.info("Link vehicle with device using vehicle id")

        vin_payload = vehicle_payload_with_no_device.copy()
        vin_resp = vk_tools.keycore_requests.create_vehicle(vin_payload)
        vehicle_id = vin_resp.get("id")
        vk_tools.keycore_requests.authenticate()
        vk_tools.keycore_requests.create_module_and_device_rabbit()
        device_serial = str(vk_tools.keycore_requests.kc_info['module_serial'])
        resp = vk_tools.keycore_requests.link_vehicle_with_device_using_vehicle_id(vehicle_id=vehicle_id,
                                                                                   device_serial=device_serial)
        assert vk_tools.keycore_requests.cloud.response_code == 200

    def test_vehicle_181_link_vehicle_with_device_using_vehicle_vin(self):
        """
        Link vehicle with device using vehicle VIN
        """
        logger.info("Link vehicle with device using vehicle VIN")
        vehicle_id_1 = vk_tools.keycore_requests.vehicle.id
        device_serial_1 = str(vk_tools.keycore_requests.kc_info['module_serial'])

        VEHICLE_PAYLOAD_WITH_NO_DEVICE["vin"] = str(random.randint(10000000000000000, 99999999999999999))
        vin_payload = VEHICLE_PAYLOAD_WITH_NO_DEVICE.copy()
        vin_resp = vk_tools.keycore_requests.create_vehicle(vin_payload)
        vehicle_id = vin_resp.get("vin")
        vin = vin_resp.get("id")
        vk_tools.keycore_requests.authenticate()
        vk_tools.keycore_requests.create_module_and_device_rabbit()
        device_serial = str(vk_tools.keycore_requests.kc_info['module_serial'])
        resp = vk_tools.keycore_requests.link_vehicle_with_device_using_vehicle_vin(vin=vin,
                                                                                    device_serial=device_serial)
        logger.info(resp)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        logger.info("Verify swapping of vehicle and devices are working...")
        logger.info("Unlinking the two vehicles from devices")
        vk_tools.keycore_requests.unlink_vehicle_from_device_with_id(vehicle_id=vehicle_id_1,
                                                                     device_serial=device_serial_1)
        vk_tools.keycore_requests.unlink_vehicle_from_device_with_vin(vehicle_vin=VEHICLE_PAYLOAD_WITH_NO_DEVICE["vin"],
                                                                      device_serial=vk_tools.keycore_requests.kc_info[
                                                                          'module_serial'])
        logger.info("Link vehicle_1 with device_2")
        resp = vk_tools.keycore_requests.link_vehicle_with_device_using_vehicle_id(vehicle_id=vehicle_id_1,
                                                                                   device_serial=
                                                                                   vk_tools.keycore_requests.kc_info[
                                                                                       'module_serial'])
        logger.info(resp)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        logger.info("Link vehicle_1 with device_2 - success")
        logger.info("Link the vehicle_2 with device_1")
        resp = vk_tools.keycore_requests.link_vehicle_with_device_using_vehicle_vin(
            vin=VEHICLE_PAYLOAD_WITH_NO_DEVICE["vin"],
            device_serial=device_serial_1)
        logger.info(resp)
        vk_tools.keycore_requests.kc_info['module_serial'] = device_serial_1
        assert vk_tools.keycore_requests.cloud.response_code == 200
        logger.info("Link the vehicle_2 with device_1 - success")

    def test_vehicle_182_link_vehicle_which_is_already_linked(self):
        """
        Link vehicle with device using vehicle VIN
        """
        logger.info("Link vehicle with device using vehicle VIN")

        resp = vk_tools.keycore_requests.link_vehicle_with_device_using_vehicle_id(
            vehicle_id=vk_tools.keycore_requests.vehicle.id,
            device_serial=vk_tools.keycore_requests.kc_info['module_serial'])
        assert resp.get("errorId") == 1104
        assert resp.get("message") == 'Cannot create resource. ID already exists'
        assert vk_tools.keycore_requests.cloud.response_code == 409

        resp = vk_tools.keycore_requests.link_vehicle_with_device_using_vehicle_vin(
            vin=VEHICLE_PAYLOAD_WITH_NO_DEVICE["vin"],
            device_serial=vk_tools.keycore_requests.kc_info['module_serial'])
        assert resp.get("errorId") == 1104
        assert resp.get("message") == 'Cannot create resource. ID already exists'
        assert vk_tools.keycore_requests.cloud.response_code == 409

    def test_vehicle_183_link_vehicle_with_invalid_device_serial(self):
        """
        Try linking vehicle with invalid device serial number, it should return 404 error.
        """

        vk_tools.keycore_requests.unlink_vehicle_from_device_with_vin(vehicle_vin=VEHICLE_PAYLOAD_WITH_NO_DEVICE["vin"],
                                                                      device_serial=vk_tools.keycore_requests.kc_info[
                                                                          'module_serial'])
        logger.info("Link vehicle with invalid device serial...")
        resp = vk_tools.keycore_requests.link_vehicle_with_device_using_vehicle_id(
            vehicle_id=vk_tools.keycore_requests.vehicle.id,
            device_serial="invalid_serial")
        assert resp.get('errorId') == 404
        assert resp.get('message') == 'Unable to find resource'
        assert vk_tools.keycore_requests.cloud.response_code == 404

        resp = vk_tools.keycore_requests.link_vehicle_with_device_using_vehicle_vin(
            vin=VEHICLE_PAYLOAD_WITH_NO_DEVICE["vin"],
            device_serial="invalid_serial")
        assert resp.get('errorId') == 404
        assert resp.get('message') == 'Unable to find resource'
        assert vk_tools.keycore_requests.cloud.response_code == 404

    def test_vehicle_184_link_vehicle_with_invalid_vehicle_id_and_vin(self):
        """
        Link vehicle with device using invalid vehicle id and vin
        """
        logger.info("Link vehicle with device using invalid vehicle id and vin")

        resp = vk_tools.keycore_requests.link_vehicle_with_device_using_vehicle_id(vehicle_id="invalid_vehicle_id",
                                                                                   device_serial=
                                                                                   vk_tools.keycore_requests.kc_info[
                                                                                       'module_serial'])
        assert resp.get('errorId') == 404
        assert resp.get('message') == 'Unable to find resource'
        assert vk_tools.keycore_requests.cloud.response_code == 404

        resp = vk_tools.keycore_requests.link_vehicle_with_device_using_vehicle_vin(vin="invalid_vin",
                                                                                    device_serial=
                                                                                    vk_tools.keycore_requests.kc_info[
                                                                                        'module_serial'])
        assert resp.get('errorId') == 404
        assert resp.get('message') == 'Unable to find resource'
        assert vk_tools.keycore_requests.cloud.response_code == 404

    def test_vehicle_185_check_permission_when_link_vehicle(self):
        """
        Try linking a vehicle with device from the user who doesnt have a permission, it should give 403 error.
        """
        apikeyNoRights = get_env_organisation_item("apikeyNoRights")
        secretkeyNoRights = get_env_organisation_item("secretkeyNoRights")
        resp = vk_tools.keycore_requests.link_vehicle_with_device_using_vehicle_id(
            vehicle_id=vk_tools.keycore_requests.vehicle.id,
            device_serial=vk_tools.keycore_requests.kc_info['module_serial'],
            custom_apikey=apikeyNoRights,
            custom_secretkey=secretkeyNoRights)
        assert resp.get('errorId') == 10000000
        assert resp.get('message') == 'Authentication failed. Access denied'
        assert vk_tools.keycore_requests.cloud.response_code == 403

        resp = vk_tools.keycore_requests.link_vehicle_with_device_using_vehicle_vin(
            vin=VEHICLE_PAYLOAD_WITH_NO_DEVICE["vin"],
            device_serial=vk_tools.keycore_requests.kc_info['module_serial'],
            custom_apikey=apikeyNoRights,
            custom_secretkey=secretkeyNoRights)
        assert resp.get('errorId') == 10000000
        assert resp.get('message') == 'Authentication failed. Access denied'
        assert vk_tools.keycore_requests.cloud.response_code == 403

    def test_ev_010_create_electric_vehicle(self):
        """
        Create a electric vehicle and check that the response body contains the correct fields
        Stores the vehicle id for next tests
        """
        vk_tools.keycore_requests.authenticate()
        vk_tools.keycore_requests.create_module_and_device_rabbit()

        ELECTRIC_VEHICLE_PAYLOAD["device"]["serialNumber"] = "{}".format(
            vk_tools.keycore_requests.kc_info['module_serial'])
        payload = ELECTRIC_VEHICLE_PAYLOAD.copy()

        resp = vk_tools.keycore_requests.create_vehicle_rabbit_device(payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.keycore_requests.vehicle.id = resp.get("id")
        vehicle_id_list.append(resp.get("id"))
        device_serial_list.append(resp.get("device").get("serialNumber"))
        assert resp.get("enabled") == ELECTRIC_VEHICLE_PAYLOAD["enabled"]
        assert resp.get("device").get("type") == ELECTRIC_VEHICLE_PAYLOAD["device"]["type"]
        assert resp.get("device").get("serialNumber") == ELECTRIC_VEHICLE_PAYLOAD["device"]["serialNumber"]
        assert resp.get("vin") == ELECTRIC_VEHICLE_PAYLOAD["vin"]
        assert resp.get("make") == ELECTRIC_VEHICLE_PAYLOAD["make"]
        assert resp.get("model") == ELECTRIC_VEHICLE_PAYLOAD["model"]
        assert resp.get("year") == int(ELECTRIC_VEHICLE_PAYLOAD["year"])
        assert resp.get("licensePlate") == ELECTRIC_VEHICLE_PAYLOAD["licensePlate"]
        assert resp.get("color") == ELECTRIC_VEHICLE_PAYLOAD["color"]
        assert resp.get("tank_capacity") == ELECTRIC_VEHICLE_PAYLOAD["tank_capacity"]
        assert resp.get("generation") == ELECTRIC_VEHICLE_PAYLOAD["generation"]
        assert resp.get("transmissionType") == ELECTRIC_VEHICLE_PAYLOAD["transmissionType"]
        assert resp.get("regionOfSale") == ELECTRIC_VEHICLE_PAYLOAD["regionOfSale"]
        assert resp.get("engineType") == ELECTRIC_VEHICLE_PAYLOAD["engineType"]
        assert resp.get("engineSize") == ELECTRIC_VEHICLE_PAYLOAD["engineSize"]
        assert resp.get("protocol") == ELECTRIC_VEHICLE_PAYLOAD["protocol"]

    def test_ev_020_get_electric_vehicle_by_id(self):
        """
        Get the electric vehicle created by test_create_electric_vehicle and check that the response contains the correct fields
        """
        resp = vk_tools.keycore_requests.get_vehicle_by_id()
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(resp.get("vehicles")) == 1
        vehicle = resp.get("vehicles")[0]
        assert vehicle.get("enabled") == ELECTRIC_VEHICLE_PAYLOAD["enabled"]
        assert vehicle.get("device").get("type") == ELECTRIC_VEHICLE_PAYLOAD["device"]["type"]
        assert vehicle.get("device").get("serialNumber") == ELECTRIC_VEHICLE_PAYLOAD["device"]["serialNumber"]
        assert vehicle.get("vin") == ELECTRIC_VEHICLE_PAYLOAD["vin"]
        assert vehicle.get("make") == ELECTRIC_VEHICLE_PAYLOAD["make"]
        assert vehicle.get("model") == ELECTRIC_VEHICLE_PAYLOAD["model"]
        assert vehicle.get("year") == ELECTRIC_VEHICLE_PAYLOAD["year"]
        assert vehicle.get("licensePlate") == ELECTRIC_VEHICLE_PAYLOAD["licensePlate"]
        assert vehicle.get("color") == ELECTRIC_VEHICLE_PAYLOAD["color"]
        assert vehicle.get("tank_capacity") == ELECTRIC_VEHICLE_PAYLOAD["tank_capacity"]
        assert vehicle.get("generation") == ELECTRIC_VEHICLE_PAYLOAD["generation"]
        assert vehicle.get("transmissionType") == ELECTRIC_VEHICLE_PAYLOAD["transmissionType"]
        assert vehicle.get("regionOfSale") == ELECTRIC_VEHICLE_PAYLOAD["regionOfSale"]
        assert vehicle.get("engineType") == ELECTRIC_VEHICLE_PAYLOAD["engineType"]
        assert vehicle.get("engineSize") == ELECTRIC_VEHICLE_PAYLOAD["engineSize"]
        assert vehicle.get("protocol") == ELECTRIC_VEHICLE_PAYLOAD["protocol"]

    def test_ev_030_create_vk_for_ev(self):
        self.test_vk_011_create_vk()

    def test_ev_040_test_get_vks_for_ev(self):
        self.test_vk_060_get_vks()

    def test_ev_050_update_vk_for_ev(self):
        self.test_vk_170_update_vk()

    def test_ev_060_revoke_vk_for_ev(self):
        self.test_vk_200_revoke_vk()

    def test_ev_070_get_ev_telemetry_merged_negative_time_60sec(self):
        """
        Send a ecu message to insert a full telemetry for electric vehicle.
        Call the telemetry merged API with a -ve timestamp (-60) and check the response
        """
        # Sending a telemetry to the BE prior to the test
        send_telemetry_ecu_custom(device_serial=ELECTRIC_VEHICLE_PAYLOAD["device"]["serialNumber"],
                                  vin=ELECTRIC_VEHICLE_PAYLOAD["vin"], cbor_type="ev")
        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        timestamp = -60
        resp = vk_tools.keycore_requests.get_telemetry_merged(start_timestamp=timestamp)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("paginationInfo").get("offset") == 0
        assert resp.get("paginationInfo").get("limit") == 100
        assert resp.get("paginationInfo").get("size") >= 1
        assert resp.get("paginationInfo").get("total") >= 1
        assert resp.get("transactionId") == ""
        assert resp.get("lastTimestamp") != ""

    def test_ev_080_unlink_ev_vehicle_from_device_with_id(self):
        self.test_vehicle_120_unlink_vehicle_from_device_with_id()

    def test_ev_090_disable_ev_vehicle(self):
        self.test_vehicle_130_disable_vehicle()

    def test_telemetry_073_get_vehicle_telemetry_last(self):
        """
        Call the telemetry API for specific vehicle with vin to get the last telemetry
        and check the response
        """
        # This test needs to create a new vehicle because the 1st one has been disable in previous test
        VEHICLE_PAYLOAD["device"]["serialNumber"] = "{}".format(vk_tools.keycore_requests.kc_info['module_serial'])
        VEHICLE_PAYLOAD["vin"] = str(random.randint(10000000000000000, 99999999999999999))
        payload = VEHICLE_PAYLOAD.copy()
        resp = vk_tools.keycore_requests.create_vehicle_rabbit_device(payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.keycore_requests.vehicle.id = resp.get("id")
        vehicle_id_list.append(resp.get("id"))
        device_serial_list.append(resp.get("device").get("serialNumber"))
        # Need to create a vk in order to check that the vk is revoked after the unlink
        vk_tools.create_vk()
        assert vk_tools.keycore_requests.cloud.response_code == 200

        # Sending a telemetry to the BE prior to the test
        vin_num = VEHICLE_PAYLOAD["vin"]
        send_telemetry_ecu_custom(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"],
                                  vin=VEHICLE_PAYLOAD["vin"], cbor_type="all")
        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        # Getting vehicle telemetry
        resp = vk_tools.keycore_requests.get_vehicle_telemetry(vin=vin_num, start_timestamp=-300)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vehicle_id_from_vehicle_data = resp.get("telemetry")[0].get("vehicleId")
        device_serial_from_vehicle_data = resp.get("telemetry")[0].get("deviceId")
        fuel_level_info_from_vehicle_data = resp.get("telemetry")[0].get("fuelLevel")
        ignition_info_from_vehicle_data = resp.get("telemetry")[0].get("ignitionReconstructionStatus")
        location_info_from_vehicle_data = resp.get("telemetry")[0].get("location")
        odometer_info_from_vehicle_data = resp.get("telemetry")[0].get("odometer")

        # Getting latest telemetry
        resp = vk_tools.keycore_requests.get_latest_vehicle_telemetry(vin=vin_num)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("vehicleId") == vehicle_id_from_vehicle_data
        assert resp.get("Items").get("ignitionStatus").get("timestamp") == ignition_info_from_vehicle_data.get(
            "timestamp")
        assert resp.get("Items").get("ignitionStatus").get("value") == ignition_info_from_vehicle_data.get("value")
        assert resp.get("Items").get("location").get("timestamp") == location_info_from_vehicle_data.get("timestamp")
        assert resp.get("Items").get("location").get("latitude") == location_info_from_vehicle_data.get("latitude")
        assert resp.get("Items").get("location").get("longitude") == location_info_from_vehicle_data.get("longitude")
        assert resp.get("Items").get("odometer").get("timestamp") == odometer_info_from_vehicle_data.get("timestamp")
        assert round(resp.get("Items").get("odometer").get("value")) == round(
            odometer_info_from_vehicle_data.get("value"))
        assert resp.get("Items").get("odometer").get("unit") == odometer_info_from_vehicle_data.get("unit")
        assert resp.get("Items").get("fuelLevel").get("timestamp") == fuel_level_info_from_vehicle_data.get("timestamp")
        assert resp.get("Items").get("fuelLevel").get("unit") == fuel_level_info_from_vehicle_data.get("unit")
        assert resp.get("serial") == device_serial_from_vehicle_data
        assert round(resp.get("Items").get("fuelLevel").get("value"), 2) == round(
            fuel_level_info_from_vehicle_data.get("value"), 2)

        # unlink vehicle from device
        vk_tools.keycore_requests.unlink_vehicle_from_device_with_vin(VEHICLE_PAYLOAD["vin"])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        # get the vehicle and check that no device is linked to the vehicle anymore
        resp = vk_tools.keycore_requests.get_vehicle_by_id()
        vehicle = resp.get("vehicles")[0]
        assert vehicle.get("device").get("serialNumber") == ""
        time.sleep(3)

    def test_telemetry_074_get_electric_vehicle_telemetry_last(self):
        """
        Call the telemetry API for specific electric vehicle with vin to get the last telemetry
        and check the response
        """
        # Sending a telemetry to the BE prior to the test
        electric_vehicle_vin = ELECTRIC_VEHICLE_PAYLOAD["vin"]
        send_telemetry_ecu_custom(device_serial=ELECTRIC_VEHICLE_PAYLOAD["device"]["serialNumber"],
                                  vin=ELECTRIC_VEHICLE_PAYLOAD["vin"], cbor_type="ev")
        time.sleep(3)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        resp = vk_tools.keycore_requests.get_vehicle_telemetry(vin=electric_vehicle_vin, start_timestamp=-300)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vehicle_id_from_vehicle_data = resp.get("telemetry")[0].get("vehicleId")
        device_serial_from_vehicle_data = resp.get("telemetry")[0].get("deviceId")
        fuel_level_info_from_vehicle_data = resp.get("telemetry")[0].get("fuelLevel")
        ignition_info_from_vehicle_data = resp.get("telemetry")[0].get("ignitionReconstructionStatus")
        location_info_from_vehicle_data = resp.get("telemetry")[0].get("location")
        odometer_info_from_vehicle_data = resp.get("telemetry")[0].get("odometer")
        state_of_charge_info_from_vehicle_data = resp.get("telemetry")[0].get("stateOfCharge")

        # Getting latest telemetry
        resp = vk_tools.keycore_requests.get_latest_vehicle_telemetry(vin=electric_vehicle_vin)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("vehicleId") == vehicle_id_from_vehicle_data
        assert resp.get("Items").get("ignitionStatus").get("timestamp") == ignition_info_from_vehicle_data.get(
            "timestamp")
        assert resp.get("Items").get("ignitionStatus").get("value") == ignition_info_from_vehicle_data.get("value")
        assert resp.get("Items").get("location").get("timestamp") == location_info_from_vehicle_data.get("timestamp")
        assert resp.get("Items").get("location").get("latitude") == location_info_from_vehicle_data.get("latitude")
        assert resp.get("Items").get("location").get("longitude") == location_info_from_vehicle_data.get("longitude")
        assert resp.get("Items").get("odometer").get("timestamp") == odometer_info_from_vehicle_data.get("timestamp")
        assert round(resp.get("Items").get("odometer").get("value")) == round(
            odometer_info_from_vehicle_data.get("value"))
        assert resp.get("Items").get("odometer").get("unit") == odometer_info_from_vehicle_data.get("unit")
        assert resp.get("Items").get("fuelLevel").get("timestamp") == fuel_level_info_from_vehicle_data.get("timestamp")
        assert resp.get("Items").get("fuelLevel").get("unit") == fuel_level_info_from_vehicle_data.get("unit")
        assert resp.get("Items").get("stateOfCharge").get("timestamp") == state_of_charge_info_from_vehicle_data.get(
            "timestamp")
        assert round(resp.get("Items").get("stateOfCharge").get("value"), 2) == round(
            state_of_charge_info_from_vehicle_data.get(
                "value"), 2)
        assert resp.get("Items").get("stateOfCharge").get("unit") == state_of_charge_info_from_vehicle_data.get(
            "unit")
        assert resp.get("serial") == device_serial_from_vehicle_data
        assert round(resp.get("Items").get("fuelLevel").get("value"), 2) == round(
            fuel_level_info_from_vehicle_data.get("value"), 2)

        # unlink vehicle from device
        resp = vk_tools.keycore_requests.unlink_vehicle_from_device_with_vin(ELECTRIC_VEHICLE_PAYLOAD["vin"])

        if vk_tools.keycore_requests.cloud.response_code == 400:
            assert str(resp.get("errorId")) == "1102"
            assert resp.get("message") == "Vehicle not linked with device"
        else:
            assert vk_tools.keycore_requests.cloud.response_code == 200
            # get the vehicle and check that no device is linked to the vehicle anymore
            resp = vk_tools.keycore_requests.get_vehicle_by_id()
            vehicle = resp.get("vehicles")[0]
            assert vehicle.get("device").get("serialNumber") == ""
            time.sleep(3)

    def test_client_device_100_disable_client_device(self):
        """
        Disable the device created in test_create_client_device
        Check that the response contains the correct id and has the correct length
        """
        new_cd_id = vk_tools.keycore_requests.kc_info['new_cd_id']
        resp = vk_tools.keycore_requests.disable_clientdevice(new_cd_id).json()

        assert resp.get("id") == new_cd_id and len(resp) == 1, \
            "Wrong response format for disabling client device"

    def test_client_device_101_temp_disable_nfc_before_delete(self):
        """
        Temp disable the nfc and check the response
        """
        nfc_client_device_id = vk_tools.keycore_requests.kc_info['nfc_client_device_id']
        resp = vk_tools.keycore_requests.nfc_temp_disable_enable_client_device(state="disable",
                                                                               client_device_id=nfc_client_device_id)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("id") == vk_tools.keycore_requests.kc_info['nfc_client_device_id']

    def test_client_device_102_delete_client_device_nfc(self):
        """
        Disable the device created in nfc create client device test
        Check that the response contains the correct id and has the correct length
        """
        new_nfc_client_device_id = vk_tools.keycore_requests.kc_info['nfc_client_device_id']
        resp = vk_tools.keycore_requests.disable_clientdevice(new_nfc_client_device_id).json()
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("id") == new_nfc_client_device_id and len(resp) == 1, \
            "Wrong response format for disabling client device"

    def test_client_device_102_nfc_create_vk_already_deleted_client_device(self):
        """
        Create a virtual key with nfc for the vehicle created by test_create_vehicle
        on already deleted client device, Check that the response contains the correct fields
        """
        start_date = int(time.time())
        end_date = start_date + 10 * 60
        payload = {
            "vehicleId": vk_tools.keycore_requests.vehicle.id,
            "clientDeviceId": vk_tools.keycore_requests.kc_info['nfc_client_device_id'],
            "validityStartDate": start_date,
            "validityEndDate": end_date,
            "clientDeviceNumberOfActionsAllowed": vk_tools.data['clientDeviceNumberOfActionsAllowed'],
            "clientDeviceActionsAllowedBitfield": vk_tools.data['clientDeviceActionsAllowedBitfield'],
            "userAuthentication": False,
            "label": "testing"
        }
        resp = vk_tools.keycore_requests.create_vk(payload)
        assert vk_tools.keycore_requests.cloud.response_code == 404
        assert resp.get("errorId") == 404
        assert resp.get("message") == "Unable to find resource"

    def test_client_device_110_disable_already_disabled_client_device(self):
        """
        Try disabling already disabled client device and check for the response and status code
        """
        new_cd_id = vk_tools.keycore_requests.kc_info['new_cd_id']
        resp = vk_tools.keycore_requests.disable_clientdevice(new_cd_id).json()
        assert vk_tools.keycore_requests.cloud.response_code == 404
        assert resp.get("errorId") == 404
        assert resp.get("message") == "Unable to find resource"

    def test_client_device_120_delete_bulk_created_nfc(self):
        """
            Delete the NFCs created in bulk in the previous tests
        """
        resp = vk_tools.keycore_requests.get_client_device_nfc_v2(limit=100)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        total_number_of_nfc = resp.get("paginationInfo").get("total")

        cd_list = vk_tools.keycore_requests.get_all_client_device_id_list()
        #    for tag_id in nfc_tag_ids_bulk_created:
        for tag_id in vk_tools.keycore_requests.kc_info['nfc_tag_ids_list']:
            for i in range(total_number_of_nfc):
                if tag_id == cd_list[i]["NFC_tag_id"]:
                    vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list'].append(cd_list[i]["id"])
                    break
        for client_device_id in vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']:
            vk_tools.keycore_requests.disable_clientdevice(client_device_id).json()
            assert vk_tools.keycore_requests.cloud.response_code == 200

        resp = vk_tools.keycore_requests.get_client_device_nfc_v2(limit=100)
        assert vk_tools.keycore_requests.cloud.response_code == 200

        total_number_of_nfc_after_disable = resp.get("paginationInfo").get("total")
        assert total_number_of_nfc_after_disable != total_number_of_nfc

    def test_cleanup_010_cleanup_data(self):
        """
        Delete the vehicles and devices created during the campaign
        """
        # Delete vehicles
        for v_id in vehicle_id_list:
            vk_tools.keycore_requests.delete_vehicle(v_id)

        # Delete devices (must get device list first in order to retrieve the internal id of devices)
        finished = False
        id_from_serial = {}
        page = 0
        while not finished:
            resp = vk_tools.keycore_requests.get_devices(page_size=100, page=page)
            for device in resp.get("data"):
                id_from_serial[device.get("serial")] = device.get("id")
            page += 1
            if page >= resp.get("paginationInfo").get("total_pages"):
                finished = True

        for d_serial in device_serial_list:
            vk_tools.keycore_requests.delete_device(id_from_serial[d_serial])

    def test_00_reset_variables(self):
        """
        Reset the below items before proceeding with actual execution
        """
        vk_tools.keycore_requests.kc_info['nfc_tag_ids_list'].clear()
        vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list'].clear()

    def test_00a_create_client_device_in_bulk(self):
        """
        Create client devices using bulk create nfc client device api and get the ids of those client devices to use
        """
        # create client devices
        for i in range(2):
            random_string = "a" + str(random.randint(1000000, 9999999))
            vk_tools.keycore_requests.kc_info['nfc_tag_ids_list'].append(random_string)
        payload = {
            "nfcTagIds": vk_tools.keycore_requests.kc_info['nfc_tag_ids_list']
        }
        resp = vk_tools.keycore_requests.create_nfc_client_device_bulk(payload=payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert vk_tools.keycore_requests.kc_info['nfc_tag_ids_list'] == resp.get(
            "nfcTagIdsAdded"), "nfc batches created are not as per the list provided"
        assert len(resp.get("errors")) == 0
        logger.info("list of nfc client devices created" + str(resp.get("nfcTagIdsAdded")))

        # get the client devices to read the client device ids created
        cd_list = vk_tools.keycore_requests.get_all_client_device_id_list()
        for cd in cd_list:
            if cd.get('NFC_tag_id') in vk_tools.keycore_requests.kc_info['nfc_tag_ids_list']:
                vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list'].append(cd.get('id'))
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']) == len(
            vk_tools.keycore_requests.kc_info['nfc_tag_ids_list'])
        logger.info("client device ids for the nfc badges '{}' are '{}'".format(
            vk_tools.keycore_requests.kc_info['nfc_tag_ids_list'],
            vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']))

    def test_01a_temp_disable_bulk_nfc_valid_cd_ids(self):
        """
        Temp disable nfc client devices which are enabled in bulk and check that the response contains correct fields
        """
        # S#04: Temp disable nfc in bulk [all the nfcs are enabled]
        disable_payload = {
            "ids": vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']
        }
        disable_resp = vk_tools.keycore_requests.disable_nfc_client_device_bulk(payload=disable_payload)
        assert vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list'] == disable_resp.get(
            'ids_disabled'), "Some client devices are not disabled, errors are: " + str(disable_resp.get('errors'))
        assert vk_tools.keycore_requests.cloud.response_code == 200
        logger.info(
            "disabled client devices are: " + str(vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']))

    def test_01b_temp_disable_bulk_already_temp_disabled_cd_ids(self):
        """
        Temp disable nfc client devices which are already temp disabled and check that the response is valid
        """
        # S#06: temp disable the client devices [that are already temp disabled] by the client device id
        disable_payload = {
            "ids": vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']
        }
        disable_resp = vk_tools.keycore_requests.disable_nfc_client_device_bulk(payload=disable_payload)
        assert len(disable_resp.get('ids_disabled')) == 0, "Some client devices disabled again, errors are: " + str(
            disable_resp.get('ids_disabled'))
        assert vk_tools.keycore_requests.cloud.response_code == 200
        logger.info("Expected error when disabling the disabled cds already: " + str(disable_resp.get('errors')))

    def test_01c_enable_bulk_nfc_valid_cd_ids(self):
        """
        Enable nfc client devices which temp disabled and check that the response is valid
        """
        # S#01: Enable the client devices by the client device id
        enable_payload = {
            "ids": vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']
        }
        enable_resp = vk_tools.keycore_requests.enable_nfc_client_device_bulk(payload=enable_payload)
        assert vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list'] == enable_resp.get(
            'ids_enabled'), "Some client devices are not enabled, errors are: " + str(enable_resp.get('errors'))
        logger.info(
            "enabled client devices are: " + str(vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']))
        assert vk_tools.keycore_requests.cloud.response_code == 200

    def test_01d_enable_bulk_nfc_valid_cd_ids(self):
        """
        Enable nfc client devices which are already enabled and check that the response is valid
        """
        # S#03: Enable the client devices [that are already enabled] by the client device id
        enable_payload = {
            "ids": vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']
        }
        enable_resp = vk_tools.keycore_requests.enable_nfc_client_device_bulk(payload=enable_payload)
        assert len(enable_resp.get('ids_enabled')) == 0, "Some client devices enabled again, errors are: " + str(
            enable_resp.get('ids_enabled'))
        logger.info(
            "expected error response when trying to enable the enabled devices: " + str(enable_resp.get('errors')))
        assert vk_tools.keycore_requests.cloud.response_code == 200

    def test_00b_delete_nfc_client_devices(self):
        """
        Delete the client devices to do validation with deleted client devices in bulk api call
        """
        # disable (Delete) the client devices by client device id
        for new_nfc_client_device_id in vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']:
            delete_resp = vk_tools.keycore_requests.disable_clientdevice(new_nfc_client_device_id).json()
            assert delete_resp.get(
                "id") == new_nfc_client_device_id, "Wrong response format for disabling client device"
            logger.info(new_nfc_client_device_id + " is deleted")
            assert vk_tools.keycore_requests.cloud.response_code == 200

    def test_01e_temp_disable_bulk_nfc_deleted_cd_ids(self):
        """
        Temp disable the client devices with deleted client devices in bulk
        """
        # S#05: temp disable nfc client devices [that are deleted] in bulk
        disable_payload = {
            "ids": vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']
        }
        disable_resp = vk_tools.keycore_requests.disable_nfc_client_device_bulk(payload=disable_payload)
        assert len(
            disable_resp.get('ids_disabled')) == 0, "Some client devices disabled unexpectedly, those are: " + str(
            disable_resp.get('ids_disabled'))
        assert vk_tools.keycore_requests.cloud.response_code == 200
        logger.info("Expected Error Response when temp disabling the deleted cds: " + str(disable_resp.get("errors")))

    def test_01f_enable_bulk_nfc_deleted_cd_ids(self):
        """
        Enable the client devices with deleted client devices in bulk
        """
        # S#02: enable nfc client devices [that are deleted] in bulk
        enable_payload = {
            "ids": vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']
        }
        enable_resp = vk_tools.keycore_requests.enable_nfc_client_device_bulk(payload=enable_payload)
        assert len(
            enable_resp.get('ids_enabled')) == 0, "Some client devices are enabled unexpectedly, errors are: " + str(
            enable_resp.get('ids_enabled'))
        assert vk_tools.keycore_requests.cloud.response_code == 200
        logger.info("Expected Error Response when enabling deleted cds: " + str(enable_resp.get("errors")))

    def test_02a_temp_disable_bulk_nfc_with_no_client_device(self):
        """
        Temp disable the client devices with no client devices in bulk
        """
        # S#16: temp disable the client devices by the client device id
        disable_payload = {
            "ids": []  # "" - can also be applied
        }
        disable_resp = vk_tools.keycore_requests.disable_nfc_client_device_bulk(payload=disable_payload)
        assert vk_tools.keycore_requests.cloud.response_code == 400
        assert disable_resp.get("errorId") == 1102
        assert disable_resp.get("message") == 'Field is invalid'
        logger.info("disable api response for empty payload: " + str(disable_resp))

    def test_02b_enable_bulk_nfc_with_no_client_device(self):
        """
        Enable the client devices with no client devices in bulk
        """
        # S#17: Enable the client devices by the client device id
        enable_payload = {
            "ids": []
        }
        enable_resp = vk_tools.keycore_requests.enable_nfc_client_device_bulk(payload=enable_payload)
        assert vk_tools.keycore_requests.cloud.response_code == 400
        assert enable_resp.get("errorId") == 1102
        assert enable_resp.get("message") == 'Field is invalid'
        logger.info("Enable api response for empty payload: " + str(enable_resp))

    def test_02c_temp_disable_bulk_nfc_invalid_client_ids(self):
        """
        Temp disable the client devices with invalid client devices in bulk
        """
        # S#19: temp disable the client devices by the client device id
        invalid_list = ["dummy", "dummy"]
        disable_payload = {
            "ids": invalid_list  # non existing ids
        }
        disable_resp = vk_tools.keycore_requests.disable_nfc_client_device_bulk(payload=disable_payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(disable_resp.get('ids_disabled')) == 0
        error_list = disable_resp.get('errors')
        for val in invalid_list:
            if not any(val in s for s in error_list):
                logger.error(val + " is not supposed to be enabled, some error")
                assert False
        assert vk_tools.keycore_requests.cloud.response_code == 200
        logger.info("Expected error when invalid cds are disabled: " + str(disable_resp.get('errors')))

    def test_02d_temp_disable_bulk_nfc_invalid_client_ids(self):
        """
        Enable the client devices with invalid client devices in bulk
        """
        # S#18: Enable the client devices by the client device id
        invalid_list = ["dummy", "dummy"]
        enable_payload = {
            "ids": ["dummy", "dummy"]  # non existing ids
        }
        enable_resp = vk_tools.keycore_requests.enable_nfc_client_device_bulk(payload=enable_payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(enable_resp.get('ids_enabled')) == 0
        error_list = enable_resp.get('errors')
        for val in invalid_list:
            if not any(val in s for s in error_list):
                logger.error(val + " is not supposed to be enabled, some error")
                assert False
        assert vk_tools.keycore_requests.cloud.response_code == 200
        logger.info("Expected error when invalid cds are enabled: " + str(enable_resp.get('errors')))

    def test_00c_create_mixed_status_nfc_client_device_list(self):
        """
        Create client device list with mixed status [enabled, temp disabled]
        """
        self.test_00_reset_variables()
        vk_tools.keycore_requests.kc_info['batch_two_client_ids'] = []
        self.test_00a_create_client_device_in_bulk()
        # temp disable the client devices by the client device id
        self.test_01a_temp_disable_bulk_nfc_valid_cd_ids()
        # create few more cds,
        set_two_tag = []
        for i in range(2):
            random_string = "a" + str(random.randint(1000000, 9999999))
            set_two_tag.append(random_string)
        payload = {
            "nfcTagIds": set_two_tag
        }
        resp = vk_tools.keycore_requests.create_nfc_client_device_bulk(payload=payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert set_two_tag == resp.get("nfcTagIdsAdded"), "nfc batches created are not as per the list provided"
        assert len(resp.get("errors")) == 0
        logger.info("list of nfc client devices created" + str(resp.get("nfcTagIdsAdded")))
        # get the client devices to read the client device ids created
        cd_list = vk_tools.keycore_requests.get_all_client_device_id_list()
        for cd in cd_list:
            if cd.get('NFC_tag_id') in set_two_tag:
                vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list'].append(cd.get('id'))
                vk_tools.keycore_requests.kc_info['batch_two_client_ids'].append(cd.get('id'))
        assert vk_tools.keycore_requests.cloud.response_code == 200
        logger.info(
            "updated client device ids are: '" + str(vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']))

    def test_03a_bulk_enable_cds_with_enabled_temp_disabled_cd_list(self):
        """
        Enable the client devices with some are enabled and some are temp disabled in client devices list
        """
        # enable client device [where some are enabled and some are temp disabled],
        # from above, two are in disabled and two newly added are in enabled so
        # S#07: enable nfcs in bulk [where some of the nfcs are enabled already
        # S#08: enable nfcs in bulk [where some of the nfcs are temporary disabled]
        enable_payload = {
            "ids": vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']
        }
        enable_resp = vk_tools.keycore_requests.enable_nfc_client_device_bulk(payload=enable_payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        total_enabled = enable_resp.get("ids_enabled")
        total_errors = enable_resp.get("errors")
        assert len(vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']) == len(total_errors) + len(
            total_enabled)
        logger.info("Enabled IDs: " + str(total_enabled))
        logger.info("Error IDs: " + str(total_errors))

    def test_03b_bulk_temp_disable_cds_with_enabled_temp_disabled_cd_list(self):
        """
        Temp disable the client devices with some are enabled and some are temp disabled in client devices list
        """
        # disable "batch_two_client_ids" client devices, so we will have some enabled and some disabled
        disable_payload = {
            "ids": vk_tools.keycore_requests.kc_info['batch_two_client_ids']
        }
        disable_resp = vk_tools.keycore_requests.disable_nfc_client_device_bulk(payload=disable_payload)
        assert vk_tools.keycore_requests.kc_info['batch_two_client_ids'] == disable_resp.get(
            'ids_disabled'), "Some client devices are not disabled, errors are: " + str(disable_resp.get('errors'))
        assert vk_tools.keycore_requests.cloud.response_code == 200
        logger.info(
            "disabled client devices are: " + str(vk_tools.keycore_requests.kc_info['batch_two_client_ids']))
        # S#11: temp disable client device [where some are temp disabled and some are enabled]
        disable_payload = {
            "ids": vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']
        }
        disable_resp = vk_tools.keycore_requests.disable_nfc_client_device_bulk(payload=disable_payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        total_disabled = disable_resp.get("ids_disabled")
        total_errors = disable_resp.get("errors")
        assert len(vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']) == len(total_errors) + len(
            total_disabled)
        logger.info("Disabled IDs: " + str(total_disabled))
        logger.info("Error IDs: " + str(total_errors))

    def test_03c_bulk_enable_cds_with_temp_disabled_deleted_cd_list(self):
        """
        Enable the client devices with some are temp disabled and some are delete in client devices list
        """
        # disable (Delete) the client devices by client device id
        for new_nfc_client_device_id in vk_tools.keycore_requests.kc_info['batch_two_client_ids']:
            delete_resp = vk_tools.keycore_requests.disable_clientdevice(new_nfc_client_device_id).json()
            assert delete_resp.get(
                "id") == new_nfc_client_device_id, "Wrong response format for disabling client device"
            logger.info(str(new_nfc_client_device_id) + " is deleted")
            assert vk_tools.keycore_requests.cloud.response_code == 200
        # Post delete 'vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']' will have two temp disabled
        # and two deleted cds
        # S#09: enable nfcs in bulk [where some of the nfcs are deleted]
        enable_payload = {
            "ids": vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']
        }
        enable_resp = vk_tools.keycore_requests.enable_nfc_client_device_bulk(payload=enable_payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        total_enabled = enable_resp.get("ids_enabled")
        total_errors = enable_resp.get("errors")
        assert len(vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']) == len(total_errors) + len(
            total_enabled)
        logger.info("Enabled IDs: " + str(total_enabled))
        logger.info("Error IDs: " + str(total_errors))

    def test_03d_bulk_temp_disable_cds_with_enabled_deleted_cd_list(self):
        """
        Temp disable the client devices with some are enabled and some are deleted in client devices list
        """
        # from above, two temp disabled id are enabled and will have two enabled and two deleted ids
        # S#10: Temp disable nfcs in bulk [where some of the nfcs are deleted already]
        disable_payload = {
            "ids": vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']
        }
        disable_resp = vk_tools.keycore_requests.disable_nfc_client_device_bulk(payload=disable_payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        total_disabled = disable_resp.get("ids_disabled")
        total_errors = disable_resp.get("errors")
        assert len(vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']) == len(total_errors) + len(
            total_disabled)
        logger.info("Disabled IDs: " + str(total_disabled))
        logger.info("Error IDs: " + str(total_errors))

    @pytest.mark.dependency()
    def test_04a_verify_temp_disable_bulk_nfc_max_limit(self):
        """
        Verify Temp disable bulk api max limit
        """
        # create client devices
        try:
            self.test_00b_delete_nfc_client_devices()
        except Exception:
            pass
        self.test_00_reset_variables()
        for i in range(200):
            random_string = "a" + str(random.randint(1000000, 9999999))
            vk_tools.keycore_requests.kc_info['nfc_tag_ids_list'].append(random_string)
        payload = {
            "nfcTagIds": vk_tools.keycore_requests.kc_info['nfc_tag_ids_list']
        }
        resp = vk_tools.keycore_requests.create_nfc_client_device_bulk(payload=payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert vk_tools.keycore_requests.kc_info['nfc_tag_ids_list'] == resp.get(
            "nfcTagIdsAdded"), "nfc batches created are not as per the list provided"
        assert len(resp.get("errors")) == 0
        logger.info("list of nfc client devices created" + str(resp.get("nfcTagIdsAdded")))
        # get the client devices to read the client device ids created
        cd_list = vk_tools.keycore_requests.get_all_client_device_id_list()
        for cd in cd_list:
            if cd.get('NFC_tag_id') in vk_tools.keycore_requests.kc_info['nfc_tag_ids_list']:
                vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list'].append(cd.get('id'))
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert len(vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']) == len(
            vk_tools.keycore_requests.kc_info['nfc_tag_ids_list'])
        logger.info("client device ids for the nfc badges '{}' are '{}'".format(
            vk_tools.keycore_requests.kc_info['nfc_tag_ids_list'],
            vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']))
        # temp disable the client devices by the client device id
        # attaching an invalid client id to the list to make it as 201 and check the max limit in enable
        vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list'].append("dummy201")
        # S#13: verify max limit in disable [max 200]
        disable_payload = {
            "ids": vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']
        }
        disable_resp = vk_tools.keycore_requests.disable_nfc_client_device_bulk(payload=disable_payload)
        logger.info("===bulk disable nfc api response with more than 200 client devices are given ===")
        logger.info(disable_resp)
        assert vk_tools.keycore_requests.cloud.response_code == 400
        # remove the dummy id to perform successful bulk disable action with max device 200
        try:
            vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list'].remove("dummy201")
        except Exception:
            pass
        disable_payload = {
            "ids": vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']
        }
        vk_tools.keycore_requests.disable_nfc_client_device_bulk(payload=disable_payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200

    @pytest.mark.dependency(depends=["test_04a_verify_temp_disable_bulk_nfc_max_limit"])
    def test_04b_verify_enable_bulk_nfc_max_limit(self):
        """
        Verify Enable bulk api max limit
        """
        # attaching an invalid client id to the list to make it as 201 and check the max limit in enable
        vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list'].append("dummy201")
        # S#12: verify max limit in enable [max 200]
        enable_payload = {
            "ids": vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']
        }
        enable_resp = vk_tools.keycore_requests.enable_nfc_client_device_bulk(payload=enable_payload)
        logger.info("===bulk enable nfc api response with more than 200 client devices are given ===")
        logger.info(enable_resp)
        assert vk_tools.keycore_requests.cloud.response_code == 400
        # remove the dummy id to perform successful bulk enable action with max device 200
        try:
            vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list'].remove("dummy201")
        except Exception:
            pass
        enable_payload = {
            "ids": vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']
        }
        vk_tools.keycore_requests.enable_nfc_client_device_bulk(payload=enable_payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200

    def test_00d_clean_up_delete_nfcs_created(self):
        """
        Delete the nfcs created during max limit check
        """
        # delete the nfcs created
        for new_nfc_client_device_id in vk_tools.keycore_requests.kc_info['nfc_client_device_ids_list']:
            vk_tools.keycore_requests.disable_clientdevice(new_nfc_client_device_id).json()
            logger.info(new_nfc_client_device_id + " is deleted")

    def test_04c_temp_disable_bulk_nfc_min_limit(self):
        """
        Verify Temp disable bulk api min limit
        """
        # S#15: temp disable the client devices by the client device id
        disable_payload = {
            "ids": ['c5xityeh5nnk']
        }
        disable_resp = vk_tools.keycore_requests.disable_nfc_client_device_bulk(payload=disable_payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        logger.info("bulk nfc temp disable is working fine with minimum number of client device ids")
        logger.info(disable_resp)

    def test_04d_enable_bulk_nfc_min_limit(self):
        """
        Verify enable bulk api min limit
        """
        # S#14: Enable the client devices by the client device id
        enable_payload = {
            "ids": ['c5xityeh5nnk']
        }
        enable_resp = vk_tools.keycore_requests.enable_nfc_client_device_bulk(payload=enable_payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        logger.info("bulk nfc temp enable is working fine with minimum number of client device ids")
        logger.info(enable_resp)

    def test_sms_100_sms_api_provider_id_toggle_panic_command(self):
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["TOGGLE_PANIC"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_110_sms_api_provider_id_remote_engine_start_action_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["REMOTE_ENGINE_START_ACTION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_120_sms_api_provider_id_remote_engine_stop_action_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["REMOTE_ENGINE_STOP_ACTION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_130_sms_api_provider_id_panic_start_action_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["PANIC_START_ACTION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_140_sms_api_provider_id_panic_stop_action_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["PANIC_STOP_ACTION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_150_sms_api_provider_id_safe_lock_person_action_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["SAFE_LOCK_PERSON_ACTION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_160_sms_api_provider_id_unlock_all_action_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["UNLOCK_ALL_ACTION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_170_sms_api_provider_id_close_windows_action_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["CLOSE_WINDOW_ACTION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_180_sms_api_provider_id_open_window_action_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["OPEN_WINDOW_ACTION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_190_sms_api_provider_id_fold_mirrors_action_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["FOLD_MIRRORS_ACTION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_200_sms_api_provider_id_open_hatch_action_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["OPEN_HATCH_ACTION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_210_sms_api_provider_id_close_hatch_action_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["CLOSE_HATCH_ACTION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_220_sms_api_provider_id_backward_from_parking_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["BACKWARD_FROM_PARKING_ACTION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_230_sms_api_provider_id_forward_in_parking_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["FORWARD_IN_PARKING_ACTION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_240_sms_api_provider_id_open_charge_port_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["OPEN_CHARGE_PORT_ACTION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_250_sms_api_provider_id_preheat_action_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["PREHEAT_ACTION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_260_sms_api_provider_id_custom_one_action_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["CUSTOM_ONE_ACTION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    def test_sms_270_sms_api_provider_id_custom_two_action_command(self):
        time.sleep(5)
        resp = vk_tools.keycore_requests.send_remote_operation(vehicle_id=test_bench_vehicle_id,
                                                               operations=["CUSTOM_TWO_ACTION"],
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_post_template, True)
        provider_id = resp.get("remoteOperation").get("providerId")
        time.sleep(5)
        resp1 = vk_tools.keycore_requests.get_remote_operation(provider_id=provider_id,
                                                               vehicle_id=test_bench_vehicle_id,
                                                               custom_apikey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.apikey'],
                                                               custom_secretkey=vk_tools.keycore_requests.kc_info[
                                                                   'org1.secretkey'])
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(sms_api_get_template, True)
        assert resp1.get("remoteOperation").get("status") == "DELIVERED"

    @pytest.mark.skipif(is_keycore_dev(), reason="keycore-dev : 403 forbidden error")
    def test_telemetry_161_open_telemetry_data_logger_stream(self):
        """
        Test the web socket for getting telemetries:
        - Connect to the websocket
        - Send a telemetry a few seconds later
        - Check that the telemetry was pushed through the websocket
        """

        def run():
            time.sleep(5)

        send_telemetry_data_logger_ecu(device_serial=VEHICLE_PAYLOAD["device"]["serialNumber"])

        # Launching the thread that will send a telemetry in 5 seconds
        thread = Thread(target=run)
        thread.start()
        # Connecting with the websocket to receive telemetries
        list_telemetries = vk_tools.receive_data_logger_telemetry_web_socket()
        assert len(list_telemetries) > 0
        telemetry_found = False
        for telemetry in list_telemetries:
            try:
                if telemetry["vin"] == VEHICLE_PAYLOAD["vin"]:
                    telemetry_found = True
            except Exception:
                if telemetry["subscribeResponse"]["errorId"] == 0:
                    telemetry_found = True
                    logger.warning("There are no telemetries received during the validation. However no errors found")
        assert telemetry_found

    def test_vehicle_190_get_device_information(self):
        """
        Returns the information about the device serial number provided
        """
        device_serial = env_config.get("serial_number")
        resp = vk_tools.keycore_requests.get_device_info(device_serial=device_serial)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(device_info_payload, True)

    def test_vehicle_131_check_sim_status_when_vehicle_disabled(self):
        """
        Check if the SIM status is moved to PAUSE when the vehicle is disabled
        """
        vehicle_id = env_config.get("linking_vehicle_id")
        device_serial = env_config.get("serial_number")
        resp = vk_tools.keycore_requests.disable_vehicle(vehicle_id=vehicle_id)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("id") == env_config.get("linking_vehicle_id")
        resp = vk_tools.keycore_requests.get_device_sim_status(device_serial=device_serial)
        assert resp == "PAUSE"
        logger.info("SIM Status is PAUSED when vehicle is disabled")

    def test_vehicle_132_check_sim_status_when_vehicle_enabled(self):
        """
        Check if the SIM status is moved to ACTIVE when the vehicle is enabled
        """
        vehicle_id = env_config.get("linking_vehicle_id")
        device_serial = env_config.get("serial_number")
        resp = vk_tools.keycore_requests.enable_vehicle(vehicle_id=vehicle_id)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("id") == env_config.get("linking_vehicle_id")
        resp = vk_tools.keycore_requests.get_device_sim_status(device_serial=device_serial)
        assert resp == "ACTIVE"
        logger.info("SIM Status is ACTIVE when vehicle is enabled")

    def test_vehicle_121_check_sim_status_when_device_unlinked(self):
        """
        Check if the SIM status is moved to PAUSE when the device is unlinked from the vehicle
        """
        vehicle_id = env_config.get("linking_vehicle_id")
        device_serial = env_config.get("serial_number")
        resp = vk_tools.keycore_requests.unlink_vehicle_from_device_with_id(vehicle_id=vehicle_id,
                                                                            device_serial=device_serial)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        resp = vk_tools.keycore_requests.get_device_sim_status(device_serial=device_serial)
        assert resp == "PAUSE"
        logger.info("SIM Status is PAUSED when vehicle is disabled")

    def test_vehicle_186_check_sim_status_when_device_linked(self):
        """
        Check if the SIM status is moved to ACTIVE when the device is linked to the vehicle
        """
        vehicle_id = env_config.get("linking_vehicle_id")
        device_serial = env_config.get("serial_number")
        resp = vk_tools.keycore_requests.link_vehicle_with_device_using_vehicle_id(vehicle_id=vehicle_id,
                                                                                   device_serial=device_serial)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        resp = vk_tools.keycore_requests.get_device_sim_status(device_serial=device_serial)
        assert resp == "ACTIVE"
        logger.info("SIM Status is ACTIVE when vehicle is enabled")

    def test_vehicle_011_create_vehicle_v2(self):
        """
        This test to test the create vehicle v2 API and is working fine as expected
        endpoint = /2/vehicles
        """
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
        vk_tools.keycore_requests.vehicle.id = resp.get("id")
        vehicle_id_list.append(resp.get("id"))
        device_serial_list.append(resp.get("device").get("serialNumber"))
        assert resp.get("enabled") == VEHICLE_PAYLOAD["enabled"]
        assert resp.get("device").get("type") == VEHICLE_PAYLOAD["device"]["type"]
        assert resp.get("device").get("serialNumber") == VEHICLE_PAYLOAD["device"]["serialNumber"]
        assert resp.get("vin") == VEHICLE_PAYLOAD["vin"]
        assert resp.get("make") == VEHICLE_PAYLOAD["make"]
        assert resp.get("model") == VEHICLE_PAYLOAD["model"]
        assert resp.get("year") == int(VEHICLE_PAYLOAD["year"])
        assert resp.get("licensePlate") == VEHICLE_PAYLOAD["licensePlate"]
        assert resp.get("color") == VEHICLE_PAYLOAD["color"]
        assert resp.get("tank_capacity") == VEHICLE_PAYLOAD["tank_capacity"]
        assert resp.get("generation") == VEHICLE_PAYLOAD["generation"]
        assert resp.get("transmissionType") == VEHICLE_PAYLOAD["transmissionType"]
        assert resp.get("regionOfSale") == VEHICLE_PAYLOAD["regionOfSale"]
        assert resp.get("engineType") == VEHICLE_PAYLOAD["engineType"]
        assert resp.get("engineSize") == VEHICLE_PAYLOAD["engineSize"]
        assert resp.get("protocol") == VEHICLE_PAYLOAD["protocol"]

    def test_vehicle_012_create_vehicle_with_accm_already_linked_with_vehicle(self):
        """
        This test to test the create vehicle v2 API and is working fine when the device is already linked to another vehicle
        endpoint = /2/vehicles
        """
        VEHICLE_PAYLOAD["device"]["serialNumber"] = "{}".format(vk_tools.keycore_requests.kc_info['module_serial'])
        payload = VEHICLE_PAYLOAD.copy()
        resp = vk_tools.keycore_requests.create_vehicle_rabbit_device(payload=payload, version=2)
        logger.info(resp)
        assert vk_tools.keycore_requests.cloud.response_code == 409
        assert resp.get("errorId") == 1111
        assert resp.get("message").startswith("Device already linked to ") and \
               resp.get("message").endswith(", please, disable the vehicle or unlink the device")
        logger.info("Unable to create a new vehicle when the device is linked to another vehicle already as expected")

    def test_vehicle_013_create_vehicle_with_invalid_device_serial(self):
        """
        This test to test the create vehicle v2 API and is working fine when invalid device serial was given
        endpoint = /2/vehicles
        """
        device_serial = "dummy"
        VEHICLE_PAYLOAD["device"]["serialNumber"] = "{}".format(device_serial)
        payload = VEHICLE_PAYLOAD.copy()
        resp = vk_tools.keycore_requests.create_vehicle_rabbit_device(payload=payload, version=2)
        logger.info(resp)
        assert vk_tools.keycore_requests.cloud.response_code == 404
        assert resp.get("errorId") == 404
        assert resp.get("message") == "Unable to find resource"
        logger.info("Unable to create vehicle with invalid device serial number as expected")

    def test_vehicle_014_create_sae_with_invalid_ecu_id(self):
        """
        This test to test the create vehicle v2 API and is working fine when invalid ecu id was given for type SAE as expected
        endpoint = /2/vehicles
        """
        resp = vk_tools.keycore_requests.create_vehicle_sae_device(version=2, ecu_id=122222222)
        logger.info(resp)
        assert vk_tools.keycore_requests.cloud.response_code == 404
        assert resp.get("errorId") == 404
        assert resp.get("message") == "Unable to find resource"
        logger.info("Unable to create vehicle with invalid ecu id for the Type SAE as expected")

    def test_vehicle_015_create_vehicle_in_north_america(self):
        """
        Create a vehicle and check that the response body contains the correct fields
        Stores the vehicle id for next tests
        """
        vk_tools.keycore_requests.authenticate()
        vk_tools.keycore_requests.create_module_and_device_rabbit()

        VEHICLE_PAYLOAD["device"]["serialNumber"] = "{}".format(vk_tools.keycore_requests.kc_info['module_serial'])
        payload = VEHICLE_PAYLOAD.copy()
        payload["vin"] = str(random.randint(10000000000000000, 99999999999999999))
        payload["regionOfSale"] = "North America"
        resp = vk_tools.keycore_requests.create_vehicle_rabbit_device(payload=payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.keycore_requests.vehicle.id = resp.get("id")
        logger.info("vehicle created - {}".format(resp.get("id")))
        vehicle_id_list.append(resp.get("id"))
        device_serial_list.append(resp.get("device").get("serialNumber"))
        assert resp.get("enabled") == payload["enabled"]
        assert resp.get("device").get("type") == payload["device"]["type"]
        assert resp.get("device").get("serialNumber") == payload["device"]["serialNumber"]
        assert resp.get("vin") == payload["vin"]
        assert resp.get("make") == payload["make"]
        assert resp.get("model") == payload["model"]
        assert resp.get("year") == int(payload["year"])
        assert resp.get("licensePlate") == payload["licensePlate"]
        assert resp.get("color") == payload["color"]
        assert resp.get("tank_capacity") == payload["tank_capacity"]
        assert resp.get("generation") == payload["generation"]
        assert resp.get("transmissionType") == payload["transmissionType"]
        assert resp.get("regionOfSale") == payload["regionOfSale"]
        assert resp.get("engineType") == payload["engineType"]
        assert resp.get("engineSize") == payload["engineSize"]
        assert resp.get("protocol") == payload["protocol"]

    def test_vehicle_016_create_vehicle_with_existing_vin(self):
        """
        Create a vehicle with existing VIN and check that it is not allowing
        Read the vin from ACCM_environment.yaml file
        """
        vk_tools.keycore_requests.authenticate()
        vk_tools.keycore_requests.create_module_and_device_rabbit()

        VEHICLE_PAYLOAD["device"]["serialNumber"] = "{}".format(vk_tools.keycore_requests.kc_info['module_serial'])
        payload = VEHICLE_PAYLOAD.copy()
        payload["vin"] = get_env_organisation_item("ACCM_Vehicles.VIN")
        resp = vk_tools.keycore_requests.create_vehicle_rabbit_device(payload=payload)
        assert vk_tools.keycore_requests.cloud.response_code == 409
        assert resp.get("errorId") == 1104
        assert resp.get("message") == "Cannot create resource. ID already exists"
        logger.info("Vehicle is not created with the VIN - {} as vehicle with this VIN already exists.".format(
            payload["vin"]))

    def test_vehicle_017_create_vehicle_with_invalid_device_serial(self):
        """
        Create vehicle with invalid device serial number and check if it throwing 404 error
        """
        VEHICLE_PAYLOAD["device"]["serialNumber"] = "invalid_serial"
        payload = VEHICLE_PAYLOAD.copy()
        resp = vk_tools.keycore_requests.create_vehicle_rabbit_device(payload=payload)
        assert vk_tools.keycore_requests.cloud.response_code == 404
        assert resp.get("errorId") == 404
        assert resp.get("message") == "Unable to find resource"
        logger.info("Getting 404 Unable to find resource when the device serial is invalid while creating vehicle")

    def test_client_device_140_create_client_device_invalid_session_request_token(self):
        """
        Create a client device with invalid session response token
        and check that the response contains the correct error message
        """
        payload = {
            "sessionRequestToken": "invalid_request_token",
            "enabled": True
        }
        resp = vk_tools.keycore_requests.create_client_device(payload=payload, save_response_data=False)
        assert vk_tools.keycore_requests.cloud.response_code == 400
        assert resp.get("errorId") == 1
        assert resp.get("message") == "Error creating client device"

    def test_client_device_150_enable_client_device_nfc_already_enabled(self):
        """
        Enable the nfc client device that is already in enabled state and check the response
        """
        random_string = "a" + str(random.randint(1000000, 9999999))
        vk_tools.keycore_requests.kc_info['nfc_tag_id'] = random_string
        payload = {
            "NFCTagId": vk_tools.keycore_requests.kc_info['nfc_tag_id'],
            "NFCAlgorithm": "0",
            "NFCPage": 0,
            "NFCBlock": 1,
            "enabled": True
        }
        resp = vk_tools.keycore_requests.create_nfc_client_device(payload=payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.keycore_requests.kc_info['nfc_client_device_id'] = resp.get("id")
        logger.info("Created NFC Client Device id is - " + resp.get("id"))
        vk_tools.assert_correct_field(nfc_device_creation_template, True)
        assert resp.get("NFC_tag_id") == random_string
        assert resp.get("enabled") is True
        nfc_client_device_id = vk_tools.keycore_requests.kc_info['nfc_client_device_id']
        resp = vk_tools.keycore_requests.nfc_temp_disable_enable_client_device(state="enable",
                                                                               client_device_id=nfc_client_device_id)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        assert resp.get("id") == vk_tools.keycore_requests.kc_info['nfc_client_device_id']
        logger.info("When already enabled nfc client device is enabled, Response code is 200 as expected not 404")

    def test_vk_170a_update_nfc_vk(self):
        """
        Create virtual key for nfc client device, then call the API to update it.
        Check that the response contains the correct fields
        """
        start_date = int(time.time())
        end_date = start_date + 10 * 60
        payload = {
            "vehicleId": vk_tools.keycore_requests.vehicle.id,
            "clientDeviceId": vk_tools.keycore_requests.kc_info['nfc_client_device_id'],
            "validityStartDate": start_date,
            "validityEndDate": end_date,
            "clientDeviceNumberOfActionsAllowed": vk_tools.data['clientDeviceNumberOfActionsAllowed'],
            "clientDeviceActionsAllowedBitfield": vk_tools.data['clientDeviceActionsAllowedBitfield'],
            "userAuthentication": False,
            "generationInterval": 3600
        }
        resp = vk_tools.keycore_requests.create_vk(payload)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_id = resp.get("virtualkey")["id"]
        logger.info("Virtual key created - {}".format(vk_id))
        new_validity_end_date = end_date + 30
        new_generation_interval = 20 * 60
        resp = vk_tools.keycore_requests.update_vk(new_validityenddate=new_validity_end_date,
                                                   new_generationinterval=new_generation_interval)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_update_template, True)
        assert resp.get("validityEndDate") == str(new_validity_end_date)
        assert resp.get("generationInterval") == str(new_generation_interval)

        resp = vk_tools.keycore_requests.get_vk_ivkapi(id=vk_id)
        assert vk_tools.keycore_requests.cloud.response_code == 200
        vk_tools.assert_correct_field(vk_get_template, True)
        assert resp.get("virtualKeys")[0].get("status") == "CREATED"
        logger.info("NFC Vk is working fine post update API call")

