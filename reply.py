import bot_events
print(bot_events)

"""
	명령어와 질의어를 구분한다.
"""


def detect_event(str):
    if '/' not in str:
        print('명령어가 /으로  시작하지않음')
        return False
    else:
        real_message = str.split('/')[1:][0]
        print(f'real_message: {real_message}')

        c_command = real_message.split(' ')[0]
        value = ' '.join(real_message.split(' ')[1:])
        print(f'c_command: {c_command} value: {value}')
        return c_command, value


"""
	명령에 대한 이벤트를 등록한다.
"""


def send_reply(client, value):
    event_data = value
    message = event_data["event"]
    try:
        if message.get("subtype") is None:
            command = message.get("text").lower()
            channel_id = message["channel"]
            c_command, value = detect_event(command)
            print(f'c_command: {c_command}, value: {value}')
            if c_command == 'help':
                blocks = bot_events.get_bot_doc()

                client.chat_postMessage(
                    channel=channel_id,
                    blocks=blocks
                )
            elif c_command == '날씨':
                attachments = bot_events.get_weather(value)

                client.chat_postMessage(
                    channel=channel_id,
                    attachments=attachments
                )
            elif c_command == '결석':
                blocks = bot_events.get_absentable_day(value)

                client.chat_postMessage(
                    channel=channel_id,
                    blocks=blocks
                )
            elif c_command == '블로그':
                blocks = bot_events.get_post()
                client.chat_postMessage(
                    channel=channel_id,
                    blocks=blocks
                )
            else:
                client.chat_postMessage(
                    channel=channel_id,
                    blocks=[{
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": ":warning: *존재하지 않는 명령어입니다!*"
                        }
                    }]
                )
    except:
        channel_id = message["channel"]
        client.chat_postMessage(
            channel=channel_id,
            blocks=[{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":no_entry_sign: *오류가 발생했습니다. 만든이에게 문의해주세요*"
                    }
                }]
        )
