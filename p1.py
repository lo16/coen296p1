import sys
import re
from nltk.stem.porter import *

########################################################################################

#tokenStemmer handles the tokenization and stemming part of P1
class tokenStemmer:
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

    def __init__(self):
        self.grammar_non_terminals = ['S', 'NP', 'VP', 'Nominal', 'PP']
        self.lexicon_non_terminals = ['Aux', 'Det', 'Pronoun', 'Proper-Noun',  'Noun', 'Verb', 'Prep']
        self.grammar = {}
        self.lexicon = {}
        self.sentence = None

    #tokenize the given line
    def tokenize(self, line):
        #add whitespace around symbols
        line = re.sub('(' + tokenStemmer.alwayssep + ')', r' \g<1> ', line)

        #add whitespace around commas not in numbers
        line = re.sub('([^0-9]),', r'\g<1> , ', line)
        line = re.sub(',([^0-9])', r' , \g<1>', line)

        #add whitespace around single quotes that are not apostrophes
        line = re.sub('^\'', '^\' ', line)
        line = re.sub('(' + tokenStemmer.notletter + ')\'', r'\g<1> \'', line)

        #add whitespace around periods that are not decimal points
        line = re.sub('(' + tokenStemmer.letternumber + ')\.$', r'\g<1> .', line)
        line = re.sub('(' + tokenStemmer.letternumber + ')\. ', r'\g<1> . ', line)
        words = line.split()
        return words

    #find the type of the given word
    def find_type(self, w):
        if tokenStemmer.int_obj.match(w):
            return 'INT'
        elif tokenStemmer.double_obj.match(w):
            return 'DOUBLE'
        elif tokenStemmer.op_obj.match(w):
            return 'OP'
        elif tokenStemmer.string_obj.match(w):
            return 'STRING'
        else:
            print ('invalid symbol found')
            sys.exit(1)

    #remove punctuation from the tokenized line
    def remove_punctuation(self, s):
        return [w for w in s if not tokenStemmer.op_obj.match(w)]

    #find the given word's part of speech
    def find_part_of_speech(self, w):
        parts = []
        for key in self.lexicon.keys():
            if w in self.lexicon[key]:
                parts.append(key)
        return parts

    #read and process input from stdin
    def process_input(self):
        #initialize helper variables
        #last_non_terminal and continuation are used to check for and handle
        #rules that span multiple lines
        line_num = 1
        last_non_terminal = None
        continuation = False

        for line in sys.stdin:
            line = line.strip()
            split_line = self.tokenize(line)

            #check if line should be ignored
            if not (split_line == [] or split_line[0] == '#'):
                #handle line with input sentence
                if split_line[0] == 'W':
                    for w in split_line[:2]:
                        print ('{0} {1} {2}'.format(w, self.find_type(w), line_num))

                    #input sentence is here
                    for w in split_line[2:]:
                        #print stem if the word is a string
                        if self.find_type(w) == 'STRING':
                            print ('{0} {1} {2} {3}'.format(w, self.find_type(w), line_num, tokenStemmer.stemmer.stem(w)))
                        else:
                            print ('{0} {1} {2}'.format(w, self.find_type(w), line_num))

                    #store the tokenized and stemmed sentence
                    self.sentence = list(map(tokenStemmer.stemmer.stem, self.remove_punctuation(split_line[2:])))#remove_punctuation(split_line[2:])

                #check first word of the line to determine how to handle it
                else:
                    #print all tokens first
                    for w in split_line:
                        print ('{0} {1} {2}'.format(w, self.find_type(w), line_num))

                    first_word = split_line[0]
                    start = 1

                    #handle '|' and ';' as first word
                    #do a continuation check first
                    if first_word in "|;":
                        if not continuation:
                            print ('continuation error')
                            sys.exit(1)
                        first_word = last_non_terminal
                        start = 0
                    #do continuation check for non-terminal first word
                    else:
                        if continuation and (first_word != last_non_terminal):
                            #handle error
                            print ('improperly formatted input, continuation error')
                            sys.exit(1)

                    #handle first word of each line appropriately
                    #fill up grammar rules and lexicon
                    if first_word in self.lexicon_non_terminals:
                        if first_word not in self.lexicon:
                            self.lexicon[first_word] = []

                        for w in split_line[start:]:
                            if w not in ":|;":
                                if self.find_type(w) != 'OP':
                                    #this is working under the assumption that all terminals are single words
                                    self.lexicon[first_word].append(w)
                                else:
                                    #invalid OP found:
                                    print ('improperly formatted input, OP error')
                                    sys.exit(1)

                    elif first_word in self.grammar_non_terminals:
                        if first_word not in self.grammar:
                            self.grammar[first_word] = []

                        for w in split_line[start:]:
                            #print ('processing ' + w)
                            if w == ":":
                                #first rule
                                rule = []
                            elif w == "|":
                                #new rule
                                self.grammar[first_word].append(rule)
                                rule = []
                            elif w == ";":
                                #no more rules
                                self.grammar[first_word].append(rule)
                            elif self.find_type(w) != 'OP':
                                rule.append(w)
                            else:
                                print ('improperly formatted input, OP error')
                                sys.exit(1)

                    else:
                        #invalid line, handle error
                        print ('improperly formatted input, non-terminal error')
                        sys.exit(1)
                    
                    #if line was processed, keep track of its operation for the next line
                    last_non_terminal = first_word
                    continuation = split_line[-1] != ";"

                line_num += 1
        print ('ENDFILE\n')

    #provide data for parser
    def results(self):
        return (self.sentence, self.grammar, self.lexicon)

