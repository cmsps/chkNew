# chkNew
Shell script to check if a BBC programme is a repeat

It works with TV and radio programmes.

It is needed because:

1) the Radio 4 schedule (at least) has dropped nearly all the
'(R)' indicators it used to have:

2) repeats are shown in the "Radio Times" and on the programme's
individual web page but are often unflagged in the shedule.

Examples
--------

$ chkNew m0000sdx 2018/10/21-20:00  
Friday 16:30 - BBC Radio 4  
$

$ chkNew b092m9j6  
Tue 5 Sep 2017 11:30 - BBC Radio 4  
$

$ chkNew https://www.bbc.co.uk/programmes/b080t87y  
Tue 1 Nov 2016 14:15 - BBC Radio 4  
$ echo $?  
1                         # repeat  
$

$ chkNew b0bprgc2   
$ echo $?  
0                         # NOT a repeat  
$
