import sys
import re

line_num = 1
letternumber = r'[A-Za-z0-9]'
notletter = r'[^A-Za-z0-9]'
alwayssep = r'[:|;=!?&]'
word = r'[A-Za-z0-9]+-?[A-Za-z0-9]*'

def tokenize(line):
	line = re.sub('(' + alwayssep + ')', r' \g<1> ', line)

	#commas not in numbers
	line = re.sub('([^0-9]),', r'\g<1> , ', line)
	line = re.sub(',([^0-9])', r' , \g<1>', line)

	#single quotes
	line = re.sub('^\'', '^\' ', line)
	line = re.sub('(' + notletter + ')\'', r'\g<1> \'', line)

	#periods
	line = re.sub('(' + letternumber + ')\.$', r'\g<1> .', line)
	line = re.sub('(' + letternumber + ')\. ', r'\g<1> . ', line)
	words = line.split()
	print words
# string_obj = re.compile('^\w+$')
# int_obj = re.compile('^-?\d+$')
# double_obj = re.compile('^-?\d+\.\d+$')
# op_obj = re.compile('^[:|;]$')

for line in sys.stdin:
    line = line.strip()
    split_line = tokenize(line)
    if split_line != [] and split_line[0] != '#':
    	print '{0} {1} {2} {3}'.format(w, find_type(w), line_num)#, stem(w))
    	line_num += 1
print 'ENDFILE\n'




