__author__ = 'root'

import sys
from datetime import datetime
import TestCase as tc
import Report as rp
import SysConfig as sysconf

'''class arguments():
    def __init__(self):
        self.cmdLine = dict({
            "-f": "Test Case File"
        })
    def argHelp(self):
        print("\nCommands:")
        for key in self.cmdLine.keys():
            print("\t%-5s [%s]:\n" % (key, self.cmdLine.get(key)))
            print("\t\t%-50s\n" % ("Load test case files."))
    def detectArg(self, argv):
        argDict = {}
        index = 0
        while index < len(argv):
            if "help" == argv[index]:
                self.argHelp()
                return False, argDict
            argValue = self.cmdLine.get(argv[index])
            if argValue: #Find a key
                argList = []
                index += 1
                while index < len(argv):
                    if self.cmdLine.get(argv[index]) == None: #If it's not a key, append to list
                        argList.append(argv[index])
                        index += 1
                    else:
                        break
                if 0 == len(argList): #Command key is with no value
                    print("Command line fail!")
                    self.argHelp()
                    return False, argDict
                argDict[argValue] = argList
            else:
                self.argHelp()
                return False, argDict
        return True, argDict'''

class timer:
    def __init__(self):
        self.sTime = None
        self.eTime = None
        self.start = ""
        self.end = ""
        self.duration = ""
    def timeStart(self):
        self.sTime = datetime.now()
        self.start = self.sTime.strftime('%Y-%m-%d %H:%M:%S')
    def timeEnd(self):
        self.eTime = datetime.now()
        self.end = self.eTime.strftime('%Y-%m-%d %H:%M:%S')
    def spendTime(self):
        if self.start and self.end:
            delta = self.eTime - self.sTime
            self.duration = "{0}s".format(str(delta.seconds))

def doPlan(plan, report):
    for case in plan.testcaseList:
        print("Doing test \"{0}\" ..".format(case.name))
        ret = case.doTest()

        print("\tcase {0} is {1}".format(case.name,ret[2]))

        report.addcase(case, ret[0], ret[1], ret[2])

def main(argv):
    '''args = arguments()
    isArgRight, argDict = args.detectArg(argv[1:])
    if False == isArgRight:
        return False'''

    config = sysconf.SysConfig("config.txt")
    for deviceConf in config.deviceconf:
        testTime = timer()
        testTime.timeStart()
        print("{0} test start...".format(deviceConf.device))
        plan =tc.TestPlan(deviceConf)

        if True == plan.loadCase():
            report = rp.TestReport()

            doPlan(plan, report)
            testTime.timeEnd()
            testTime.spendTime()
            print("\nStart time: {0}".format(testTime.start))
            print("End time: {0}".format(testTime.end))
            print("Duration: {0}\n\n".format(testTime.duration))

            report.preProcess()
            report.ReportFileTxt(deviceConf.device, testTime)
            report.ReportFileHtml(deviceConf.device, testTime)
            report.dumpJson(deviceConf.device)
            reportTmp = rp.TestReport()
            reportTmp.mergeJson(["output/DEVICE1/TestReport.json"])
            reportTmp.ReportFileTxt("MERGE", None)
            reportTmp.ReportFileHtml("MERGE", None)
            reportTmp.dumpJson("MERGE")
        else:
            print("{0} load test case file fail!".format(deviceConf.device))
            return False
    return True

if __name__ == "__main__":
    main(sys.argv)