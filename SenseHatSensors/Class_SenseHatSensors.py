import os
import time
from SenseHatCustomExceptions import DisplayErrors as DiEr


LIVE = None
try:
    from sense_hat import SenseHat
    LIVE = True
except ImportError as e1:
    try:
        from sense_emu import SenseHat
        LIVE = False
    except ImportError as e2:
        raise DiEr.MissingDisplay()

print("===========================")
print("= using: {:^16} =".format({True: "SenseHat", False: "Emulator"}[LIVE]))
print("===========================")


class EnvironmentalReadings:
    """=== Class name: EnvironmentalReadings ===========================================================================
    Objects measures, stores and responds environmental data such as:
    - (T)emperature,
    - (r)elative(H)umidity and
    - air(P)ressure
    In order to work as intended, user needs a RaspberryPi with a SenseHat mounted.
    Each instance measures the set of data according to users choice, and scrolls these on the LED Display.
    ============================================================================================== by Sziller ==="""
    def __init__(self,
                 code: int = 7,
                 scroll_speed: int = 1,
                 low_light: bool = True,
                 **kwargs):
        self.sense                  = SenseHat()
        self.sense.low_light        = low_light
        self.code: int              = code
        self.scroll_speed: float    = scroll_speed

        # creating dictionary for the entire life-cycle of the object. All measurements will be stored here.
        self.sensehat_measurements_list: list = []  #

        self.delta_t_h = 0
        self.delta_t_m = 0
        
    def show_data(self, pointer: int = -1):
        """=== Method name: show_data ==================================================================================
        Method shows 'pointer'-represented data read out of <self.sensehat_measurements_list> over the
        SenseHat-LED-Display.
        :var self.sensehat_measurements_list: list of all measurements in sequence
        ========================================================================================== by Sziller ==="""
        # print(self.sensehat_measurements_list[pointer])
        
        if 'humidity' in self.sensehat_measurements_list[pointer]\
                and self.sensehat_measurements_list[pointer]['humidity'] is not None:
            self.sense.show_message('rH:' + str(self.sensehat_measurements_list[pointer]['humidity']) + "%",
                                    scroll_speed=self.scroll_speed,
                                    text_colour=[0, 0, 255])
        if 'temperature' in self.sensehat_measurements_list[pointer]\
                and self.sensehat_measurements_list[pointer]['temperature'] is not None:
            self.sense.show_message('T:' + str(self.sensehat_measurements_list[pointer]['temperature']) + "'C",
                                    scroll_speed=self.scroll_speed,
                                    text_colour=[255, 0, 0])
        if 'air_pressure' in self. sensehat_measurements_list[pointer]\
                and self.sensehat_measurements_list[pointer]['air_pressure'] is not None:
            self.sense.show_message('p:' + str(self.sensehat_measurements_list[pointer]['air_pressure']) + 'bar',
                                    scroll_speed=self.scroll_speed,
                                    text_colour=[255, 255, 0])
    
    def show_actual_data(self):
        """=== Method name: show_actual_data ===========================================================================
        Displaying actual environmental data. Picking data type is a simple addition:
        'measurement type'  1:  temperature
                            2:  humidity
                            4:  pressure
        You simply add the integers of each of the measurement type, you want to read:
        e.g.: temperature + humidity = 3
        Method displays data stored in Instance RIGHT AFTER actualizing said data.
        ========================================================================================== by Sziller ==="""
        self.measure_sensehat_env_data()
        self.show_data(pointer=-1)

    def write_data_to_disc(self, db_session):
        pass

    def measure_sensehat_env_data(self):
        """=== Method name: measure_sensehat_env_data ==================================================================
        Method measures and stores environmental readings
        'code' behaviour:   1:  temperature
                            2:  humidity
                            4:  pressure
        You simply add the integers of each measurement type, you want to read:
        e.g.: temperature + humidity = 3
        :return:
        ========================================================================================== by Sziller ==="""
        current_system_time = time.time() - 3600 * self.delta_t_h - 60 * self.delta_t_m
        dst = time.gmtime(current_system_time)  # Detailed System Time
        curr_date_str = time.strftime("%Y-%m-%d", dst)
        curr_time_str = time.strftime("%H:%M", dst)

        current_dataset = {'time': "{}_{}".format(curr_date_str, curr_time_str),
                           'temperature': None,
                           'humidity': None,
                           'air_pressure': None,
                           'warning': None}

        if self.code in [1, 3, 5, 7]:
            temp = round(self.sense.get_temperature_from_pressure(), 1)
            cpu_temp = round(float(measure_cpu_temp()), 1)
            factor = 1
            current_dataset['temperature']  = round((temp - cpu_temp) * factor, 1)
        if self.code in [2, 3, 6, 7]:
            current_dataset['humidity']     = round(self.sense.get_humidity(), 1)
        if self.code in [4, 5, 6, 7]:
            current_dataset['air_pressure'] = round(self.sense.get_pressure(), 1)
        
        self.sensehat_measurements_list.append(dict(current_dataset))


def measure_cpu_temp():
    temp = os.popen("vcgencmd measure_temp").readline()
    print(temp)
    if LIVE:
        return temp.replace("temp=", "").replace("'C", "")
    else:
        return 0


if __name__ == "__main__":
    sensor = EnvironmentalReadings()
    sensor.show_actual_data()
