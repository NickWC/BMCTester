__author__ = 'root'
import os
import json
from enum import Enum
import SysConfig as sconf

class TestType(Enum):
    IPMI = "IPMI"
    CYCLE = "CYCLE"
    SPECIFIC = "SPECIFIC"
    MANUAL = "MANUAL"

class TestCase:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.testType = ""
        self.testMethod = None
        self.platform = ""
        self.reportType = ""

    def doTest(self):
        pass

class IPMITest(TestCase):
    def __init__(self, name, sysConf, data):
        self.sysConf = sysConf
        self.testType = TestType.IPMI
        self.description = data.get("description")
        self.name = name
        self.platform = data.get("platform")
        self.testMethod = data.get("testmethod")
        self.reportType = ""
        self.interface = data.get("interface")
        self.netfn = data.get("netfn")
        self.cmd = data.get("cmd")
        self.expectResult = data.get(self.sysConf.platform + "_expectResult")
        self.data = data.get("data")
        self.getCmd = data.get("getCmd")
        self.setCmd = data.get("setCmd")
        if(None == self.expectResult):
            self.expectResult = data.get("expectResult")
        self.target = data.get("target")
        self.bridge = data.get("bridge")
        self.authType = data.get("authType")

    def strLower(self):
        if self.interface:
            self.interface = self.interface.lower()
        if self.netfn and self.cmd:
            self.netfn = self.netfn.lower()
            self.cmd = self.cmd.lower()
            self.command = self.netfn+" "+self.cmd
        if self.expectResult:
            self.expectResult = self.expectResult.lower()
        if self.target:
            self.preCmd = "-t " + self.target.lower() + " -b " + self.bridge.lower()

    def doTest(self):
        if self.testMethod != None and self.testMethod != "":
            self.strLower()
            if self.platform == "ANY":
                modname = "testmethod."+self.testType.name.lower()
            else:
                modname = "testmethod.{0}.{1}".format(self.platform.lower(),self.testType.name.lower())
            mod = __import__(modname,fromlist=[TestType.IPMI.name.lower()])
            testfunction = getattr(mod,self.testMethod)
            return testfunction(self)
        else:
            return "Error!! There is no test method in \"{0}\" test case.\nPlease check test case file.".format(self.name), "", "Fail"

class CycleTest(TestCase):
    def __init__(self):
        super.__init__(self)
        self.testType = TestType.CYCLE

class SpecificTest(TestCase):
    def __init__(self, name, sysConf, data):
        self.sysConf = sysConf
        self.testType = TestType.SPECIFIC
        self.description = data.get("description")
        self.name = name
        self.platform = data.get("platform")
        self.testMethod = data.get("testmethod")
        self.reportType = ""
    def doTest(self):
        if self.testMethod != None and self.testMethod != '':
            if self.platform == "ANY":
                modname = "testmethod."+self.testType.name.lower()
            else:
                modname = "testmethod.{0}.{1}".format(self.platform.lower(),self.testType.name.lower())
            mod = __import__(modname,fromlist=[TestType.SPECIFIC.name.lower()])
            testfunction = getattr(mod,self.testMethod)
            return testfunction(self)
        else:
            return "Error!! There is no test method in \"{0}\" test case.\nPlease check test case file.".format(self.name), "", "Fail"

class ManualTest(TestCase):
    def __init__(self, name, sysConf, data):
        self.sysConf = sysConf
        self.testType = TestType.MANUAL
        self.description = data.get("description")
        self.name = name
        self.platform = data.get("platform")
        self.reportType = ""
    def doTest(self):
        return "Need manual test!", "", "Fail"


class TestPlan:
    def __init__(self,deviceconf):
        self.lists = list()
        self.cases = list()
        self.libCases = dict()
        self.testcaseList = list()
        #self.sysConf = sconf.SysConfig("config.txt")
        self.sysConf = deviceconf
    def convert2TestCase(self):
        for tc in self.cases:
            keys = dict(tc).keys()
            for key in keys:
                testcase = dict(tc).get(key)
                case = None
                if "IPMI" == dict(testcase).get("testType"):
                    case = IPMITest(key, self.sysConf, testcase)

                if "CYCLE" == dict(testcase).get("testType"):
                    case = None
                    #case = CycleTest(key, self.sysConf, testcase)

                if "SPECIFIC" == dict(testcase).get("testType"):
                    case = SpecificTest(key, self.sysConf, testcase)

                if "MANUAL" == dict(testcase).get("testType"):

                    case = ManualTest(key, self.sysConf, testcase)

                if case != None:
                    if case.platform == case.sysConf.platform or case.platform == "ANY":
                        self.testcaseList.append(case)

    def findFile(self, file, casePath):
        existFileList = os.listdir(casePath)
        isFind = False
        for existFile in existFileList:
            if file == existFile:
                isFind = True
                return True
        return False

    def loadPlan(self):
        casePath = "{0}/testcase/case".format(os.getcwd())
        for planList in self.lists:
            for caseList in planList["list"]:
                for casefile in caseList.keys():
                    if True == self.findFile(casefile, casePath):
                        if None == self.libCases.get(casefile):
                            print("Load \"" + casefile + "\" test case ..\n")
                            f = open(casePath+"/"+casefile)
                            self.libCases[casefile]=dict(json.load(f))
                            f.closed
                        for case in caseList.get(casefile):
                            caseInfo = self.libCases[casefile].get(case)
                            if None == caseInfo:
                                print("Error! Can't find \"{0}\" case in {1}".format(case, casefile))
                            else:
                                self.cases.append({case:caseInfo})
                    else:
                        print("{0} is not found in {1}.".format(casefile, casePath))
                        return False
        return True

    def loadCase(self):
        planPath = "{0}/testcase/list".format(os.getcwd())
        for plan in self.sysConf.testplan:
            if True == self.findFile(plan, planPath):
                print("Load \"" + plan + "\" test plan ..\n")
                f = open(planPath+"/"+plan)
                self.lists.append(dict(json.load(f)))
                f.closed
            else:
                print("{0} is not found in {1}.".format(plan, planPath))
                return False
        if False == self.loadPlan():
            return False
        self.convert2TestCase()
        return True