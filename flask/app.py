from flask import Flask
from DataBase import DB
from multiprocessing import Process, Value
from process import adder


app = Flask(__name__)

a = adder()


@app.route("/mindata")
def mindata():
    return a.get_data()


def inf_loop():
    print("run")
    try:
        a.run()
    except:
        return "error"


if __name__ == "__main__":
    print("run")
    p = Process(target=inf_loop)
    p.start()
    app.run(debug=True)
    p.join()
