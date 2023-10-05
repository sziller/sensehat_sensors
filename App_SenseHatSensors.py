from SenseHatSensors import Class_SenseHatSensors as SHSe

if __name__ == "__main__":
    measurements = SHSe.EnvironmentalReadings()
    measurements.show_actual_data()
