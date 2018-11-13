__author__ = 'Linda Huang'

ipmiReport = dict({
    "0x00": "CHASSIS", "0x02": "BRIDGE", "0x04": "SENSOR_EVENT", "0x06": "APP", "0x08": "FIRMWARE", "0x0a": "STORAGE", "0x0c": "TRANSPORT", "0x3a": "OEM", "0x3c": "OEM",
    "CHASSIS": "CHASSIS", "BRIDGE": "BRIDGE", "SENSOR_EVENT": "SENSOR_EVENT", "APP": "APP", "FIRMWARE": "FIRMWARE", "STORAGE": "STORAGE", "TRANSPORT": "TRANSPORT", "OEM": "OEM",
    "CMD_LINE": "CMD_LINE","OTHER": "OTHER"
})

class ipmiReportStr:
    chassis = "CHASSIS"
    bridge = "BRIDGE"
    sensor_event = "SENSOR_EVENT"
    app = "APP"
    firmware = "FIRMWARE"
    storage = "STORAGE"
    transport = "TRANSPORT"
    oem = "OEM"
    other = "OTHER"
    cmdLine = "CMD_LINE"

class interface:
    lan = "lan"
    lanplus = "lanplus"