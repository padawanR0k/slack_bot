import reply
from datetime import date, datetime
import time
import schedule
import bot_events
import calendar

from slack import WebClient
import json
from flask import Flask, Response
from slackeventsapi import SlackEventAdapter
import os
from threading import Thread, Event

from apscheduler.schedulers.background import BackgroundScheduler
sched = BackgroundScheduler()


# This `app` represents your existing Flask app
app = Flask(__name__)

# 환경변수 값

# 슬랙 봇 암호키
SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
# 슬랙 봇 키
VERIFICATION_TOKEN = os.environ['VERIFICATION_TOKEN']
# 슬랙 토큰
slack_token = os.environ['SLACK_BOT_TOKEN']

print(
    SLACK_SIGNING_SECRET,
	VERIFICATION_TOKEN,
    slack_token,
)

# 슬랙 봇 고유값
SLACK_BOT_PK = '<@u01erlmhyuc>'
# 일반 채널 고유값
SLACK_CH_01 = 'C01EY4N7CRX'

# 슬랙에서 제공하는 webclient 클래스
slack_client = WebClient(slack_token)



@app.route("/slack/events")
def event_for_verify(request):
	json_dict = json.loads(request.body.decode("utf-8"))
	if json_dict["token"] != VERIFICATION_TOKEN:
		return {"status": 403}

	if "type" in json_dict:
		if json_dict["type"] == "url_verification":
			response_dict = {"challenge": json_dict["challenge"]}
			return response_dict
	return {"status": 500}


@app.route("/")
def event_hook(request):
	json_dict = json.loads(request.body.decode("utf-8"))
	if json_dict["token"] != VERIFICATION_TOKEN:
		return {"status": 403}

	if "type" in json_dict:
		if json_dict["type"] == "url_verification":
			response_dict = {"challenge": json_dict["challenge"]}
			return response_dict
	return {"status": 500}


slack_events_adapter = SlackEventAdapter(
	SLACK_SIGNING_SECRET, "/slack/events", app
)


"""
멘션한 경우 실행시킬 함수
"""
@slack_events_adapter.on("app_mention")  # 특정함수를 슬랙이벤트에 바인딩시킬 떄 이런식으로 어노테이션을 추가한다.
def handle_message(event_data):
	thread = Thread(target=reply.send_reply, kwargs={
		"client": slack_client,
		"value": event_data})
	thread.start()

	return Response(status=200)



NOTICE_QR_FLAG = False
# 매일 12시 30분에 실행
@sched.scheduled_job('cron', id='end_qrcode', hour=18, minute=0, second=0, end_date='2021-04-21')
def notice_qrcode():
	global NOTICE_QR_FLAG

	if NOTICE_QR_FLAG:
		today = datetime.today()
		d = datetime(today.year, today.month, today.day).isoformat()[:10]
		if today.weekday != calendar.SATURDAY and today.weekday != calendar.SUNDAY:
			if d not in bot_events.holydays:
				print('qr코드이미지를 보낸다')
				slack_client.chat_postMessage(
					channel=SLACK_CH_01,
					blocks=[
						{
							"type": "section",
							"text": {
								"type": "mrkdwn",
								"text": ":star: :star: :star:  *혹시 퇴실처리 하셨나요 ?* :star: :star: :star: "
							}
						},
						{
							"type": "image",
							"title": {
								"type": "plain_text",
								"text": "아 맞다! 퇴근처리!",
								"emoji": True
							},
							"image_url": "https://gist.github.com/padawanR0k/09a9df22a6ebbffb949787ba003808b2#file-aha-jpg",
							# "image_url": "https://gist.githubusercontent.com/padawanR0k/09a9df22a6ebbffb949787ba003808b2/raw/ce86828e02d33f8bc2c57171ca310d12207f0168/qrcode.jpeg",
							"alt_text": "아 맞다! 퇴근처리"
						}
					]
				)
	else:
		NOTICE_QR_FLAG = True

# Start the server on port 3000
print(f'__name__: {__name__}')

if __name__ == "__main__":
	print(f'tab is running')
	sched.start()
	app.run(port=3000, debug=True)
