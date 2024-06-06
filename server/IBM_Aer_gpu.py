from qiskit_aer.noise import NoiseModel
from qiskit_aer.primitives import Sampler
from qutils import marshaller, program_serializers
import json
from more_itertools import divide
import logging

class AER_GPU:
    def exec_circuitAER(subexperiments,devices):
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
                    sampler = Sampler(backend_options={"noise_model": noise_model,'device':"GPU"})
                else:
                    sampler = Sampler(backend_options={'device':"GPU"})
                # print(batched_subexperiments)

                for subexperiment_keys in batched_subexperiments[i]:
                    for key in subexperiment_keys:
                        result = sampler.run(subexperiments[key]).result()
                        # print(result)
                        results[key] = json.dumps(result, cls=program_serializers.QiskitObjectsEncoder)
            data = {}
            data['results'] = results
            data=json.dumps(data)
            return data
        except Exception as e:
            print(e)
            logging.info(e)
            logging.info("Error in AER-GPU-Simulator function")
            raise Exception("Error at user function",e)