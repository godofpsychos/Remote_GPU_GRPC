from concurrent import futures
import logging
import grpc
import gpusimulator_pb2
import gpusimulator_pb2_grpc
import socket
import requests
from Simulator import Simulator


class GPUSimulator(gpusimulator_pb2_grpc.GPUSimulatorServicer):
    def ExecuteCircuit(self, request, context):
        # print('Request Payload:', request)
        print(type(request.input))
        obj=request.input
        # print(obj.subexperiments,obj.devices)
        Results=Simulator.exec_circuit(obj.subexperiments,obj.devices)
        return gpusimulator_pb2.GetCircuitResponse(results=Results)

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
        s.connect(("8.8.8.8", 80)) #Send packect to google
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
    logging.basicConfig()
    serve()
