#!/usr/bin/env python
from datetime import datetime, timedelta
from webapp import connect_db
import envoy
import os
# email
# optparse - verbose output

'''
Makes a video for specified interval using encode.sh and creates DB reference.
Runs hourly via cron.
'''

# cwd when called form cron ???
SCRIPTDIR = '/home/michael/Development/timelapse'
VIDDIR = '/media/ww/vids'
now = datetime.now()

def mkvid(datetime_str, interval_param):
    if interval_param == 'week':
        pass
    else:
        cmd = "%s/bin/encode.sh -%s %s" % \
            (SCRIPTDIR, interval_param[0], datetime_str)

    print cmd
    p = envoy.run(cmd)
    print "Status code: ", p.status_code

    # if status OK, add to DB
    if p.status_code == 0:
        db_insert(datetime_str, interval_param)
    # else, email

def db_insert(dt, interval):
    db = connect_db()
    #TODO - check for this filename's existence in DB

    timestamp = datetime.now().strftime("%Y%m%d%H%M%s")
    fpath = '%s/%s/%s.avi' % (VIDDIR, interval, dt)
    fsize = os.stat(fpath).st_size
    #TODO - prettier tile e.g. March 1, 2014
    COLUMNS = "(title, filename, fullpath, datetimestamp, notable, size)"
    VALUES = "('%s', '%s.avi', '%s', '%s', 0, '%s')" % \
              (dt, dt, fpath, timestamp, fsize)
    query = "insert into tl_videos %s values %s" % (COLUMNS, VALUES)
    db.execute(query)
    db.commit()
    db.close()

def email():
    pass

def encode():
    # Always run hourly for previous hour
    hour_ago = now - timedelta(hours=1)
    mkvid(hour_ago.strftime("%Y%m%d%H"), 'hour')

    # if 1 AM, run for previous day
    if now.hour == 1:
        day_ago = now - timedelta(days=1)
        mkvid(day_ago.strftime("%Y%m%d"), 'day')

    # if Monday, run for previous week
    if now.weekday() == 0:
        week_ago = now - timedelta(weeks=1)
        mkvid(week_ago.strftime("%Y%m%d"), 'week')

    # if 1st of month, run for previous month
    if now.day == 1:
        month_ago = now - timedelta(months=1)
        mkvid(month_ago.strftime("%Y%m"), 'month')

    # if 1st of Jan, run for previous year
    if now.day == 1 and now.month == 1:
        year_ago = now.year - 1
        cmd = SCRIPTDIR + '/bin/encode.sh -y ' + str(year_ago)
        p = envoy.run(cmd)

if __name__ == "__main__":
    encode()
