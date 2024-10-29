from concurrent import futures
import logging
import grpc
import gpusimulator_pb2
import gpusimulator_pb2_grpc
import socket
import requests
from Simulator import Simulator
import uuid
import json
import threading
import os
import time

jobs_file = "jobs.json"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_jobs():
    if os.path.exists(jobs_file):
        with open(jobs_file, 'r') as f:
            return json.load(f)
    return {}

def save_jobs(jobs):
    with open(jobs_file, 'w') as f:
        json.dump(jobs, f)

class GPUSimulator(gpusimulator_pb2_grpc.GPUSimulatorServicer):
    def ExecuteCircuit(self, request, context):
        job_id = str(uuid.uuid4())
        obj = request.input
        jobs = load_jobs()
        jobs[job_id] = {"is_done": False, "results": None, "start_time": time.time()}
        save_jobs(jobs)
        logging.info(f"ExecuteCircuit request: job_id={job_id}")

        def execute():
            results = Simulator.exec_circuit(obj.subexperiments, obj.devices)
            jobs[job_id]["results"] = results
            jobs[job_id]["is_done"] = True
            jobs[job_id]["end_time"] = time.time()
            jobs[job_id]["time_taken"] = jobs[job_id]["end_time"] - jobs[job_id]["start_time"]
            save_jobs(jobs)
            logging.info(f"Job completed: job_id={job_id}")

        threading.Thread(target=execute).start()
        return gpusimulator_pb2.ExecuteCircuitResponse(job_id=job_id)

    def CheckJobStatus(self, request, context):
        job_id = request.job_id
        logging.info(f"CheckJobStatus request: job_id={job_id}")
        jobs = load_jobs()

        if job_id in jobs:
            return gpusimulator_pb2.CheckJobStatusResponse(
                is_done=jobs[job_id]["is_done"],
                results=jobs[job_id]["results"] if jobs[job_id]["is_done"] else ""
            )
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Job ID not found")
            return gpusimulator_pb2.CheckJobStatusResponse()

def get_global_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        if response.status_code == 200:
            return response.json()["ip"]
        else:
            print("Failed to retrieve global IP, status code:", response.status_code)
            return None
    except Exception as e:
        print("Error retrieving global IP:", str(e))
        return None

def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_address = s.getsockname()
        s.close()
        print("Local IP Address:", local_address)
        return local_address[0]

def serve():
    serverip = get_ip()
    print(serverip)
    serverip =  get_global_ip()
    print(serverip)
    serverip="0.0.0.0"
    # serverip ="14.139.128.10"
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gpusimulator_pb2_grpc.add_GPUSimulatorServicer_to_server(GPUSimulator(), server)
    server.add_insecure_port(serverip+':'+ port)
    server.start()
    print("Server started, listening on " +serverip+ ":" + port)
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
