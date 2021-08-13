# create variable class
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
    