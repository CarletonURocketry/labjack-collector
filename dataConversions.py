class genericAmplifier:
    """Class to use for any sensor which give a radiometic output
    """
    def __init__(self, range: tuple[float, float], range_volt: tuple[float, float]):
        """Constructor for generic amplifier class

        Args:
            range (tuple[float, float]): Range of output values (e.g., 0 to 1000 psi)
            range_volt (tuple[float, float]): Range of input voltages (e.g., 0 to 5 volts)
        """
        self.range = range
        self.range_volt = range_volt

    def volt_to_output(self, voltage: float) -> float:
        """Function to give the output of the sensor given an input

        Args:
            voltage (float): Input voltage value

        Returns:
            float: The output value corresponding to the input voltage given
        """
        volt_min, volt_max = self.range_volt
        output_min, output_max = self.range
        output = ((voltage - volt_min) / (volt_max - volt_min)) * (output_max - output_min) + output_min
        return output