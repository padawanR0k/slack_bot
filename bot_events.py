import requests
from bs4 import BeautifulSoup
import calendar
from datetime import datetime

def get_html(url, **kwargs):
	params = {}
	if kwargs.get('params'):
		params = kwargs['params']
	response = requests.get(url, params=params)
	html = BeautifulSoup(response.text, 'html.parser')
	return html


"""
이 봇의 사용방법
"""
def get_bot_doc():

	def build_block(**kwargs):
		block = [
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "*`/help`*"
				}
			},
			{
				"type": "divider"
			},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": f"지금 보고 있는 봇 설명서를 보여준다. \n"
				}
			},

			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "*`/날씨 {{자치구}}`*"
				}
			},
			{
				"type": "divider"
			},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "{{자치구}}에 대한 날씨를 보여준다. 정보 출처: 다음 \n ex) `/날씨 강남구` \n"
				}
			},

			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "*`/결석 {{이번 달 결석횟수}}`*"
				}
			},
			{
				"type": "divider"
			},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "{{이번 달 결석횟수}}를 기반으로 이번 달(단위기간)에 결석할 수 있는 잔여일수를 알려준다. \n ex) `/결석 1`"
				}
			},

			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "*`/블로그`*"
				}
			},
			{
				"type": "divider"
			},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "최근 개발 블로그들에 올라온 글들을 가져온다. \n"
				}
			},
		]
		return block
	return build_block()


"""
개발블로그에서 글을 크롤링하여 반환한다.
"""
def get_post():

	def build_blocks(data, **kwargs):
		blocks = [
			{
				"type": "header",
				"text": {
					"type": "plain_text",
					"text": f":newspaper: 최신 팀 블로그 포스트 | {kwargs['provider']}"
				}
			},
			{
				"type": "divider"
			},
		]

		for i, post in enumerate(data):
			link = post['link']
			author = post['author']
			title = post['title']
			desc = post['description']
			section = {
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": f":arrow_forward:  *<{link}|{title}>* | `{author}` \n {desc}… \n"
				}
			}
			blocks.append(section)
		return blocks

	def get_dev_blog_post():
		data = []
		try:
			res = requests.get('https://awesome-devblog.netlify.app/.netlify/functions/ko_teams_feeds?sort=date.desc&page=1&size=5')
			html_awesome_devblog_team_post = res.json()
			data = html_awesome_devblog_team_post['data']
		except Exception:
			data = []
			print(Exception)

		return build_blocks(data, provider="awesome-devblog")

	def get_geeks_news():
		data = []
		try:
			url = 'https://news.hada.io/new'
			html = get_html(url)
			titles = [a.get_text() for a in html.select('.topic .topictitle a')]
			authors = [span.get_text() for span in html.select('.topic span.topicurl')]
			descs = [a.get_text() for a in html.select('.topicdesc td a')]
			links = [f"{url}/{a.get('href')}" for a in html.select('.topicdesc td a')]
			for i in range(0,5):
				data.append({
					"link": links[i],
					"author": authors[i],
					"title": titles[i],
					"description": descs[i],
				})
		except Exception:
			data = []
			print(Exception)

		return build_blocks(data, provider="GeekNews")


	dev_blog_post = get_dev_blog_post();
	geeks_news = get_geeks_news();
	source = [
		{
			"type": "divider"
		},
		{
		"type": "section",
		"text": {
			"type": "mrkdwn",
			"text": f":computer: *출처* \n - <https://news.hada.io/new|GeekNews>   \n - <https://awesome-devblog.netlify.app/|어썸 데브블로그>"
		}
	}]
	return dev_blog_post + geeks_news + source;


