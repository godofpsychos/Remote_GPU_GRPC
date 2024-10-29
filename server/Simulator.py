import json
import logging
from IBM_Aer_gpu import AER_GPU
from AWS_Braket import Braket_Simulator
import time
import plotter
from dotenv import dotenv_values
from qiskit_ibm_runtime import QiskitRuntimeService

class Simulator:
    config = dotenv_values(".env")
    token = config.get("IBMQ_TOKEN")
    service = QiskitRuntimeService(token=token, channel="ibm_quantum")
    
    def exec_simulator(simulator_func, *args):
        try:
            result = simulator_func(*args)
            return result
        except Exception as e:
            print(f"Error in {simulator_func.__name__} function: {e}")
            return {
                "error": str(e),
                "time": time.time()
            }

    # def exec_circuit(subexperiments, devices):
    #     try:
    #         results = {}

    #         try:
    #             with open("output.json", "r+") as f:
    #                 results = json.load(f) or {}
    #         except FileNotFoundError:
    #             pass
            
    #         result1, time1 = Simulator.exec_simulator(AER_GPU.exec_circuitAER, subexperiments, devices, 0, Simulator.service)
    #         result2, time2 = Simulator.exec_simulator(AER_GPU.exec_circuitAER, subexperiments, devices, 1, Simulator.service)
    #         result3, time3 = Simulator.exec_simulator(Braket_Simulator.exec_circuit, subexperiments, devices)

    #         results[time.time()] = {
    #             "output": {
    #                 "AER_without_GPU": result1,
    #                 "AER_with_GPU": result2,
    #                 "Braket_without_GPU": result3,
    #             },
    #             "time_taken": {
    #                 "AER_without_GPU": time1,
    #                 "AER_with_GPU": time2,
    #                 "Braket_without_GPU": time3
    #             }
    #         }

    #         with open("output.json", "w") as f:
    #             json.dump(results, f, indent=4)

    #         json.dumps(results)
    #         plotter.plot("output.json", "chart.png", xlabel="Runs", ylabel="Seconds", title="Time taken")
    #         return results
    #     except Exception as e:
    #         print(e)
    #         logging.error(e)
    #         logging.error("Error in GPU-Simulator function")
    #         raise Exception("Error at Simulator function", e)

    def exec_circuit(subexperiments, devices):
        try:
            results = Simulator.exec_simulator(AER_GPU.exec_circuitAER, subexperiments, devices, Simulator.service)
            
            return json.dumps(results)
        
        except Exception as e:
            print(e)
            logging.error(e)
            logging.error("Error in GPU-Simulator function")
            raise Exception("Error at Simulator function", e)