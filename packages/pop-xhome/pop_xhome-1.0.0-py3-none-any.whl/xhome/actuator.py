import json 
import platform
import paho.mqtt.client as mqtt 

machine = platform.machine().lower() 
if machine == "aarch64":
    product_file_path = "/etc/product"
else:
    product_file_path = "product"

class ActuatorBase:
    ID = 0x00
    def __init__(self, device=None):
        """
        Initialization for sending actuator control commands

        :param device: Multicast Group, If None, refer to the contents of /etc/product.
        """
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
        
        self.state = {}
        for k in self.PLACE:
            self.state[k] = None
        self.value = None
        self.__client = mqtt.Client()
        self.__client.on_connect = self._on_connect
        self.__client.on_message = self._on_message
        self.__client.connect(self.BROKER_DOMAIN)
        self.__client.loop_start()
    
    def _on_connect(self, client, userdat4a, flags, rc):
        if rc == 0:
            self.__client.subscribe(self.TOPIC_HEADER+"/+/"+self.NAME+"/state")

    def _on_message(self, client, userdata, message):
        self.state[message.topic.split("/")[2].lower()] = message.payload.decode('utf-8')

    def _publish(self, topic, payload):
        """
        Transmits actuator control commands.

        :param raw: Control Commands.
        """
        self.__client.publish(topic,payload,0)
    
    def _control(self, turn, target=None):
        try:
            if target is None:
                for i in self.PLACE:
                    self._publish(self.TOPIC_HEADER+"/"+i+"/"+self.NAME+"/set",turn)
            else:
                self.id = target.lower()
                self._publish(self.TOPIC_HEADER+"/"+self.id+"/"+self.NAME+"/set",turn)
        except AttributeError:
            raise AttributeError("Input only string!")
        #except KeyError:
        #    raise KeyError(f"Please input target in {self.PLACE}")

    def on(self, target=None):
        """
        GPIO Device Act High 
        
        :param target: Actuator Device String, Default None
        """
        self._control("on", target)
    
    def off(self, target=None):
        """
        GPIO Device Act Low 

        :param target: Actuator Device String, Default None 
        """
        self._control("off", target)

class Lamp(ActuatorBase):
    """ 
    SmartHome Lamp Control 
    Controls lamps in the following locations: 'door', 'livingroom', 'kitchen', 'room', 'bathroom'
    """
    PLACE = ['entrance','livingroom','kitchen','room','bathroom']
    NAME = "lamp"
    
class Fan(ActuatorBase):
    """ 
    SmartHome FAN Control 
    Control FAN in the following locations: 'livingroom', 'kitchen', 'room', 'bathroom'
    """
    PLACE = ['livingroom','kitchen','room','bathroom']
    NAME = "fan"

class DoorLock(ActuatorBase):
    """ 
    SmartHome DoorLock Control 
    Control DoorLock in the following locations: 'door'
    """
    PLACE = ["entrance"]
    NAME = "doorlock"

    def open(self):
        """ Open the Door """
        self._control("open") 
    
    def close(self):
        """ Close the Door """
        self._control("close") 

class GasBreaker(ActuatorBase):
    """ 
    SmartHome GasBreaker Control 
    Control GasBreaker in the following locations: 'kitchen'
    """
    PLACE = ["kitchen"]
    NAME = "gasbreaker"

    def open(self):
        """ Open the circuit breaker to supply gas. """
        self._control("open",None)
    
    def close(self):
        """ Close the circuit breaker to turn off the gas. """
        self._control("close",None)

class Curtain(ActuatorBase):
    """ 
    SmartHome Curtain Control 
    Control Curtain in the followoing locations: 'room'
    """
    PLACE = ["room"]
    NAME = "curtain"

    def open(self):
        """ Open the Curtain """
        self._control("open")
    
    def close(self):
        """ Close the Curtain """
        self._control("close")
    
    def stop(self):
        """ Stop the move"""
        self._control("stop")

class MoodLamp(ActuatorBase):
    """ 
    SmartHome MoodLamp Control 
    Control MoodLamp in the following locations: 'room'
    """
    PLACE = ["home"]
    NAME = "moodlamp"

    def _control(self, pwm, target=None):
        send_data = {"red":pwm[0],"green":pwm[1],"blue":pwm[2]}
        for i in self.PLACE:
            self._publish(self.TOPIC_HEADER+"/"+i+"/"+self.NAME+"/set",json.dumps(send_data))

    def setColor(self, r=255,g=255,b=255):
        """
        Turn on the mood lamp.

        :param r: Red Color, value 0~255, default 255
        :param g: Green Color, value 0~255, default 255
        :param b: Blue Color, value 0~255, default 255
        """
        self._control([r,g,b])
    
    def off(self):
        """ Turn off the mood lamp. """
        self._control([0,0,0])