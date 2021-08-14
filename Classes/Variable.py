"""
- create variable class
- store variable properties including their servers references (mqtt topic, opcua ref...), name, unit,
 input, output,....
- store variables current value and a user defined past ones
"""
class Variable:
    def __init__(self, AcceptedValues, MqttTopic, OpcUaRef="ns=3;i=1008", DataType=str, InputVariable=False,
                 UpdateCycle=1):
        self.AcceptedValues = AcceptedValues
        self.MqttTopic = MqttTopic
        self.DataType = DataType
        self.InputVariable = InputVariable
        self.UpdateCycle = UpdateCycle
        self.OpcUaRef = OpcUaRef

        pass
    