"""
다음에서 날씨를 검색한 결과를 크롤링하여 전달한다.
ex) 000 날씨
"""
def get_weather(query):

	def build_attachments(temp, desc, **kwargs):
		print(kwargs)
		attachments = [
			{
				# "type": "section",
				"mrkdwn_in": ["text"],
				"color": '#5080d5',
				"pretext": f"{kwargs['loc']} {kwargs['time']} ",

				"fields": [
					{
						"title": '🌡 온도',
						"value": f"{temp} ({desc})",
						"short": True,
					},
				],
				"accessory": {
					"type": "image",
							"image_url": "https://i.pinimg.com/564x/77/0b/80/770b805d5c99c7931366c2e84e88f251.jpg",
					"alt_text": "날씨 아이콘"
				}
			},
		]
		return attachments

	url = 'https://search.daum.net/search'
	params = {'q': query.strip() + ' 날씨'}
	html = get_html(url, params=params)

	try:
		time = html.select('.mg_cont .txt_weather')[0].get_text()
		current_temp = html.select('.mg_cont .txt_temp')[0].get_text()
		description = html.select('.mg_cont .txt_desc')[0].get_text()

	except Exception:
		print(Exception)
		time = ''
		current_temp = 0
		description = '키워드를 잘못입력하신거 같아요! 예시) /날씨 서초구'

	return build_attachments(current_temp, description, time=time, loc=query.strip())


"""
결석가능한 날 반환기
1. 단위기간 중 무단으로 결석한 일수가 단위기간 소정훈련일수의 50 퍼센트 이상(소수점 이하 첫째자리에서 반올림하여 계산한다)에 해당하는 훈련생: 단위기간 소정훈련일수의 50 퍼센트 이상을 결석한 날의 다음 날로 제적 처리할 것
2. 총 결석일수가 전체 소정훈련일수(훈련일수가 10일 미만이거나 훈련시간이 40시간 미만 훈련일 경우에는 소정훈련시간)의 20퍼센트를 초과하는 훈련생: 전체 소정훈련일수(소정훈련시간)의 20 퍼센트를 초과하여 결석한 날의 다음 날로 제적 처리할 것

@params absent 이번 단위기간중 결석한 횟수
"""
holydays = [
		'2020-11-20',
		'2020-12-24',
		'2020-12-25',
		'2020-12-31',
		'2021-01-01',
		'2021-01-21',
		'2021-01-22',
		'2021-02-10',
		'2021-02-11',
		'2021-02-12',
		'2021-02-26',
		'2021-03-01',
		'2021-03-26',
		'2021-04-21',
		'2021-04-22',
		'2021-04-26',
		'2021-04-27',
		'2021-04-28',
		'2021-04-29',
		'2021-04-30',
	]

def get_absentable_day(absent_cnt):
	def build_block(text, desc, **kwargs):
		block = [
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": f":calendar: |   *{kwargs['month']}월의 결석일 가능일 체크*  | :calendar: "
				}
			},
			{
				"type": "divider"
			},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": f"{text} \n {desc} \n {kwargs['month']}월의 소정훈련일수: {kwargs['workday']}일 \n 결석가능일: {kwargs['workday']*0.2}일 (소정훈련일수 20퍼 이하)"
				},
				"accessory": {
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "플레이데이터 센터 휴일 달력",
						"emoji": True
					},
					"url": "https://www.notion.so/d73c3e16897f4f30b6bfb6217b9ffbde",
					"action_id": "button-action"
				}
			}
		]
		return block


	# 이번 단위기간 소정훈련일수

	this_month = calendar.Calendar()
	today = datetime.today()
	month_range = this_month.itermonthdays2(today.year, today.month)
	work_days = []

	for date, day in list(month_range):
		if date > 0:
			if day != calendar.SATURDAY and day != calendar.SUNDAY:
				str = datetime(today.year, today.month, date).isoformat()[:10]
				if str not in holydays:
					work_days.append(str)

	warn_cnt = len(work_days) * 0.2
	text = f'{warn_cnt}일 이상 무단결석하면 재적 처리됩니다! \n'

	remain = (warn_cnt - int(absent_cnt))
	desc = ''

	if remain > 0:
		desc = f'결석가능일 {remain}일 남음'
	elif remain == 0:
		desc = f'결석가능일 없음'
	elif remain < 0:
		desc = f'결석가능일 {0}일 재적 ㅅㄱ'
	block = build_block(text, desc, workday=len(work_days), month=today.month)

	return block




if __name__ == "__main__":
	# 날씨 이벤트
	# data = get_weather('도봉구')
	# print(data)
	print('bot_events')
