import time

import pytest

from rpi_bench.libs.selenium_lib.lib_selenium import BaseTestClass, Actions
from rpi_bench.libs.selenium_lib.webpages import WebLoginPage
from rpi_bench.test_api.Webutility_AP.webuitlity import Utility, locators, wait_time
from rpi_bench.test_api.tools import get_bench_configuration, get_environment_configuration
import logging
from rpi_bench.libs.selenium_lib.webpages import WebLoginPage, HomePage, VehiclesPage, DashBoardPage, DevicePage, \
    ConfigPage, DevicesPage, UpgradePage, AdminPage, environment, VhOperation, Inventory, Eventslog, SummaryPage, Trip

locators = BaseTestClass.load_pages()

jira_flag = get_environment_configuration().get("NEED_RESULTS_IN_JIRA", default=False)

bc = get_bench_configuration()
url = bc['Signpage.web_url']
email = bc['Signpage.email']
password = bc['Signpage.pwd']
invalidpwd = bc['Signpage.invalidpwd']
superemail = bc['Signpage.superadmin']
superpwd = bc['Signpage.superpwd']
vehiclename = bc['Signpage.vhName']
useremailid = bc['Signpage.emailid']
user_mail = bc['Signpage.user_email']
user_name = bc['Signpage.user_name']
accm = bc['Signpage.deleteACCM']
make = bc['Signpage.vhMake']
model = bc['Signpage.vhModel']
year = bc['Signpage.vhYear']
transmission = bc['Signpage.vhTransmission']
generation = bc['Signpage.vhgeneration']
engineType = bc['Signpage.vhEngine']
engsize = bc['Signpage.vhengSize']
tankcap_vehicle = bc['Signpage.vtankcap_vehicle']
serial = bc['Signpage.serialno']
emailadd = bc['Signpage.emailadd']
fname = bc['Signpage.fname']
lname = bc['Signpage.lname']
country = bc['Signpage.country']
phno = bc['Signpage.phno']
org_list = bc['Signpage.org_expected']
reboot_desc_msg = bc['Signpage.reboot_desc_msg']
reboot_success = bc['Signpage.reboot_success']
time_out = bc['Signpage.time_out']
car_refresh_data = bc['Signpage.car_refresh_data']
multi_search_data = bc['Signpage.multiSearch_list']
select_parameter = bc['Signpage.select_parameter']
fw_version = bc['Signpage.fotaVersionNo']
send_all_config = bc['Signpage.send_all_config']
log_category = bc['Signpage.log_category']
log_description = bc['Signpage.log_description']
timeout_in_seconds = bc['Signpage.wait_time']
check_box_values = bc['Signpage.check_box_values']
editing_values = bc['Signpage.editing_values']



