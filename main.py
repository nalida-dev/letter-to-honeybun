from flask import Flask, request, render_template, redirect, url_for
from database_wrapper_redis import DatabaseWrapperRedis
import credentials
import assets
import random
import json
from string import ascii_letters

import requests
import queue
import time
import threading

app = Flask(__name__)
db = DatabaseWrapperRedis(host='localhost', port=6379, db=0, namespace="Nalida-Honeybun")
alphabet = ascii_letters + '0123456789'

report_queue = queue.Queue()

def check_report_queue():
    while True:
        if not report_queue.empty():
            text = report_queue.get()
            t = threading.Thread(target = requests.post,
                args = (credentials.api_base + 'sendMessage', ),
                kwargs = {
                    'data': {
                        "chat_id" : credentials.monitoring_room_id,
                        "text" : text
                        }
                    }
                )
            t.setDaemon(True)
            t.start()
        time.sleep(1)

threading.Thread(target=check_report_queue, args=(), daemon=True).start()

def report(text):
    report_queue.put(text)
    db.lpush('reports', text)

@app.route("/")
def root():
    return render_template('honeybun.html', questions=assets.questions)

@app.route("/result/<result_id>")
def result(result_id):
    answers = json.loads(db.get("answer:%s" % result_id))
    return render_template('honeybun.html', questions=assets.questions, answers=answers)


@app.route("/save", methods=['POST'])
def save():
    result_id = ''.join(random.choice(alphabet) for _ in range(10))
    answers = list(map(lambda x:x[1], sorted(request.form.items(), key=lambda x:int(x[0][1:]))))
    report('http://honeybun.nalida.info/result/' + result_id)
    db.set("answer:%s" % result_id, json.dumps(answers))
    return redirect(url_for('result', result_id=result_id))

app.run(host=credentials.HOST, port=credentials.PORT)
