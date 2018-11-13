__author__ = 'Linda Huang'
import CommandUtil as util
from time import sleep

# Turn hexadecimal output string to value array
def StrToIntArray(str):
    str_tmp = ""
    value = []
    str = str.strip()
    strlen = len(str)
    for i in range(0, strlen):
        if " " == str[i]:
            value.append(int(str_tmp,16))
            str_tmp = ""
        else:
            str_tmp = str_tmp + str[i]
            if i == strlen-1:
                value.append(int(str_tmp,16))
    return value

# Add "0x" header for hexadecimal output string
# EX: "12 34 56" to "0x12 0x34 0x56"
def RawDataStrToHexStr(str):
    HexStr = ""
    valueList = StrToIntArray(str)
    for value in valueList:
        HexStr = "{0} 0x{1:02x}".format(HexStr, value)
    return HexStr.strip()

# Select raw data range
def RawDataSelection(str, offsetStart, offsetEnd):
    seleDataStr = ""
    valueList = StrToIntArray(str)
    for value in valueList[offsetStart:offsetEnd]:
        seleDataStr = "{0} {1:02x}".format(seleDataStr, value)
    return seleDataStr

def RawDataLength(str):
    valueList = StrToIntArray(str)
    return len(valueList)

# Transform big endian Hex string to value
def BigEndianHexStrToValue(str):
    valueList = StrToIntArray(str)
    value = 0
    for i in range(0, len(valueList)):
        value = value + (valueList[i]<<(8*i))
    return value

# Transform value to big endian Hex string
def ValueToBigEndianHexStr(value):
    BEBHexStr = ""
    Hexstr = hex(int(value))
    HexStrLen = len(Hexstr)
    if (HexStrLen % 2) == 0:
        HexStr = "{0}".format(Hexstr[2: HexStrLen])
    else:
        HexStr = "{0}{1}".format(0, Hexstr[2: HexStrLen])
    for iStr in range(0, len(HexStr), 2).__reversed__():
        BEBHexStr = "{0} 0x{1}".format(BEBHexStr, HexStr[iStr:iStr+2])
    return BEBHexStr.strip()

# Compare two output string
def DiffExpectResult(output, expect):
    cmpStr = ""
    cmpState = 0
    outputVal = StrToIntArray(output)
    expectVal = StrToIntArray(expect)
    outputLen = len(outputVal)
    expectLen = len(expectVal)
    if outputLen <= expectLen:
        for i in range(0, expectLen):
            if i >= outputLen:
                cmpStr = cmpStr + "(" + format(expectVal[i], "02x") + ") "
                cmpState = 1
            else:
                if outputVal[i] == expectVal[i]:
                    cmpStr = cmpStr + format(outputVal[i], "02x") + " "
                else:
                    cmpStr = cmpStr + format(outputVal[i], "02x") + "(" + format(expectVal[i], '02x') + ") "
                    cmpState = 1
    else:
        for i in range(0, outputLen):
            if i >= expectLen:
                cmpStr = cmpStr + format(outputVal[i], "02x") + "(N/A) "
                cmpState = 1
            else:
                if outputVal[i] == expectVal[i]:
                    cmpStr = cmpStr + format(outputVal[i], "02x") + " "
                else:
                    cmpStr = cmpStr + format(outputVal[i], "02x") + "(" + format(expectVal[i], '02x') + ") "
                    cmpState = 1
    return cmpStr, cmpState

def FindSel(sysConf, type, num, eventType, eventD1, eventD2, eventD3):
    selRecordId = "0x00 0x00"
    IdL = 0
    IdH = 0
    while (IdL + (IdH<<8)) != 0xffff:
        ret = util.exec_ipmi_rawcmd(sysConf, "lan", "0x0a 0x43 0x00 0x00 "+ selRecordId+" 0x00 0xff")
        if ret[2] !=0:
            return ret[0].decode("utf-8"), ret[1].decode("utf-8"), -1
        selout = (ret[0].decode("utf-8"))
        selout = selout.replace("\n", "")
        outputVal = StrToIntArray(selout)
        if (outputVal[12] == type) and (outputVal[13] == num) and (outputVal[14] == eventType) and (outputVal[15] == eventD1) and (outputVal[16] == eventD2) and (outputVal[17] == eventD3):
            return "OK\n", ret[1].decode("utf-8"), 0
        IdL = outputVal[0]
        IdH = outputVal[1]
        selRecordId = "{0} {1}".format(str(IdL),str(IdH))
    output = "Fail({0})\n".format("There is no log in SEL")
    return output, ret[1].decode("utf-8"), -1

def GetPowerStatus(sysConf):
    ret = util.exec_ipmi_rawcmd(sysConf, "lan", "0x00 0x01")
    if ret[2] !=0:
        return -1
    outputVal = StrToIntArray(ret[0].decode("utf-8"))
    if outputVal[0] & 0x01:
        #power on
        return 1
    else:
        #power off
        return 0

def GetDeviceFwVersion(sysConf):
    ret = util.exec_ipmi_rawcmd(sysConf, "lan", "0x06 0x01")
    if ret[2] !=0:
        return None
    outputVal = StrToIntArray(ret[0].decode("utf-8"))
    fw_1 = hex(outputVal[2])
    fw_2 = hex(outputVal[3])
    return "{0}.{1}".format(fw_1[2:], fw_2[2:])

def setRawIPMICmdCheckRecover(case, orlOutputStr, offsetStart, offsetEnd):
    recoverStr = RawDataStrToHexStr(RawDataSelection(orlOutputStr, offsetStart, offsetEnd))

    # Set command
    sleep(1)
    ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(case.command, case.data))
    output = "Test step: \n1. Set command: "
    if ret[2] !=0:
        output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
        return output, ret[1].decode("utf-8"), "Fail"
    output = output + "OK\n"
    sleep(1)

    # Check Setting (Get command then check)
    output = output + "2. Check setting command: "
    ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(case.netfn, case.getCmd))
    if ret[2] !=0:
        output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
        return output, ret[1].decode("utf-8"), "Fail"
    outputStr = (ret[0].decode("utf-8"))[1:].strip("\n")
    cmpOutput, cmpState = DiffExpectResult(RawDataSelection(outputStr, offsetStart, offsetEnd), case.data)
    if cmpState !=0:
        output = output + "Fail({0})\n".format(cmpOutput)
        return output, "", "Fail"
    output = output + "OK\n"

    # Recover data
    ret = util.exec_ipmi_rawcmd(case.sysConf, case.interface, "{0} {1}".format(case.command, recoverStr))
    output = output + "3. Recover data: "
    if ret[2] !=0:
        output = output + "Fail({0})\n".format(ret[0].decode("utf-8").strip())
        return output, ret[1].decode("utf-8"), "Fail"
    output = output + "OK\n"
    sleep(1)
    return output, "", "Success"

def ColdReset(sysConf):
    ret =  util.exec_ipmi_rawcmd(sysConf, "lan", "{0} {1}".format(0x06, 0x02))
    sleep(150)
    return ret[0].decode("utf-8"), ret[1].decode("utf-8"), ret[2]