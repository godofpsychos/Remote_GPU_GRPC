from concurrent import futures
import logging
import grpc
import gpusimulator_pb2
import gpusimulator_pb2_grpc

class GPUSimulator(gpusimulator_pb2_grpc.GPUSimulatorServicer):
    def ExecuteCircuit(self, request, context):
        print('Request Payload:', request)
        return gpusimulator_pb2.GetCircuitResponse(results="Results")

def serve():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gpusimulator_pb2_grpc.add_GPUSimulatorServicer_to_server(GPUSimulator(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig()
    serve()
