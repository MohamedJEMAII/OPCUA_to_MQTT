import sys

sys.path.insert(0, "..")
import time

from opcua import Client
import paho.mqtt.client as mqtt
import json
from datetime import datetime


################################MQTT prepare#####################################################
def on_connect(client, userdata, flag, rc):
    print("Connected with result code " + str(rc))
    mqtt_client.publish("opcua/client/status", "Connected", qos=2, retain=True)
    global j
    j=0
    log("Event", "Successfully connected to MQTT server")


def disconnect():
    client.publish("python/client/status", payload="disconnected", qos=0, retain=True)
    client.loop_stop()
    client.disconnect()
    log("Event", "Disconnected from MQTT server")

def log(type,message):
    #Get and format current datetime
    time = datetime.now()
    time_string = time.strftime("%d/%m/%Y %H:%M:%S")
    # Open log file with access mode 'a'
    log_file = open('log.txt', 'a')
    # Append log at the end of file
    log_file.write(f"{time_string}        {type}        {message} \n")
    # Close the file
    log_file.close()


mqtt_client = mqtt.Client(client_id="opc_to_mqtt", clean_session=True)
mqtt_client.will_set("opcua/client/status", "Connection Error", qos=2, retain=True)
mqtt_client.connect("54.37.155.209", port=1883)
time.sleep(2)
mqtt_client.loop_start()
mqtt_client.on_connect = on_connect

#        self.Outputvalue = self.ids.server_ip.text+ ":" + self.ids.server_port.text
# self.client.publish("OPCUA/client/message/", payload="Hello2", qos=2, retain=True)
# self.client.loop_start()  # start the loop
# print(self.ids.port.text)

# client.subscribe(OPCUA/client/message/)


#############################################################

client = Client("opc.tcp://DESKTOP-OP68EIL:53530/OPCUA/SimulationServer")
# client = Client("opc.tcp://admin@localhost:4840/freeopcua/server/") #connect using a user
try:
    client.connect()

    # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
    root = client.get_root_node()
    print("Objects node is: ", root)

    # Node objects have methods to read and write node attributes as well as browse or populate address space
    print("Children of root are: ", root.get_children())

    value = None
    i = 0
    j = 0
    while True:
        data = {}
        # get a specific node knowing its node id
        # var = client.get_node(ua.NodeId(1007, 2))
        var = client.get_node("ns=3;i=1003")
        # print(var)
        y = var.get_data_value()  # get value of node as a DataValue object
        x = var.get_value()  # get value of node as a python builtin
        data["name"] = "Variable 01"
        data["timestamp"] = str(str(int(time.mktime(y.SourceTimestamp.timetuple()))))
        data["value"] = y.Value.Value
        jdata = json.dumps(data)

        # var.set_value(ua.Variant([23], ua.VariantType.Int64)) #set node value using explicit data type
        # var.set_value(3.9) # set node value using implicit data type
        # print(x, end="\r")
        if not mqtt_client.is_connected():
            try:
                j +=1
                mqtt_client.reconnect()
                print(f"Trying to reconnect for {j} time(s)")
                log("warning", "Reconnected to MQTT server")
            except OSError as error:
                print("Mqtt connection error")
                log("Error","Mqtt connection error: OSError")

        if value != x:
            #print(f' Value is : {y.Value.Value}  Time Stamp : {y.SourceTimestamp}')

            mqtt_client.publish("opcua/client/message", payload=jdata, qos=2, retain=False)
            value = x
        # Now getting a variable node using its browse path
        # myvar = root.get_child(["0:Objects", "2:MyObject", "2:MyVariable"])
        # obj = root.get_child(["0:Objects", "2:MyObject"])
        # print("myvar is: ", myvar)
        # print("myobj is: ", obj)
        cycle = .5
        time.sleep(cycle)
        i += 1
        # if i==5:
        # new_value = input("enter new value")
        # var.set_value(new_value)
        # i=0
    # Stacked myvar access
    # print("myvar is: ", root.get_children()[0].get_children()[1].get_variables()[0].get_value())
#        if i==10:
#            break

finally:
    client.disconnect()
