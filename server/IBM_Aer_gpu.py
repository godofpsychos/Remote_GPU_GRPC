from qiskit_aer.noise import NoiseModel
from qutils import serializers, program_serializers
import json
import logging
from qiskit_aer.primitives import Sampler

class AER_GPU:
    def exec_circuitAER(subexperiments, devices, service=None):
        try:
            device = json.loads(devices)
            print("device", device)
            subexperiments = json.loads(subexperiments)
            print(len(subexperiments))
            results = {}
            noise_model = None

            shots = device.get("shots", 1024)
            print(f"shots used: {shots}")

            sampler = None

            if "noise-model" in device:
                custom_noise_model = None
                with open(device.get("noise-model"), "r") as f:
                    custom_noise_model = json.load(f)
                noise_model = NoiseModel.from_dict(custom_noise_model)

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
            
            output = [serializers.circuit_deserializer(item) for item in subexperiments]

            result = sampler.run(output, shots=shots).result()
            results = json.dumps(
                result, cls=program_serializers.QiskitObjectsEncoder
            )
            return results, json.dumps(noise_model.to_dict(), cls=program_serializers.QiskitObjectsEncoder)
        except Exception as e:
            print("Error in AER-GPU-Simulator function: ", e)
            logging.error(e)
            logging.error("Error in AER-GPU-Simulator function")
            raise Exception("Error at IBM function", e)
