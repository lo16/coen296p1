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
continuation = False

grammar_non_terminals = ['S', 'NP', 'VP', 'Nominal', 'PP']
lexicon_non_terminals = ['Aux', 'Det', 'Pronoun', 'Proper-Noun',  'Noun', 'Verb', 'Prep']
grammar = {}
lexicon = {}

for line in sys.stdin:
    line = line.strip()
    split_line = tokenize(line)
    #check if line should be ignored
    if not (split_line == [] or split_line[0] == '#'):
        #handle line with input sentence
        if split_line[0] == 'W':
            for w in split_line[:2]:
                print '{0} {1} {2}'.format(w, find_type(w), line_num)

            #input sentence is here
            for w in split_line[2:]:
                if find_type(w) == 'STRING':
                    print '{0} {1} {2} {3}'.format(w, find_type(w), line_num, stemmer.stem(w))
                else:
                    print '{0} {1} {2}'.format(w, find_type(w), line_num)

        #check first word of the line to determine how to handle it
        else:
            #print all tokens first
            for w in split_line:
                print '{0} {1} {2}'.format(w, find_type(w), line_num)

            first_word = split_line[0]
            start = 1

            #handle '|' and ';' as first word
            #do a continuation check first
            if first_word in "|;":
                if not continuation:
                    #throw error
                    pass
                first_word = last_non_terminal
                start = 0
            #do continuation check for non-terminal first word
            else:
                if continuation and (first_word != last_non_terminal):
                    #throw error
                    print ('improperly formatted input')
                    sys.exit(1)

            if first_word in lexicon_non_terminals:
                if first_word not in lexicon:
                    lexicon[first_word] = []

                for w in split_line[start:]:
                    if w not in ":|;":
                        #this is working under the assumption that all terminals are single words
                        lexicon[first_word].append(w)

            elif first_word in grammar_non_terminals:
                if first_word not in grammar:
                    grammar[first_word] = []

                for w in split_line[start:]:
                    if w == ":":
                        #first rule
                        rule = []
                    elif w == "|":
                        #new rule
                        grammar[first_word].append(rule)
                        rule = []
                    elif w == ";":
                        #no more rules
                        grammar[first_word].append(rule)
                    else:
                        rule.append(w)

            else:
                #invalid line, throw error
                print ('improperly formatted input')
                sys.exit(1)
            
            #if line was processed, keep track of its operation for the next line
            last_non_terminal = first_word
            continuation = split_line[-1] != ";"
            
        line_num += 1
print 'ENDFILE\n'

print grammar
print lexicon


