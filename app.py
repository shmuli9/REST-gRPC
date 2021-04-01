import asyncio
import csv
import io
import os
import random
import time

from flask import Flask, render_template, jsonify, send_from_directory, request

from matrix_client import multiplyMatrixBlock

app = Flask(__name__)


@app.route('/mult_matrices', methods=["POST"])
def do_maths():
    deadline = request.form.get("deadline", 90, int)

    if 'mat1' not in request.files or "mat2" not in request.files:
        matrix_dimension = request.form.get("dimension", 256, int)
        mat1 = test_matrix(matrix_dimension)
        mat2 = test_matrix(matrix_dimension)
    else:
        mat1 = parse_matrix(request.files['mat1'])
        mat2 = parse_matrix(request.files['mat2'])

    # print(mat1, mat2, deadline)
    if mat1 != [] and mat2 != []:
        t1 = time.time()
        result = asyncio.run(multiplyMatrixBlock(mat1, mat2, deadline))
        total_time = time.time() - t1

        print(f"total time taken: {total_time} seconds")

        out = {
            "res": result,
            "mat1": mat1,
            "mat2": mat2
        }

        return jsonify(out), 200


def test_matrix(size):
    mat = []
    for i in range(size):
        row = []
        for j in range(size):
            row.append(random.randint(0, 1000))
        mat.append(row)
    return mat


def parse_matrix(mat):
    stream = io.StringIO(mat.stream.read().decode("UTF8"), newline=None)
    csv_input = csv.reader(stream)

    matrix = []
    for row in csv_input:
        mat_row = []
        for num in row[0].split():
            mat_row.append(int(num))

        n = len(mat_row)
        if not ((n & (n - 1) == 0) and n != 0):
            print("error - matrix must be nxn, where n is a power of 2")
            return []

        matrix.append(mat_row)

    return matrix


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/')
def main():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
