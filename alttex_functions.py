'''
altex_functions

Tokenises a LaTeX write-up document and inserts alt text for math text.

Classes:
    Token

Functions:
    alt_commands
    alt_symbols
    begin_doc
    check_brackets
    convert_commands
    convert_symbols
    eqn_tokenise
    find_commands
    find_equations
    flatten
    multi_replace
    nested_brackets
    next_bracket
    tabular
    tokenise
'''

import re
from typing import NamedTuple
from string import ascii_letters
from pyparsing import nestedExpr


class Token(NamedTuple):
    '''
    Class to represent a token of a string in 'tokenise' and 'eqn_tokenise'

    Attributes:
        type (str) : Type of symbol out of options in 'token_specification'
        value (str) : Substring of token
        index (int) : Start index of 'value' in main string
        end_index (int) : End index of 'value' in main string
    '''
    type: str
    value: str
    index: int
    end_index: int


def begin_doc(original_doc):
    '''
    Function to insert the todo package statement into the LaTeX document

    Parameters:
        original_doc (list) : List of lines within the original LaTeX document

    Returns:
        latex_doc (str) : Edited LaTeX document as a single string
    '''
    latex_doc = '\n'.join(original_doc)
    if bool(re.search(r'{todonotes}', latex_doc)) is True:
        return latex_doc
    begin_index = re.search(r'\\begin\{document\}', latex_doc).start()
    latex_doc = (latex_doc[:begin_index] +
                 '\\usepackage[color=white, bordercolor=black]{todonotes}\n' +
                 latex_doc[begin_index:])
    return latex_doc


def find_equations(token, delimiters):
    '''
    Function to find the math text within the given delimiters

    Parameters:
        token (str) : Token of text from LaTeX document
        delimiters (list) : Math text characters to search between

    Returns:
        equation (str) : Math text found between the delimiters (returns None
            if no delimiters are found)
    '''
    for delimiter in delimiters:
        if re.findall(delimiter, token) != []:
            equation = re.findall(delimiter, token)[0]
            if equation != '':
                return equation


def find_commands(equation):
    '''
    Function to identify '\' LaTeX commands within math text

    Parameters:
        equation (str) : Equation within math text

    Returns:
        commands (list) : List of identified commands within 'equation'
    '''
    commands = []
    for match in re.finditer(r'\\', equation):
        if equation[match.start() + 1] in ('{', '}', ':', ',', '%'):
            commands.append(equation[match.start() + 1])
            continue
        try:
            start_index = match.start()
            index = start_index + 1
            while True:
                try:
                    if equation[index] in ascii_letters:
                        index += 1
                    else:
                        break
                except IndexError:
                    break
            commands.append(equation[start_index + 1: index])
        except ValueError:
            pass
    return commands


def convert_commands(commands, symbols, converted_symbols):
    '''
    Function to convert the commands found in the math text to alt text

    Paramters:
        commands (list) : List of identified commands within the equation
        symbols (list) : List of LaTeX symbols in csv file
        converted_symbols (list) : List of alt text versions of 'symbols'

    Returns:
        converted (dict) : Dictionary of 'commands' with their alt text

    '''
    converted = {}
    if isinstance(commands, str):
        if commands != [] and commands in symbols:
            converted[commands] = converted_symbols[symbols.index(commands)]
        else:
            print(commands + ' not in CSV file.')
    else:
        for command in commands:
            if command != [] and command in symbols:
                converted[command] = converted_symbols[symbols.index(command)]
            else:
                print(command + ' not in CSV file.')
    return converted


def alt_commands(arg, track_commands, symbols, converted_symbols,
                 special_symbols):
    '''
    Function to convert the commands to alt text

    Parameters:
        arg (str) : Math text within brackets
        commands (list) : List of identified commands within the equation
        symbols (list) : List of LaTeX symbols in csv file
        converted_symbols (list) : List of alt text versions of 'symbols'
        special_symbols (dict) : Dictionary of math symbols to be replaced

    Returns:
        alt_equation (list) : Alt text of 'arg'
    '''
    alt_equation = []
    commands = find_commands(arg)
    for command in commands:
        if command in ('left', 'right', 'rm', 'text', ':', ','):
            continue
        converted = convert_commands(command, symbols, converted_symbols)
        if command in ('cos', 'sin', 'tan', 'arccos', 'arcsin', 'arctan',
                       'cosh', 'sinh', 'tanh', 'cot', 'sec', 'coth'):
            index = re.search(command, arg).end()
            try:
                if arg[index] == '^':
                    key, value = list(converted.items())[0]
                    convert_command = value.replace('of', '')
                    converted[command] = convert_command
            except IndexError:
                pass
        alt_command = multi_replace(arg, converted)
        alt_command = alt_symbols(alt_command, track_commands, special_symbols)
        alt_command = ''.join(flatten(alt_command))
        alt_equation.append(alt_command.replace('\\', ''))
    return alt_equation


