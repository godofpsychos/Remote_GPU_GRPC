from qutils import marshaller
import json
from more_itertools import divide
import logging
from qiskit_braket_provider import BraketLocalBackend
import time

class Braket_Simulator:
    def exec_circuit(subexperiments, devices):
        try:
            devices = json.loads(devices)
            subexperiments = marshaller.objectifyCuts(subexperiments)
            num_devices = len(devices)
            batched_subexperiments = [
                list(b) for b in divide(num_devices, subexperiments.keys())
            ]
            results = {}
            time_taken = 0
            for i in range(num_devices):
                sampler = BraketLocalBackend(name="default")
                for subexperiment_keys in batched_subexperiments[i]:
                    for key in subexperiment_keys:
                        circ_results = []
                        for i, circuit in enumerate(subexperiments[key]):
                            start_time = time.time()
                            result = sampler.run(circuit, shots=100).result()
                            end_time = time.time()  
                            circ_results.append(result)
                        results[key] = json.dumps(circ_results)
                        time_taken += end_time - start_time
            data = {}
            data["results"] = results
            data = json.dumps(data)
            print("Braket-Simulator Time Taken: ", time_taken)
            return data, time_taken
        except Exception as e:
            print("Error in Braket-Simulator function: ", e)
            logging.info(e)
            logging.info("Error in Braket-Simulator function")
            raise Exception("Error at Braket function", e)