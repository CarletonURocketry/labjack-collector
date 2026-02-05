"""
Contains the class to manage logging data to a CSV file.
"""
import config
import os
import aiofiles

class dataLogger:
    """
    Class to manage logging data to a CSV file.
    """
    def __init__(self, filepath: str, channels: list[str], config: dict[str, config.Sensor]) -> None:
        """_summary_

        Args:
            filepath (str): Path to the file to log data to
            channels (list[str]): List of channel names which will be logged. This must be the same list as was passed to the labjack for streaming.
            config (dict[str, config.Sensor]): Configuration dictionary mapping channel names to Sensor objects.
        """
        self.filepath = filepath
        self.channels = channels
        self.config = config
        with open(self.filepath, "a", newline="") as f:
            header = "Timestamp,"
            for channel in self.channels:
                sensor = self.config[channel]
                header += f"{sensor.name}_Raw,"
            for channel in self.channels:
                sensor = self.config[channel]
                header += f"{sensor.name}_Converted,"
            header = header + "\n"
            f.write(header)
            f.flush() # Clear Python's buffer
            os.fsync(f.fileno()) # Ensure data is written to disk
        '''with open(self.filepath + ".back", "a", newline="") as f:
            header = "Timestamp,"
            for channel in self.channels:
                sensor = self.config[channel]
                header += f"{sensor.name}_Raw,{sensor.name}_Converted,"
            header = header + "\n"
            f.write(header)
            f.flush() # Clear Python's buffer
            os.fsync(f.fileno())''' # Ensure data is written to disk

    async def writeRow(self, dataRaw: list[float], dataConverted: list[int], timestamp: float) -> None:
        """Function to write a row of data to the CSV. NOTE: Data must be in the same order as channels passed to the constructor.

        Args:
            dataRaw (list[float]): List of raw voltage values from the LabJack
            dataConverted (list[int]): List of converted sensor values
            timestamp (float): Timestamp of the data
        """
        async with aiofiles.open(self.filepath, "a", newline="") as f:
            row = f"{timestamp},"
            for i in range(len(self.channels)):
                row += f"{round(dataRaw[i], 3)},{dataConverted[i]},"
            row = row + "\n"
            await f.write(row)
            await f.flush() # Clear Python's buffer
            os.fsync(f.fileno()) # Ensure data is written to disk
        '''with open(self.filepath + ".back", "a", newline="") as f:
            row = f"{timestamp},"
            for i in range(len(self.channels)):
                row += f"{dataRaw[i]},{dataConverted[i]},"
            row = row + "\n"
            f.write(row)
            f.flush() # Clear Python's buffer
            os.fsync(f.fileno())''' # Ensure data is written to disk