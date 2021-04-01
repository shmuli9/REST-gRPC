import logging
import os
from concurrent import futures
from multiprocessing import Process

import grpc

import matrix_pb2
import matrix_pb2_grpc


def list2mat(list_matrix):
    rpc_matrix = matrix_pb2.Mat()
    for row in list_matrix:
        v = matrix_pb2.Vector(value=row)
        rpc_matrix.row.extend([v])
    return rpc_matrix


def mat2list(rpc_matrix):
    l = []
    for row in rpc_matrix.row:
        r = []
        for val in row.value:
            r.append(val)
        l.append(r)
    return l


class Matrix(matrix_pb2_grpc.MatrixCalcServicer):

    def BlockAdd(self, request, context):
        A = mat2list(request.matA)
        B = mat2list(request.matB)
        MAX = len(A)

        C = [[A[i][j] + B[i][j] for j in range(MAX)] for i in range(MAX)]

        return matrix_pb2.Reply(matResult=list2mat(C))

    def BlockMult(self, request, context):
        A = mat2list(request.matA)
        B = mat2list(request.matB)
        MAX = len(A)

        C = [[0 for j in range(MAX)] for i in range(MAX)]

        for i in range(MAX):
            for j in range(MAX):
                for k in range(MAX):
                    C[i][j] += A[i][k] * B[k][j]

        return matrix_pb2.Reply(matResult=list2mat(C))


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
