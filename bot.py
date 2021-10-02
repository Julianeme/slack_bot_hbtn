import slack
import os
from pathlib import Path
from dotenv import load_dotenv
import requests
from flask import Flask, Response, request
from slackeventsapi import SlackEventAdapter
from werkzeug.sansio.response import Response
from werkzeug.wrappers import response
from datetime import datetime, timedelta
import requests.auth

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'], '/slack/events', app)
# SIGNING_SECRET secret pass provided by Slack API
# endpoint to deal with the redirections of events from
# ngrok redirect service


client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
# SIGNING_SECRET token provided by Slack API to authentica the api
# This last two variables are stored in the .env file
# so if someone is using this repo make sure you set them as
# provided by Slack API

BOT_ID = client.api_call("auth.test")['user_id']
# getting our bot ID

messages_count = {}
welcome_messages = {}

class WELCOMEMESSAGE:

    START_TEXT = {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            # mrkdwn is kind of what we use in github to make a .md file
            # we will use it -markdonw' to do a welcome file
            'text': (
                'Welcome to this Nerdy Toxic channel!\n\n'
                'Get started by completing the tasks!*'
                # welcome text file
            )
        },
    }

    DIVIDER = {'type': 'divider'}

    def __init__(self, channel, user):
        self.channel = channel
        self.user = user
        self.icon_emoji = ':robot_face:'
        #:text: -> is emoji format
        self.timestamp = ''
        #captures the time the message was sent
        self.completed = False

    def get_message(self):
        """
        defines the final message using the get_reaction_task method
        defines the keywords for chat_postMessage
        """
        return {
            'ts': self.timestamp,
            'channel': self.channel,
            'username': 'JulianemeBOT',
            'icon_emoji': self.icon_emoji,
            'blocks':[
                self.START_TEXT,
                self.DIVIDER,
                self._get_reaction_task()
            ]
        }

    def _get_reaction_task(self):
        checkmark = ':white_check_mark:'
        if not self.completed:
            checkmark = ':white_large_square:'

        text = "{} * React to this message!*".format(checkmark)

        return {'type': 'section', 'text': {'type': 'mrkdwn', 'text': text}}


def send_welcome_message(channel, user):
    welcome = WELCOMEMESSAGE(channel, user)
    message = welcome.get_message()
    respnse = client.chat_postMessage(**message)
    # ** -> is the unpack operator for dictionaries: takes all of the
    # get_message values and re writes them
    welcome.timestamp = response['ts']

    if channel not in welcome_messages:
        welcome_messages[channel] = {}
        # store all the channels we sent the message to
    welcome_messages[channel][user] = welcome
    # for the channels we sent the message to, we will store the recipient users


def schedule_messages(messages):
    """
    The message scheduler
    """
    ids = []
    for msg in messages:
        post_time = float(msg['post_at'])
        int_post = int(post_time)
        response = client.chat_scheduleMessage(channel=msg['channel'], post_at=int_post, text=msg['text'])
        id_ = response.get('id')
        ids.append(id_)
    return ids

@slack_event_adapter.on('message')
def message(payload):
    """
    Method that act as parrot bot, repeating all the users type in the channel
    """
    event = payload.get('event', {})
    # event will give us information about what the event was
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    if user_id != None and BOT_ID != user_id:
        # checking user_id != None prevents the program breaks when we
        # update a message there is technicalla no user for it, is the
        # way slack works
        if user_id in messages_count:
            messages_count[user_id] += 1
        else:
            messages_count[user_id] = 1

        if text.lower() == 'start':
            send_welcome_message('{}'.format(user_id), user_id)

        client.chat_postMessage(channel=channel_id, text=text)
        #conditional so we only reply messages others than our own bot

@app.route('/info', methods=['POST'])
def message_count():
    """
    Method that returns info about a requested holberton project
    """
    data = request.form
    channel_id = data.get("channel_id")
    try:
        req = requests.get(
            'https://intranet.hbtn.io/projects/215.json?auth_token=9df9aa3d2e073bfccb82581176a735dc87844200b78db4d10eb18979709434b7')
        json_req = req.json()
        """if 'status' in json_req:
            print("Not a valid project id")
            continue"""
        title = "---- {} ----\n\nTHIS PROJECT HAS: {} TASKS:".format(
            json_req['name'], len(json_req['tasks']))
        tasks = json_req['tasks']
        mandatory_tasks = 0
        advanced_tasks = 0

        for task in tasks:
            splitted_task = task.get('github_file').split('-')[:1]
            if int(splitted_task[0]) < 100:
                mandatory_tasks += 1
            else:
                advanced_tasks += 1
        tasks_brief = "- {} Mandatory Tasks\n- {} Advanced Tasks\n\n".format(
            mandatory_tasks, advanced_tasks)
        project_message = "{}\n{}\n".format(title, tasks_brief)
        client.chat_postMessage(channel=channel_id, text=project_message)
    except:
        return("Request failed")

    return '', 200



if __name__ == "__main__":
    app.run(debug=True)
