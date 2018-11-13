__author__ = 'root'
import CommandUtil as util
import testmethod.methodfunc as mfunc
from lib.funcStruct import ipmiReportStr
from lib.funcStruct import interface
from time import sleep
import lib.libipmi.chassis as chassis
import lib.libipmi.app as app
import lib.libipmi.storage as storage


def doRawIPMICommandExpectValue(case):
    case.reportType = case.netfn
    ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, case.command)
    outputStr = (ret[0].decode("utf-8"))[1:]
    outputStr = outputStr.strip("\n")
    output, cmpState = mfunc.DiffExpectResult(outputStr, case.expectResult)
    error = ret[1].decode("utf-8")
    if 0 == ret[2]:
        if 0 == cmpState:
            isSuccess = "Success"
        else:
            isSuccess = "Fail"
    else:
        isSuccess = "Fail"

    return output,error,isSuccess

def doIPMICommandGetMeFw(case):
    case.reportType = case.netfn
    ret = util.exec_ipmi_getMeFw(case.sysConf, case.interface, case.preCmd, case.command)
    outputStr = (ret[0].decode("utf-8"))[1:]
    outputStr = outputStr.strip("\n")
    output, cmpState = mfunc.DiffExpectResult(outputStr, case.expectResult)
    error = ret[1].decode("utf-8")
    if 0 == ret[2]:
        if 0 == cmpState:
            isSuccess = "Success"
        else:
            isSuccess = "Fail"
    else:
        isSuccess = "Fail"

    return output,error,isSuccess

def doRawIPMICommandShowStatus(case):
    case.reportType = case.netfn
    ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, case.command)
    output = (ret[0].decode("utf-8"))
    output = output.strip("\n")
    error = ret[1].decode("utf-8")
    if ret[2] == 0:
        isSuccess = "Success"
    else:
        isSuccess = "Fail"
    return output,error,isSuccess

def doIPMICommandLine(case):
    case.reportType = ipmiReportStr.cmdLine
    ret = util.exec_ipmi_cmd(case.sysConf, case.interface, case.cmd)
    output = (ret[0].decode("utf-8"))
    output = output.strip("\n")
    error = ret[1].decode("utf-8")
    if ret[2] == 0:
        isSuccess = "Success"
    else:
        isSuccess = "Fail"
    return output,error,isSuccess

def doSetCmdCheckRecover(case):
    case.reportType = case.netfn
    # Get command
    ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(case.netfn, case.getCmd))
    if ret[2] !=0:
        output = "Get command before setting fail."
        return output, ret[1].decode("utf-8"), "Fail"
    orlOutputStr = mfunc.RawDataStrToHexStr((ret[0].decode("utf-8"))[1:].strip("\n"))
    return mfunc.setRawIPMICmdCheckRecover(case, orlOutputStr, 0, mfunc.RawDataLength(orlOutputStr))

def doSetCmdLineSetRecover(case):
    case.reportType = ipmiReportStr.cmdLine
    # Set command
    sleep(1)
    ret = util.exec_ipmi_cmd(case.sysConf, case.interface, case.cmd)
    output = "Test step: \n1. Set command: "
    if ret[2] !=0:
        output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
        return output, ret[1].decode("utf-8"), "Fail"
    output = output + "OK\n"
    sleep(1)

    # Recover data
    ret = util.exec_ipmi_cmd(case.sysConf, case.interface, case.setCmd)
    output = output + "2. Set recover data: "
    if ret[2] !=0:
        output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
        return output, ret[1].decode("utf-8"), "Fail"
    output = output + "OK\n"
    sleep(1)
    return output, "", "Success"

def doIPMI15Auth(case):
    case.reportType = ipmiReportStr.other
    ret = util.exec_ipmi_15_authType(case.sysConf, case.authType, interface.lan, "0x06 0x01")
    output = (ret[0].decode("utf-8"))
    output = output.strip("\n")
    error = ret[1].decode("utf-8")
    if ret[2] == 0:
        isSuccess = "Success"
    else:
        isSuccess = "Fail"
    return output,error,isSuccess

def doIPMI20Auth(case):
    case.reportType = ipmiReportStr.other
    ret = util.exec_ipmi_20_authType(case.sysConf, case.authType, interface.lanplus, "0x06 0x01")
    output = (ret[0].decode("utf-8"))
    output = output.strip("\n")
    error = ret[1].decode("utf-8")
    if ret[2] == 0:
        isSuccess = "Success"
    else:
        isSuccess = "Fail"
    return output,error,isSuccess

def doPowerDown(case):
    case.reportType = ipmiReportStr.chassis
    chassisConl = chassis.chassisControl()
    return chassisConl.powerDownTest(case)

