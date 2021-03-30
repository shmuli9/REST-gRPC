import logging
import random

import grpc

import matrix_pb2
import matrix_pb2_grpc


def multiplyMatrixBlock(A, B):
    MAX = len(A)
    bSize = 2

    A1 = [[0 for _ in range(MAX)] for _ in range(MAX)]
    A2 = [[0 for _ in range(MAX)] for _ in range(MAX)]
    A3 = [[0 for _ in range(MAX)] for _ in range(MAX)]
    B1 = [[0 for _ in range(MAX)] for _ in range(MAX)]
    B2 = [[0 for _ in range(MAX)] for _ in range(MAX)]
    B3 = [[0 for _ in range(MAX)] for _ in range(MAX)]
    C1 = [[0 for _ in range(MAX)] for _ in range(MAX)]
    C2 = [[0 for _ in range(MAX)] for _ in range(MAX)]
    C3 = [[0 for _ in range(MAX)] for _ in range(MAX)]
    D1 = [[0 for _ in range(MAX)] for _ in range(MAX)]
    D2 = [[0 for _ in range(MAX)] for _ in range(MAX)]
    D3 = [[0 for _ in range(MAX)] for _ in range(MAX)]
    res = [[0 for _ in range(MAX)] for _ in range(MAX)]

    for i in range(bSize):
        for j in range(bSize):
            A1[i][j] = A[i][j]
            A2[i][j] = B[i][j]

    for i in range(bSize):
        for j in range(bSize, MAX):
            B1[i][j - bSize] = A[i][j]
            B2[i][j - bSize] = B[i][j]

    for i in range(bSize, MAX):
        for j in range(bSize):
            C1[i - bSize][j] = A[i][j]
            C2[i - bSize][j] = B[i][j]

    for i in range(bSize, MAX):
        for j in range(bSize, MAX):
            D1[i - bSize][j - bSize] = A[i][j]
            D2[i - bSize][j - bSize] = B[i][j]

    A3 = mat2list(add(mult(A1, A2), mult(B1, C2)))
    B3 = mat2list(add(mult(A1, B2), mult(B1, D2)))
    C3 = mat2list(add(mult(C1, A2), mult(D1, C2)))
    D3 = mat2list(add(mult(C1, B2), mult(D1, D2)))

    for i in range(bSize):
        for j in range(bSize):
            res[i][j] = A3[i][j]

    for i in range(bSize):
        for j in range(bSize, MAX):
            res[i][j] = B3[i][j - bSize]

    for i in range(bSize, MAX):
        for j in range(bSize):
            res[i][j] = C3[i - bSize][j]

    for i in range(bSize, MAX):
        for j in range(bSize, MAX):
            res[i][j] = D3[i - bSize][j - bSize]

    return res


servers = [f"localhost:{port}" for port in range(8080, 8088)]


def getStub():
    server = random.choice(servers)
    # print(f"using server {server}")
    stub = matrix_pb2_grpc.MatrixCalcStub(grpc.insecure_channel(server))
    return stub


def add(A, B):
    stub = getStub()
    return stub.BlockAdd(matrix_pb2.Request(matA=A, matB=B)).matResult


def mult(A, B):
    stub = getStub()
    return stub.BlockMult(matrix_pb2.Request(matA=list2mat(A), matB=list2mat(B))).matResult


def mat2list(rpc_matrix):
    l = []
    for row in rpc_matrix.row:
        r = []
        for val in row.value:
            r.append(val)
        l.append(r)
    return l


def list2mat(list_matrix):
    rpc_matrix = matrix_pb2.Mat()
    for row in list_matrix:
        v = matrix_pb2.Vector(value=row)
        rpc_matrix.row.extend([v])
    return rpc_matrix


def run():
    A = [[i + (4 * j) + 1 for i in range(4)] for j in range(4)]
    B = [[i + (4 * j) + 1 for i in range(4)] for j in range(4)]

    result = multiplyMatrixBlock(A, B)
    for i in range(MAX):
        for j in range(MAX):
            print(result[i][j], end=" ")
        print()


if __name__ == '__main__':
    logging.basicConfig()
    run()
