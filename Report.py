__author__ = 'Linda Huang'

import os
import json
from TestCase import TestType
from lib.funcStruct import ipmiReport

class InfoResult():
    def __init__(self):
        self.description = ""
        self.testType = ""
        self.reportType = ""
    def autoTestInfoResult(self, caseInfo):
        self.description = caseInfo.description
        self.testType = caseInfo.testType.value
        self.reportType = caseInfo.reportType
        return self
    def loadJsonResult(self, dictJson):
        self.description = dictJson.get('description')
        self.testType = dictJson.get('testType')
        self.reportType = dictJson.get('reportType')
        return self

class TestResult():
    def __init__(self):
        self.info = None
        self.output = ""
        self.error = ""
        self.issuccess = ""
    def autoTestResult(self, caseInfo, output, error, issuccess):
        self.info = InfoResult().autoTestInfoResult(caseInfo)
        self.output = output
        self.error = error
        self.issuccess = issuccess
        return self
    def loadJsonResult(self, dictJson):
        self.info = dictJson.get('info')
        self.output = dictJson.get('output')
        self.error = dictJson.get('error')
        self.issuccess = dictJson.get('issuccess')
        return self

class ReportSum():
    def __init__(self):
        self.success = 0
        self.fail = 0
    def sumUpdate(self, result):
        if "Success" == result.issuccess:
            self.success += 1
        elif "Fail" == result.issuccess:
            self.fail += 1

class JsonReport():
    def __init__(self):
        self.ipmi = dict(CHASSIS = {}, BRIDGE = {}, SENSOR_EVENT = {}, APP = {}, FIRMWARE = {},
                         STORAGE = {}, TRANSPORT = {}, OEM = {}, OTHER = {}, CMD_LINE = {})
        self.cycle = {}
        self.specific = {}
        self.manual = {}
    def autoTestJsonReport(self, report):
        self.ipmi = report.ipmi
        self.cycle = report.cycle
        self.specific = report.specific
        self.manual = report.manual
        return self
    def loadJsonReport(self, dictJson):
        self.ipmi = dictJson.get('ipmi')
        self.cycle = dictJson.get('cycle')
        self.specific = dictJson.get('specific')
        self.manual = dictJson.get('manual')
        return self

class ReportEncoder(json.JSONEncoder):
    def default(self, obj):
        dumpObj = {}
        dumpObj.update(obj.__dict__)
        return dumpObj

class ReportDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.dict2obj)
    def dict2obj(self, dictJson):
        if "ipmi" in dictJson:
            return JsonReport().loadJsonReport(dictJson)
        if "info" in dictJson:
            return TestResult().loadJsonResult(dictJson)
        if "description" in dictJson:
            return InfoResult().loadJsonResult(dictJson)
        else:
            return dictJson

