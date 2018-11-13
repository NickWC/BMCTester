__author__ = 'Linda Huang'
import CommandUtil as util
import testmethod.methodfunc as mfunc
from time import sleep

class chassisControl():
    def __init__(self):
        self.netfn = "0x00"
        self.netfnCmd = "{0} {1}".format(self.netfn, "0x02")
        self.powDown = "0x00"
        self.powUp = "0x01"
        self.powCycle = "0x02"
        self.hardReset = "0x03"
    def powerDownTest(self, case):
        if mfunc.GetPowerStatus(case.sysConf) == 0: # power off
            # Do power up
            ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(self.netfnCmd, self.powUp))
            sleep(5)
            if ret[2] !=0:
                output = "Do power up before test power down fail."
                return output, ret[1].decode("utf-8"), "Fail"
        # Do power down
        output = "Test step: \n1. Power down: "
        ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(self.netfnCmd, self.powDown))
        sleep(5)

        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + "OK\n"

        # Get chassis status
        output = output + "2. Check power status down: "
        if mfunc.GetPowerStatus(case.sysConf) == 0: # power off
            output = output + "OK\n"
            return output, ret[1].decode("utf-8"), "Success"
        output = output + "Fail\n"
        return output, ret[1], "Fail"

    def powerUpTest(self, case):
        if mfunc.GetPowerStatus(case.sysConf) == 1: # power on
            # Do power down
            ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(self.netfnCmd, self.powDown))
            sleep(5)
            if ret[2] !=0:
                output = "Do power down before test power up fail."
                return output, ret[1].decode("utf-8"), "Fail"
        # Do power up
        output = "Test step: \n1. Power up: "
        ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(self.netfnCmd, self.powUp))
        sleep(5)
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + "OK\n"

        # Get chassis status
        output = output + "2. Check power status up: "
        if mfunc.GetPowerStatus(case.sysConf) == 1: # power on
            output = output + "OK\n"
            return output, ret[1].decode("utf-8"), "Success"
        output = output + "Fail\n"
        return output, ret[1], "Fail"

    # PwrUnitStatusSensorNum might be different from platform
    def powerCycleTest(self, case, PwrUnitStatusSensorNum):
        if mfunc.GetPowerStatus(case.sysConf) == 0: # power off
            # Do power up
            ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(self.netfnCmd, self.powUp))
            sleep(5)
            if ret[2] !=0:
                output = "Do power up before test power cycle fail."
                return output, ret[1].decode("utf-8"), "Fail"

        # Clear SEL
        output = "Test step: \n1. Clear SEL: "
        ret = util.exec_ipmi_cmd(case.sysConf, case.interface, "sel clear")
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + "OK\n"
        sleep(3)

        # Do power cycle
        output = output + "2. Power cycle: "
        ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(self.netfnCmd, self.powCycle))
        sleep(10)
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + "OK\n"

        # Check power cycle
        output = output + "3 Check power cycle SEL:"
        # Check power off
        ret = mfunc.FindSel(case.sysConf, 0x09, PwrUnitStatusSensorNum, 0x6f, 0x00, 0xff, 0xff)
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

    # ChassisStatusSensorNum might be different from platform
    def hardResetTest(self, case, ChassisStatusSensorNum):
        if mfunc.GetPowerStatus(case.sysConf) == 0: # power off
            # Do power up
            ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(self.netfnCmd, self.powUp))
            sleep(5)
            if ret[2] !=0:
                output = "Do power up before test hard reset fail."
                return output, ret[1].decode("utf-8"), "Fail"

        # Clear SEL
        output = "Test step: \n1. Clear SEL: "
        ret = util.exec_ipmi_cmd(case.sysConf, case.interface, "sel clear")
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + "OK\n"
        sleep(3)

        # Do hard reset
        output = output + "2. Hard reset: "
        ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(self.netfnCmd, self.hardReset))
        sleep(5)
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + "OK\n"

        # Check hard reset
        output = output + "3 Check hard reset SEL:"
        ret = mfunc.FindSel(case.sysConf, 0xc1, ChassisStatusSensorNum, 0x6f, 0x08, 0xff, 0xff)
        if ret[2] == 0:
            isSuccess = "Success"
        else:
            isSuccess = "Fail"
        output = output + ret[0]
        return output, ret[1], isSuccess