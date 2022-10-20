# -*- coding: utf-8 -*-

"""Simple Bot to send timed Telegram messages.
# This program is dedicated to the public domain under the CC0 license.
This Bot uses the Updater class to handle the bot and the JobQueue to send
timed messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import telebot
import imgkit
import requests
import sqlite3

key = ''
#273770462

league_name = 'mega'

app = telebot.TeleBot(key)

def getWeek(cmd, url, options):
    #config = imgkit.config(wkhtmltoimage='/usr/local/bin/wkhtmltoimage')
    config = imgkit.config(wkhtmltoimage='/usr/bin/wkhtmltoimage')


    imgkit.from_url(url, cmd+'.png', options=options, config=config)

def sendPick(name, chat_dest):
    url = "https://api.telegram.org/bot" + key + "/sendPhoto"
    files = {'photo': open(name + '.png', 'rb')}
    data = {'chat_id': chat_dest}
    requests.post(url, files=files, data=data)


@app.route('/week')
def week(message):
    week_num(message, '')

@app.route('/week ?(\\d+)')
def week_num(message, cmd):
    chat_dest = message['chat']['id']
    url = f'http://www.daddyleagues.com/{league_name}/schedules'
    msg = "Starting: week " + cmd
    app.send_message(chat_dest, msg)
    options = {
        'crop-y': 400,
        'crop-h': 2800,
        'quality': 50,
        'height': 3000,
        'width': 1250
    }

    getWeek('week' + cmd, url+'/'+cmd, options)


    sendPick('week' + cmd, chat_dest)

@app.route('/res')
def res(message):
    chat_dest = message['chat']['id']
    url = f'http://www.daddyleagues.com/{league_name}/gamerecap/548877212'
    msg = "Starting: result 1.312"
    app.send_message(chat_dest, msg)
    options = {
      'crop-x': 450,
      'crop-y': 200,
      'quality': 100,
      'height': 500,
      'width': 2400,
      'javascript-delay': 1000,
        'run-script' : [
            "javascript:\$(function() { document.querySelector('.nav.nav-tabs > li:nth-child(2) > a').dispatchEvent(new  MouseEvent('click', {bubbles: true,cancelable: true,view: window}))})"
        ]


}



    sendPick('res', chat_dest)


@app.route('/who ?(.*)')
def team_owner(message, cmd):
    chat_dest = message['chat']['id']

    item = c.execute(u"select owner from owners where team like '"+cmd+"'").fetchone()
    msg = "For " + cmd + " " + str(item)
    app.send_message(chat_dest, msg.encode('utf-8'))

@app.route('/setTeam ?([A-z]+) ?(.*)')
def team_owner(message, team, owner):
    chat_dest = message['chat']['id']

    c.execute(u'update owners set owner=? where team =?', (owner.encode('utf-8'),team))
    msg = "For " + team + " new owner is " + owner
    conn.commit()
    app.send_message(chat_dest, msg)

if __name__ == '__main__':
    app.config['api_key'] = key
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS owners (team, owner)')
    c.execute('CREATE TABLE IF NOT EXISTS data (key, value)')
    app.poll(debug=True)
