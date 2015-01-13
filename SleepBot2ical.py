# -*- coding: utf-8 -*-
# script by Ludovic Lacoste <ludolacost@gmail.com>

from datetime import datetime, timedelta

def readSB(f):
    import csv
    dialect = csv.Sniffer().sniff(f.read(256))
    f.seek(0)
    return csv.DictReader(f, dialect = dialect)

def new2oldref(sleep):
    ret = {}
    ret['Date'] = datetime.strptime(sleep['Date'], '%d/%m/%y').strftime('%d-%m-%Y')
    ret['Sleep Time'] = sleep[' Sleep Time']
    ret['Awake Time'] = sleep[' Wake Time']
    tmp = float(sleep[' Hours'])
    h = int(tmp)
    tmp -= h
    m = int(tmp * 60)
    ret['Duration'] = '{0:02} hr {1:02} min'.format(h, m)
    ret['Rating'] = sleep['Note']
#    print 'ret', ret
    return ret

def sleep2dates(sleep):
    duration = datetime.strptime(sleep['Duration'], '%H hr %M min')
    duration = timedelta(hours=duration.hour, minutes=duration.minute)
    # the Date field corresponds to the day you awake
    sleep_stop = datetime.strptime(sleep['Date'] + ' ' + sleep['Awake Time'], '%d-%m-%Y %H:%M')
    # trick to compute the start of the sleep
    sleep_start = sleep_stop - duration
#    print sleep
#    print 'duration', duration
#    print 'sleep_start ', sleep_start
#    print 'sleep_stop  ', sleep_stop
    return [sleep_start, sleep_stop]

def writeIcal(sleeps, f, fmt='Sleeping...zzZzz'):
    from icalendar import Calendar, Event
    import md5

    cal = Calendar()
    cal.add('prodid', '-//SleepBot Calendar//LUDO6431//FR')
    cal.add('version', '2.0')
    
    for sleep in sleeps:
        event = Event()
        try:
            dts = sleep2dates(sleep)
            event.add('summary', fmt.format(**sleep))
        except KeyError:
            sleep = new2oldref(sleep)
            dts = sleep2dates(sleep)
            event.add('summary', fmt.format(**sleep))
        event.add('dtstart', dts[0])
        event.add('dtend', dts[1])
        event['uid'] = md5.new(str(dts[0])+'SleepBot'+str(dts[1])).hexdigest()+'@mysleepbot.com'

        cal.add_component(event)

    f.write(cal.to_ical())

if __name__ == "__main__":
    import sys

    csvfile = open(sys.argv[1], 'rb')
    icalfile = open(sys.argv[2], 'wb')

    sleeps = readSB(csvfile) # <sleeps> can be iterated only once as-is

    writeIcal(sleeps, icalfile, '{Duration} de sommeil')

