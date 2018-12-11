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
import csv
from time import sleep
import matplotlib.pyplot as plt
import numpy as np
import datetime
import googleapiclient.errors as errors


def create_message_with_attachment(sender, to, subject, body, file):

  message = MIMEMultipart()
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject

  msg = MIMEText(body)
  message.attach(msg)

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
  elif main_type == 'audio':
    fp = open(file, 'rb')
    msg = MIMEAudio(fp.read(), _subtype=sub_type)
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

def sendEmail(to):

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

    subject = "Song Data from %d/%d" % (lastmonth, lastday)
    body = "Top Ten Songs from yesterday!"
    sender = "HyssMusicTracker@gmail.com"
    filename = "Top10Songs.png"

    message = create_message_with_attachment(sender, to, subject, body, filename)

    send_message(service, message)

def dataOven(num, username):
    scope = 'user-read-recently-played'
    token = util.prompt_for_user_token(username,
                                       scope,
                                       client_id='d59d161a8be9454ca86be7a9270c7a18',
                                       client_secret='ed7384daaa9243c0b4435160d4e138a2',
                                       redirect_uri='http://localhost/')

    sp = spotipy.Spotify(auth=token)
    order = sp._get('me/player/recently-played', limit=num)
    servedData = []
    mainDish = {}
    dessertData = {}
    rawData = order['items']

    for i in range(0, len(rawData)):
        cutData = rawData[i]
        cookedData = cutData['track']

        saltedData = cookedData['artists']
        sweetenedData = saltedData[0]
        caramelizedData = sweetenedData['name']

        preparedData = cookedData['name']

        if preparedData in mainDish:
            mainDish[preparedData][1] += 1
        else:
            mainDish[preparedData] = [caramelizedData, 1]

        if caramelizedData in dessertData:
            dessertData[caramelizedData] += 1
        else:
            dessertData[caramelizedData] = 1

    servedData.append(mainDish)
    servedData.append(dessertData)

    return servedData

def getPlays(iterable):
    return iterable[2]

def makePlot(dictionary):

    inputData = []
    for n in list(dictionary.keys()):
        inputData.append([n, dictionary[n][0], dictionary[n][1]])
    inputData.sort(key=getPlays, reverse=True)

    top10 = []
    top10values = []
    max = 10

    if len(inputData) < 10:
        max = len(inputData)

    for i in range(0, max):
        song = inputData[i][0]
        listens = inputData[i][2]
        top10.append(song)
        top10values.append(listens)
    ticks = np.arange(len(top10))
    plt.figure(figsize=(10, 10))
    plt.barh(ticks, top10values, height=.5)
    plt.yticks(ticks, top10, fontsize=7.5)
    plt.xlabel('Listens')
    plt.title('Top 10 Songs')
    plt.tight_layout()
    plt.savefig('Top10Songs')

def reWriteCSV(dictionary):
    inputData = []
    for n in list(dictionary.keys()):
        inputData.append([n, dictionary[n][0], dictionary[n][1]])
    inputData.sort(key=getPlays, reverse=True)
    csvfile = open('HissData.csv', 'w')
    writer = csv.writer(csvfile)
    header = ['Song', 'Artist', 'Listens']
    writer.writerow(header)
    writer.writerows(inputData)

user = input("Email: ")
username = input("Spotify Username: ")

songTracker = dataOven(50, username)[0]

reWriteCSV(songTracker)

leftOvers = []

masterdict = {}
offset = datetime.timedelta(hours=5)
today = datetime.datetime.today() - offset
day = today.day
month = today.month
masterdict[month] = {}
masterdict[month][day] = songTracker
makePlot(songTracker)
sendEmail(user)

while (True):

    today = datetime.datetime.today() - offset
    day = today.day
    month = today.month

    if month not in masterdict:
        masterdict[month] = {}

    if day not in masterdict[month]:
        masterdict[month][day] = {}
        sendEmail(user)

    plate = dataOven(10, username)

    mainDish = plate[0]
    dessert = plate[1]

    mainMenu = list(mainDish.keys())
    dessertMenu = list(dessert.keys())

    if leftOvers != mainMenu:
        new = mainMenu[0]
        if new in songTracker:
            songTracker[new][1] += 1
        else:
            songTracker[new] = mainDish[new]

        if new in masterdict[month][day]:
            masterdict[month][day][new][1] += 1
        else:
            masterdict[month][day][new] = mainDish[new]

        makePlot(masterdict[month][day])

        print('\n\nRecently Played')

        for i in range(0, len(mainDish)):
            print(mainMenu[i])

        reWriteCSV(songTracker)
    leftOvers = mainMenu

    sleep(30)
