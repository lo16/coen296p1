import sys
import re

line_num = 1
letternumber = r'[A-Za-z0-9]'
notletter = r'[^A-Za-z0-9]'
alwayssep = r'[:|;=!?&]'
word = r'[A-Za-z0-9]+-?[A-Za-z0-9]*'

string_obj = re.compile('^\w+$')
int_obj = re.compile('^-?\d+$')
double_obj = re.compile('^-?\d+\.\d+$')
op_obj = re.compile('^[:|;]$')

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
	return words

# string_obj = re.compile('^\w+$')
# int_obj = re.compile('^-?\d+$')
# double_obj = re.compile('^-?\d+\.\d+$')
# op_obj = re.compile('^[:|;]$')
def find_type(w):
    if string_obj.match(w):
        return 'STRING'
    elif int_obj.match(w):
        return 'INT'
    elif double_obj.match(w):
        return 'DOUBLE'
    elif op_obj.match(w):
        return 'OP'

for line in sys.stdin:
    line = line.strip()
    split_line = tokenize(line)
    if not (split_line == [] or split_line[0] == '#'):
        for w in split_line:
    	   print '{0} {1} {2}'.format(w, find_type(w), line_num)#, stem(w))
    	line_num += 1
print 'ENDFILE\n'




