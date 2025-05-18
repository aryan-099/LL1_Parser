
# DRIVER CODE - MAIN

# NOTE: To test any of the sample sets, uncomment ->
# 'rules' list, 'nonterm_userdef' list, 'term_userdef' list
# and for any String validation uncomment following line with
# 'sample_input_String' variable.

sample_input_string = None

# sample set 1 (Result: Not LL(1))
# rules=["A -> S B | B",
#        "S -> a | B c | #",
#        "B -> b | d"]
# nonterm_userdef=['A','S','B']
# term_userdef=['a','c','b','d']
# sample_input_string="b c b"

# sample set 2 (Result: LL(1))
# rules=["S -> A | B C",
#        "A -> a | b",
#        "B -> p | #",
#        "C -> c"]
# nonterm_userdef=['A','S','B','C']
# term_userdef=['a','c','b','p']
# sample_input_string="p c"

# sample set 3 (Result: LL(1))
# rules=["S -> A B | C",
#        "A -> a | b | #",
#        "B-> p | #",
#        "C -> c"]
# nonterm_userdef=['A','S','B','C']
# term_userdef=['a','c','b','p']
# sample_input_string="a c b"

# sample set 4 (Result: Not LL(1))
# rules = ["S -> A B C | C",
#          "A -> a | b B | #",
#          "B -> p | #",
#         "C -> c"]
# nonterm_userdef=['A','S','B','C']
# term_userdef=['a','c','b','p']
# sample_input_string="b p p c"

# sample set 5 (With left recursion)
# rules=["A -> B C c | g D B",
#        "B -> b C D E | #",
#        "C -> D a B | c a",
#        "D -> # | d D",
#        "E -> E a f | c"
#       ]
# nonterm_userdef=['A','B','C','D','E']
# term_userdef=["a","b","c","d","f","g"]
# sample_input_string="b a c a c"

# sample set 6
# rules=["E -> T E'",
#        "E' -> + T E' | #",
#        "T -> F T'",
#        "T' -> * F T' | #",
#        "F -> ( E ) | id"
# ]
# nonterm_userdef=['E','E\'','F','T','T\'']
# term_userdef=['id','+','*','(',')']
# sample_input_string="id * * id"
# example string 1
# sample_input_string="( id * id )"
# example string 2
# sample_input_string="( id ) * id + id"

# sample set 7 (left factoring & recursion present)
rules=["S -> A k O",
       "A -> A d | a B | a C",
       "C -> c",
       "B -> b B C | r"]

nonterm_userdef=['A','B','C']
term_userdef=['k','O','d','a','c','b','r']
#sample_input_string="a r k O"
sample_input_string = input("Enter input string: ")  # <-- instead of hardcoding

# sample set 8 (Multiple char symbols T & NT)
# rules = ["S -> NP VP",
#          "NP -> P | PN | D N",
#          "VP -> V NP",
#          "N -> championship | ball | toss",
#          "V -> is | want | won | played",
#          "P -> me | I | you",
#          "PN -> India | Australia | Steve | John",
#          "D -> the | a | an"]
#
# nonterm_userdef = ['S', 'NP', 'VP', 'N', 'V', 'P', 'PN', 'D']
# term_userdef = ["championship", "ball", "toss", "is", "want",
#                 "won", "played", "me", "I", "you", "India",
#                 "Australia","Steve", "John", "the", "a", "an"]
# sample_input_string = "India won the championship"

# diction - store rules inputted
# firsts - store computed firsts
diction = {}
firsts = {}
follows = {}

# computes all FIRSTs for all non terminals
computeAllFirsts()
# assuming first rule has start_symbol
# start symbol can be modified in below line of code
start_symbol = list(diction.keys())[0]
# computes all FOLLOWs for all occurrences
computeAllFollows()
# generate formatted first and follow table
# then generate parse table

(parsing_table, result, tabTerm) = createParseTable()

# validate string input using stack-buffer concept
if sample_input_string != None:
    validity = validateStringUsingStackBuffer(parsing_table, result,
                                              tabTerm, sample_input_string,
                                              term_userdef,start_symbol)
    print(validity)
else:
    print("\nNo input String detected")

# Author: Tanmay P. Bisen