#!/bin/sh
<<'______________D__O__C__U__M__E__N__T__A__T__I__O__N_____________'

  chkNew [ -s station ] [url]/pid [ time ] - check pid was NOT
                                             broadcast before time

       time is in getPids format: yyyy/mm/dd-hh:mm

       station is as it is in the URL of station's home page,
       eg: bbcone, radio4.

  Option:
          -s   look for repeats only on station

  Returns: 0   new programme
           1   repeat
           2+  problem

  Displays:    date of most recent repeat, with the station unless the
               -s option is used.

  Version
  -------
      Mon Sep 9 12:31:44 BST 2019

  Copyright
  ---------
     Copyright (C) 2019 Peter Scott - peterscott@pobox.com

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

        1) at one stage, the Beeb had dropped nearly all the '(R)'
           indicators it used to have in the Radio 4 schedule.

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
     $ chkNew -s radio4extra b08tj4y1
     Sun 26 May 2019 19:00
     $ chkNew -s radio4 b08tj4y1
     Fri 07 Jun 2019 21:00
     $

  The above output may be different in the future depending on broadcasts
  after the revision date.

  Bugs
  ----
     email: peterscott@pobox.com

______________D__O__C__U__M__E__N__T__A__T__I__O__N_____________


# usage - display usage message
#
usage(){
  cat <<-! >&2
	Usage: $NAME [ -s station ] [url/]pid [yyyy/mm/dd-hh:mm]

	Option:
	       -s   look for repeats only on station
!
  exit 2
}


# mkTmp - make temp dir and delete it automatically on exit or failure
#         Eg: mkTmp; ... > $TMP/temp
#
# Be careful not to exit from a subshell and lose an exit code!
# -------------------------------------------------------------
#
mkTmp(){
  TMP=/tmp/$NAME.$$

  trap 'code=$?; rm -fr $TMP 2> /dev/null; exit $code' EXIT HUP INT QUIT TERM
  mkdir $TMP && return
  echo "$NAME: couldn't make \`$TMP' directory" >&2
  exit 3
}


# prevent the user giving the script a name containing white space
# -- saving the hassle of quoting TMP file names
#
NAME=`basename "$0"`
words=`echo "$NAME" | wc -w`
if [ $words -ne 1 ] ;then
     echo "\`$NAME': I don't allow white space in command names" >&2
     exit 4
fi

# check for option
#
while getopts ':s:' option ;do
     case $option in
       s) station=$OPTARG
          case $station in
            -*) echo "$NAME: $station: station can't begin with dash" >&2
                exit 5
                ;;
            ?) echo "$NAME: $station: station can't be only one letter" >&2
                exit 6
          esac
          ;;
       :) echo "$NAME: option \`-$OPTARG' requires a station" >&2 ;;
      \?) echo "$NAME: bad option: -$OPTARG" >&2
          usage
     esac
done
shift `expr $OPTIND - 1`

# sort out arguments
#
case $# in
  1) pid=$1
     time=`date '+%s'`
     ;;
  2) pid=$1
     time=$2
     case $time in
       [0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]-[0-9][0-9]:[0-9][0-9])
          time=`echo $time |
                  sed 's/-/T/
                       s?/?-?g'`
          time=`date --date $time '+%s'`
          ;;
       *) echo "$NAME: $time isn't yyyy/mm/dd-hh:mm" >&2
          exit 7
     esac
     ;;
  *) usage
esac
case "$pid" in
  */*)
     : ;;
  *)
     pid="https://www.bbc.co.uk/programmes/$pid"
esac

mkTmp

# get page, reformat HTML, and extract Broadcasts section (if any)
#
wget -O $TMP/pid -q $pid
if [ $? -ne 0 ] ;then
     echo "$NAME: couldn't get $pid" >&2
     exit 8
fi
sed -n 's/^[	 ][	 ]*//
        />[ 	]*</s//>\n</g
        /^<h2>Broadcasts<.h2>$/,/^<\/ul>$/p' $TMP/pid > $TMP/broadcasts

# exit early if no Broadcasts section
#
test -s $TMP/broadcasts || exit 0

# look for an earlier broadcast (avoiding exit from a subshell)
#
earlier=$(
  # pass on individual broadcast times and channels
  #
  sed -n '/^<div class="broadcast-event__time beta"/{
                N; N; N; N; N; N; N; N; N
                s/\n//g
                s/.*content="//
                s/">.*subtle">//
                s?<a href="/? ?
                s/">/ /
                s?</a>? ?
                p
           }' $TMP/broadcasts |
    tac |

      # return details and finish if an earlier broadcast found
      #
      while read date broadcastStation details ;do
           broadcastTime=$(date --date $date '+%s')
           if [ $broadcastTime -lt $time ] ;then
                displayDate=$(date --date $date '+%a %d %b %Y %R')
                if [ -z "$station" ] ;then
                     echo "$displayDate - $details"
                     break        # exit 1 here would lose the exit code!
                elif [ $broadcastStation = $station ] ;then
                     echo $displayDate
                     break        # exit 1 here would lose the exit code!
                fi
           fi
      done
)

# indicate repeat or not
#
if [ -z "$earlier" ] ;then
     exit 0
else
     echo $earlier
     exit 1
fi
