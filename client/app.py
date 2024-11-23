from __future__ import print_function
import grpc
import gpusimulator_pb2
import gpusimulator_pb2_grpc
import json
import time

ip_address = "14.139.128.83:9092"
# ip_address = "localhost:50051"

def run(subexperiments, devices):
    with grpc.insecure_channel(ip_address) as channel:
        stub = gpusimulator_pb2_grpc.GPUSimulatorStub(channel)

        subexperiments_str, devices_str = json.dumps(subexperiments), json.dumps(devices)

        input_message = gpusimulator_pb2.Input(
            subexperiments=subexperiments_str, devices=devices_str
        )
        request = gpusimulator_pb2.GetCircuitRequest(input=input_message)

        try:
            response = stub.ExecuteCircuit(request)
            job_id = response.job_id
            print("jobid", job_id)
            return job_id
        except grpc.RpcError as e:
            print("Error making gRPC request:", e)

def poll(job_id):
    with grpc.insecure_channel(ip_address) as channel:
        stub = gpusimulator_pb2_grpc.GPUSimulatorStub(channel)
        request = gpusimulator_pb2.CheckJobStatusRequest(job_id=job_id)

        try:
            response = stub.CheckJobStatus(request)
            print("status:", response.is_done)
            return response
        except grpc.RpcError as e:
            print("Error polling:", e)

if __name__ == "__main__":
    f = open("payload.json")
    input = json.load(f)
    subexperiments = input["data"]["subexperiments"]
    devices = input["device"]

    jobid = run(subexperiments, devices)

    while True:
        status = poll(jobid)
        if status.is_done:
            results = status.results
            with open("output.json", "w") as f:
                json.dump(results, f, indent=4)
            print("saved")
            break
        print("not completed, waiting for 5 seconds and retrying...")
        time.sleep(5)
