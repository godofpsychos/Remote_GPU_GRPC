from qiskit_aer.noise import NoiseModel
from qiskit_aer.primitives import Sampler
from qutils import marshaller, program_serializers
import json
from more_itertools import divide
import logging
from IBM_Aer_gpu import AER_GPU

class Simulator:
    def exec_circuit(subexperiments,devices):
        try:
            results= AER_GPU.exec_circuitAER(subexperiments,devices)
            print(results)
            return results
        except Exception as e:
            print(e)
            logging.info(e)
            logging.info("Error in GPU-Simulator function")
            raise Exception("Error at user function",e)

