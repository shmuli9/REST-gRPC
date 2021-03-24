from flask import Flask, render_template, jsonify, redirect

app = Flask(__name__)


@app.route('/mult_matrices', methods=["POST"])
def hello_world():

    return 'Hello World!'

@app.route('/')
def main():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
