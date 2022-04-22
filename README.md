# chkNew
Python script to check if a BBC programme is a repeat

It works with TV and radio programmes.

## It is needed because:

1. the Radio 4 schedule (at least) has completely dropped the '(R)' indicators

1. repeats are shown in the "Radio Times" and on the programme's individual web page but are often unflagged in the shedules.

## Examples

    $ chkNew m0000sdx 2018/10/21-20:00  
    Friday 16:30 - BBC Radio 4  
    $ echo $?  
    1                         # repeat  
    $

    $ chkNew b092m9j6  
    Tue 5 Sep 2017 11:30 - BBC Radio 4  
    $

    $ chkNew https://www.bbc.co.uk/programmes/b080t87y  
    Tue 1 Nov 2016 14:15 - BBC Radio 4  
    $

    $ chkNew  m000k26j
    Sun 17 Apr 2022 17:00 - BBC Radio 3
    $ chkNew -s radio_three m000k26j
    Sun 17 Apr 2022 17:00
    $ chkNew -s radio_four m000k26j
    $ 

    $ chkNew b0bprgc2   
    $ echo $?  
    0                         # NOT a repeat  
    $
