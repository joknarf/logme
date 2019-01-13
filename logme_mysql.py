#!/usr/bin/python
import sys
from subprocess import call, Popen, PIPE
from threading import Thread
from time import sleep
from datetime import datetime
import argparse

class Logmelogger(Thread):
    """In a thread continously read a log file to send to a log facility"""
    MYSQL=['/usr/bin/mysql', '-Bsu', 'joknarf', '-D', 'logme']

    def __init__(self, logfile):
        Thread.__init__(self)
        self.finished = False
        self.logread = open(logfile, 'r')
        self.logid = ""
        self.logme = None
        self.logopen()

    @staticmethod
    def __timestamp():
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S ')

    def logconnect(self):
        self.logme = Popen(Logmelogger.MYSQL, stdin=PIPE, stdout=PIPE)

    def logopen(self):
        """open log facility """
        sql = "insert into log set log_text='';select last_insert_id()"
        self.logid = Popen(Logmelogger.MYSQL + ['-e', sql], stdout=PIPE).communicate()[0].rstrip('\n')
        self.logconnect()

    def logwrite(self, line):
        """write to log facility """
        sql = b"update log set log_text=concat(log_text,'" + self.__timestamp() + line + "') where log_id=" + self.logid +";\n"
        self.logme.stdin.write(sql)
        self.logme.stdin.flush()
        return True

    def logclose(self):
        """close log facility """
        self.logme.stdin.close()
        self.logme.wait()

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

    def stop(self):
        self.finished = True

class Logme():
    """
        A class to run command with script to get logged output
        Send the log to a log facility
    """
    def __init__(self, logfile='/var/tmp/logme.log'):
        self.logfile = logfile
        open(logfile, 'w').close()
        self.logthread = Logmelogger(self.logfile)
        self.logthread.start()

    def logwrite(self, line):
        logf = open(self.logfile, 'a')
        logf.write(line + "\n")
        logf.close()
        
    def run(self, command):
        self.logwrite('Starting command: ' + command)
        cmd = ['/usr/bin/script', '--return', '--flush', '--quiet', '--append']
        if command:
            cmd += ['--command', command]
        cmd.append(self.logfile)
        exit_code = call(cmd)
        self.logwrite('End of command: ' + command + ' : exit code: ' + str(exit_code) + "\n")
        return exit_code

    def close(self):
        self.logthread.stop()
        self.logthread.join()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--logfile', '-f', default='/var/tmp/logme.log')
    parser.add_argument('--command', '-c', default='')
    args = parser.parse_args()
    logjob = Logme(args.logfile)
    exit_code = logjob.run(args.command)
    logjob.close()
    print('==> logme done')
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