def multi_replace(equation, replace_dict):
    '''
    Function to replace multiple substrings within 'equation'

    Parameters:
        equation (str) : Equation within math text
        replace_dict (dict) : Dictionary of substrings to be replaced

    Returns:
        replaced_eqn (str) : 'equation' with replaced commands and symbols
    '''
    dict_keys = [re.escape(k) for k in sorted(replace_dict, key=len,
                                              reverse=True)]
    pattern = re.compile("|".join(dict_keys), flags=re.DOTALL)
    replaced_eqn = pattern.sub(lambda x: replace_dict[x.group(0)], equation)
    replaced_eqn = replaced_eqn.replace('\\', ' ')
    return replaced_eqn


def convert_symbols(equation, index, value, track_commands, special_symbols):
    '''
    Function to convert symbols to alt text

    Parameters:
        equation (str) : Equation within math text
        index (int) : Index of 'value' in 'equation'
        value (str) : Symbol found in math text
        track_commands (list) : List of previous commands found in math text
        alt_equation (list) : Alt text of previous math text
        special_symbols (dict) : Dictionary of math symbols to be replaced

    Returns:
        alt_equation (list) : Alt text of 'value' added onto previous alt text
    '''
    symbol = []
    alt_equation = []
    try:
        if (track_commands[-1] == 'sum' or track_commands[-1] == 'int' or
                track_commands[-1] == 'prod'):
            if value == '^':
                if '^' not in symbol:
                    alt_equation.append(' to ')
                else:
                    alt_equation.append(' superscript ')
                symbol.append(value)
            elif value == '_':
                symbol.append(value)
                if equation[index + 1] == '{':
                    close_brac = len(next_bracket(equation, index + 1)[0])
                    if (equation[index + close_brac] != '^' and 
                            '^' not in symbol):
                        alt_equation.append(' over ')
                    else:
                        alt_equation.append(' from ')
                else:
                    if equation[index + 2] != '^' and '^' not in symbol:
                        alt_equation.append(' over ')
                    else:
                        alt_equation.append(' from ')
            else:
                alt_equation.append(multi_replace(value, special_symbols))
        elif value == '^' and 'prime' in equation[index+1:index+8]:
            alt_equation.append(' ')
        elif track_commands[-1] == 'log' and value == '_':
            alt_equation.append(' base ')
        elif value == '_' and equation[index - 1] == '|':
            alt_equation.append(' ')
        elif value == '|' and equation[index + 1] == '_':
            alt_equation.append(' evaluated at ')
        else:
            alt_equation.append(multi_replace(value, special_symbols))
    except IndexError:
        alt_equation.append(multi_replace(value, special_symbols))
    return alt_equation


def alt_symbols(equation, track_commands, special_symbols):
    '''
    Function to convert all of the special symbols within an equation

    Parameters:
        equation (str) : Equation within math text
        track_commands (list) : List of previous commands found in math text
        special_symbols (dict) : Dictionary of math symbols to be replaced

    Returns:
        alt_equation (str) : Equation string with all special symbols
            converted
    '''
    alt_equation = []
    for i, char in enumerate(equation):
        if char in special_symbols.keys():
            alt_equation.append(convert_symbols(equation, i, char, 
                                                track_commands, 
                                                special_symbols))
        else:
            alt_equation.append(char)
    return alt_equation


def check_brackets(equation):
    '''
    Function to check for open and closed parentheses in 'equation'

    Parameters:
        equation (str) : Equation within math text

    Returns:
        True - if 'equation' is valid; else False
    '''
    brackets = {}
    for i, char in enumerate(equation):
        if char in (r'{', r'}'):
            brackets[i] = char
    brackets_str = ''.join(brackets.values())

    if len(brackets_str)%2 != 0:
        return False
    par_dict = {'(':')', '{':'}', '[':']'}
    stack = []
    for char in brackets_str:
        if char in par_dict.keys():
            stack.append(char)
        else:
            if stack == []:
                return False
            open_brac = stack.pop()
            if char != par_dict[open_brac]:
                return False
    return stack == []


