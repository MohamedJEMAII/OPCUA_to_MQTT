import sys

sys.path.insert(0, "..")
import time
import concurrent.futures
from opcua import Client as Opcua_client
import opcua.ua
import paho.mqtt.client as Mqtt_client
import json
from datetime import datetime

opcua_nodes = {'Counter':"ns=3;i=1001", 'Random':"ns=3;i=1002", 'Sawtooth':"ns=3;i=1003", 'Sinusoid':"ns=3;i=1004", 'Square':"ns=3;i=1005", 'Triangle':"ns=3;i=1006"}


################################MQTT prepare#####################################################
def on_connect(client, userdata, flag, rc):
    #print("Connected with result code " + str(rc))
    mqtt_client.publish("opcua/client/status", "Connected", qos=2, retain=True)
    global j
    j=0
    log("Event", "Successfully connected to MQTT server",print_error=True)


def disconnect():
    mqtt_client.publish("python/client/status", payload="disconnected", qos=0, retain=True)
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    log("Event", "Disconnected from MQTT server")

def log(type,message, print_error = False):
    #Get and format current datetime
    time = datetime.now()
    time_string = time.strftime("%d/%m/%Y %H:%M:%S")
    # Open log file with access mode 'a'
    log_file = open('log.txt', 'a')
    # Append log at the end of file
    log_file.write(f"{time_string}        {type}        {message} \n")
    if print_error:
        print(f"{time_string}        {type}        {message} \n")
    # Close the file
    log_file.close()


log("Start", "Starting application",print_error=True)


mqtt_client = Mqtt_client.Client(client_id="opc_to_mqtt", clean_session=True)
mqtt_client.will_set("opcua/client/status", "Connection Error", qos=2, retain=True)
mqtt_client.on_connect = on_connect

#        self.Outputvalue = self.ids.server_ip.text+ ":" + self.ids.server_port.text
# self.client.publish("OPCUA/client/message/", payload="Hello2", qos=2, retain=True)
# self.client.loop_start()  # start the loop
# print(self.ids.port.text)

# client.subscribe(OPCUA/client/message/)


#############################################################
mqtt_connected = False

while not mqtt_connected:
    try:
        mqtt_client.connect("54.37.155.209", port=1883)
        time.sleep(2)
        mqtt_client.loop_start()
        mqtt_connected = True

    except:
        log("Error", "MQTT connection error, retrying after 5s",print_error=True)
        mqtt_connected = False

opcua_client = Opcua_client("opc.tcp://localhost:53530/OPCUA/SimulationServer")
# client = Client("opc.tcp://admin@localhost:4840/freeopcua/server/") #connect using a user
opcua_connected = False

value = None
i = 0
j = 0
old_data = {}
publish = False
while True:


    while not opcua_connected:
        try:
            opcua_client.connect()
            opcua_connected = True
        except:
            log("Error", "OPCUA connection error, retrying after 5s",print_error=True)
            opcua_connected = False
            time.sleep(5)
            continue
        log("Event", "OPCUA successfully connected",print_error=True)
    try:

        data = {}

        for variable_name in opcua_nodes.keys():
            #print(f'processing variable name : {variable_name}')
            variable = opcua_client.get_node(opcua_nodes[variable_name])
            variable_opc_dict = variable.get_data_value()  # get value of node as a DataValue object

            variable_dict = {"timestamp": str(str(int(time.mktime(variable_opc_dict.SourceTimestamp.timetuple())))),"value": variable_opc_dict.Value.Value}
            #print(f'variable dictionary to be added is :{variable_dict}')
            if old_data == None or old_data == {} or variable_name not in old_data.keys():
                data[variable_name] = variable_dict
                publish = True
                #print(f'added, new dictionnary: {data}')
            elif (variable_dict['value'] != old_data[variable_name]['value']):
                data[variable_name] = variable_dict
                publish = True
                #print(f'added, new dictionnary: {data}')

        jdata = json.dumps(data)
    except opcua.ua.uaerrors._auto.BadNodeIdUnknown:
        log("Error", "The node id refers to a node that does not exist in the server address space, Please correct", print_error=True)
        break
    except opcua.ua.uaerrors._auto.BadAttributeIdInvalid:
        log("Error", "The namespace does not exist in the server, Please correct", print_error=True)
        break
    except:
        log("Error", "OPCUA connection error, trying to reconnect",print_error=True)
        opcua_connected = False
        continue

    while not mqtt_client.is_connected():
        try:

            j +=1
            mqtt_client.reconnect()
            #print(f"Trying to reconnect for {j} time(s)")
        except:
            #print("Mqtt connection error")
            log("Error","Mqtt connection lost, trying to reconnect after 5s",print_error=True)
            time.sleep(5)

    if publish:

        mqtt_client.publish("opcua/client/message", payload=jdata, qos=2, retain=False)
        publish = False
        old_data = data
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

if opcua_connected:
    opcua_client.disconnect()
log("Stop ", "Exiting application",print_error=True)