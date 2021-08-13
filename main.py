from opcua import Client
import time

url = "opc.tcp://192.168.1.103:53530/OPCUA/SimulationServer"

client = Client(url)

client.connect()
print("Client Connected")

while True:
           counter = client.get_node("ns=3;i=1001")
           count = counter.get_value()
           print(count)
           time.sleep(1)