def next_bracket(equation, index):
    '''
    Function to find the equation string with complete brackets

    Parameters:
        equation (str) : Equation within math text
        index (int) : Index of the start bracket (or the index for the end of
            '\\frac' in the case of searching for fractions)

    Returns:
        complete (tup) : Tuple where the first element is the equation string
            containing complete brackets and the second element is the index
            of the closed bracket
    '''
    complete = []
    count = index + 1
    while count < len(equation):
        for _ in equation[index:]:
            if check_brackets(equation[index:count]) is True:
                complete.append((equation[index:count], count))
            count += 1
    return complete[0]


def flatten(eqn_list):
    '''
    Function to 'flatten' a list of strings and lists into one list of strings

    Parameters:
        eqn_list (list) : List of strings and strings within lists

    Returns:
        flattened (list) : List of items in 'eqn_list' as single list entries
    '''
    flattened = []
    for eqn in eqn_list:
        if isinstance(eqn, list):
            flattened.extend(flatten(eqn))
        else:
            flattened.append(eqn)
    return flattened


def nested_brackets(equation, track_commands, symbols, converted_symbols,
                    special_symbols):
    '''
    Function to find the elements within nested brackets

    Parameters:
        equation (str) : Equation within math text
        symbols (list) : List of LaTeX symbols in csv file
        converted_symbols (list) : List of alt text versions of 'symbols'
        special_symbols (dict) : Dictionary of math symbols to be replaced

    Returns:
        alt_equation (list) : List of alt text components within the brackets
    '''
    decomposed = []
    parser = nestedExpr(opener='{', closer='}')
    parts = parser.parseString(equation, parseAll=True).asList()[0]
    for i, part in enumerate(parts):
        if part[-1] == '^' or part[-1] == '_' and isinstance(parts[i+1], list):
            if len(parts[i+1]) < 2:
                continue
            else:
                parts.insert(i+1, '(')
                parts.insert(i+3, ')')
        if part == '\\sqrt':
            parts.insert(i+1, '(')
            parts.insert(i+3, ')')
        if '\\frac' in part:
            if len(parts[i+1]) < 3 and len(parts[i+2]) < 3:
                parts.insert(i+2, ' over ')
            else:
                parts.insert(i+2, ' and denominator ')
            parts.insert(i+4, ' end fraction ')
        if '\\left' in part:
            parts[i] = part.replace('\\left', ' ')
        if '\\right' in part:
            parts[i] = part.replace('\\right', ' ')
    decomposed = flatten(parts)
    alt_equation = []
    for part in decomposed:
        commands = find_commands(part)
        if commands != [] and (alt_commands(part, track_commands, symbols,
                                            converted_symbols,
                                            special_symbols) == []):
            continue
        if commands != []:
            alt_equation.append(alt_commands(part, track_commands, symbols,
                                             converted_symbols,
                                             special_symbols)[0])
        if commands == []:
            for char in part:
                if bool(re.match('[A-Z]', char)) is True:
                    capital_dict = {char: ' uppercase ' + char}
                    part = multi_replace(part, capital_dict)
                else:
                    pass
            alt_equation.append(multi_replace(part, special_symbols))
    return alt_equation