########################################################################################

#chartState represents the state of a rule under evaluation
class chartState:
    parts_of_speech = ['Aux', 'Det', 'Pronoun', 'Proper-Noun',  'Noun', 'Verb', 'Prep']

    def __init__(self, left, right, begin, dot, dot_position):
        #expression on the left of the arrow
        self.left = left

        #expression on the right of the arrow
        self.right = right

        #where the rule begins in the sentence
        self.begin = begin

        #position of the dot in the sentence
        self.dot = dot

        #position of the dot in the right-hand expression
        self.dot_position = dot_position

    #returns true if the rule is not complete
    def incomplete(self):
        return self.dot_position < len(self.right) 

    #check if the part of the right-hand expression to the right of the dot is a part of speech
    def next_cat_is_part_of_speech(self):
        if self.incomplete():
            return self.right[self.dot_position] in chartState.parts_of_speech
        else:
            print ('parsing error, reached end of rule')
            sys.exit(1)

    #define how the state is printed
    def __repr__(self):
        new_right = self.right[:]
        new_right.insert(self.dot_position, '^')
        new_right = ' '.join(new_right)
        return "{0} -> {1} [{2},{3}]".format(self.left, new_right, self.begin, self.dot)

    #define how the states are compared for equality
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

########################################################################################

#parser takes the results from tokenStemmer and parses the sentence
#implementation of predictor/scanner/completer/parse are based on the algorithm in chapter 13
class parser:
    def __init__(self, sentence, grammar, lexicon):
        self.sentence = sentence
        self.grammar = grammar
        self.lexicon = lexicon
        self.chart = [[] for i in range(len(sentence) + 1)]
        self.procedures = [[] for i in range(len(sentence) + 1)]

    #same function in tokenStemmer
    def find_part_of_speech(self, w):
        parts = []
        for key in self.lexicon.keys():
            if w in self.lexicon[key]:
                parts.append(key)
        return parts

    def predictor(self, state, temp_chart):
        B = state.right[state.dot_position]
        j = state.dot
        rules = self.grammar[B]

        for rule in rules:
            new_state = chartState(B, rule, j, j, 0)
            if self.enqueue(new_state, self.chart[j], self.procedures[j], 'Predictor'):
               self.enqueue_without_caller(new_state, temp_chart)

    def scanner(self, state):
        j = state.dot
        B = state.right[state.dot_position]

        #end of sentence check
        if j == len(sentence):
            return
        elif B in self.find_part_of_speech(self.sentence[j]):
            new_state = chartState(B, [self.sentence[j]], j, j + 1, 1)
            self.enqueue(new_state, self.chart[j + 1], self.procedures[j + 1], 'Scanner')

    def completer(self, state, temp_chart):
        j = state.begin
        k = state.dot
        B = state.left

        for temp_state in self.chart[j]:
            if (j == temp_state.dot) and temp_state.incomplete() and (B == temp_state.right[j - temp_state.begin]) and (temp_state.left != 'y'):
                new_state = chartState(temp_state.left, temp_state.right, temp_state.begin, k, temp_state.dot_position + 1)
                if self.enqueue(new_state, self.chart[k], self.procedures[k], 'Completer'):
                    self.enqueue_without_caller(new_state, temp_chart)

    #add state and procedure information (used for self.chart and self.procedures)
    def enqueue(self, state, entry, procedures, procedure):
        if state not in entry:
            entry.append(state)
            procedures.append(procedure)
            return True
        return False

    #add state (used for temp_chart)
    def enqueue_without_caller(self, state, entry):
        if state not in entry:
            entry.append(state)
            return True
        return False

    def parse(self):
        #add dummy start state
        startState = chartState('y', ['S'], 0, 0, 0)
        self.enqueue(startState, self.chart[0], self.procedures[0], 'Dummy start state')

        #run the Earley parser algorithm
        for i in range(0, len(self.sentence) + 1):
            temp_chart = self.chart[i][:]
            while temp_chart:
                state = temp_chart.pop(0)

                if state.incomplete() and not state.next_cat_is_part_of_speech():
                    self.predictor(state, temp_chart)
                elif state.incomplete() and state.next_cat_is_part_of_speech():
                    self.scanner(state)
                else:
                    self.completer(state, temp_chart)

    #helper function to format and print the parsed chart
    def output(self):
        state_counter = 0
        for i in range(len(self.chart)):
            print ('Chart[{0}]'.format(i), end = ' ')
            for j in range(len(self.chart[i])):
                state_string = self.chart[i][j].__repr__()
                state_string_split = state_string.index('[')
                
                state_string_1 = state_string[:state_string_split]
                state_string_2 = state_string[state_string_split:]
                if state_counter < 10:
                    state_string_2 = ' ' + state_string_2

                print_statement = 'S{0} {1:35} {2} {3}'.format(state_counter, state_string_1, state_string_2, self.procedures[i][j])

                if j != 0:
                    print_statement = '\t\t ' + print_statement
                print (print_statement)
                state_counter += 1
            print()

########################################################################################

if __name__ == '__main__':
    ts = tokenStemmer()
    ts.process_input()
    sentence, grammar, lexicon = ts.results()
    p = parser(sentence, grammar, lexicon)
    p.parse()
    p.output()
