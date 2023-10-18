'''
main

Uses 'alttex_functions' to convert a given document into its alt text version. 
'''

import re
import csv
from alttex_functions_Edit import *


if __name__ == '__main__':
    with open('LaTeX_Symbols.csv', 'r') as csv_file:
        symbols_table = [row for row in csv.reader(csv_file)]
        symbols, converted_symbols = ([symbols_table[j][i] 
                                       for j in range(len(symbols_table))] 
                                       for i in range(2))
    with open('LaTeX_Doc.txt', 'r', encoding="utf8") as latex_file:
        latex_doc = [line for line in latex_file]     

    special_symbols = {
        r'_': ' subscript ', r'^': ' superscript ', 
        r'>': ' greater than ', r'<': ' less than ', r'-': ' minus ',
        r'/': ' over ', r'!': ' factorial ', r'|': ' vertical bar '
    }
    delimiters = [ 
        r'\$\$(.*?)\$\$', r'\$(.*?)\$', r'\\\((.*?)\\\)', r'\\\[(.*?)\\\]', 
        r'\\begin\{math\}(.*?)\\end\{math\}',
        r'(?s)\\begin\{equation\}(.*)\\end\{equation\}'
    ]


    latex_doc = begin_doc(latex_doc)


# DEBUGGING

    test = ''
#   use the yeild statement at the end of 'eqn_tokenise'
    [print(token) for token in eqn_tokenise(test, symbols, converted_symbols, 
                                            special_symbols)]
#   use the return statement at the end of 'eqn_tokenise'
    print(eqn_tokenise(test, symbols, converted_symbols, special_symbols))

#   use the yield statement at the end of 'tokenise' and return statement at the
#       end of 'eqn_tokenise'
    [print(token) for token in tokenise(latex_doc, delimiters, symbols, 
                                        converted_symbols, special_symbols)]

#   use the return statement at the end of 'tokenise' and return statement at
#      the end of 'eqn_tokenise'
    altex_doc = tokenise(latex_doc, delimiters, symbols, converted_symbols, 
                         special_symbols)
    altex = re.split(r'\n', altex_doc)
    
with open('Alt_Text', 'w') as file:
    for line in altex:
        if line == '':
            continue
        if re.search(r'^\\\\.*', line) == None:
            file.write(line)
            file.write('\n')
        else:
            file.write(line)
    file.close()
