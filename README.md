# Running the gRPC Simulator Locally

To run the gRPC simulator locally, follow the steps below.

## 1. Install Dependencies

First, install the required dependencies using the following command:

```bash
pip install -r requirements.txt
```

## 2. Start the Server

Navigate to the `server` directory and start the server by running:

```bash
cd server
python app.py
```

## 3. Make Requests to the Server

In a new terminal window, navigate to the `client` directory and run the following command to make requests to the server:

```bash
cd client
python app.py
```

## 4. Job Processing

When a request is made to the server, the server processes it as a job and returns the job ID to the client. The client will then poll the server every 5 seconds to check if the job is complete. Once the job is finished, the server will return the result to the client.

## 5. Job Logs

The server logs the job ID and the results (both GPU and CPU) in the `server/jobs.json` file for reference.

## 6. Simulator Code

The server runs the simulator (both CPU and GPU) using the code provided in the `server/IBM_Aer_gpu.py` file.

## 7. Modifying Request Parameters

You can modify the request parameters in the `client/payload.json` file. For example:

```json
{
    "device": {
        "device": "aer",
        "backend": "ibm_brisbane",
        "gpu": true,
        "shots": 1024
    }
}
```

- If the `gpu` parameter is set to `true`, the simulator will run on the GPU.
- If the `gpu` parameter is set to `false`, the simulator will run on the CPU.

- The `shots` parameter specifies the number of shots to run. The default value is 1024.