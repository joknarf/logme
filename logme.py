#!/usr/bin/python
import sys
from subprocess import call
from threading import Thread
from time import sleep
from datetime import datetime
import argparse

class Logmelogger(Thread):
    def __init__(self, logfile):
        Thread.__init__(self)
        self.logfile = logfile
        self.finished = False
        self.exit_code = 0
        open(logfile, 'w').close()

    @staticmethod
    def __timestamp():
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S ')

    def run(self):
        logf = open(self.logfile, 'r')
        log = open('logme.out', 'w')
        new = ""
        while True:
            new += logf.readline()
            if new and new != new.rstrip("\n"):
                log.write(self.__timestamp() + new)
                log.flush()
                new = ""
            else:
                if self.finished:
                    break
                sleep(0.5)
        logf.close()
        log.write(self.__timestamp() + 'exit_code:' + str(self.exit_code) + "\n")
        log.close()

    def finish(self, exit_code):
        self.exit_code = exit_code
        self.finished = True

class Logme():
    def __init__(self, logfile):
        self.logfile = logfile

    def run(self, command):
        logthread = Logmelogger(self.logfile)
        logthread.start()
        cmd = ['/usr/bin/script', '--return', '--flush', '--quiet']
        if command:
            cmd += ['--command', command]
        cmd.append(self.logfile)
        exit_code = call(cmd)
        logthread.finish(exit_code)
        logthread.join()
        return exit_code


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--logfile', '-f', default='typescript')
    parser.add_argument('--command', '-c', default='')
    args = parser.parse_args()
    logjob = Logme(args.logfile)
    exit_code = logjob.run(args.command)
    print('==> logme done')
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
