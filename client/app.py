from __future__ import print_function
import grpc
import gpusimulator_pb2
import gpusimulator_pb2_grpc

def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = gpusimulator_pb2_grpc.GPUSimulatorStub(channel)
        
        input_message = gpusimulator_pb2.Input(subexperiments="your_subexperiments_data1", devices="your_devices_data1")
        request = gpusimulator_pb2.GetCircuitRequest(input=input_message)

        try:
            response = stub.ExecuteCircuit(request)
            print("Response received:", response.results)
        except grpc.RpcError as e:
            print("Error making gRPC request:", e)

if __name__ == "__main__":
    run()
