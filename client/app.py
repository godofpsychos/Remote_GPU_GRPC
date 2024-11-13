from __future__ import print_function
import grpc
import gpusimulator_pb2
import gpusimulator_pb2_grpc
import json
import time

def run(subexperiments, devices):
    ip_address = "localhost:50051"
    # ip_address = "14.139.128.83:9092"
    with grpc.insecure_channel(ip_address) as channel:
        stub = gpusimulator_pb2_grpc.GPUSimulatorStub(channel)

        input_message = gpusimulator_pb2.Input(
            subexperiments=subexperiments, devices=devices
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
    ip_address = "localhost:50051"
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
    body = json.load(f)
    input = json.loads(body)
    subexperiments = json.dumps(input["data"]["subexperiments"])
    devices = json.dumps(input["devices"])

    jobid = run(subexperiments, devices)

    print("jobid", jobid)

    while True:
        status = poll(jobid)
        if status.is_done:
            results = status.results
            with open("output.json", "w") as f:
                json.dump(results, f, indent=4)
            print("saved")
            break
        time.sleep(5)
