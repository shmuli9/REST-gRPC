## gRPC Lab

This project uses gRPC to do block matrix multiplication (BMM). 
The benefit being able to spread the load over multiple servers.

block_mult.py contains the procedural way of doing BMM

matrix_client.py, matrix_server.py and matrix.proto are the main parts
of the gRPC implementation.


### Run:
   
   Make sure the pb2 files have been generated (see the next step, if not)

   _then_

   Run the **server**:

    $ python matrix_server.py

   From a different terminal, run the **client**:

    $ python matrix_client.py

### Modify

Editing the client or server files doessnt require any build step in Python. But,
if you want to edit the .proto file you will need to regenerate the pb2 files - 
details below:

#### 1. Install pre-reqs: (just the first time)

    $ python -m pip install grpcio grpcio-tools

#### 2. Generate the code:

    $ python -m grpc_tools.protoc -I./ --python_out=. --grpc_python_out=. matrix.proto

#### Run
    
See first section, above 