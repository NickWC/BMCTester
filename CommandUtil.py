__author__ = 'root'
import tempfile
import subprocess
import json
import SysConfig as syscfg
from smb.SMBConnection import *
from smb.base import *
from nmb.NetBIOS import NetBIOS
from operator import itemgetter, attrgetter
from os import *
from time import sleep

def run_script(script):
    #print script
    with tempfile.NamedTemporaryFile() as script_file:
        f = open(script_file.name,"w")
        f.write(script)
        f.flush()
        pipe = subprocess.Popen(['/bin/bash', f.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = pipe.communicate()
        return out, err, pipe.returncode

def run_command(cmd,args=""):
    pipe = None
    out = None
    err = None

    if( len(args) > 1):
        pipe = subprocess.Popen([str(cmd), str(args)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        pipe = subprocess.Popen([str(cmd)], stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
    out, err = pipe.communicate()
    return out, err, pipe.returncode

def exec_ipmi_rawcmd(sysConf, interface, cmd):
    assert isinstance(sysConf,syscfg.DeviceConfig)
    cmdStr = "ipmitool -I {0} -H {1} -U {2} -P {3} raw {4}".format(interface, sysConf.ipAddr, sysConf.userName, sysConf.passWord, cmd)
    return run_command(cmdStr)

def exec_ipmi_cmd(sysConf, interface, cmd):
    assert isinstance(sysConf,syscfg.DeviceConfig)
    cmdStr = "ipmitool -I {0} -H {1} -U {2} -P {3} {4}".format(interface, sysConf.ipAddr, sysConf.userName, sysConf.passWord, cmd)
    return run_command(cmdStr)

def exec_ipmi_getMeFw(sysConf, interface, preCmd, cmd):
    assert isinstance(sysConf,syscfg.DeviceConfig)
    cmdStr = "ipmitool -I {0} -H {1} -U {2} -P {3} {4} raw {5}".format(interface, sysConf.ipAddr, sysConf.userName, sysConf.passWord, preCmd, cmd)
    return run_command(cmdStr)

def exec_ipmi_15_authType(sysConf, auth, interface, cmd):
    assert isinstance(sysConf,syscfg.DeviceConfig)
    cmdStr = "ipmitool -A {0} -I {1} -H {2} -U {3} -P {4} raw {5}".format(auth, interface, sysConf.ipAddr, sysConf.userName, sysConf.passWord, cmd)
    return run_command(cmdStr)

def exec_ipmi_20_authType(sysConf, auth, interface, cmd):
    assert isinstance(sysConf,syscfg.DeviceConfig)
    cmdStr = "ipmitool -C {0} -I {1} -H {2} -U {3} -P {4} raw {5}".format(auth, interface, sysConf.ipAddr, sysConf.userName, sysConf.passWord, cmd)
    return run_command(cmdStr)

def exec_ipmi_login(sysConf, userName, passWord, interface, cmd):
    assert isinstance(sysConf,syscfg.DeviceConfig)
    cmdStr = "ipmitool -I {0} -H {1} -U {2} -P {3} raw {4}".format(interface, sysConf.ipAddr, userName, passWord, cmd)
    return run_command(cmdStr)

def dowload_latest_image(sysConf):
    serverIP = sysConf.imgServer['IP']
    netbios = NetBIOS()
    serverName = netbios.queryIPForName(serverIP)
    conn = SMBConnection(sysConf.imgServer['USER'],sysConf.imgServer['PASSWORD'],my_name="BMC_Tester",remote_name=serverName[0],domain="COMPAL")
    if (False == conn.connect(serverIP)):
        return None
    platformImage = "BMC/Daily_Build/"+sysConf.platform
    path = conn.listPath(sysConf.imgServer['ROOT'],platformImage)
    sortedFile = sorted(path,key=attrgetter('create_time'))
    lastFile = sortedFile[len(sortedFile) - 1]
    imagePath = os.getcwd() + "/download"

    if not os.path.exists(imagePath):
        os.mkdir(imagePath)

    image = open(imagePath+"/"+lastFile.filename,"wb")
    print("\tDownloading %s to %s ....."%(lastFile.filename, imagePath+"/"+lastFile.filename))
    conn.retrieveFile(sysConf.imgServer['ROOT'], platformImage+"/"+lastFile.filename, image)
    image.close()
    return lastFile.filename

def exec_yafuflash_updateFw(sysConf, imagefile):
    assert isinstance(sysConf,syscfg.DeviceConfig)
    print("\tDoing firmware update...")
    cmdStr = "./tools/Yafuflash -iml -isi -nw -ip {0} -u {1} -p {2} download/{3}".format(sysConf.ipAddr,sysConf.userName,sysConf.passWord,imagefile)
    result = run_command(cmdStr)
    if 0 == result[2]:
        print("\tResetting firmware...")
        sleep(150)
    return result

def exec_iflash_updateFw(sysConf, imagefile):
    assert isinstance(sysConf,syscfg.DeviceConfig)
    print("\tDoing firmware update...")
    cmdStr = "./tools/iflash --skip_min_level --user {0} --password {1} --host {2} --force --package download/{3}".format(sysConf.userName,sysConf.passWord,sysConf.ipAddr,imagefile)
    result = run_command(cmdStr)
    #Need to reboot BMC after updating FW success
    return result