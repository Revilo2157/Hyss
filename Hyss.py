
from __future__ import print_function
import datetime
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import mimetypes
import os
import base64
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import spotipy
import spotipy.util as util
from time import sleep
import matplotlib.pyplot as plt
import numpy as np
import datetime
import googleapiclient.errors as errors
import pickle
from collections import Counter
from spotipy import oauth2 as auth

def create_message_with_attachment(sender, to, subject, body, file = ""):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(body)
    message.attach(msg)

    if file != "":
        content_type, encoding = mimetypes.guess_type(file)
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'text':
            fp = open(file, 'rb')
            msg = MIMEText(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'image':
            fp = open(file, 'rb')
            msg = MIMEImage(fp.read(), _subtype=sub_type)
            fp.close()
        else:
            fp = open(file, 'rb')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            fp.close()

        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

def send_message(service, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """

  try:
    message = (service.users().messages().send(userId="me", body=message)
               .execute())
    print('Message Id: %s' % message['id'])
    return message
  except errors.HttpError as error :
    print('An error occurred: %s' % error)

def sendVerif(to):

    SCOPES = 'https://www.googleapis.com/auth/gmail.send'
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    subject = "You\'re all set!"
    body = "Your Hyss Music Tracker is ready to start logging your music!"
    sender = "HyssMusicTracker@gmail.com"

    message = create_message_with_attachment(sender, to, subject, body)

    send_message(service, message)

def sendEmail(to, which = 0):

    SCOPES = 'https://www.googleapis.com/auth/gmail.send'
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    delta = datetime.timedelta(days=1)
    yesterday = datetime.datetime.today() - delta
    lastmonth = yesterday.month
    lastday = yesterday.day

    if which == 1:
        subject = "Song Data from %s" % (yesterday.strftime("%B"))
        body = "Top Ten Songs from %s!" % (yesterday.strftime("%B"))
        filename = "Top10Monthly.png"
    elif which == 2:
        lastWeek = today - datetime.timedelta(days=7)
        subject = "Song Data from %s to %s" % (lastWeek.strftime("%D") , yesterday.strftime("%D"))
        body = "Top Ten Songs from %s to %s!" % (lastWeek.strftime("%D") , yesterday.strftime("%D"))
        filename = "Top10Weekly.png"
    else:
        subject = "Song Data from %d/%d" % (lastmonth, lastday)
        body = "Top Ten Songs from yesterday!"
        filename = "Top10Songs.png"
    sender = "HyssMusicTracker@gmail.com"

    message = create_message_with_attachment(sender, to, subject, body, filename)

    send_message(service, message)

def dataOven(num, username):
    scope = 'user-read-recently-played'
    client_id = 'd59d161a8be9454ca86be7a9270c7a18'
    client_secret = 'ed7384daaa9243c0b4435160d4e138a2'
    redirect_uri = 'http://localhost/'

    token = util.prompt_for_user_token(username,
                                       scope=scope,
                                       client_id=client_id,
                                       client_secret=client_secret,
                                       redirect_uri=redirect_uri)

    sp = spotipy.Spotify(auth=token)
    while(True):
        try:
            order = sp._get('me/player/recently-played', limit=num)
            break
        except:
            sp_oauth = auth.SpotifyOAuth(client_id, client_secret, redirect_uri,
                                           scope=scope, cache_path=".cache-" + username)
            token = sp_oauth.get_cached_token()["access_token"]
            sp = spotipy.Spotify(auth=token)
            print("Token Expired. Retrying...")

    songs = []
    rawData = order['items']

    for i in range(0, len(rawData)):
        songData = rawData[i]
        songInfo = songData['track']

        artistInfo = songInfo['artists']
        nameLoc = artistInfo[0]
        artist = nameLoc['name']
        songName = songInfo['name']

        songs.append((songName, artist))

    return songs

def getPlays(iterable):
    return iterable[1]

def makePlot(dictionary, which = 0):

    inputData = []
    for n in list(dictionary.keys()):
        inputData.append([n, dictionary[n]])
    inputData.sort(key=getPlays, reverse=True)

    top10 = []
    top10values = []
    numSongs = 10

    if len(inputData) < 10:
        numSongs = len(inputData)

    for i in range(0, numSongs):
        song = inputData[i][0]
        listens = inputData[i][1]
        top10.append(song)
        top10values.append(listens)
    ticks = np.arange(len(top10))
    print(top10)
    plt.figure(figsize=(10, 10))
    plt.barh(ticks, top10values, height=.5)
    plt.yticks(ticks, top10, fontsize=7.5)
    plt.xticks(np.arange(0, max(top10values), step=1))
    plt.xlabel('Listens')
    plt.title('Top 10 Songs')
    plt.tight_layout()

    if which == 1:
        plt.savefig('Top10Monthly')
    elif which == 2:
        plt.savefig('Top10Weekly')
    else:
        plt.savefig('Top10Songs')


today = datetime.datetime.today()
day = today.day
month = today.month

try:
    f = open("HyssData", "rb")
    info = pickle.load(f)
    f.close()
    masterdict = info[0]
    user = info[1]
    username = info[2]
    flag = 1
    try:
        songTracker = masterdict[month][day]
    except:
        songTracker = {}
    print("Logging Resumed")

except:
    masterdict = {}
    user = input("Email: ")
    username = input("Spotify Username: ")
    flag = 0
    songTracker = {}

    with open("HyssData", "wb") as newFile:
        pickle.dump([masterdict, user, username], newFile)

    print("Welcome!")

leftOvers = dataOven(10, username)
delta = datetime.timedelta(days=1)

while (True):

    today = datetime.datetime.today()
    day = today.day
    month = today.month

    if month not in masterdict:
        if masterdict:
            yesterday = today - delta
            lastMonth = yesterday.month

            if lastMonth in masterdict:
                masterdict[lastMonth]["Total"] = Counter(songTracker)

                for n in list(masterdict[lastMonth].keys()):
                    if n == "Total":
                        continue
                    toAdd = Counter(masterdict[lastMonth][n])
                    masterdict[lastMonth]["Total"] = Counter(masterdict[lastMonth]["Total"]) + toAdd

                makePlot(masterdict[lastMonth]["Total"], 1)
                sendEmail(user, 1)

        masterdict[month] = {}

    if day not in masterdict[month]:
        songTracker = {}
        if flag == 1:
            yesterday = today - delta
            #if masterdict[yesterday.month]:
                # try:
                #     makePlot(masterdict[yesterday.month][yesterday.day])
                #     sendEmail(user)
                # except:
                #     pass

            if today.weekday() == 6:
                weekData = {}
                for n in range(1, 8):
                    week = today - datetime.timedelta(days=n)
                    weekMonth = week.month
                    weekDay = week.day
                    try:
                        weekData = Counter(weekData) + Counter(masterdict[weekMonth][weekDay])
                    except:
                        pass

                try:
                    makePlot(weekData, 2)
                    sendEmail(user, 2)
                except:
                    pass

        masterdict[month][day] = {}
        f = open("HyssData", "wb")
        pickle.dump([masterdict, user, username], f)
        f.close()

    current = dataOven(50, username)

    if leftOvers != current:
        index = len(current) - 1
        for n in range(0, len(current)):
            if n <= (len(current) - 3):
                if (current[n] == leftOvers[0] and
                        current[n + 1] == leftOvers[1] and
                        current[n + 2] == leftOvers[2]):
                    index = n
                    break
            elif n <= (len(current) - 2):
                if (current[n] == leftOvers[0] and
                        current[n + 1] == leftOvers[1]):
                    index = n
                    break
            else:
                if current[n] == leftOvers[0]:
                    index = n
                    break

        for i in range(0, index):
            song = current[i][0]
            if song not in songTracker:
                songTracker[song] = 1
            else:
                songTracker[song] += 1

        masterdict[month][day] = songTracker
        f = open("HyssData", "wb")
        pickle.dump([masterdict, user, username], f)
        f.close()

        # print('\n\nRecently Played')
        # for n in current:
        #     print(n[0])

    leftOvers = current

    if flag != 1:
        print("Sending Confirmation...")
        sendVerif(user)
        print("Sent.")
        flag = 1

    sleep(5)