def doPowerUp(case):
    case.reportType = ipmiReportStr.chassis
    chassisConl = chassis.chassisControl()
    return chassisConl.powerUpTest(case)

def doPowerCycle(case):
    case.reportType = ipmiReportStr.chassis
    chassisConl = chassis.chassisControl()
    if "RQ750" == case.sysConf.platform:
        return chassisConl.powerCycleTest(case, 0xf4)
    elif "AAHA0B0" == case.sysConf.platform:
        return chassisConl.powerCycleTest(case, 0xf4)
    else:
        return "BMCTester: There is no optional platform in doPowerCycle test!", "", "Fail"

def doWatchDogTimer(case):
    case.reportType = ipmiReportStr.app
    watchDog = app.watchDogTimer()
    if "RQ750" == case.sysConf.platform:
        return watchDog.watchDogTimerTest(case, 0xf8, 0xf4)
    elif "AAHA0B0" == case.sysConf.platform:
        return watchDog.watchDogTimerTest(case, 0xf8, 0xf4)
    else:
        return "BMCTester: There is no optional platform in doWatchDogTimer test!", "", "Fail"

def doSetSysInfoParameters(case):
    case.reportType = case.netfn

    # Get command
    ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(case.netfn, case.getCmd))
    if ret[2] !=0:
        output = "Get command before setting fail."
        return output, ret[1].decode("utf-8"), "Fail"
    orlOutputStr = (ret[0].decode("utf-8"))[1:].strip("\n")

    return mfunc.setRawIPMICmdCheckRecover(case, orlOutputStr, 1, mfunc.RawDataLength(orlOutputStr))

def doSetUserPasswordLogin(case):
    case.reportType = ipmiReportStr.app
    userAccess = app.userAccess()
    return userAccess.setUserPasswordAndLogin(case)

def doSetSerialConf(case):
    case.reportType = case.netfn

    # Get command
    ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(case.netfn, case.getCmd))
    if ret[2] !=0:
        output = "Get command before setting fail."
        return output, ret[1].decode("utf-8"), "Fail"
    orlOutputStr = (ret[0].decode("utf-8"))[1:].strip("\n")

    return mfunc.setRawIPMICmdCheckRecover(case, orlOutputStr, 1, mfunc.RawDataLength(orlOutputStr))

def doSetPEFConfPara(case):
    case.reportType = case.netfn

    # Get command
    ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(case.netfn, case.getCmd))
    if ret[2] !=0:
        output = "Get command before setting fail."
        return output, ret[1].decode("utf-8"), "Fail"
    orlOutputStr = (ret[0].decode("utf-8"))[1:].strip("\n")

    return mfunc.setRawIPMICmdCheckRecover(case, orlOutputStr, 1, mfunc.RawDataLength(orlOutputStr))

def doReserveSel(case):
    case.reportType = ipmiReportStr.storage
    selDevice = storage.SelDevice()
    return selDevice.reserveSelTest(case)

def doAddSelEntry(case):
    case.reportType = ipmiReportStr.storage
    selDevice = storage.SelDevice()
    if "AAHA0B0" == case.sysConf.platform:
        return selDevice.addSelEntryTest(case, 0x01, 0x03, 0x01, 0x00, 0xff, 0xff)
    elif "Odin" == case.sysConf.platform:
        return selDevice.addSelEntryTest(case, 0x01, 0x03, 0x01, 0x00, 0xff, 0xff)
    else:
        return "BMCTester: There is no optional platform in doAddSelEntry test!", "", "Fail"

def doSetSelTime(case):
    case.reportType = ipmiReportStr.storage
    selDevice = storage.SelDevice()
    return selDevice.setSelTimeTest(case)

def doReserveSdr(case):
    case.reportType = ipmiReportStr.storage
    sdrDevice = storage.SdrDevice()
    return sdrDevice.reserveSdrTest(case)

def doGetSdrTime(case):
    case.reportType = ipmiReportStr.storage
    sdrDevice = storage.SdrDevice()
    return sdrDevice.getSdrTimeTest(case)

def doSetSdrTime(case):
    case.reportType = ipmiReportStr.storage
    sdrDevice = storage.SdrDevice()
    return sdrDevice.setSdrTimeTest(case)

def doSetLanConfig(case):
    case.reportType = case.netfn

    # Get command
    ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(case.netfn, case.getCmd))
    if ret[2] !=0:
        output = "Get command before setting fail."
        return output, ret[1].decode("utf-8"), "Fail"
    orlOutputStr = (ret[0].decode("utf-8"))[1:].strip("\n")

    return mfunc.setRawIPMICmdCheckRecover(case, orlOutputStr, 1, mfunc.RawDataLength(orlOutputStr))