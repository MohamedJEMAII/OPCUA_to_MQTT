"""
- connect to a certain opcua server
- have a function to publish to the configured server
- update local variables classes according to OPCua topic
- update OPCua topic according to local variables changes
"""

from opcua import Client as Opcua_client
import opcua.ua
import time

opcua_client = Opcua_client("opc.tcp://localhost:53530/OPCUA/SimulationServer")
opcua_connected = False

value = None
i = 0
j = 0


data={}
opcua_client.connect()

var = opcua_client.get_node("ns=3;i=1001")

y = var.get_data_value()  # get value of node as a DataValue object

data["name"] = "Variable 01"
data["timestamp"] = str(str(int(time.mktime(y.SourceTimestamp.timetuple()))))
data["value"] = y.Value.Value

print(data)