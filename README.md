# slack_bot_hbtn

Slack bot that accepts different commands to get information about holberton projects:

Command: /info/<project_id>:
Will return info about an specific project, for example:

	- PROJECT TITLE
		-Total tasks
		-Mandatory tasks
		-Advanced tasks

Command: /language/<project_id>:
Will return info about an the language to use in a specific project:

	- PROJECT TITLE
		Language: Python

Command: /recheck/<project_id>:
Will recheck all tasks of an specific project and return an answer with
the following structure:

	- PROJECT TITLE
		Number of pendint tasks: XX
		Pendint tasks:
			- Task xx
			- Task xx
			- Task XX

Command: /project/<keyword>:
Will return a list of all projects with the provided keyword:

	- PROJECT THAT CONTAINS <keyword>
		-Project 1
		-Project 2
		-Project 3
		-Project n

The bot requieres an appserver run and redirect slack user requests to your
flask app server, there are some sites that provide such a service for free,
but they have their limitations.
For testing this bot I used ngrok service, feel free to user your favorite
appserver service.

You must create an additional file named .env and place it in the same folder as the bot.py file,
this file must contain the following information:

SLACK_TOKEN=<YOUR SLACK_TOKEN>
SIGNING_SECRET=<YOR SLACK SIGNING_SECRET>

It is intended to keep your personal slack credentials secret and out of your github space.