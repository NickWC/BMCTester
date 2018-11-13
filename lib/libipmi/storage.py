__author__ = 'Linda Huang'
import CommandUtil as util
import testmethod.methodfunc as mfunc
from time import sleep
from datetime import datetime

class SelDevice():
    def __init__(self):
        self.netfn = "0x0a"
        self.reserveSelCmd = "0x42"
        self.getSelEntryCmd = "0x43"
        self.addSelEntryCmd = "0x44"
        self.getSelTimeCml = "sel time get"
        self.setSelTimeCml = "sel time set"

    # Reserve SEL (Generate a reservation ID) and try to get SEL entry via reservation ID.
    def reserveSelTest(self, case):
        # Reserve SEL
        output = "Test step: \n1. Reserve SEL: "
        sleep(1)
        ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(self.netfn, self.reserveSelCmd))
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        reserveIdStr = ret[0].decode("utf-8").strip()
        output = output + reserveIdStr + "\n"
        sleep(1)

        # Get SEL entry via reservation ID
        output = output + "2. Get SEL entry via reservation ID: "
        ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface,
                                    "{0} {1} {2} {3}".format(self.netfn, self.getSelEntryCmd,
                                                                 mfunc.RawDataStrToHexStr(reserveIdStr), "0x00 0x00 0x00 0xff"))
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + "OK\n"

        return output, "", "Success"

    # Input sensor type, sensor number, event type, event data to add SEL entry
    # check SEL after adding SEL.
    def addSelEntryTest(self, case, type, num, eventType, eventD1, eventD2, eventD3):
        # Clear SEL
        output = "Test step: \n1. Clear SEL: "
        ret = util.exec_ipmi_cmd(case.sysConf, case.interface, "sel clear")
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + "OK\n"
        sleep(2)

        # Add SEL entry
        output = output + "2. Add SEL entry: "
        ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface,
                                    "{0} {1} {2} {3} {4} {5} {6} {7} {8}".format(self.netfn, self.addSelEntryCmd,
                                                                 "0x00 0x00 0x02 0x00 0x00 0x00 0x00 0x20 0x00 0x04",
                                                                 type, num, eventType, eventD1, eventD2, eventD3))
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + "OK\n"
        sleep(2)

        # Check SEL after adding SEL
        output = output + "3. Check SEL after adding SEL: "
        ret = mfunc.FindSel(case.sysConf, type, num, eventType, eventD1, eventD2, eventD3)
        if ret[2] !=0:
            output = output + ret[0]
            return output, ret[1], "Fail"
        output = output + "OK\n"

        return output, "", "Success"

    # Set SEL time as current time.
    def setSelTimeTest(self, case):
        # Set SEL time as current time
        output = "Test step: \n1. Set SEL time as current time: "
        ret = util.exec_ipmi_cmd(case.sysConf, case.interface, "{0} \"{1}\"".format(self.setSelTimeCml,
                                                                                  datetime.now().strftime('%m/%d/%Y %H:%M:%S')))
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + "OK\n"
        sleep(2)

        # Show SEL time after setting
        output = output + "2. Show SEL time after setting: "
        ret = util.exec_ipmi_cmd(case.sysConf, case.interface,
                                 "{0}".format(self.getSelTimeCml))
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + ret[0].decode("utf-8") + "\n"

        return output, "", "Success"

class SdrDevice():
    def __init__(self):
        self.netfn = "0x0a"
        self.reserveSdrCmd = "0x22"
        self.getSdrCmd = "0x23"
        self.getSdrTimeCmd = "0x28"
        self.setSdrTimeCmd = "0x29"

    # Reserve SDR (Generate a reservation ID) and try to get SDR entry via reservation ID.
    def reserveSdrTest(self, case):
        # Reserve SDR
        output = "Test step: \n1. Reserve SDR: "
        sleep(1)
        ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(self.netfn, self.reserveSdrCmd))
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        reserveIdStr = ret[0].decode("utf-8").strip()
        output = output + reserveIdStr + "\n"
        sleep(1)

        # Get SDR via reservation ID
        output = output + "2. Get SDR entry via reservation ID: "
        ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface,
                                    "{0} {1} {2} {3}".format(self.netfn, self.getSdrCmd,
                                                                 mfunc.RawDataStrToHexStr(reserveIdStr), "0x00 0x00 0x00 0xff"))
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + "OK\n"

        return output, "", "Success"

    # Get SDR time.
    def getSdrTimeTest(self, case):
        ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(self.netfn, self.getSdrTimeCmd))
        if ret[2] !=0:
            return ret[0].decode("utf-8").strip(), ret[1].decode("utf-8").strip(), "Fail"
        timeHexstr = ret[0].decode("utf-8").strip()
        timeSec = mfunc.BigEndianHexStrToValue(timeHexstr)
        dateTime = datetime.fromtimestamp(timeSec + datetime(1970,1,1).timestamp())
        return dateTime.strftime('%m/%d/%Y %H:%M:%S'), "", "Success"

    # Set SDR time as current time.
    def setSdrTimeTest(self, case):
        # Set SDR time as current time
        output = "Test step: \n1. Set SDR time as current time: "
        timeSec = (datetime.now()-datetime(1970,1,1)).total_seconds()
        time4byte = mfunc.ValueToBigEndianHexStr(timeSec)
        ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1} {2}".format(self.netfn, self.setSdrTimeCmd, time4byte))
        if ret[2] !=0:
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1].decode("utf-8"), "Fail"
        output = output + "OK\n"
        sleep(2)

        # Show SDR time after setting
        output = output + "2. Show SDR time after setting: "
        ret = self.getSdrTimeTest(case)
        if ret[2] != "Success":
            output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
            return output, ret[1], "Fail"
        output = output + ret[0] + "\n"

        return output, "", "Success"