#!/usr/bin/env python3
'''
  chkNew [ -s station ] [url/]pid [ time ] - check pid was NOT
                                             broadcast before time

       time is in getPids format: yyyy/mm/dd-hh:mm

       station is as it is in the URL of station's .svg logo, except
       that the superflous "bbc_" is removed from the start of radio
       station names.

       eg: bbc_one, radio_four, radio_four_extra, bbc_alba.

  Option:
          -s   look for repeats only on station

  Returns: 0   new programme
           1   repeat
           2+  problem

  Displays:    date of most recent repeat with the station
               (the station is omitted if the -s option was used)


  Version: Fri Apr 22 15:51:48 BST 2022

  Copyright (C) 2023 Peter Scott - peterscott@pobox.com

  Licence
  -------
     This program is free software: you can redistribute it and / or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation, either version 3 of the License, or
     (at your option) any later version.

     This program is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     GNU General Public License for more details.

     You should have received a copy of the GNU General Public License
     along with this program.  If not, see <http://www.gnu.org/licenses/>.

  Purpose
  -------
     This script checks that a BBC programme is not a repeat.
     It works with TV and radio programmes.

     With a date+time from a schedule `chkNew' checks for broadcasts before
     that date.  Without a date it checks for broadcasts before today.

     Only the last earlier broadcast is shown.  The Beeb usually has them
     in the correct order so it should be the most recent repeat.

  Rationale
  ---------
     It is needed because:

        1) the Beeb had dropped nearly all the '(R)' indicators it used
           to have in the Radio 4 schedule;

        2) repeats are shown in the "Radio Times" and on the programme's
           individual web page but are often unflagged in the shedule.

  Examples
  --------
     $ chkNew m0000sdx 2018/10/21-20:00
     Fri 19 Oct 2018 16:30 - BBC Radio 4
     $ echo $?
     1                         # repeat
     $ chkNew b092m9j6
     Sat 20 Oct 2018 15:30 - BBC Radio 4
     $ chkNew https://www.bbc.co.uk/programmes/b080t87y
     Fri 19 Oct 2018 14:15 - BBC Radio 4
     $ chkNew b0bprgc2
     $ echo $?
     0                         # NOT a repeat
     $ chkNew -s radio_four_extra b08tj4y1
     Sun 26 May 2019 19:00
     $ chkNew -s radio_four b08tj4y1
     Fri 07 Jun 2019 21:00
     $

  The above output may be different in the future depending on further
  broadcasts

  Notes:
  ------
  If your installation doesn't have them, you will need to install
  'requests' and 'HTMLParser'(via pip.)

  Bugs
  ----
     email: peterscott@pobox.com
'''

import requests, re, sys, os, string, argparse
from datetime import datetime
from html.parser import HTMLParser

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
    if self.step < 2:
        return        # nothing to look at until we get 'Broadcasts' in an h2

    # examine the attributes and values and collect the relevant ones
    #
    for n in range( 0, len( attrs)):
        attr  = attrs[n][0]
        value = attrs[n][1]
        if self.step == 2 and attr == 'src':
            self.station = re.sub( '.*/svg/', '', value, 1)
            self.station = re.sub( 'bbc_radio', 'radio', self.station, 1)
            self.station = re.sub( '/.*', '', self.station, 1)
            self.step = 3
        elif self.step == 3 and attr == 'content':
            self.time = value
            self.step = 4
        elif self.step == 4 and attr == 'class' and 'programme_' in value:
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
                print( time.strftime( '%a %d %b %Y %H:%M'), end='')
                if ourStation:
                    print()
                else:
                    print( ' -', name)
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
      #
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

  if len( spareArgs):
      reportExtraArgs( spareArgs)

  if args.station:
      ourStation = args.station

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
      ourTime = re.sub( '-', 'T', ourTime)
      ourTime = re.sub( '/', '-', ourTime)


def reportExtraArgs( list):
  extras = list.pop(0)
  if not list:
      ess = '\n'
  else:
      ess = 's\n'
      while list:
          extras = extras + ' ' + list.pop(0)
  errorMessage( extras + ': unexpected extra argument' + ess)
  usage()


NAME = ''        # globals
USAGE = ''
url = ''
ourStation = ''
ourTime = datetime.now().strftime( '%Y-%m-%dT%H:%M')   # default

if __name__ == '__main__':

  parser = MyHTMLParser()

  getArgs()
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