def tabular(table, delimiters, symbols, converted_symbols, special_symbols):
    '''
    Function to create alt text for a table in the LaTeX document

    Parameters:
        table (str) : String of text within the tabular environment
        delimiters (list) : Math text characters to search between
        symbols (list) : List of LaTeX symbols in csv file
        converted_symbols (list) : List of alt text versions of 'symbols'
        special_symbols (dict) : Dictionary of math symbols to be replaced

    Returns:
        alt_tab (str) : Alt text version of 'table'
    '''
    alt_text = []
    cols = next_bracket(table, 0)[0]
    separators = re.findall(r'c', cols)
    newlines = [match.start() for match in re.finditer(r'\\\\', table)]
    alt_text.append('\\todo[inline]{begin alt text. Table with ' +
                    str(len(separators)) + ' columns and ' +
                    str(len(newlines)) + ' rows.')

    row_indices = [match.end() for match in re.finditer(r'\\hline', table)]
    for i, index in enumerate(row_indices):
        try:
            eqn = table[index:row_indices[i+1]]
            if re.search(r'\n\n', eqn) is not None:
                eqn = eqn[re.search(r'\n\n', eqn).end():]
            and_indices = [char.start() for char in re.finditer(r'\&', eqn)]
            line_end = re.search(r'\\\\', eqn).start()
        except IndexError:
            continue
        except AttributeError:
            continue

        alt_text.append(eqn[:and_indices[0]])
        for j in range(1, len(and_indices)):
            if and_indices[j - 1] < and_indices[j]:
                alt_text.append(' and ')
                tab_entry = eqn[and_indices[j-1]+1:and_indices[j]]
                alt_text.append(tab_entry)
        alt_text.append(' and ')
        alt_text.append(eqn[and_indices[-1]+1:line_end])
        alt_text.append('next row')

    incl_delims = [r'(\$\$(.*?)\$\$)', r'(\$(.*?)\$)', r'(\\\((.*?)\\\))',
                   r'(\\\[(.*?)\\\])', r'(\\begin\{math\}(.*?)\\end\{math\})']

    alt_tab = []
    for element in alt_text:
        tab_eqn = find_equations(element, delimiters)
        if tab_eqn is not None:
            tab_eqn_delim = find_equations(element, incl_delims)[0]
            alt_eqn = (eqn_tokenise(tab_eqn, symbols, converted_symbols,
                                    special_symbols))
            alt_tab.append(element.replace(tab_eqn_delim, alt_eqn))
        else:
            alt_tab.append(element)
    if alt_tab[-1] == 'next row':
        alt_tab = alt_tab[:-1]
    alt_tab.append(' end alt text}')
    return alt_tab


