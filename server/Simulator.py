from qiskit_aer.noise import NoiseModel
from qiskit_aer.primitives import Sampler
from qutils import marshaller, program_serializers
import json
from more_itertools import divide
from python.src.utils.classes.commons.serwo_objects import SerWOObject
import logging

def user_function(input):
    try:
        subexperiments = input['data']['subexperiments']
        devices = json.dumps(input['devices'])
        print(type(devices))
        print(type(subexperiments))
        return Simulator.exec_circuit(subexperiments,devices)
    except Exception as e:
        print(e)
        logging.info(e)
        logging.info("Error in user Function function")
        raise Exception("[SerWOLite-Error]::Error at user function",e)


class Simulator:
    def exec_circuit(subexperiments,devices):
        try:
            devices= json.loads(devices)
            subexperiments = marshaller.objectifyCuts(subexperiments)
            num_devices = len(devices)
            # print(len(subexperiments), num_devices)
            batched_subexperiments = [list(b) for b in divide(num_devices, subexperiments.keys())]
            results = {}
            for i in range(num_devices):
                device = devices[i]
                if 'noise-model' in device:
                    noise_model = NoiseModel.from_dict(device['noise-model'])
                    sampler = Sampler(backend_options={"noise_model": noise_model})
                else:
                    sampler = Sampler()
                # print(batched_subexperiments)

                for subexperiment_keys in batched_subexperiments[i]:
                    for key in subexperiment_keys:
                        result = sampler.run(subexperiments[key]).result()
                        # print(result)
                        results[key] = json.dumps(result, cls=program_serializers.QiskitObjectsEncoder)
            data = {}
            data['results'] = results
            data=json.dumps(data)
            # print(results)
            # print(type(data))
            return data
        except Exception as e:
            print(e)
            logging.info(e)
            logging.info("Error in GPU-Simulator function")
            raise Exception("[SerWOLite-Error]::Error at user function",e)


f=open("/home/tarun/XFaaS/serwo/examples/SerialSimulatorAWS/transpiler_out.json")
body=json.load(f)
body=json.loads(body)
z=user_function(body)
body=json.loads(z)
# obj=json.dumps(body,default=str)
# with open("/home/tarun/XFaaS/serwo/examples/SerialSimulatorAWS/simulator_out.json", "w") as f:
#   json.dump(obj, f)
# print("Output object:"+str(obj))
# print(body)