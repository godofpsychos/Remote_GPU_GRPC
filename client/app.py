from __future__ import print_function
import grpc
import gpusimulator_pb2
import gpusimulator_pb2_grpc
import json

def run(subexperiments,devices):
    ip_address="localhost:50051"
    with grpc.insecure_channel(ip_address) as channel:
        stub = gpusimulator_pb2_grpc.GPUSimulatorStub(channel)
        
        input_message = gpusimulator_pb2.Input(subexperiments=subexperiments, devices=devices)
        request = gpusimulator_pb2.GetCircuitRequest(input=input_message)

        try:
            response = stub.ExecuteCircuit(request)
            results=response.results
            print("Response received:", results)
            print(type(results))
            return results
        except grpc.RpcError as e:
            print("Error making gRPC request:", e)

if __name__ == "__main__":
    f=open("payload.json")
    body=json.load(f)
    input=json.loads(body)
    # print("Input:",input)
    subexperiments = input['data']['subexperiments']
    devices = json.dumps(input['devices'])
    
    run(subexperiments,devices)
