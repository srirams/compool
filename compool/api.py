import serial
import sys
import datetime
import threading
import time

class CompoolAckPacket:

    def __init__(self, data = [0]*24):
        self.data = data
    
    def is_primary_equipment_on(self, number):
        return (self.data[8] & 1<<number)>0
        
    def is_spa_remote_on(self):
        return (1<<3 & self.data[9])>0
        
    def is_delay_on(self, number):
        if number < 3:
            return (self.data[10] & 1<<number)              

    def get_water_temp(self):
        if self.data[11]:
            return self.data[11]/4.0
        return 0
        
    def get_desired_spa_temp(self):
        if self.data[16]:
            return self.data[16]/4.0
        return 0
        
    def get_air_temp(self):
        if self.data[17]:
            return self.data[17]/2.0
        return 0
            
    def is_heater_on(self):
        return (1<<1 & self.data[9])>0
        
    def is_spa_heater_mode_on(self):
        return not (not (1<<6 & self.data[10])) and (not (1<<7 & self.data[10]))
            
    def is_pump_on(self):
        return (self.data[8] & 0b00000011)>0
        
    def is_delayed(self):
        return (self.data[10] & 0b00000111)>0
        

class CompoolAPI:

    def __init__(self, port=None):
        self.state = CompoolAckPacket()
        self.lock = threading.Lock()
        self.update_callbacks = []
        if port:
            self.serial = serial.Serial(port, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=.2)
            self.reader = threading.Thread(target=self.read).start()        
        
    def read(self):        
        while True:
            x = self.serial.read(100)
            if len(x)==0:
                continue
            #print ("in: " + ":".join("{:02x}".format(int(v)) for v in x))
            datas = []
            data = None            
            for idx in range(len(x)):
                if idx+2<len(x):
                    if x[idx]==0x5a and x[idx+1]==0xff and x[idx+2]==0xaa:
                        if data is not None:
                            datas.append(data)
                        data = []
                if data is not None:
                    data.append(x[idx])
            if data:
                datas.append(data)
            for data in datas:
                #print ("out: " + ":".join("{:02x}".format(int(v)) for v in data))
                self.process_status(data)
    
    def write(self,
              primary_equipment = None,
              secondary_equipment = None,
              heat_source = None,
              desired_pool_temp = None,
              desired_spa_temp = None,
              switch_state = None):

        data = [0xff, 0xaa, 0x00, 0x01, 0x82, 0x09]
        now = datetime.datetime.now()
        data.append(now.minute)
        data.append(now.hour)

        use_enable = 0

        def add_data(val, bit):
            if val is not None:
                data.append(val)
                nonlocal use_enable
                use_enable |= (1<<bit)
            else:
                data.append(0)

        add_data(primary_equipment, 2)
        add_data(secondary_equipment, 3)
        add_data(heat_source, 4)
        add_data(desired_pool_temp, 5)
        add_data(desired_spa_temp, 6)
        add_data(switch_state, 7)
				
        data.append(use_enable)

        checksum = sum(data)
        data.append(checksum>>8)
        data.append(((1<<8) - 1) & checksum)
        self.serial.write(data)
        #print ("write: " + ":".join("{:02x}".format(int(v)) for v in data))

    def process_status(self, data):
        #print ("process: " + ":".join("{:02x}".format(int(v)) for v in data))
        if len(data)<5:
            print ("too little data: " + ":".join("{:02x}".format(int(v)) for v in data))
            return            
        if data[0]==0x5a:
            data = data[1:]
        if data[0]!=0xff or data[1]!=0xaa:
            return        
        if data[4]==0:
            print ("nack")
            return
        if data[4]==1:
            print ("ack")
            return
        data = data[:24]
        if data[4]!=0x2:            
            print ("unknown data: " + ":".join("{:02x}".format(int(v)) for v in data))
            return
        if (sum(data[0:-2])!=(data[-2]<<8 | data[-1])):
            print ("checksum error: " + ":".join("{:02x}".format(int(v)) for v in data))
            return        
        with self.lock:
            old = self.state
            self.state = CompoolAckPacket(data)
        for c in self.update_callbacks:
            c(old)
        return

    def set_primary_equipment_state(self, number, on):
        if self.state.is_primary_equipment_on(number) ^ on:
            self.write(primary_equipment = 1<<number)

    def set_spa_remote_state(self, on):
        if self.state.is_spa_remote_on() ^ on:
            self.write(secondary_equipment = 1<<0)

    def spa_mode(self, on):
        pass
 #       if (self.data[8] & 1<<0) ^ on:
    #        pass
            #self.write(primary_equipment = 1<<0)
        # if off, turn off heat
        # if on, turn on remote, else off
        
    def set_desired_spa_temp(self, temp):
        self.write(desired_spa_temp = int(temp*4))
        
    def set_spa_heater_mode(self, on):
        if on:
            self.write(heat_source = 0b00000001)
        else:
            self.write(heat_source = 0b00000000)  