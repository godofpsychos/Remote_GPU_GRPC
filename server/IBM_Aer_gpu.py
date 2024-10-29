from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_aer.noise import NoiseModel
from qutils import marshaller, program_serializers
import json
from more_itertools import divide
import logging
import os
from qiskit_aer.primitives import Sampler
import time

class AER_GPU:
    def exec_circuitAER(subexperiments, devices, service=None):
        try:
            devices = json.loads(devices)
            subexperiments = marshaller.objectifyCuts(subexperiments)
            num_devices = len(devices)
            # print(len(subexperiments), num_devices)
            batched_subexperiments = [
                list(b) for b in divide(num_devices, subexperiments.keys())
            ]
            results = {}
            for i in range(num_devices):
                device = devices[i]
                if "noise-model" in device:
                    custom_noise_model = None
                    with open(device.get("noise-model"), "r") as f:
                        custom_noise_model = json.load(f)
                    noise_model = NoiseModel.from_dict(custom_noise_model)

                    backend_options = {"noise_model": noise_model}

                    if "gpu" in device and device.get("gpu"):
                        backend_options["device"] = "GPU"

                    sampler = Sampler(backend_options=backend_options)
                elif "backend" in device:
                    real_backend = service.backend(device.get("backend"))
                    noise_model = NoiseModel.from_backend(real_backend)
                    backend_options = {"noise_model": noise_model}

                    if "gpu" in device and device.get("gpu"):
                        backend_options["device"] = "GPU"

                    sampler = Sampler(backend_options=backend_options)
                else:
                    backend_options = {}
                    if "gpu" in device and device.get("gpu"):
                        backend_options["device"] = "GPU"
                    
                    sampler = Sampler(backend_options=backend_options)

                for subexperiment_keys in batched_subexperiments[i]:
                    for key in subexperiment_keys:
                        result = sampler.run(subexperiments[key]).result()
                        results[key] = json.dumps(
                            result, cls=program_serializers.QiskitObjectsEncoder
                        )
            return results
        except Exception as e:
            print("Error in AER-GPU-Simulator function: ", e)
            logging.info(e)
            logging.info("Error in AER-GPU-Simulator function")
            raise Exception("Error at IBM function", e)
