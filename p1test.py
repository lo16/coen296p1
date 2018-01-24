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
    else:
        print ('invalid symbol found')
        sys.exit(1)

def remove_punctuation(sentence):
    return [w for w in sentence if not op_obj.match(w)]

last_non_terminal = None
continuation = False

grammar_non_terminals = ['S', 'NP', 'VP', 'Nominal', 'PP']
lexicon_non_terminals = ['Aux', 'Det', 'Pronoun', 'Proper-Noun',  'Noun', 'Verb', 'Prep']
grammar = {}
lexicon = {}
sentence = None

def find_part_of_speech(w):
    parts = []
    word_stem = stemmer.stem(w)
    for key in lexicon.keys():
        if word_stem in lexicon[key]:
            parts.append(key)
    return parts

for line in sys.stdin:
    line = line.strip()
    split_line = tokenize(line)
    #check if line should be ignored
    if not (split_line == [] or split_line[0] == '#'):
        #handle line with input sentence
        if split_line[0] == 'W':
            for w in split_line[:2]:
                print ('{0} {1} {2}'.format(w, find_type(w), line_num))

            #input sentence is here
            for w in split_line[2:]:
                if find_type(w) == 'STRING':
                    print ('{0} {1} {2} {3}'.format(w, find_type(w), line_num, stemmer.stem(w)))
                else:
                    print ('{0} {1} {2}'.format(w, find_type(w), line_num))

            sentence = split_line[2:]#remove_punctuation(split_line[2:])

        #check first word of the line to determine how to handle it
        else:
            #print all tokens first
            for w in split_line:
                print ('{0} {1} {2}'.format(w, find_type(w), line_num))

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
                    print ('improperly formatted input, continuation error')
                    sys.exit(1)

            if first_word in lexicon_non_terminals:
                if first_word not in lexicon:
                    lexicon[first_word] = []

                for w in split_line[start:]:
                    if w not in ":|;":
                        if find_type(w) != 'OP':
                            #this is working under the assumption that all terminals are single words
                            lexicon[first_word].append(w)
                        else:
                            #invalid OP found:
                            print ('improperly formatted input, OP error')
                            sys.exit(1)

            elif first_word in grammar_non_terminals:
                if first_word not in grammar:
                    grammar[first_word] = []

                for w in split_line[start:]:
                    #print ('processing ' + w)
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
                    elif find_type(w) != 'OP':
                        rule.append(w)
                    else:
                        print ('improperly formatted input, OP error2')
                        print (w)
                        sys.exit(1)

            else:
                #invalid line, throw error
                print ('improperly formatted input, non-terminal error')
                sys.exit(1)
            
            #if line was processed, keep track of its operation for the next line
            last_non_terminal = first_word
            continuation = split_line[-1] != ";"

        line_num += 1
print ('ENDFILE\n')

#################################################################################

class chartState:
    parts_of_speech = ['Aux', 'Det', 'Pronoun', 'Proper-Noun',  'Noun', 'Verb', 'Prep']
    def __init__(self, left, right, begin, dot):
        self.left = left
        self.right = right
        self.begin = begin
        self.dot = dot

    def next_cat_is_part_of_speech(self):
        if self.dot - self.begin < len(self.right) and self.dot - self.begin >= 0:
            return self.right[self.dot - self.begin] in chartState.parts_of_speech
        else:
            print ('parsing error, reached end of rule')
            print (chart)
            print (self)
            sys.exit(1)

    def incomplete(self):
        return (self.dot - self.begin) < len(self.right) 

    def __repr__(self):
        new_right = self.right[:]
        new_right.insert(self.dot - self.begin, '^')
        new_right = ' '.join(new_right)
        return "{0} -> {1} \t [{2},{3}]\n".format(self.left, new_right, self.begin, self.dot)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__



chart = [[] for i in range(len(sentence) + 1)]

def predictor(state, temp_chart):
    #print ('in predictor')
    B = state.right[state.dot - state.begin]
    j = state.dot
    rules = grammar[B]
    #print state
    for rule in rules:
        new_state = chartState(B, rule, j, j)
        if enqueue(new_state, chart[j], 'Predictor'):
            enqueue(new_state, temp_chart, 'Predictor')

def scanner(state):
    j = state.dot
    B = state.right[j - state.begin]

    if B in find_part_of_speech(sentence[j]):
        new_state = chartState(B, [sentence[j]], j, j + 1)
        enqueue(new_state, chart[j + 1], 'Scanner')

def completer(state, temp_chart):
    j = state.begin
    k = state.dot
    B = state.left

    for temp_state in chart[j]:
        if (j == temp_state.dot) and ((temp_state.dot - temp_state.begin) < len(temp_state.right)) and (B == temp_state.right[j - temp_state.begin]) and (temp_state.left != 'y'):
            new_state = chartState(temp_state.left, temp_state.right, temp_state.begin, k)
            if enqueue(new_state, chart[k], 'Completer'):
                enqueue(new_state, temp_chart, 'Completer')

def enqueue(state, entry, caller):
    if state not in entry:
        entry.append(state)
        return True
    return False

startState = chartState('y', ['S'], 0, 0)
enqueue(startState, chart[0], 'Dummy start state')

#i = 0
for i in range(0, len(sentence)):
    print ('processing chart ' + str(i) + 'a')
    temp_chart = chart[i][:]
    while temp_chart:
        state = temp_chart.pop(0)

        if state.incomplete() and not state.next_cat_is_part_of_speech():
            predictor(state, temp_chart)
        elif state.incomplete() and state.next_cat_is_part_of_speech():
            scanner(state)
        else:
            completer(state, temp_chart)

print (chart)