def eqn_tokenise(equation, symbols, converted_symbols, special_symbols):
    '''
    Function to tokenise an equation within the LaTeX document

    Parameters:
        equation (str) : Equation within math text
        symbols (list) : List of LaTeX symbols in csv file
        converted_symbols (list) : List of alt text versions of 'symbols'
        special_symbols (dict) : Dictionary of math symbols to be replaced

    Returns:
        alt_equation (str) : Alt text version of 'equation'
    '''
    alt_equation = []
    track_commands = ['']
    track_symbols = ['']
    track_environ = ['']
    duplicates = []
    token_specification = [
        ('NUMBER',       r'\d+(\.\d*)?'),          # Integer or decimal
        ('ID',           r'[A-Za-z]+'),            # Words
        ('SYMBOL',       r'[_/\^/>/</\-///!/\|]'), # Special symbols
        ('OPEN_BRAC',    r'\\{'),                  # Curly bracket command
        ('CLOSE_BRAC',   r'\\}'),                  # Curly bracket command
        ('COLON',        r'\\:'),                  # Colon command
        ('BRACKET',      r'[\(/\)/\[/\]]'),        # Parentheses
        ('FRACTION',     r'\\frac'),               # \\frac
        ('DFRACTION',    r'\\dfrac'),              # \\dfrac
        ('BRACE',        r'\{(.*?\})'),            # Curly brackets
        ('AND',          r'\&'),                   # And
        ('NEWLINE',      r'\\\\'),                 # Newline
        ('COMMAND',      r'\\'),                   # Command statement
        ('MISMATCH',     r'.'),                    # Any other character
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    for match in re.finditer(tok_regex, equation):
        kind = match.lastgroup
        value = match.group()
        index = match.start()
        end_index = index + len(value)
        if len(duplicates) > 0 and index in duplicates[-1]:
            continue
        if kind == 'NUMBER':
            alt_equation.append(str(value))
        elif kind == 'ID':
            if value in symbols and value == track_commands[-1]:
                continue
            if equation[index - 1] == '^' and len(value) > 1:
                for letter in value:
                    if bool(re.match('[A-Z]', letter)) is True:
                        alt_equation.append(' uppercase ' + letter)
                    else:
                        alt_equation.append(letter)
            elif len(value) == 1 and bool(re.match('[A-Z]', value)) is True:
                alt_equation.append(' uppercase ' + value)
            else:
                alt_equation.append(value)
        elif kind == 'SYMBOL':
            track_symbols.append(value)
            if track_commands[-1] == 'lim' and value == '_':
                continue
            alt_equation.append(convert_symbols(equation, index, value,
                                                track_commands,
                                                special_symbols)[0])
        elif kind == 'OPEN_BRAC':
            alt_equation.append(value)
        elif kind == 'CLOSE_BRAC':
            alt_equation.append(value)
        elif kind == 'COLON':
            continue
        elif kind == 'BRACKET':
            alt_equation.append(value)
        elif kind in ('FRACTION', 'DFRACTION'):
            track_commands.append('frac')
            first_brac = next_bracket(equation, end_index)
            second_brac = next_bracket(equation, first_brac[1])
            list_first = nested_brackets(first_brac[0], track_commands,
                                         symbols, converted_symbols,
                                         special_symbols)
            list_second = nested_brackets(second_brac[0], track_commands,
                                          symbols, converted_symbols,
                                          special_symbols)
            alt_first = ''.join(list_first)
            alt_second = ''.join(list_second)
            if len(alt_first) < 3 and len(alt_second) < 3:
                alt_equation.append(alt_first + ' over ' + alt_second +
                                    ' end fraction ')
            else:
                alt_equation.append(' fraction with numerator ' + alt_first +
                                    ' and denominator ' + alt_second +
                                    ' end fraction ')
            duplicates.append(list(range(end_index, second_brac[1])))
        elif kind == 'BRACE':
            if track_commands[-1] == 'label' or track_commands[-1] == 'hspace':
                continue
            if value == '{equation}':
                continue
            if value == '{array}':
                if track_commands[-1] == 'end':
                    alt_equation.append(' End array environment. ')
                    continue
                track_environ.append('array')
                alt_equation.append(' Begin array environment. ')
                eqn_index = next_bracket(equation, end_index)[1] - 1
                duplicates.append(list(range(end_index, eqn_index)))
                continue
            if (equation[index - 1] == '^' or equation[index - 1] == '_' or
                    track_commands[-1] == 'sqrt'):
                alt_equation.append('(')
            arg = re.findall(r'\{(.*?)\}', value)[0]
            if '{' in arg:
                complete_brac = next_bracket(equation, index)
                alt_equation.append(nested_brackets(complete_brac[0],
                                                    track_commands, symbols,
                                                    converted_symbols,
                                                    special_symbols))
                duplicates.append(list(range(end_index, complete_brac[1])))
            else:
                commands = find_commands(arg)
                if commands != []:
                    convert = convert_commands(
                        commands, symbols, converted_symbols)
                    alt = multi_replace(arg, convert)
                    if ('dot' in track_commands[-1] or
                            'ddot' in track_commands[-1] or
                            'hat' in track_commands[-1]):
                        alt_equation.insert(len(alt_equation) - 1, alt)
                    else:
                        alt_equation.append(multi_replace(alt,
                                                          special_symbols))
                else:
                    if ('dot' in track_commands[-1] or
                            'ddot' in track_commands[-1] or
                            'hat' in track_commands[-1]):
                        alt_equation.insert(len(alt_equation) - 1, arg)
                    else:
                        alt_equation.append(multi_replace(arg,
                                                          special_symbols))
            if (equation[index - 1] == '^' or equation[index - 1] == '_' or
                    track_commands[-1] == 'sqrt'):
                alt_equation.append(')')
        elif kind == 'AND':
            if track_environ[-1] == 'array':
                alt_equation.append(' for ')
        elif kind == 'NEWLINE':
            if track_environ[-1] == 'array':
                alt_equation.append(' and ')
            else:
                alt_equation.append(' \n\n newline ')
        elif kind == 'COMMAND':
            try:
                command = find_commands(equation[index:])[0]
            except IndexError:
                continue
            track_commands.append(command)
            if command in ('left', 'right', 'rm', 'label', 'begin', 'end',
                           'text', 'nonumber', ',', 'quad'):
                continue
            if command == 'prime' and track_symbols[-1] == '^':
                alt_equation = alt_equation[:-1]
            converted = convert_commands(command, symbols, converted_symbols)
            alt_equation.append(multi_replace(command, converted))
        elif kind == 'MISMATCH':
            if value in track_commands[-1]:
                continue
            alt_equation.append(value)
#        yield Token(kind, value, index, end_index)
    alt_equation = ' '.join(flatten(alt_equation))
    return alt_equation


altex = []
def tokenise(latex_doc, delimiters, symbols, converted_symbols,
             special_symbols):
    '''
    Function to tokenise the LaTeX document

    Parameters:
        latex_doc (str) : LaTeX document (all as a single string)
        delimiters (list) : Math text characters to search between
        symbols (list) : List of LaTeX symbols in csv file
        converted_symbols (list) : List of alt text versions of 'symbols'
        special_symbols (dict) : Dictionary of math symbols to be replaced

    Returns:
        altex_doc (str) : Alt text verions of 'latex_doc'
    '''
    duplicates = []
    token_specification = [
        ('NUMBER',     r'\d+(\.\d*)?'),           # Integer or decimal number
        ('NEWLINE',    r'\n'),                    # Newline
        ('SKIP',       r'[ \t]+'),                # Skip over spaces and tabs
        ('ID',         r'[A-Za-z]+'),             # Words
        ('EQN_1',      r'\$\$(.*?)\$\$'),         # EQN_1-EQN_5 = delimiters
        ('EQN_2',      r'\$(.*?)\$'),
        ('EQN_3',      r'\\begin\{math\}(.*?)\\end\{math\}'),
        ('EQN_4',      r'\\\((.*?)\\\)'),
        ('EQN_5',      r'\\\[(.*?)\\\]'),
        ('EQN_6',      r'\\begin\{equation\}'),   # Begin{equation}
        ('END_EQN',    r'\\end\{equation\}'),     # End{equation}
        ('EQN_7',      r'\\begin\{align\}'),      # Begin{align}
        ('END_ALIGN',  r'\\end\{align\}'),        # End{align}
        ('BEGIN_TAB',  r'\\begin{tabular}'),      # Begin{tabular}
        ('END_TAB',    r'\\end{tabular}'),        # End{tabular}
        ('MISMATCH',   r'.'),                     # Any other character
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    for match in re.finditer(tok_regex, latex_doc):
        kind = match.lastgroup
        value = match.group()
        index = match.start()
        end_index = index + len(value)
        if len(duplicates) > 0 and index in duplicates[-1]:
            continue
        if kind in ('NUMBER', 'NEWLINE', 'SKIP', 'ID'):
            altex.append(value)
        elif kind in ('EQN_1', 'EQN_2', 'EQN_3', 'EQN_4', 'EQN_5'):
            equation = find_equations(value, delimiters)
            if bool(re.match('^[0-9]+$', equation)) is True:
                altex.append(value)
            else:
                alt_text = eqn_tokenise(equation, symbols, converted_symbols,
                                        special_symbols)
                altex.append(value)
                altex.append('\\todo[inline]{begin alt text ' + alt_text +
                             ' end alt text}')
        elif kind == 'EQN_6':
            end_equation = re.search(r'\\end{equation}', latex_doc[index:])
            end_index = end_equation.span()[1] + index
            equation = re.findall(
                r'(?s)\\begin\{equation\}(.*)\\end\{equation\}',
                latex_doc[index:end_index])[0]
            alt_text = eqn_tokenise(equation, symbols, converted_symbols,
                                    special_symbols)
            altex.append(value + '\n')
        elif kind == 'END_EQN':
            altex.append(value)
            altex.append('\\todo[inline]{begin alt text ' + alt_text +
                         ' end alt text}')
        elif kind == 'EQN_7':
            end_equation = re.search(r'\\end{align}', latex_doc[index:])
            end_index = end_equation.span()[1] + index
            equation = re.findall(
                r'(?s)\\begin\{align\}(.*)\\end\{align\}',
                latex_doc[index:end_index])[0]
            alt_text = eqn_tokenise(equation, symbols, converted_symbols,
                                    special_symbols)
            altex.append(value)
        elif kind == 'END_ALIGN':
            altex.append(value)
            altex.append('\\todo[inline]{begin alt text ' + alt_text +
                         ' end alt text}')
        elif kind == 'BEGIN_TAB':
            end_tab_span = (re.search(r'\\end{tabular}',
                                      latex_doc[end_index:]).span())
            end_tab = (end_tab_span[0] + end_index)
            alt_table = tabular(latex_doc[end_index:end_tab], delimiters,
                                symbols, converted_symbols, special_symbols)
            altex.append(latex_doc[index:end_tab_span[0] + end_index])
            duplicates.append(list(range(index, end_tab_span[0] + end_index)))
        elif kind == 'END_TAB':
            altex.append(value)
            altex.append(alt_table)
        elif kind == 'MISMATCH':
            altex.append(value)
#        yield Token(kind, value, index, end_index)
    altex_doc = ''.join(flatten(altex))
    return altex_doc
