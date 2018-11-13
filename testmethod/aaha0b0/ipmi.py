__author__ = 'root'
import lib.libipmi.chassis as chassis
from lib.funcStruct import ipmiReportStr
from lib.funcStruct import interface

def doHardReset(case):
    case.reportType = ipmiReportStr.chassis
    chassisConl = chassis.chassisControl()
    return chassisConl.hardResetTest(case, 0xbd)
