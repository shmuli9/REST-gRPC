from concurrent import futures
import logging

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
        C = [[A[i][j] + B[i][j] for j in range(4)] for i in range(4)]

        return matrix_pb2.Reply(matResult=list2mat(C))

    def BlockMult(self, request, context):
        A = mat2list(request.matA)
        B = mat2list(request.matB)

        C = [[0 for j in range(4)] for i in range(4)]
        C[0][0] = A[0][0] * B[0][0] + A[0][1] * B[1][0]
        C[0][1] = A[0][0] * B[0][1] + A[0][1] * B[1][1]
        C[1][0] = A[1][0] * B[0][0] + A[1][1] * B[1][0]
        C[1][1] = A[1][0] * B[0][1] + A[1][1] * B[1][1]
        return matrix_pb2.Reply(matResult=list2mat(C))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    matrix_pb2_grpc.add_MatrixCalcServicer_to_server(Matrix(), server)
    server.add_insecure_port('[::]:8080')
    server.start()
    print("Server started")
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