class TestReport():
    def __init__(self):
        self.resultDict = {}
        self.ipmi = dict(CHASSIS = {}, BRIDGE = {}, SENSOR_EVENT = {}, APP = {}, FIRMWARE = {},
                         STORAGE = {}, TRANSPORT = {}, OEM = {}, OTHER = {}, CMD_LINE = {})
        self.cycle = {}
        self.specific = {}
        self.manual = {}
        self.rpSum = ReportSum()

    def rpSumCunt(self, resultDict):
        for key in resultDict.keys():
            self.rpSum.sumUpdate(resultDict[key])

    def rpJsonSumCunt(self):
        for key in self.ipmi.keys():
            self.rpSumCunt(self.ipmi[key])
        self.rpSumCunt(self.cycle)
        self.rpSumCunt(self.specific)
        self.rpSumCunt(self.manual)

    def dumpJson(self, device):
        outputPath = "{0}/output".format(os.getcwd())
        if not os.path.exists(outputPath):
            os.mkdir(outputPath)
        imagePath = "{0}/{1}".format(outputPath, device)
        if not os.path.exists(imagePath):
            os.mkdir(imagePath)
        file = open(imagePath+"/TestReport.json","w")
        file.write("{0}\n".format(ReportEncoder(sort_keys = True, indent = 4).encode(JsonReport().autoTestJsonReport(self).__dict__)))
        file.close()

    def mergeJson(self, jsonList):
        for jsonfile in jsonList:
            file = open(jsonfile,"r")
            obj = ReportDecoder().decode(file.read())
            file.close()
            for key in obj.ipmi.keys():
                self.ipmi[key].update(obj.ipmi[key])
            self.cycle.update(obj.cycle)
            self.specific.update(obj.specific)
            self.manual.update(obj.manual)
        self.rpJsonSumCunt()

    def addcase(self, caseInfo, output, error, issuccess):
        self.resultDict[caseInfo.name] = TestResult().autoTestResult(caseInfo, output, error, issuccess)

    def preProcess(self):
        def displaySort(resultDict):
            ipmi_reportType = {
                "CHASSIS" : lambda: self.ipmi["CHASSIS"].update({key:case}),
                "BRIDGE" : lambda: self.ipmi["BRIDGE"].update({key:case}),
                "SENSOR_EVENT" : lambda: self.ipmi["SENSOR_EVENT"].update({key:case}),
                "APP" : lambda: self.ipmi["APP"].update({key:case}),
                "FIRMWARE" : lambda: self.ipmi["FIRMWARE"].update({key:case}),
                "STORAGE" : lambda: self.ipmi["STORAGE"].update({key:case}),
                "TRANSPORT" : lambda: self.ipmi["TRANSPORT"].update({key:case}),
                "OEM" : lambda: self.ipmi["OEM"].update({key:case}),
                "OTHER" : lambda: self.ipmi["OTHER"].update({key:case}),
                "CMD_LINE" : lambda: self.ipmi["CMD_LINE"].update({key:case})
            }
            for key in resultDict.keys():
                case = resultDict[key]
                if(TestType.IPMI.value == case.info.testType):
                    ipmi_reportType.get(ipmiReport.get(case.info.reportType), lambda: self.ipmi["OTHER"].update({key:case}))()
                if(TestType.CYCLE.value == case.info.testType):
                    self.cycle.update({key:case})
                if(TestType.SPECIFIC.value == case.info.testType):
                    self.specific.update({key:case})
                if(TestType.MANUAL.value == case.info.testType):
                    self.manual.update({key:case})

        displaySort(self.resultDict)
        self.rpSumCunt(self.resultDict)

    def findEndLine(self, str):
        lineList = []
        str = str.strip()
        str = "\n" + str + "\n"
        index = 0
        strStart = index
        index += 1
        while index < len(str):
            if ("\n" == str[index]) or ("\r" == str[index]): #"Str"+"\n" or "Str"+"\r"
                if "\n" == str[strStart]: # "\n"+"Str"
                    lineList.append(str[strStart:index].strip())
                    strStart = index
                elif "\r" == str[strStart] and "\n" == str[strStart+1]: # "\r\n"+"Str"
                    # "\r\n" is treated as "\n"
                    lineList.append(str[strStart:index].strip())
                    strStart = index
                elif "\r" == str[strStart]: # "\r"+"Str"
                    lineList.pop()
                    lineList.append(str[strStart:index].strip())
                    strStart = index
                if "\r" == str[index] and "\n" == str[index+1]: # "Str"+"\r\n"
                    index += 1
            index += 1
        if 0 == len(lineList):
            lineList.append(str)
        return lineList

    def ReportFileTxt(self, device, testTime):
        def wrapInTxt(rawStr):
            str = ""
            lineList = self.findEndLine(rawStr)
            for line in lineList:
                str = str + "\t\t" + line + "\n"
            return str
        def writeTxt(nfName, caseDict, file):
            file.write("**------------ %s\n\n" %(nfName))
            for key in caseDict.keys():
                case = caseDict[key]
                info = caseDict[key].info
                file.write("%-15s %s\n" %("Case Name:", key))
                file.write("%-15s \n%s\n" %("Description:", wrapInTxt(info.description)))
                file.write("%-15s \n%s\n" %("Output:", wrapInTxt(case.output)))
                if case.error:
                    file.write("%-15s \n%s\n" %("Error:", wrapInTxt(case.error)))
                file.write("%-15s %s\n" %("Result:", case.issuccess))
                file.write("----------------------------------------------\n\n")

            file.write("\n\n")

        outputPath = "{0}/output".format(os.getcwd())
        if not os.path.exists(outputPath):
            os.mkdir(outputPath)
        imagePath = "{0}/{1}".format(outputPath, device)
        if not os.path.exists(imagePath):
            os.mkdir(imagePath)
        file = open(imagePath+"/TestReport.txt","w")

        file.write("*************************** %-20s ***************************\n" %("BMC Tester Report"))
        file.write("** %-12s %s\n" %("Device:", device))
        if testTime != None:
            file.write("** %-12s %s\n" %("Start time :", testTime.start))
            file.write("** %-12s %s\n" %("End time :", testTime.end))
            file.write("** %-12s %s\n" %("Duration:", testTime.duration))
        file.write("**\n")
        file.write("** %-12s %d/%d\n" %("Success:", self.rpSum.success, (self.rpSum.success+self.rpSum.fail)))
        file.write("** %-12s %d/%d\n" %("Fail:", self.rpSum.fail, (self.rpSum.success+self.rpSum.fail)))
        file.write("****************************************************************************\n\n")
        file.write("**------------------------------ %-10s ------------------------------**\n\n" %(TestType.IPMI.value))
        if self.ipmi["CHASSIS"]:
            writeTxt("CHASSIS", self.ipmi["CHASSIS"], file)
        if self.ipmi["BRIDGE"]:
            writeTxt("BRIDGE", self.ipmi["BRIDGE"], file)
        if self.ipmi["SENSOR_EVENT"]:
            writeTxt("SENSOR EVENT", self.ipmi["SENSOR_EVENT"], file)
        if self.ipmi["APP"]:
            writeTxt("APP", self.ipmi["APP"], file)
        if self.ipmi["FIRMWARE"]:
            writeTxt("FIRMWARE", self.ipmi["FIRMWARE"], file)
        if self.ipmi["STORAGE"]:
            writeTxt("STORAGE", self.ipmi["STORAGE"], file)
        if self.ipmi["TRANSPORT"]:
            writeTxt("TRANSPORT", self.ipmi["TRANSPORT"], file)
        if self.ipmi["OEM"]:
            writeTxt("OEM", self.ipmi["OEM"], file)
        if self.ipmi["OTHER"]:
            writeTxt("OTHER", self.ipmi["OTHER"], file)
        if self.ipmi["CMD_LINE"]:
            writeTxt("CMD LINE", self.ipmi["CMD_LINE"], file)

        file.write("**------------------------------ %-10s ------------------------------**\n\n" %(TestType.CYCLE.value))
        writeTxt("CYCLE", self.cycle, file)

        file.write("**------------------------------ %-10s ------------------------------**\n\n" %(TestType.SPECIFIC.value))
        writeTxt("SPECIFIC", self.specific, file)

        file.write("**------------------------------ %-10s ------------------------------**\n\n" %(TestType.MANUAL.value))
        writeTxt("MANUAL", self.manual, file)

        file.close()

    def ReportFileHtml(self, device, testTime):
        def wrapInHtml(rawStr):
            str = ""
            lineList = self.findEndLine(rawStr)
            for line in lineList:
                str = str + "\t\t\t\t\t\t" + line + "<br>\n"
            return str
        def writeHtml(nfName, caseDict, file):
            file.write("\t<section>\n")
            file.write("\t\t<p><blockquote><fieldset>\n")
            file.write("\t\t\t<legend><h2>" + nfName + "</h2></legend>\n")
            file.write("\t\t\t<blockquote><table class=\"reportTb\"  border=\"1\">\n")
            file.write("\t\t\t\t<tr>\n")
            file.write("\t\t\t\t\t<th class=\"testCase\">Test case</th>\n")
            file.write("\t\t\t\t\t<th class=\"description\">Description</th>\n")
            file.write("\t\t\t\t\t<th class=\"output\">Output</th>\n")
            file.write("\t\t\t\t\t<th class=\"result\">Result</th>\n")
            file.write("\t\t\t\t</tr>\n")

            for key in caseDict.keys():
                case = caseDict[key]
                info = caseDict[key].info
                file.write("\t\t\t\t<tr>\n")
                file.write("\t\t\t\t\t<td class=\"testCase\">" + key + "</td>\n")
                file.write("\t\t\t\t\t<td class=\"description\">" + info.description + "</td>\n")
                file.write("\t\t\t\t\t<td class=\"output\">\n" + wrapInHtml(case.output) + "\n")
                if case.error:
                    file.write("\t\t\t\t\t\tError:\n")
                    file.write(wrapInHtml(case.error) + "\n")
                file.write("\t\t\t\t\t</td>\n")
                if "Success"== case.issuccess:
                    file.write("\t\t\t\t\t<td class=\"result success\">" + case.issuccess + "</td>\n")
                else:
                    file.write("\t\t\t\t\t<td class=\"result fail\">" + case.issuccess + "</td>\n")
                file.write("\t\t\t\t</tr>\n")

            file.write("\t\t\t</table></blockquote>\n")
            file.write("\t\t</fieldset></blockquote></p>\n")
            file.write("\t</section><br><br>\n")
        def cssStyle():
            file.write("\t\tbody{\n\t\t\tmin-width: 1450px;\n\t\t\tmax-width: 1450px;\n\t\t\tmargin:0px auto;\n\t\t}\n")
            file.write("\t\tlegend{\n\t\t\tcolor: #008B00;\n\t\t}\n")
            file.write("\t\tfieldset{\n\t\t\tborder-radius: 30px;\n\t\t}\n")
            file.write("\t\t.reportTb{\n\t\t\tborder:8px #EFB35A groove;\n\t\t}\n")
            file.write("\t\t.success{\n\t\t\tbackground-color: #6AD25A;\n\t\t}\n")
            file.write("\t\t.fail{\n\t\t\tbackground-color: #FF9797;\n\t\t}\n")
            file.write("\t\t.testCase{\n\t\t\tmin-width: 350px;\n\t\t\tmax-width: 350px;\n\t\t}\n")
            file.write("\t\t.description{\n\t\t\tmin-width: 400px;\n\t\t\tmax-width: 400px;\n\t\t}\n")
            file.write("\t\t.output{\n\t\t\tmin-width: 400px;\n\t\t\tmax-width: 400px;\n\t\t}\n")
            file.write("\t\t.result{\n\t\t\tmin-width: 80px;\n\t\t\tmax-width: 80px;\n\t\t\ttext-align: center;\n\t\t}\n")

        outputPath = "{0}/output".format(os.getcwd())
        if not os.path.exists(outputPath):
            os.mkdir(outputPath)
        imagePath = "{0}/{1}".format(outputPath, device)
        if not os.path.exists(imagePath):
            os.mkdir(imagePath)
        file = open(imagePath+"/TestReport.html","w")

        file.write("<html>\n")
        file.write("<head>\n")
        file.write("\t<title>{0} BMC Tester</title>\n".format(device))
        file.write("\t<style type=\"text/css\">\n")
        cssStyle()
        file.write("\t</style>\n")
        file.write("</head>\n")
        file.write("<body>\n")

        file.write("\t<table align=right><tr>\n")
        # Success & Fail
        file.write("\t\t<td width=200><table border=1>\n")
        file.write("\t\t\t<tr><td align=center width=80 class=\"success\">Success</td>\n")
        file.write("\t\t\t\t<td align=center width=60 class=\"success\">{0}/{1}</td></tr>\n".format(self.rpSum.success, (self.rpSum.success+self.rpSum.fail)))
        file.write("\t\t\t<tr><td align=center width=80 class=\"fail\">Fail</td>\n")
        file.write("\t\t\t\t<td align=center width=60 class=\"fail\">{0}/{1}</td></tr>\n".format(self.rpSum.fail, (self.rpSum.success+self.rpSum.fail)))
        file.write("\t\t</table></td>\n")
        if testTime != None:
            #Time stamp
            file.write("\t\t<td><table border=1>\n")
            file.write("\t\t\t<tr><td align=center width=100>Start time</td>\n")
            file.write("\t\t\t\t<td align=center width=150>{0}</td></tr>\n".format(testTime.start))
            file.write("\t\t\t<tr><td align=center width=100>End time</td>\n")
            file.write("\t\t\t\t<td align=center width=150>{0}</td></tr>\n".format(testTime.end))
            file.write("\t\t\t<tr><td align=center width=100>Duration</td>\n")
            file.write("\t\t\t\t<td align=center width=150>{0}</td></tr>\n".format(testTime.duration))
            file.write("\t\t</table></td>\n")
        file.write("\t</tr></table>\n")

        file.write("\t<header>\n\t\t<h1>{0} BMC Test Report</h1>\n\t</header>\n".format(device))

        file.write("\t<h2><font color=\"0000ff\">" + TestType.IPMI.value + "</font></h2>\n")
        file.write("\t<hr size=\"5\" align=\"center\" noshade width=\"90%\" color=\"0000ff\">\n")

        if self.ipmi["CHASSIS"]:
            writeHtml("CHASSIS", self.ipmi["CHASSIS"], file)
        if self.ipmi["BRIDGE"]:
            writeHtml("BRIDGE", self.ipmi["BRIDGE"], file)
        if self.ipmi["SENSOR_EVENT"]:
            writeHtml("SENSOR EVENT", self.ipmi["SENSOR_EVENT"], file)
        if self.ipmi["APP"]:
            writeHtml("APP", self.ipmi["APP"], file)
        if self.ipmi["FIRMWARE"]:
            writeHtml("FIRMWARE", self.ipmi["FIRMWARE"], file)
        if self.ipmi["STORAGE"]:
            writeHtml("STORAGE", self.ipmi["STORAGE"], file)
        if self.ipmi["TRANSPORT"]:
            writeHtml("TRANSPORT", self.ipmi["TRANSPORT"], file)
        if self.ipmi["OEM"]:
            writeHtml("OEM", self.ipmi["OEM"], file)
        if self.ipmi["OTHER"]:
            writeHtml("OTHER", self.ipmi["OTHER"], file)
        if self.ipmi["CMD_LINE"]:
            writeHtml("CMD LINE", self.ipmi["CMD_LINE"], file)

        file.write("\t<h2><font color=\"0000ff\">" + TestType.CYCLE.value + "</font></h2>\n")
        file.write("\t<hr size=\"5\" align=\"center\" noshade width=\"90%\" color=\"0000ff\">\n")
        if self.cycle:
            writeHtml("CYCLE", self.cycle, file)

        file.write("\t<h2><font color=\"0000ff\">" + TestType.SPECIFIC.value + "</font></h2>\n")
        file.write("\t<hr size=\"5\" align=\"center\" noshade width=\"90%\" color=\"0000ff\">\n")
        if self.specific:
            writeHtml("SPECIFIC", self.specific, file)

        file.write("\t<h2><font color=\"0000ff\">" + TestType.MANUAL.value + "</font></h2>\n")
        file.write("\t<hr size=\"5\" align=\"center\" noshade width=\"90%\" color=\"0000ff\">\n")
        if self.manual:
            writeHtml("MANUAL", self.manual, file)

        file.write("</body>\n")
        file.write("</html>\n")
        file.close()