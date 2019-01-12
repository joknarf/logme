#!/usr/bin/python
import sys
from subprocess import call
from threading import Thread
from time import sleep
from datetime import datetime

class Logme( Thread ):
  def __init__( self, logfile ):
    Thread.__init__(self)
    self.logfile = logfile
    self.finished = False
    self.exit_code = 0
    fd = open( logfile, 'w' )
    fd.close()
    
  def __timestamp(self):
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S ')

  def run( self ):
    fd = open( self.logfile, 'r' )
    log = open( 'logme.out', 'w' )
    new = ""
    while True:
      new += fd.readline()
      if new and new != new.rstrip("\n"):
        log.write( self.__timestamp() + new )
        log.flush()
        new = ""
      else:
        if self.finished:
            break
        sleep(0.5)
    fd.close()
    log.write(self.__timestamp() + 'exit_code:' + str(self.exit_code) + "\n")
    log.close()

  def finish( self, exit_code ):
    self.exit_code = exit_code
    self.finished = True

def main():
  logfile = 'typescript'
  logthread = Logme( logfile )
  logthread.start()

  cmd = [ '/usr/bin/script', '--return', '--flush', '--quiet' ]
  if len(sys.argv) == 2:
    cmd += [ '--command', sys.argv[1] ]
  cmd.append( logfile )

  exit_code = call(cmd)

  logthread.finish(exit_code)
  logthread.join()
  print('==> logme done')
  sys.exit(exit_code)

if __name__ == '__main__':
  main()
