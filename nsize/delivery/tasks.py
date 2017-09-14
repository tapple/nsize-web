from celery import Celery
import requests

app = Celery('tasks', broker='redis://localhost:6379/0')

LSL_GATEWAY_URL = 'http://nsize-dev.us-west-1.elasticbeanstalk.com/api/lsl_gateway/cap/'


@app.task
def instant_message(avatar_id, message):
    requests.post(
        LSL_GATEWAY_URL + 'agni/garments/instantMessage/',
        json={
            'target': avatar_id,
            'msg': message,
        }
    )
