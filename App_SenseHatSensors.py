from SenseHatSensors import Class_SenseHatSensors as SHSe

if __name__ == "__main__":
    measurements = SHSe.EnvironmentalReadings(low_light=False)
    measurements.show_actual_data(code=7, scroll_speed=0.1)
