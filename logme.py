#!/usr/bin/python
import sys
from subprocess import call
from threading import Thread
from time import sleep
from datetime import datetime
import argparse

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
  parser = argparse.ArgumentParser()
  parser.add_argument( '--logfile', '-f', default='typescript' )
  parser.add_argument( '--command', '-c', default='' )
  args = parser.parse_args()
  logthread = Logme( args.logfile )
  logthread.start()

  cmd = [ '/usr/bin/script', '--return', '--flush', '--quiet' ]
  if args.command:
    cmd += [ '--command', args.command ]
  cmd.append( args.logfile )

  exit_code = call(cmd)

  logthread.finish(exit_code)
  logthread.join()
  print('==> logme done')
  sys.exit(exit_code)

if __name__ == '__main__':
  main()
