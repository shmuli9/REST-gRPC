import logging
import os
from concurrent import futures
from multiprocessing import Process

import grpc
import numpy as np

import matrix_pb2
import matrix_pb2_grpc


def np2mat(np_matrix):
    rpc_matrix = matrix_pb2.Mat()

    for row in np_matrix:
        v = matrix_pb2.Vector(value=row.tolist())
        rpc_matrix.row.extend([v])
    return rpc_matrix


def mat2np(rpc_matrix):
    size = len(rpc_matrix.row)
    l = np.ndarray([size, size], dtype=int)

    for i in range(size):
        row = rpc_matrix.row[i]
        for j in range(size):
            l[i, j] = row.value[j]
    return l


class Matrix(matrix_pb2_grpc.MatrixCalcServicer):

    def BlockAdd(self, request, context):
        A = mat2np(request.matA)
        B = mat2np(request.matB)
        C = A + B

        return matrix_pb2.Reply(matResult=np2mat(C))

    def BlockMult(self, request, context):
        A = mat2np(request.matA)
        B = mat2np(request.matB)
        C = np.matmul(A, B)

        return matrix_pb2.Reply(matResult=np2mat(C))


def serve(port=8080):
    options = [
        ('grpc.max_send_message_length', 500 * 1024 * 1024),
        ('grpc.max_receive_message_length', 500 * 1024 * 1024)
    ]
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=options)
    matrix_pb2_grpc.add_MatrixCalcServicer_to_server(Matrix(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"Server started on port {port} (pid: {os.getpid()})")
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    for port in range(8080, 8088):
        p = Process(target=serve, args=(port,))
        p.start()
    # serve()
