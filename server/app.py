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
from dotenv import dotenv_values

jobs_file = "jobs.json"

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

jobs = {}

def load_jobs():
    if os.path.exists(jobs_file):
        print("Loading jobs from file.")
        with open(jobs_file, 'r') as f:
            return json.load(f)
    return {}

def save_jobs():
    global jobs
    if not jobs:
        # print("No jobs to save.")
        return
    print(f"Saving {len(jobs)} jobs to file.")
    try:
        existing_jobs = load_jobs()

        combined_jobs = {**existing_jobs, **jobs}

        with open(jobs_file, 'w') as f:
            json.dump(combined_jobs, f)

        print("Jobs saved.")
    except Exception as e:
        logging.error(f"Error saving jobs: {str(e)}")

def periodic_save():
    while True:
        time.sleep(30)
        save_jobs()

        completed_jobs = [job_id for job_id, job in jobs.items() if job["is_done"]]
        for job_id in completed_jobs:
            print(f"Removing completed job from memory: job_id={job_id}")
            del jobs[job_id]

class GPUSimulator(gpusimulator_pb2_grpc.GPUSimulatorServicer):
    def ExecuteCircuit(self, request, context):
        job_id = str(uuid.uuid4())
        obj = request.input
        jobs[job_id] = {"is_done": False, "results": None, "start_time": time.time()}
        print(f"ExecuteCircuit request: job_id={job_id}")

        def execute():
            # time.sleep(15)
            results = Simulator.exec_circuit(obj.subexperiments, obj.devices)
            jobs[job_id]["results"] = results
            jobs[job_id]["is_done"] = True
            jobs[job_id]["end_time"] = time.time()
            jobs[job_id]["time_taken"] = jobs[job_id]["end_time"] - jobs[job_id]["start_time"]
            print(f"Job completed: job_id={job_id}")

        threading.Thread(target=execute).start()
        return gpusimulator_pb2.ExecuteCircuitResponse(job_id=job_id)

    def CheckJobStatus(self, request, context):
        job_id = request.job_id
        print(f"CheckJobStatus request: job_id={job_id}")

        if job_id in jobs:
            return gpusimulator_pb2.CheckJobStatusResponse(
                is_done=jobs[job_id]["is_done"],
                results=jobs[job_id]["results"] if jobs[job_id]["is_done"] else ""
            )
        else:
            print("Job ID not found in memory, checking file.")
            file_jobs = load_jobs()
            if job_id in file_jobs:
                return gpusimulator_pb2.CheckJobStatusResponse(
                    is_done=file_jobs[job_id]["is_done"],
                    results=file_jobs[job_id]["results"] if file_jobs[job_id]["is_done"] else ""
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
            logging.error("Failed to retrieve global IP, status code: %s", response.status_code)
            return None
    except Exception as e:
        logging.error("Error retrieving global IP: %s", str(e))
        return None

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_address = s.getsockname()
    s.close()
    print("Local IP Address: %s", local_address)
    return local_address[0]

def serve():
    global jobs
    jobs = load_jobs()

    threading.Thread(target=periodic_save, daemon=True).start()

    serverip = get_ip()
    serverip = get_global_ip()
    serverip = "0.0.0.0"
    config = dotenv_values(".env")
    port = config.get("PORT")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gpusimulator_pb2_grpc.add_GPUSimulatorServicer_to_server(GPUSimulator(), server)
    server.add_insecure_port(serverip + ':' + port)
    server.start()
    print("Server started, listening on %s:%s", serverip, port)
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
