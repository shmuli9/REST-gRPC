import os

from flask import Flask, render_template, jsonify, redirect, send_from_directory

app = Flask(__name__)


@app.route('/mult_matrices', methods=["POST"])
def hello_world():

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
