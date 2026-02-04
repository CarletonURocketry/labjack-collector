"""_summary_
"""
import argparse

import sys
import time
import daq
import config
import sendData
import dataLogger
import logging
from labjack import ljm # type: ignore

parser = argparse.ArgumentParser(description="LabJack Data Collector")
parser.add_argument("-d", "--debug", help="Enable simulated labjack data", action="store_true")
parser.add_argument("--dataFile", help="Path to save data file to", type=str, default=config.dataLog)
parser.add_argument("--logFilePath", help="Path to save log files to", type=str, default=config.logFilePath)
parser.add_argument("--scanRate", help="Scan rate in Hz", type=int, default=config.scanRate)
parser.add_argument("--networkScanFraction", help="Fraction of scans to send over network (e.g., 10 means 1 out of every 10 scans)", type=int, default=config.networkScanFraction)
parser.add_argument("--mc_addr", help="Multicast address to send data to", type=str, default=config.mc_addr)
parser.add_argument("--port", help="Port to send data to", type=int, default=config.port)
parser.add_argument("--channelList", help="Comma-separated list of channels to read from LabJack", type=str, default="")
args = parser.parse_args()

errorLog = logging.getLogger(__name__)
logging.basicConfig(filename=config.logFilePath + "\\" + "error.log", encoding='utf-8', level=logging.INFO)

log = True
dataLogFileName = args.dataFile
scanRate = args.scanRate

errorLog.info("Starting labjack-collector")

startTime = time.time()

# compute channel list from args (split comma-separated string) or default to config keys
ch_list = args.channelList.split(",") if args.channelList != "" else list(config.channelToSensor.keys())

labjack = daq.labjackClass(ch_list, scanRate, args)

sender = sendData.sendData(args.mc_addr, args.port, ch_list, config.channelToSensor)

dataLogger = dataLogger.dataLogger(dataLogFileName, ch_list, config.channelToSensor)

scansSinceNetPacket = 0

try:
    while True:
        scanData = labjack.read_data()
        #print(f"Data read: {scanData}")
        if type(scanData) == int:
            time.sleep(1)
            print("Error reading data from labjack")
            errorLog.error("Error reading data from labjack")
        else:
            data, scansPendingLJM, scansPendingLJ = scanData # type: ignore
            scansSinceNetPacket += 1
            timestamp = time.time() - startTime
            #print(f"Timestamp: {timestamp}")
            dataConverted: list[int] = []
            for i in range(len(ch_list)):
                sensor = config.channelToSensor[ch_list[i]]
                convertedValue = sensor.convertClass.volt_to_output(data[i]) # type: ignore
                dataConverted.append(convertedValue)
            if scansSinceNetPacket > config.networkScanFraction:
                sender.send_packet(dataConverted, timestamp * 1000) # type: ignore
                scansSinceNetPacket = 0
                #print("Sent network packet")
            #dataLogger.writeRow(data, dataConverted, timestamp) # type: ignore
except (Exception, KeyboardInterrupt):
    e = sys.exc_info()
    ljm.closeAll()
    print(f"Unhandled exception in main loop: {e}")
    errorLog.critical(f"Unhandled exception in main loop: {e}")