#!/usr/bin/env python
#coding: utf-8

"""
Break Reminder
@author dong <ddliuhb@gmail.com>
@version 0.1
@license MIT License
"""

import pynotify
#import threading
import os.path
import time
import subprocess
import sys

class WorkManager:
    points = []
    def __init__(self, startwork = True):
        self.starttime = int(time.time())
        self.endtime = 0
        if startwork:
            self.work()
        else:
            self.rest()

    def work(self):
        self.points.append([True, int(time.time())])

    def rest(self):
        self.points.append([False, int(time.time())])

    def end(self):
        self.endtime = int(time.time())

    def getEndTime(self):
        if self.endtime > 0:
            return self.endtime
        else:
            return int(time.time())

    def getTotalTime(self):
        return self.getEndTime() - self.starttime

    def getTotalWorkTime(self):
        total = 0
        for index, (status, timestamp) in enumerate(self.points):
            if not status and index > 0:
                total = total + timestamp - self.points[index-1][1]

        status, timestamp = self.points[-1]
        if status:
            total = total + self.getEndTime() - timestamp

        return total

    def getTotalRestTime(self):
        total = 0
        for index, (status, timestamp) in enumerate(self.points):
            if status and index > 0:
                total = total + timestamp - self.points[index-1][1]

        status, timestamp = self.points[-1]
        if not status:
            total = total + self.getEndTime() - timestamp

        return total

    def isWorking(self):
        return self.points[-1][0]

    def isRest(self):
        return not self.isWorking()

    def getLastWorkingOrRestTime(self):
        return self.getEndTime() - self.points[-1][1]

    def getPrevWorkingAndRestTime(self):
        if self.isWorking():
            if len(self.points) < 3:
                return None
            return self.points[-2][1] - self.points[-3][1], self.points[-1][1] - self.points[-2][1]
        else:
            if len(self.points) < 2:
                return None
            return self.points[-1][1] - self.points[-2][1], self.getLastWorkingOrRestTime() - self.points[-1][1]


class BreakReminder:
    NAME = "Break Reminder"
    VERSION = "0.1"
    LOOP_FREQ = 3
    last_remind = None
    options = {
        'rest_freq': 30*60,
        'rest_time': 5*60,
        'remind_limit': 60,
        'autolock': True,
        'autolock_delay': 3
    }

    ICONS = {
        'take-rest': 'coffee-black.png',
        'rest-none-enough': 'exclamation-circle.png'
    }

    def __init__(self, options = None):
        if options is not None:
            self.options.update(options)
        self.workmanager = WorkManager()
        self.locked = self.isScreenLocked()

    def onLock(self):
        print "screen locked"
        self.workmanager.rest()

    def onUnlock(self):
        print "screen unlocked"
        self.workmanager.work()
        t = self.workmanager.getPrevWorkingAndRestTime()
        if t is not None:
            working_time, rest_time = t
            if working_time >= self.options['rest_freq'] and rest_time < self.options['rest_time']:
                self.notify('You didn\'t take enough rest', '%s is not enough' % format_seconds(rest_time), 'rest-none-enough')

    def lockScreen(self):
        subprocess.Popen(['gnome-screensaver-command', '-l'])

    def isScreenLocked(self):
        proc = subprocess.Popen(['gnome-screensaver-command', '-q'], stdout=subprocess.PIPE)
        (out, err) = proc.communicate()

        return 'inactive' not in out

    def notify(self, title, message, icon):
        """
        icon: take-rest, rest-none-enough
        """
        if self.ICONS.has_key(icon):
            icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', self.ICONS[icon])
        pynotify.init("breakreminder")
        n = pynotify.Notification(title, message, icon)
        n.show()

    def needRemind(self):
        return \
            self.workmanager.isWorking() \
            and ( \
                not self.last_remind \
                or \
                (int(time.time()) - self.last_remind > self.options['remind_limit']) \
            ) \
            and self.workmanager.getLastWorkingOrRestTime() >= self.options['rest_freq']

    def loop(self):
        sys.stdout.write('.')
        sys.stdout.flush()
        if(self.locked != self.isScreenLocked()):
            self.locked = not self.locked
            if(self.locked):
                self.onLock()
            else:
                self.onUnlock()

        if self.needRemind():
            title = "Take a rest"
            message = "You have been working for %s" % format_seconds(self.workmanager.getLastWorkingOrRestTime())
            if self.options['autolock']:
                message = message + "，screen will be locked in %s" % format_seconds(self.options['autolock_delay'])

            self.notify(title, message, 'take-rest')
            self.last_remind = int(time.time())
            print "\n Notification sent"

            # lock screen
            if self.options['autolock']:
                if(self.options['autolock_delay']):
                    time.sleep(self.options['autolock_delay'])
                self.lockScreen()
                self.locked = True
                self.onLock()

    def run(self):
        print "%s v%s" % (self.NAME, self.VERSION)
        while(True):
            self.loop()
            time.sleep(self.LOOP_FREQ)

    def stop(self):
        #raw_input("press ")
        pass

def format_seconds(seconds):
    hours = seconds / 3600
    seconds = seconds % 3600

    minutes = seconds / 60
    seconds = seconds % 60

    s = []
    if hours:
        s.append('%d hours' % hours)
    if minutes:
        s.append('%d minutes' % minutes)
    if seconds:
        s.append('%d seconds' % seconds)

    if not s:
        return 'no time'
    return ' '.join(s)

if __name__ == '__main__':
    config_test = {
        'remind_limit': 60,
        'rest_freq': 10,
        'autolock': True,
        'rest_time': 30,
    }
    config_default = {
    }
    m = BreakReminder('-t' in sys.argv[1:] and config_test or config_default)
    m.run()