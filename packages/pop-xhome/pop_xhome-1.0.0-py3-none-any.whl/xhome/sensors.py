import time
import json 
import threading
import platform
import paho.mqtt.client as mqtt 

machine = platform.machine().lower() 
if machine == "aarch64":
    product_file_path = "/etc/product"
else:
    product_file_path = "product"

# NOTE :: Must make /etc/product reading part!
# NOTE :: Abstract Class
# NOTE :: Must set class member variable -- ID, LENGTH
class SensorBase:
    def __init__(self, timeout=3):
        """
        Initialize Sensor Data Recv 

        :param group: Muticast Group, If None, refer to the contents of /etc/product. 
        :param timeout: recv timeout, default 3sec 
        """
        self.TIMEOUT = timeout
        try:
            with open(product_file_path) as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('BROKER_DOMAIN'):
                        self.BROKER_DOMAIN = line.split('=')[1].strip()
                    if line.startswith('DEV_NUM='):
                        self.DEV_NUM = line.split('=')[1].strip()
                    if line.startswith('DEVICE_NAME='):
                        self.DEV_NAME = line.split('=')[1].strip()
                    if line.startswith('INSITUTION_NAME='):
                        self.INSITUTION_NAME = line.split('=')[1].strip()
            self.TOPIC_HEADER = self.DEV_NAME+"/"+self.INSITUTION_NAME+self.DEV_NUM
        except FileNotFoundError:
            raise FileNotFoundError("Can't detect hbe device. Please set device argument.")

        self.value = None
        self.__client = mqtt.Client()
        self.__client.on_connect = self.__on_connect
        self.__client.on_message = self.__on_message
        self.__client.connect(self.BROKER_DOMAIN)
        self.__client.loop_start()
        self.__func = None 
        self.__param = None 
        self.__thread = None 
        self.__stop = False
        self.__repeat = 0

    def __del__(self):
        self.client.disconnect()

    def __on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.__client.subscribe(self.topic)
    
    def __on_message(self, client, userdata, message):
        try:
            self.value = json.loads(message.payload)
        except:
            self.value = message.payload.decode('utf-8')

    @property
    def topic(self):
        """ Sensor Data Packet ID """
        return self.TOPIC_HEADER+"/"+self.PLACE+"/"+self.NAME
   
    def __callback(self):
        while not self.__stop:
            if self.__param:
                self.__func(self.read(),self.__param)
            else:
                self.__func(self.read())
            time.sleep(self.__repeat/1000)

    def callback(self, func, repeat=1000,param=None):
        if not self.__thread:
            self.__func = func 
            self.__param = param
            self.__stop = False
            self.__thread = threading.Thread(target=self.__callback)
            self.__repeat = repeat
            self.__thread.start()

    def stop(self):
        if self.__thread:
            self.__stop = True
            self.__thread = None

    def read(self):
        """
        Sensor Data Read 
        :return: Sensor Value 
        """
        time_flag = time.time()
        while self.value == None : 
            if time.time() - time_flag > self.TIMEOUT:
                raise TimeoutError("Please check network connection, or device's boot state.")
        return self.value

class Pir(SensorBase):
    """
    SmartHome PIR Sensor 
    Detects human body movements.
    """
    PLACE = "entrance"
    NAME = "pir"

class Dust(SensorBase):
    """
    SmartHome Dust Sensor 
    Provides data measured using the TSI method.
    """
    PLACE = "livingroom"
    NAME = "dust"

class Tphg(SensorBase):
    """
    SmartHome TPHG Sensor 
    Provides four types of sensor data.
    T(Temperature), P(Pressure), H(Humidity), G(Indoor Air Quality)
    """
    PLACE = "livingroom"
    NAME = "tphg"

class Gas(SensorBase):
    """
    SmartHome Gas Sensor 
    Provides gas sensor data.
    """
    PLACE = "kitchen"
    NAME = "gas"

class Light(SensorBase):
    """
    SmartHome Light Sensor 
    Measures and provides indoor brightness. Unit is lux.
    """
    PLACE = "room"
    NAME = "light"

class Reed(SensorBase):
    """
    SmartHome Reed Switch 
    Detects when a window is opened.
    """
    PLACE = "room"
    NAME = "reed"

class Accel(SensorBase):
    """
    SmartHome Acclerometer 
    It is used to detect vibrations in the house.
    """
    PLACE = "home"
    NAME = "accel"