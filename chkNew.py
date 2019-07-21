#!/usr/bin/env python

import six, requests, re, sys, os, string, getopt, argparse
from datetime import datetime 
if six.PY3:
    from html.parser import HTMLParser
else:
    from HTMLParser import HTMLParser

class MyHTMLParser( HTMLParser):
  def __init__( self):
    self.step = 0
    self.time = ''
    self.station = ''
    self.name = ''
    self.broadcasts = []             # simple list will suffice for a few items
    HTMLParser.__init__( self)


  def handle_starttag( self, tag, attrs):
    if tag == 'h2':
        self.step = 1

    # for all tags, examine the attributes and values and collect the
    # relevant ones
    #
    for n in range( 0, len( attrs)):
        attr  = attrs[n][0]
        value = attrs[n][1]
        if self.step == 2 and attr == 'datatype':
            self.step = 3
        elif self.step == 3:
            self.time = value
            self.step = 4
        elif self.step == 4 and attr == 'href':
            self.station = re.sub( '.*/', '', value, 1)
            self.step = 5


  def handle_data( self, data):
    if self.step == 1:
        if data == 'Broadcasts':
            self.step = 2
        else:
            self.step = 0      # wait for our <h2>
    elif self.step == 5:
        self.name = data
        self.step = 6


  def handle_endtag( self, tag):
    if self.step == 6 and tag == 'li':
        if ourStation == '' or self.station == ourStation:
            broadcast = (self.time, self.station, self.name)
            self.broadcasts.append( broadcast)
        self.step = 2
    elif self.step == 2 and tag == 'ul':
        for n in range( 0, len( self.broadcasts)):
            broadcast = self.broadcasts.pop( len( self.broadcasts) - 1)
            (time, station, name) = broadcast
            time = re.sub( ':00\+0[01]:00', '', time, 1)
            if time < ourTime:
                time = datetime.strptime( time, '%Y-%m-%dT%H:%M')
                six.print_( time.strftime( '%a %d %b %Y %H:%M'), end='')
                if ourStation:
                    six.print_()
                else:
                    six.print_( ' -', name)
                exit( 1)             # a repeat
        exit( 0)                     # repeats - but none met our criteria


def errorMessage( message):
  sys.stderr.write( NAME + ': ' + message + '\n')


def usage():
  sys.stderr.write( 'Usage: ' + USAGE + '\n\n' + \
      'Options:\n' + \
      '   -h, --help          show this help and exit\n' + \
      '   -s, --station       look for repeats only on specified station\n')
  exit( 2)


def getArgs():

  global NAME, USAGE, url, ourStation, ourTime

  class HelpAction( argparse.Action):
      # I don't like the (verbose) (GNU) standard help
      #
      def __call__( self, parser, namespace, values, option_string=None):
          usage()
          parser.exit()

  NAME = os.path.basename( sys.argv[0])
  USAGE = NAME + ' [-h] [-s station] [url/]pid [yyyy/mm/dd-hh:mm]'

  parser = argparse.ArgumentParser( usage=USAGE, add_help=False)
  parser.add_argument( '-h', '--help', nargs=0, action=HelpAction)
  parser.add_argument( '-s', '--station', type=str)
  parser.add_argument( 'pid')
  parser.add_argument( 'time', nargs='?')
  args, spareArgs = parser.parse_known_args()

  if len( spareArgs) != 0:
      reportExtraArgs( spareArgs)

  if args.station:
      station = args.station

  pid = args.pid
  if re.match( '.*/.*', pid):
      url = pid
  else:
      if len( pid) != 8:
          errorMessage( pid + ": programme ID isn't eight characters")
          exit( 4)
      url = 'http://www.bbc.co.uk/programmes/' + pid

  if args.time:
      ourTime = args.time
      if not re.match( '^[0-9]{4}/[0-9]{2}/[0-9]{2}-[0-9]{2}:[0-9]{2}$', \
                                                                      ourTime):
          errorMessage( ourTime + ": time isn't yyyy/mm/dd-hh:mm" )
          exit( 5)
      else:
          ourTime = re.sub( '-', 'T', ourTime)
          ourTime = re.sub( '/', '-', ourTime)


def reportExtraArgs( list):
      extras = list    .pop(0)
      if len( list    ) == 0:
          ess = '\n'
      else:
          ess = 's\n'
          while len( list    ) != 0:
              extras = extras + ' ' + list    .pop(0)
      errorMessage( extras + ': unexpected extra argument' + ess)
      usage()


def getArgs2():
  global NAME, url, ourStation, ourTime

  NAME = os.path.basename( sys.argv.pop(0))

  # deal with options
  #
  try:
      opts, args = getopt.getopt( sys.argv[0:], 'hs:', ['help', 'station='])
  except getopt.GetoptError as err:
      errorMessage( err.msg)
      exit( 3)
  for opt, value in opts:
          if opt in ( '-h', '--help'):
              usage()
          elif opt in ( '-s', '--station'):
              ourStation = value
              sys.argv.pop(0)
              sys.argv.pop(0)

  # get pid
  #
  if len( sys.argv) == 0:
      errorMessage( 'no pid or url/pid supplied\n')
      usage()
  pid = sys.argv.pop(0)
  if re.match( '.*/.*', pid):
      url = pid
  else:
      if len( pid) != 8:
          errorMessage( pid + ": isn't eight characters")
          exit( 4)
      url = 'http://www.bbc.co.uk/programmes/' + pid

  # get optional scheduled time
  #
  if len( sys.argv) == 0:
      return
  ourTime = sys.argv.pop(0)
  if len( sys.argv) != 0:
      reportExtraArgs( sys.argv)
  if not re.match( '^[0-9]{4}/[0-9]{2}/[0-9]{2}-[0-9]{2}:[0-9]{2}$', ourTime):
      errorMessage( ourTime + ": isn't yyyy/mm/dd-hh:mm" )
      exit( 5)
  else:
      ourTime = re.sub( '-', 'T', ourTime)
      ourTime = re.sub( '/', '-', ourTime)


NAME = ''        # globals
USAGE = ''
url = ''
ourStation = ''
ourTime = datetime.now().strftime( '%Y-%m-%dT%H:%M')   # default

if __name__ == '__main__':

  parser = MyHTMLParser()

  getArgs()
  exit( 0)

  try:
      page = requests.get( url)
      response = page.status_code
  except:
      errorMessage( 'network error')
      exit( 6)
  if response == 200:
      parser.feed( page.text)
  else:
      error = "couldn't get: " + url
      errorMessage( error)
      exit( 7)
  exit( 0)                               # no Broadcasts section!
