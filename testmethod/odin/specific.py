__author__ = 'Linda Huang'
import CommandUtil as util
import testmethod.methodfunc as mfunc
from time import sleep

def doiflashUpdateFw(case):
    # Download BMC FW image from server
    output = "Test step: \n1. Download BMC FW image from server: "
    filename = util.dowload_latest_image(case.sysConf)
    if filename == None:
        output = output + "Fail\n"
        return output, "", "Fail"
    output = output + filename + "\n"

    # Upgrade BMC using Yafuflash
    output = output + "2. Upgrade BMC using iflash: "
    ret = util.exec_iflash_updateFw(case.sysConf, filename)
    if ret[2] !=0:
        output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
        return output, ret[1].decode("utf-8"), "Fail"
    output = output + "OK\n"

    # BMC reboot
    output = output + "3. BMC reboot: "
    print("\tResetting firmware...")
    ret = mfunc.ColdReset(case.sysConf)
    if ret[2] !=0:
        output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
        return output, ret[1].decode("utf-8"), "Fail"
    output = output + "OK\n"

    # Get Device ID to see FW version
    output = output + "4. Get Device ID to see FW version: "
    # Wait for BMC ready
    for i in range(0,10):
        fwVersion = mfunc.GetDeviceFwVersion(case.sysConf)
        if fwVersion == None:
            sleep(10)
        else:
            break
    if fwVersion == None:
        output = output + "Fail({0})\n".format("Get device ID fail.")
        return output, "", "Fail"
    output = output + fwVersion + "\n"
    return output, "", "Success"