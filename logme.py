#!/usr/bin/python3.6 -u
import sys
from subprocess import call
from threading import Thread
from time import sleep

class Logme( Thread ):
  def __init__( self, logfile ):
    Thread.__init__(self)
    self.logfile = logfile
    self.finished = False
    self.exit_code = 0
    fd = open( logfile, 'w' )
    fd.close()
    
  def run( self ):
    fd = open( self.logfile, 'r' )
    log = open( 'logme.out', 'w' )
    new = ""
    while True:
      new += fd.readline()
      if new and new != new.rstrip("\n"):
        log.write( new )
        log.flush()
        new = ""
      else:
        if self.finished:
            break
        sleep(0.5)
    fd.close()
    log.write(f"log:exit_code:{self.exit_code}\n")
    log.close()

  def finish( self, exit_code ):
    self.exit_code = exit_code
    self.finished = True

logthread = Logme( 'typescript' )
logthread.start()
opt = ''
if len(sys.argv) == 2:
  opt = f"-c '{sys.argv[1]}'"
exit_code = call(f"script -e -f {opt}",shell=True)
logthread.finish(exit_code)
logthread.join()
print('done')
exit(exit_code)
