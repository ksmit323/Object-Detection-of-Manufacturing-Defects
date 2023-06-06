
import time

from pyModbusTCP.client import ModbusClient


c = ModbusClient(host="10.191.96.40", port=502, auto_open=True)
c.open()
print(f'{c.open()}')
InspComplete = 0
PP_Enable = 0
St_Index = 0
try:
    # InspComplete = c.read_holding_registers(5, 1)
    InspComplete = c.read_input_register(5,1)
    # When going in the step to check object, Pinpoint send value "1" to PLC->NN
    PP_Enable = c.read_holding_registers(4, 1)
    # Unknown what for and where
    St_Index = c.read_holding_registers(3, 1)
    writetoPLC = c.write_single_register(5, 1)
    # Read ModelPLC 10 digit from PLC and convert to string
    ModelPLC = c.read_holding_registers(10,10)
    if ModelPLC == ([32] * 10):
        Model_fromPLC = 'NULL'
    else:
        Model_fromPLC = ""
        for number in ModelPLC:
            char = chr(number)
            Model_fromPLC = Model_fromPLC + char

    VINint = c.read_holding_registers(20, 17)
    VIN = ''
    if VINint == ([32] * 17):
        VIN = "NO Vehicle"
    else:
        for number in VINint:
            char = chr(number)
            VIN = VIN + char
    Full_Read = 1
    # if Model_code == 0:
    #     Model_code = "NoModelRead"
    Full_Read = 1
except:
    print("PLC call fail")
    time.sleep(1)
    VIN = "NoVINRead"
    Model_fromPLC = 'NoVINRead'
    print(f'Model : {Model_fromPLC}')
    print(f'VIN : {VIN}')
    print(f'Inspection Status : {InspComplete}')
    print(f'Inspection PP_Enable : {PP_Enable}')
    print(f'Inspection St Index : {St_Index}')
# print(ModelPLC)
# print(VINint)
