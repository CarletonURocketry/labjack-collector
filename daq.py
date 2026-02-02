"""_summary_
"""

from labjack import ljm # type: ignore
import sys
import logging
import config

errorLog = logging.getLogger(__name__)
logging.basicConfig(filename=config.logFilePath + "\\" + "labjackError.log", encoding='utf-8', level=logging.INFO)

class labjack:
    def __init__(self, scanList: list[str], scanRate: int) -> None:
        """_summary_

        Args:
            scanList (list[str]): List of channel names to stream
            scanRate (int): Rate to stream at in Hz
        """

        self.scanList = scanList
        self.scanRate = scanRate

        try:
            self.labjack = ljm.openS("T7", "USB", "ANY")  # T7, USB connection, Any identifier
            ljm.eWriteName(handle, "STREAM_TRIGGER_INDEX", 0) # type: ignore Ensure triggered stream is disabled.
            ljm.eWriteName(handle, "STREAM_CLOCK_SOURCE", 0)  # type: ignore Enabling internally-clocked stream.

            for name in scanList:
                ljm.eWriteName(handle, name + "_RANGE", 1.0) # type: ignore +/-10 V
                ljm.eWriteName(handle, name + "_NEGATIVE_CH", 199)  # type: ignore Single-ended
            ljm.eWriteName(handle, "STREAM_RESOLUTION_INDEX", 0) # type: ignore
            ljm.eWriteName(handle, "STREAM_SETTLING_US", 0) # type: ignore Auto settling time
            self.stream = ljm.eStreamStart(self.labjack, 1, len(scanList), ljm.namesToAddresses(len(scanList), scanList)[0], scanRate) # type: ignore Configure and start stream
        except ljm.LJMError:
            e = sys.exc_info()
            print(e)
        except Exception:
            e = sys.exc_info()
            self.stop_stream()
            print(e)
    
    def read_data(self) -> tuple[list[float], int, int] | int:
        """Function to read a scan of streamed data from the labjack

        Returns:
            tuple[list[float], int, int] | int: A tuple containing the list of scanned data, number of scans unread on the labjack buffer, and number of scans unread in the ljm buffer. Returns -1 if an error occured.
        """
        try:
            return ljm.eStreamRead(self.labjack) # type: ignore
        except ljm.LJMError:
            e = sys.exc_info()
            print(e)
            return -1
        except Exception:
            e = sys.exc_info()
            self.stop_stream()
            print(e)
            return -1
    
    def stop_stream(self) -> int:
        """Function to stop the stream and close the labjack handle
        """
        try:
            ljm.eStreamStop(self.labjack)  # type: ignore
            ljm.close(self.labjack)  # type: ignore
            return 0
        except ljm.LJMError:
            e = sys.exc_info()
            print(e)
            return -1
        except Exception:
            e = sys.exc_info()
            print(e)
            return -1
    
    def start_stream(self) -> int:
        """Function to connect to the labjack and start the stream again after being stopped

        Returns:
            int: 0 if successful, -1 if error occured
        """
        try:
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
        except ljm.LJMError:
            e = sys.exc_info()
            print(e)
            return -1
        except Exception:
            e = sys.exc_info()
            print(e)
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
            self.stop_stream()
            self.start_stream()
            return 0
        except ljm.LJMError:
            e = sys.exc_info()
            print(e)
            return -1
        except Exception:
            e = sys.exc_info()
            print(e)
            return -1