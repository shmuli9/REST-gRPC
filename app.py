import os
import io
import csv

from flask import Flask, render_template, jsonify, redirect, send_from_directory, request
from matrix_client import multiplyMatrixBlock

app = Flask(__name__)


@app.route('/mult_matrices', methods=["POST"])
def do_maths():
    # check if the post request has the file part
    if 'mat1' not in request.files or "mat2" not in request.files:
        print('No file part')
        return jsonify(), 400
    mat1 = parse_matrix(request.files['mat1'])
    mat2 = parse_matrix(request.files['mat2'])

    # print(mat1, mat2)
    if mat1 != [] and mat2 != []:
        result = multiplyMatrixBlock(mat1, mat2)

        print(result)

    return jsonify(result), 200


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
