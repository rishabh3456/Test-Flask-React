from flask import Flask
from DataBase import DB

database = DB()

app = Flask(__name__)


@app.route("/mindata")
def mindata():
    return database.get_data()


if __name__ == "__main__":
    app.run(debug=True)
