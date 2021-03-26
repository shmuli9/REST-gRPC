import os
import io
import csv

from flask import Flask, render_template, jsonify, redirect, send_from_directory, request

app = Flask(__name__)


@app.route('/mult_matrices', methods=["POST"])
def do_maths():
    # check if the post request has the file part
    if 'mat1' not in request.files or "mat2" not in request.files:
        print('No file part')
        return jsonify(), 400
    mat1 = request.files['mat1']
    mat2 = request.files['mat2']

    stream = io.StringIO(mat1.stream.read().decode("UTF8"), newline=None)
    csv_input = csv.reader(stream)
    # print(csv_input)

    for row in csv_input:
        print(row)

    return jsonify(), 200

    return 'Hello World!'

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def main():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
