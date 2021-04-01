import asyncio
import logging
import math
import time

import grpc

import matrix_pb2
import matrix_pb2_grpc


async def multiplyMatrixBlock(A, B, timeout):
    deadline = timeout

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

    # time first mult call, and work out how many servers needed to finish on time
    print(f"footprinting... (matrix dim = {len(A)}, deadline = {deadline})")
    stub = matrix_pb2_grpc.MatrixCalcStub(grpc.insecure_channel("localhost:8080"))

    start = time.time()

    temp1 = stub.BlockMult(matrix_pb2.Request(matA=list2mat(A1), matB=list2mat(A2))).matResult

    time_taken = time.time() - start

    servers_required = min(8, math.ceil((time_taken * 12) / deadline) + 1)
    print(f"servers needed calculated at {servers_required} (took {time_taken}s for first mult calculation, "
          f"deadline {deadline})")
    mults = [(B1, C2), (A1, B2), (B1, D2), (C1, A2), (D1, C2), (C1, B2), (D1, D2)]  # pairs to multiply

    temps = []
    count = 0  # number of gRPC calls made
    servers = [f"localhost:{port}" for port in range(8080, 8088)]  # servers to use

    while True:
        params = [(m1, m2) for (m1, m2) in mults[count:count + servers_required]]
        for i in range(len(params)):
            server = servers[int(i % servers_required)]
            params[i] = (params[i][0], params[i][1], server)

        temps_asyncs = asyncio.gather(*[mult(m1, m2, server) for (m1, m2, server) in params])
        resolved = await temps_asyncs
        # print(resolved[0], type(resolved[0]))
        for item in resolved:
            temps.append(item)

        count += servers_required
        if count >= 7:
            break

    # temp2, temp3, temp4, temp5, temp6, temp7, temp8 = temps
    adds = [temp1, *temps]
    adds = [(adds[i], adds[i+1]) for i in range(0, len(adds), 2)]
    count = 0
    tempAdds = []

    while True:
        params = [(m1, m2) for (m1, m2) in adds[count:count + servers_required]]

        for i in range(len(params)):
            server = servers[int(i % servers_required)]
            params[i] = (params[i][0], params[i][1], server)

        temps_asyncs = asyncio.gather(*[add(m1, m2, server) for (m1, m2, server) in params])
        resolvedAdds = await temps_asyncs
        # print(resolved[0], type(resolved[0]))
        for item in resolvedAdds:
            tempAdds.append(item)

        count += servers_required
        if count >= 7:
            break

    a3, b3, c3, d3 = tempAdds

    A3 = mat2list(a3)
    B3 = mat2list(b3)
    C3 = mat2list(c3)
    D3 = mat2list(d3)

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


def getStub():
    server = "localhost:8080"
    # print(f"using server {server}")
    stub = matrix_pb2_grpc.MatrixCalcStub(grpc.insecure_channel(server))
    return stub


async def add(A, B, server):
    print(f"add using server {server}")
    options = [('grpc.max_message_length', 100 * 1024 * 1024)]
    stub = matrix_pb2_grpc.MatrixCalcStub(grpc.aio.insecure_channel(server, options=options))
    res = await stub.BlockAdd(matrix_pb2.Request(matA=A, matB=B))

    return res.matResult


async def mult(A, B, server):
    print(f"mult using server {server}")
    options = [('grpc.max_message_length', 100 * 1024 * 1024)]
    stub = matrix_pb2_grpc.MatrixCalcStub(grpc.aio.insecure_channel(server, options=options))
    res = await stub.BlockMult(matrix_pb2.Request(matA=list2mat(A), matB=list2mat(B)))

    return res.matResult


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
