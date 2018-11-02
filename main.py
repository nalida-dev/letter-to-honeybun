from flask import Flask, request, render_template
from database_wrapper_redis import DatabaseWrapperRedis
import credentials
import assets

app = Flask(__name__)
db = DatabaseWrapperRedis(host='localhost', port=6379, db=0, namespace="Nalida-Honeybun")

@app.route("/")
def root():
    return render_template('honeybun.html', questions = assets.questions)

app.run(host=credentials.HOST, port=credentials.PORT)
