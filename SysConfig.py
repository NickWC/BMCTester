__author__ = 'root'
import json

class DeviceConfig:
    def __init__(self, device, deviceConfig):
        self.device = device
        self.ipAddr = deviceConfig['BMCLAN']['IP']
        self.passWord = deviceConfig['BMCLAN']['PASSWORD']
        self.userName = deviceConfig['BMCLAN']['USER']
        self.platform = deviceConfig['PLATFORM']
        self.testplan = deviceConfig['TESTPLAN']
        self.imgServer = deviceConfig['IMAGE_SERVER_INFO']

class SysConfig:
    def __init__(self,configFile):
        fd = open(configFile)
        conf = dict(json.load(fd))
        self.deviceconf = []
        for key in conf.keys():
            self.deviceconf.append(DeviceConfig(key, conf[key]))

#        self.ipAddr = conf['BMCLAN']['IP']
#        self.passWord = conf['BMCLAN']['PASSWORD']
#        self.userName = conf['BMCLAN']['USER']
#        self.platform = conf['PLATFORM']
#        self.testplan = conf['TESTPLAN']
#        self.imgServer = conf['IMAGE_SERVER_INFO']
        fd.close()
