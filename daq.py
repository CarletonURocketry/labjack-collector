"""_summary_
"""

from labjack import ljm # type: ignore
import sys
import logging
import config
import argparse
import random
import time

errorLog = logging.getLogger(__name__)
logging.basicConfig(filename=config.logFilePath + "\\" + "labjackError.log", encoding='utf-8', level=logging.INFO)

class labjackClass:
    def __init__(self, scanList: list[str], scanRate: int, args: argparse.Namespace) -> None:
        """_summary_

        Args:
            scanList (list[str]): List of channel names to stream
            scanRate (int): Rate to stream at in Hz
            args (list[Any] | None, optional): Command line arguments. Refer to main program for options. Defaults to None.
        """

        ljm.closeAll()  # type: ignore Close any previously opened labjack handles

        self.scanList = scanList
        self.scanRate = scanRate
        self.args = args

        try:
            if not self.args.debug:
                print("Connecting to labjack...")
                self.labjack = ljm.openS("T7", "USB", "ANY")  # T7, USB connection, Any identifier
                ljm.eWriteName(self.labjack, "STREAM_TRIGGER_INDEX", 0) # type: ignore Ensure triggered stream is disabled.
                ljm.eWriteName(self.labjack, "STREAM_CLOCK_SOURCE", 0)  # type: ignore Enabling internally-clocked stream.
                print(f"Connected to labjack with handle: {self.labjack}")
                for name in scanList:
                    ljm.eWriteName(self.labjack, name + "_RANGE", 10) # type: ignore +/-10 V
                    ljm.eWriteName(self.labjack, name + "_NEGATIVE_CH", 199)  # type: ignore Single-ended
                ljm.eWriteName(self.labjack, "STREAM_RESOLUTION_INDEX", 0) # type: ignore
                ljm.eWriteName(self.labjack, "STREAM_SETTLING_US", 0) # type: ignore Auto settling time
                ljm.eStreamStart(self.labjack, 1, len(scanList), ljm.namesToAddresses(len(scanList), scanList)[0], scanRate) # type: ignore Configure and start stream
                print("Stream started.")
            else:
                print("Debug mode enabled, simulating labjack data...")
                self.labjack = None
                self.stream = None
                self.lastSimulatedTime = time.time()
        except ljm.LJMError:
            e = sys.exc_info()
            ljm.closeAll()
            print(e)
        except Exception:
            e = sys.exc_info()
            self.stop_stream()
            ljm.closeAll
            print(e)
    
    def read_data(self) -> tuple[list[float], int, int] | int:
        """Function to read a scan of streamed data from the labjack

        Returns:
            tuple[list[float], int, int] | int: A tuple containing the list of scanned data, number of scans unread on the labjack buffer, and number of scans unread in the ljm buffer. Returns -1 if an error occured.
        """
        try:
            if not self.args.debug:
                #print("Reading data from labjack...")
                data = ljm.eStreamRead(self.labjack)  # type: ignore Read data from stream
                print(f"Labjack Buffer {data[1]}, LJM Buffer {data[2]}")  # type: ignore
                return data # type: ignore
            else:
                print("Simulating data...")
                while ((time.time() - self.lastSimulatedTime) < 1.0 / self.scanRate):
                    pass
                self.lastSimulatedTime = time.time()
                simulatedData: list[float] = []
                for _ in self.scanList:
                    if config.channelToSensor[_].sensor_type_id in (config.SensorTypeID.TEMPERATURE, config.SensorTypeID.MASS, config.SensorTypeID.THRUST):
                        simulatedData.append(random.uniform(0, 10))
                    else:
                        simulatedData.append(random.uniform(0, 5))
                scansPendingLJM = 0
                scansPendingLJ = 0
                return (simulatedData, scansPendingLJM, scansPendingLJ)
        except ljm.LJMError as ljme:
            e = sys.exc_info()
            print(str(e) + str(ljme))
            ljm.closeAll()
            return -1
        except Exception:
            e = sys.exc_info()
            self.stop_stream()
            print(e)
            ljm.closeAll()
            return -1
    
    def stop_stream(self) -> int:
        """Function to stop the stream and close the labjack handle
        """
        try:
            if not self.args.debug:
                ljm.eStreamStop(self.labjack)  # type: ignore
                ljm.close(self.labjack)  # type: ignore
                return 0
            else:
                return 0
        except ljm.LJMError:
            e = sys.exc_info()
            print(e)
            ljm.closeAll()
            return -1
        except Exception:
            e = sys.exc_info()
            print(e)
            ljm.closeAll()
            return -1
    
    def start_stream(self) -> int:
        """Function to connect to the labjack and start the stream again after being stopped

        Returns:
            int: 0 if successful, -1 if error occured
        """
        try:
            if not self.args.debug:
                self.labjack = ljm.openS("T7", "USB", "ANY")  # T7, USB connection, Any identifier
                ljm.eWriteName(handle, "STREAM_TRIGGER_INDEX", 0) # type: ignore Ensure triggered stream is disabled.
                ljm.eWriteName(handle, "STREAM_CLOCK_SOURCE", 0)  # type: ignore Enabling internally-clocked stream.

                for name in self.scanList:
                    ljm.eWriteName(handle, name + "_RANGE", 1.0) # type: ignore +/-10 V
                    ljm.eWriteName(handle, name + "_NEGATIVE_CH", 199)  # type: ignore Single-ended
                ljm.eWriteName(handle, "STREAM_RESOLUTION_INDEX", 0) # type: ignore
                ljm.eWriteName(handle, "STREAM_SETTLING_US", 0) # type: ignore Auto settling time
                self.stream = ljm.eStreamStart(self.labjack, 1, len(scanList), ljm.namesToAddresses(len(scanList), scanList)[0], self.scanRate) # type: ignore Configure and start stream
                return 0
            return 0
        except ljm.LJMError:
            e = sys.exc_info()
            print(e)
            ljm.closeAll()
            return -1
        except Exception:
            e = sys.exc_info()
            print(e)
            ljm.closeAll()
            return -1
    
    def set_scan_rate(self, scanRate: int) -> int:
        """Function to set a new scan rate for the stream

        Args:
            scanRate (int): New scan rate in Hz
        Returns:
            int: 0 if successful, -1 if error occured
        """
        try:
            self.scanRate = scanRate
            if not self.args.debug:
                self.stop_stream()
                self.start_stream()
            return 0
        except ljm.LJMError:
            e = sys.exc_info()
            print(e)
            ljm.closeAll()
            return -1
        except Exception:
            e = sys.exc_info()
            print(e)
            ljm.closeAll()
            return -1
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LabJack Interface script")
    parser.add_argument("-d", "--debug", help="Enable simulated labjack data", action="store_true")
    args = parser.parse_args()

    ch_list = list(config.channelToSensor.keys())

    labjack = labjackClass(ch_list, config.scanRate, args)
    
    scanData = labjack.read_data()
    print(scanData)

    scansSinceNetPacket = 0

    if type(scanData) == tuple[list[float], int, int]:
        data, scansPendingLJM, scansPendingLJ = scanData # type: ignore
        scansSinceNetPacket += 1
        timestamp = time.time_ns()
        dataConverted: list[int] = []
        for i in range(len(ch_list)):
            sensor = config.channelToSensor[ch_list[i]]
            convertedValue = sensor.convertClass.volt_to_output(data[i]) # type: ignore
            dataConverted.append(convertedValue)
        if scansSinceNetPacket > config.networkScanFraction:
            sender.send_packet(dataConverted, timestamp * 1000 * 1000) # type: ignore
            scansSinceNetPacket = 0
        dataLogger.writeRow(data, dataConverted, timestamp * 1000 * 1000) # type: ignore


