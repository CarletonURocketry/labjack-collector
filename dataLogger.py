"""
Contains the class to manage logging data to a CSV file.
"""
import config
import os
import fastavro
import datetime
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
        fileExists = True
        fileCounter: int = 0
        while fileExists:
            try:
                with open(self.filepath + str(fileCounter) + ".avro", "x") as f:
                    pass
                fileExists = False
                self.filepath = self.filepath + str(fileCounter) + ".avro"
            except FileExistsError:
                fileExists = True
                fileCounter += 1
        self.schema = fastavro.schema.load_schema("schema.avsc") # type: ignore
        zeroRow: list[dict[str, datetime.datetime | float | int]] = [{"Timestamp": datetime.datetime.now()}]
        zeroRow[0]["Timestamp"] = datetime.datetime.now()
        for channel in self.channels:
            zeroRow[0][f"{channel}"] = 0.0
            sensor = self.config[channel]
            zeroRow[0][f"{sensor.name}"] = 0
        with open(self.filepath, "wb") as f:
            fastavro.writer(f, self.schema, zeroRow) # type: ignore
            f.flush() # Clear Python's buffer
            os.fsync(f.fileno()) # Ensure data is written to disk
        with open(self.filepath + ".back", "wb") as f:
            fastavro.writer(f, self.schema, zeroRow) # type: ignore
            f.flush() # Clear Python's buffer
            os.fsync(f.fileno()) # Ensure data is written to disk

        self.file = open(self.filepath, "a+b")
        self.backupFile = open(self.filepath + ".back", "a+b")

    def writeRows(self, data: list[dict[str, datetime.datetime | float | int]]) -> None:
        """Function to write rows of data to the avro file. NOTE: Data must contain all channels.

        Args:
            dataRaw (list[float]): List of raw voltage values from the LabJack
            dataConverted (list[int]): List of converted sensor values
            timestamp (float): Timestamp of the data
        """
        fastavro.writer(self.file, self.schema, data) # type: ignore
        self.file.flush() # Clear Python's buffer
        os.fsync(self.file.fileno()) # Ensure data is written to disk
        fastavro.writer(self.backupFile, self.schema, data) # type: ignore
        self.backupFile.flush() # Clear Python's buffer
        os.fsync(self.backupFile.fileno()) # Ensure data is written to disk