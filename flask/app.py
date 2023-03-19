from flask import Flask
from multiprocessing import Process
from process import adder


app = Flask(__name__)

a = adder()


@app.route("/mindata")
def mindata():
    return a.get_data()


def inf_loop():
    try:
        a.run()
    except:
        return "error"


if __name__ == "__main__":
    print(__name__)
    p1 = Process(target=a.run())
    p1.start()
    p2 = Process(target=app.run(debug=True))
    p2.start()
    p1.join()
    p2.join()
