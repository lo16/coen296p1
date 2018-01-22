import sys
import re
from nltk.stem.porter import *

line_num = 1

#patterns used for tokenization
letternumber = r'[A-Za-z0-9]'
notletter = r'[^A-Za-z0-9]'
alwayssep = r'[:|;=!?&]'
word = r'[A-Za-z0-9]+-?[A-Za-z0-9]*'

#compile regex patterns
string_obj = re.compile('^\w+-?\w*$')
int_obj = re.compile('^-?\d+$')
double_obj = re.compile('^-?\d+\.\d+$')
op_obj = re.compile('^[:\|;\.=,!\?]$')

#stemmer for input sentence
stemmer = PorterStemmer()

def tokenize(line):
    #add whitespace around symbols
    line = re.sub('(' + alwayssep + ')', r' \g<1> ', line)

    #add whitespace around commas not in numbers
    line = re.sub('([^0-9]),', r'\g<1> , ', line)
    line = re.sub(',([^0-9])', r' , \g<1>', line)

    #add whitespace around single quotes that are not apostrophes
    line = re.sub('^\'', '^\' ', line)
    line = re.sub('(' + notletter + ')\'', r'\g<1> \'', line)

    #add whitespace around periods that are not decimal points
    line = re.sub('(' + letternumber + ')\.$', r'\g<1> .', line)
    line = re.sub('(' + letternumber + ')\. ', r'\g<1> . ', line)
    words = line.split()
    return words

def find_type(w):
    if int_obj.match(w):
        return 'INT'
    elif double_obj.match(w):
        return 'DOUBLE'
    elif op_obj.match(w):
        return 'OP'
    elif string_obj.match(w):
        return 'STRING'

last_non_terminal = None

grammar_non_terminals = ['S', 'NP', 'VP', 'Nominal', 'PP']
lexicon_non_terminals = ['Aux', 'Det', 'Pronoun', 'Proper-Noun',  'Noun', 'Verb', 'Prep']
grammar = {}
lexicon = {}

for line in sys.stdin:
    line = line.strip()
    split_line = tokenize(line)
    if not (split_line == [] or split_line[0] == '#'):
        if split_line[0] == 'W':
            for w in split_line[:2]:
                print '{0} {1} {2}'.format(w, find_type(w), line_num)

            #input sentence is here
            for w in split_line[2:]:
                if find_type(w) == 'STRING':
                    print '{0} {1} {2} {3}'.format(w, find_type(w), line_num, stemmer.stem(w))
                else:
                    print '{0} {1} {2}'.format(w, find_type(w), line_num)
        else:
            first_word = split_line[0]
            if first_word in lexicon_non_terminals:
                if first_word not in lexicon:
                    lexicon[first_word] = []
                for w in split_line[2:]:
                    if w != '|':
                        lexicon[first_word].append(w)

            elif first_word in grammar_non_terminals:

            for w in split_line:
                print '{0} {1} {2}'.format(w, find_type(w), line_num)
        line_num += 1
print 'ENDFILE\n'