@pytest.mark.usefixtures("update_results_to_jira")
class Testwebapplication:

    def setup_method(self):
        self.driver = BaseTestClass.set_up(self)
        self.wb = Utility(self.driver)
        self._bt = Actions(self.driver)

    def teardown_method(self):
        BaseTestClass.teardown(self)

    def test_login(self):
        """
    TestCase: login into the backend
    """
        self.wb.test_login(url, email, password)
        # assert self._bt.elementDisplayed(locators[WebLoginPage.key]) is True, "user login unsuccessful"
        assert self._bt.check_elements(
            [locators[WebLoginPage.key], locators[HomePage.home_devices], locators[DashBoardPage.dashboard]]) == 0

    def test_invalid_pwd(self):
        """
    TestCase: login into the backend with invalid credentials
                verifying the error message displayed
     """
        self.wb.test_login(url, email, invalidpwd)
        assert self._bt.check_elements([locators[WebLoginPage.invalid_cred], locators[
            WebLoginPage.login_rememberme], locators[WebLoginPage.user_emailid],
                                        locators[WebLoginPage.user_passwordweb]]) == 0

    def test_logout_backend(self):
        """
    TestCase: login into the backend with valid credentials
                logout from backend
    """
        self.wb.test_login(url, email, password)
        self.wb.logout()
        assert self._bt.check_elements([locators[WebLoginPage.login_rememberme], locators[WebLoginPage.user_emailid],
                                        locators[WebLoginPage.user_passwordweb]]) == 0

    def test_vehicle_search(self):
        """
    TestCase: Searching a vehicle
    """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        vin_number, accm_id = self.wb.getVehicleVIN()
        assert vin_number == vehiclename, "Vehicle not found"

    @pytest.mark.skipif(jira_flag, reason="Need result in jira / not stable")
    def test_createVehicle(self):
        """
    Testcase : creating the vehicle through backend.  fail
     """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[14])
        msg = self.wb.add_vehicle(make, model, year, transmission, generation, engineType, engsize, tankcap_vehicle)
        assert msg == "Vehicle created", "vehicle not created"

    '''def test_T5327191_reboot(self):
        """
    Test : Verify the reboot of ACCm by seaching vehicle serial numbers
    """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        msg = self.wb.reboot()
        assert msg == reboot_success, "ECURebootCmd message has not sent"
        assert self.wb.check_event_logs(vehiclename, locators[VehiclesPage.vehicle_vin], reboot_desc_msg,
                                        time_out) is True, \
            "Reboot unsuccesful"'''

    def test_DashboardVerify(self):
        """
    Test : Verify the vehicles are offline reflecting red
    """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        assert self.wb.offline_Velicle() is True, "vehicle is not offlines"
        assert self.wb.online_Velicle() is True, "vehicle is not online"

    @pytest.mark.skipif(jira_flag, reason="Need result in jira / not stable")
    def test_C20398498_Backend_vehicle_ask_telemetry(self):
        """
     Test : Verify the Backend vehicle ask telemetry
    """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        assert self.wb.backend_vehicle_car_data_refresh(locators[DashBoardPage.car_refresh_data]) == car_refresh_data, \
            "ask telemetry unsuccessful"

    def test_C20398464_check_vehicle_and_device_not_in_same_organization(self):
        """
      Test : Verify the check vehicle and device not in same organization
     """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.select_environment(org_list[6])
        self.wb.searchVehicle(vehiclename)
        assert self._bt.elementDisplayed(locators[VehiclesPage.no_data_available]) is True, bc[
            'Signpage.vh_not_present']

    def test_C20398465_check_organizations(self):
        """
     Test : Verify the organizations present in backend using super admin
    """
        self.wb.test_login(url, superemail, superpwd)
        assert self.wb.search_organizations(org_list) is True, "All organizations not present"

    def test_c20398467_check_devices_registered_in_inventory(self):
        """
    TestCase :check- devices registered in inventory of organization
    can not be seen on other organization
    """
        self.wb.test_login(url, email, password)
        registered_id = self.wb.get_register_devices(serial)
        self.wb.check_register_devices_in_diff_org(registered_id)
        assert self._bt.elementDisplayed(locators[VehiclesPage.no_data_available]) is True, \
            "devices registered in inventory of organization can be seen on other organization"

    @pytest.mark.skipif(jira_flag, reason="Need result in jira / not stable")
    def test_C20836537_invoicereporting(self):
        """
    TestCase :reporting
    """
        self.wb.test_login(url, email, password)
        assert self.wb.invoiceReporting() is True, "invoiceReporting Failed"

    def test_C21074757_delete_user(self):
        """
    TestCase :Deleting a new user from the keycore BE
    """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        msg = self.wb.delete_user(useremailid)
        if msg:
            logging.info("User not found to delete")
        else:
            assert msg is not True, "User is not deleted"

    #@pytest.mark.skipif(jira_flag, reason="Need result in jira / not stable")
    def test_c20398485_custom_column_selection(self):
        """
    TestCase : Custom column selection
    """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        # All columns should be undisplayed except Timestamp and Private Mode
        assert self.wb.custom_selection_uncheck() == 2, "All columns are not disappeared"
        # Each checked item shall reappear on the synthesis table(including Timestamp and Private Mode)
        print("done")
        time.sleep(5.0)
        ele_len_items, ele_len_display = self.wb.custom_selection_recheck()
        assert ele_len_items + 2 == ele_len_display, "All columns are not displayed"

    @pytest.mark.skipif(jira_flag, reason="Need result in jira / not stable")
    def test_delete_ACCM(self):
        """
    TestCase : Delete ACCM.
    """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[14])
        if self.wb.del_ACCM(accm):
            assert self.wb.del_ACCM(accm) is True, "delete pop up not displayed"
        else:
            logging.info("device data not available")

    #@pytest.mark.skipif(jira_flag, reason="Need result in jira / not stable")
    def test_OBD_packageUpdate(self):
        """
        TestCase : Custom column selection.
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        assert "Successfully pushed OBD" in self.wb.get_obdDetails(), "OBD package unsuccesfull"

    @pytest.mark.skipif(jira_flag, reason="Need result in jira / not stable")
    def test_C21074756_edit_user(self):
        """
        TestCase45:Edit user on BLE
        """
        self.wb.test_login(url, superemail, superpwd)
        msg = "Successfully added CustomerAdmin role on EU-PreProd group(s) to " + user_name + "."
        assert self.wb.edit_user_account(user_mail,
                                         locators[AdminPage.customer_admin_role]) == msg, "Failed to edit user"

    @pytest.mark.skipif(jira_flag, reason="Need result in jira / not stable")
    def test_C20398468_unclaim_claim_devices(self):
        """
        Test : Verify the organizations present in backend using super admin.
        """
        self.wb.test_login(url, email, password)
        self.wb.unclaim_device(org_list[5], bc['Signpage.vhDevice1'])
        assert "Successfully" in self.wb.claim_device("FCS-Preprod", bc['Signpage.vhDevice1']) , \
            "Claiming failed"
        wait_time(5)
        self.wb.unclaim_device("FCS-Preprod", bc['Signpage.vhDevice1'])
        assert "Successfully" in self.wb.claim_device(org_list[5], bc['Signpage.vhDevice1']), \
            "claiming failed"

    @pytest.mark.skipif(jira_flag, reason="Need result in jira / not stable")
    def test_C21073884_forceOff_Disable(self):
        """
      TestCase:Disabling the forceoff
    """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        msg = "×\nECUDisableForceStateOFF message sent successfuly"
        assert self.wb.forceoffDisableEnable(locators[DevicesPage.disable_btn], vehiclename) == msg, \
            "ECUDisableForceStateOFF unsuccessful"

    @pytest.mark.skipif(jira_flag, reason="Need result in jira / not stable")
    def test_C21073883_forceOff_Enable(self):
        """
    TestCase:enabling the force off
    """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        msg = "×\nECUEnableForceStateOFF message sent successfuly"
        assert self.wb.forceoffDisableEnable(locators[DevicesPage.enable], vehiclename) == msg, \
            "ECUEnableForceStateOFF unsuccessful"

    @pytest.mark.skipif(jira_flag, reason="Need result in jira / not stable")
    def test_C20969033_request_device_logs(self):
        """
        TestCase:Request device logs on FE
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        assert self.wb.request_device_logs() == "×\nQueued get logs command.", "logs are not reflecting"

    def test_C20398487_Vehicle_Trips_with_dates(self):
        """
    TestCase:A map show up with last trips with 1 week time slot
    """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        assert self.wb.trips("7/4/2022", "7/5/2022", 30) is True, "Trips data failed"

    def test_OBD_and_DB_Proto_DB_customer_access_ACCMplus_with_protocl_and_OBD(self):
        """
        TestCase:OBD DB & Proto DB customer access: ACCM+ with protocl and OBD
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        obd_status = self.wb.obd_db_proto_db_customer_access(bc['Signpage.vhMake'],bc['Signpage.vhModel1'], year)
        assert obd_status is True, "OBD DB & Proto DB customer access unsuccesful"

    @pytest.mark.skipif(jira_flag, reason="Need result in jira / not stable")
    def test_C20398333_Revoke_a_loaded_vk_on_FE(self):
        """
        TestCase :Revoke a loaded vk on FE
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.searchVehicle(vehiclename)
        self.wb.selectVehicle(locators[VehiclesPage.vehicle_vin])
        status = self.wb.revoke_vk_on_FE(bc['Signpage.client_device'])
        if status:
            assert status is True, "Revoke Vk failed"
        else:
            logging.info("No Active Vk to revoke, create Vk and try again")

    def test_C21074755_add_user(self):
        """
        TestCase:Adding a new user to the keycore BE.
        """
        self.wb.test_login(url, superemail, superpwd)
        self.wb.select_environment(org_list[5])
        assert self.wb.add_user(emailadd, fname, lname, country, phno) is True, "user account creation unsuccessful"

    @pytest.mark.skip("waiting for stable new UI changes on FOTA")
    def test_T5327189_Fota_upgrade_downgrade(self):
        """
        TestCase51:Fota upgrade and downgrade
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.search_vehicle_upgrade(bc['Signpage.fotaSerialNo'], fw_version)

    def test_config_upgrade_with_multiple_search(self):
        """
        TestCase:Config upgrade with multiple search option
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.search_vehicle_config_upgrade(select_parameter, multi_search_data, send_all_config)
        self.wb.navigate_to_event_logs(vehiclename,locators[VehiclesPage.vehicle_vin])
        self.wb.verify_event_log(log_category["Config_Upgrade"], log_description["Config_Upgrade"],
                                 timeout_in_seconds)

    def test_FOTA_upgrade_with_multiple_search(self):
        """
        TestCase:Config upgrade with multiple search option
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        upgrade = self.wb.search_vehicle_FOTA_upgrade(select_parameter, multi_search_data, fw_version)
        if upgrade:
            assert email == self.wb.verify_FW_jobs()
            self.wb.navigate_to_event_logs(multi_search_data, locators[VehiclesPage.vehicle_vin])
            self.wb.verify_event_log(log_category["Fota_Upgrade"], log_description["Fota_Upgrade"]
                                     , timeout_in_seconds)
        else:
            logging.info("Try with different FW version")

    def test_default_config_check(self):
        """
        TestCase:Config upgrade with multiple search option
        """
        self.wb.test_login(url, email, password)
        self.wb.select_environment(org_list[5])
        self.wb.verify_defualt_config(check_box_values, editing_values)
        self.wb.verify_the_changes_in_default_config(check_box_values, editing_values)
