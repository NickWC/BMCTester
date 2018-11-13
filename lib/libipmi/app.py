__author__ = 'Linda Huang'
import CommandUtil as util
import testmethod.methodfunc as mfunc
from time import sleep

class watchDogTimer():
    def __init__(self):
        self.netfn = "0x06"
        self.resetCmd = "0x22"
        self.setCmd = "0x24"
        self.getCmd = "0x25"
    # WatchDogTimerSensorNum and PwrUnitStatusSensorNum might be different from platform
    def watchDogTimerTest(self, case, WatchDogTimerSensorNum, PwrUnitStatusSensorNum):
        # Power should be up to test watchDogTimerTest(do power cycle)
        if mfunc.GetPowerStatus(case.sysConf) == 0: # power off
            # Do power up
            ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0}".format("0x00 0x02 0x01"))
            sleep(80)
            if ret[2] !=0:
                output = "Do power up before test watchDogTimerTest(do power cycle) fail."
                return output, ret[1].decode("utf-8"), "Fail"

        # Clear SEL
        ret = util.exec_ipmi_cmd(case.sysConf, case.interface, "sel clear")
        output = "Test step: \n1. Clear SEL: "
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + "OK\n"
        sleep(2)

        # Set watchdog timer
        # Action: power cycle, Countdown: 4.8s
        ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1} {2}".format(self.netfn, self.setCmd, "0xc1 0x03 0x01 0x02 0x30 0x00"))
        output = output + "2. Set watchdog timer: "
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + "OK\n"
        sleep(10)

        # Get watchdog timer
        # Get watchdog timer to check setting.
        ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(self.netfn, self.getCmd))
        output = output + "3. Get watchdog timer to check setting: "
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"

        output_temp, cmpState = mfunc.DiffExpectResult(ret[0].decode("utf-8"), "0x81 0x03 0x01 0x00 0x30 0x00 0x30 0x00")
        if 0 != cmpState:
            output = output + "Fail({0})\n".format(output_temp)
            return output, "Check setting watchdog timer fail", "Fail"
        output = output + "OK\n"

        # Reset watchdog timer
        ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(self.netfn, self.resetCmd))
        output = output + "4. Reset watchdog timer: "
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + "OK\n"
        sleep(20)

        # Check SEL
        # Check watchDog timer event
        ret = mfunc.FindSel(case.sysConf, 0x23, WatchDogTimerSensorNum, 0x6f, 0xc3, 0x01, 0xff)
        output = output + "5. Check watchdog timer: "
        output = output + ret[0]
        if ret[2] !=0:
            return output, ret[1], "Fail"
        # Check power off
        ret = mfunc.FindSel(case.sysConf, 0x09, PwrUnitStatusSensorNum, 0x6f, 0x00, 0xff, 0xff)
        output = output + "6. Check power cycle:"
        if ret[2] !=0:
            output = output + ret[0]
            return output, ret[1], "Fail"
        # Check power on
        ret = mfunc.FindSel(case.sysConf, 0x09, PwrUnitStatusSensorNum, 0xef, 0x00, 0xff, 0xff)
        if ret[2] == 0:
            isSuccess = "Success"
        else:
            isSuccess = "Fail"
        output = output + ret[0]
        return output, ret[1], isSuccess

class userAccess():
    def __init__(self):
        self.netfn = "0x06"
        self.setUserAccessCml = "channel setaccess"
        self.getUserAccessCml = "channel getaccess"
        self.setUserNameCml = "user set name"
        self.setUserPasswordCml = "user set password"
        self.setUserNameCmd = "0x45"
        self.getUserNameCmd = "0x46"
        self.setUserPasswordCmd = "0x47"

    def setUserAccess(self, case, channel, userId, setting):
        return util.exec_ipmi_cmd(case.sysConf, case.interface, "{0} {1} {2} {3}".format(self.setUserAccessCml, channel, userId, setting))

    def setUserName(self, case, userId, name):
        return util.exec_ipmi_cmd(case.sysConf, case.interface, "{0} {1} {2}".format(self.setUserNameCml, userId, name))

    def setUserPassword(self, case, userId, password):
        return util.exec_ipmi_cmd(case.sysConf, case.interface, "{0} {1} {2}".format(self.setUserPasswordCml, userId, password))

    def testUserLogin(self, case, name, password):
        # Test user login via get device ID
        return util.exec_ipmi_login(case.sysConf, name, password, case.interface, "{0}".format("0x06 0x01"))

    def setUserPasswordAndLogin(self, case):
        # Set user ID 3 access
        output = "Test step: \n1. Set user ID 3 access: "
        setting = "callin={0} ipmi={1} link={2} privilege={3}".format("on", "on", "on", "4")
        ret = self.setUserAccess(case, 1, 3, setting)
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + "OK\n"

        # Set user name as "admin"
        output = output + "2. Set user name as \"admin\": "
        ret = self.setUserName(case, 3, "admin")
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + "OK\n"

        # Set password name as "admin"
        output = output + "3. Set password as \"admin\": "
        ret = self.setUserPassword(case, 3, "admin")
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + "OK\n"

        # Test BMC login"
        output = output + "4. Test BMC login: "
        ret = self.testUserLogin(case, "admin", "admin")
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + "OK\n"

        return output, "", "Success"