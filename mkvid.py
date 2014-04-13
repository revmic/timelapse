#!/usr/bin/env python
from datetime import datetime, timedelta
from webapp import connect_db
import ConfigParser
import smtplib
import socket
import envoy
import time
import os
# optparse - verbose output

'''
Makes a video for specified interval using encode.sh and creates DB reference.
Runs hourly via cron.
'''

# cwd when called form cron ???
SCRIPTDIR = '/home/michael/Development/timelapse'
VIDDIR = '/media/ww/vids'
now = datetime.now()

config = ConfigParser.ConfigParser()
config.read("/home/michael/.timelapse.cfg")

def encode(datetime_str, interval_param):
    if interval_param == 'week':
        return
    else:
        cmd = "%s/bin/encode.sh -%s %s" % \
            (SCRIPTDIR, interval_param[0], datetime_str)

    print cmd
    p = envoy.run(cmd)
    print "Status code: ", p.status_code

    # if status OK, add to DB
    if p.status_code == 0:
        db_insert(datetime_str, interval_param)
    else:
        email("Timelapse - Encode Failure", "Encoding failed.")

def db_insert(dt, interval):
    db = connect_db()
    #TODO - check for this filename's existence in DB

    timestamp = datetime.now().strftime("%Y%m%d%H%M%s")
    fpath = '%s/%s/%s.avi' % (VIDDIR, interval, dt)
    fsize = os.stat(fpath).st_size
    #TODO - prettier tile e.g. March 1, 2014
    COLUMNS = "(title, filename, fullpath, interval, datetimestamp, notable, size)"
    VALUES = "('%s', '%s.avi', '%s', '%s', '%s', 0, '%s')" % \
              (dt, dt, fpath, interval, timestamp, fsize)
    query = "insert into tl_videos %s values %s" % (COLUMNS, VALUES)
    db.execute(query)
    db.commit()
    db.close()

    # Restart system if video size is below threshold
    if interval == 'hour' and fsize < 5000000:
        print "Video size less than 5 MB which likely indicates a problem. Restarting system."
        email("Timelapse - Restarting Server",
            "The video " + os.path.basename(fpath) + " was only " + str(fsize) + " bytes. " + \
            "This likely indicates a problem with the capture device over the past hour. " + \
            "Restarting " + socket.gethostname())
        time.sleep(10)
        envoy.run("sudo reboot")

def email(subject, message):
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    recipients = 'mhilema@gmail.com'
    sender = 'mhilema@gmail.com'
    headers = ["From: " + sender,"Subject: " + subject,"To: " + recipients]
    headers = "\r\n".join(headers)
    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    session.ehlo()
    session.starttls()
    session.ehlo
    session.login(sender, config.get("email", "password"))
    session.sendmail(sender, recipients, headers+"\r\n\r\n"+message)

def mkvid():
    # Always run hourly for previous hour
    hour_ago = now - timedelta(hours=1)
    encode(hour_ago.strftime("%Y%m%d%H"), 'hour')

    ## Test system recovery
    #encode("2014041000", 'hour')

    # if 1 AM, run for previous day
    if now.hour == 1:
        day_ago = now - timedelta(days=1)
        encode(day_ago.strftime("%Y%m%d"), 'day')

    # if Monday, run for previous week
    if now.weekday() == 0:
        week_ago = now - timedelta(weeks=1)
        encode(week_ago.strftime("%Y%m%d"), 'week')

    # if 1st of month, run for previous month
    if now.day == 1 and now.hour == 2:
        day_ago = now - timedelta(days=1)
        month_ago = "%d%02d" % (day_ago.year, day_ago.month)
        encode(month_ago, 'month')

    # if 1st of Jan, run for previous year
    if now.day == 1 and now.month == 1 and now.hour == 3:
        year_ago = str(now.year-1)
        encode (year_ago, 'year')

if __name__ == "__main__":
    mkvid()
