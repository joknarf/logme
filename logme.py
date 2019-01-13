#!/usr/bin/python
import sys
from subprocess import call
from threading import Thread
from time import sleep
from datetime import datetime
import argparse

class Logmelogger(Thread):
    """In a thread continously read a log file to send to a log facility"""
    def __init__(self, logfile):
        Thread.__init__(self)
        self.finished = False
        self.logread = open(logfile, 'r')
        self.logme = self.logopen()

    @staticmethod
    def __timestamp():
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S ')

    @staticmethod
    def logopen():
        """open log facility """
        return open('logme.out', 'w')

    def logwrite(self, line):
        """write to log facility """
        self.logme.write(self.__timestamp() + line)
        self.logme.flush()
        return True

    def logclose(self):
        """close log facility """
        self.logme.close()

    def run(self):
        new = ""
        while True:
            new += self.logread.readline()
            if new and new != new.rstrip("\n"):
                if self.logwrite(new):
                    new = ""
            else:
                if self.finished:
                    break
                sleep(0.5)
        self.logread.close()
        self.logclose()

    def finish(self):
        self.finished = True

class Logme():
    """
        A class to run command with script to get logged output
        Send the log to a log facility
    """
    def __init__(self, logfile):
        self.logfile = logfile
        open(logfile, 'w').close()
        self.logthread = Logmelogger(self.logfile)
        self.logthread.start()

    def run(self, command):
        logf = open(self.logfile, 'a')
        logf.write('Starting command: ' + command + "\n")
        logf.close()
        cmd = ['/usr/bin/script', '--return', '--flush', '--quiet', '--append']
        if command:
            cmd += ['--command', command]
        cmd.append(self.logfile)
        exit_code = call(cmd)
        logf = open(self.logfile, 'a')
        logf.write('End of command: ' + command + ' : exit code: ' + str(exit_code) + "\n")
        logf.close()
        return exit_code

    def close(self):
        self.logthread.finish()
        self.logthread.join()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--logfile', '-f', default='typescript')
    parser.add_argument('--command', '-c', default='')
    args = parser.parse_args()
    logjob = Logme(args.logfile)
    exit_code = logjob.run(args.command)
    logjob.close()
    print('==> logme done')
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
