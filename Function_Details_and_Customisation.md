# Function Details and Customisation:

This document outlines some of the functions in more detail, as well as giving suggestions on customisation and potential issues.

<ins>Contents</ins>

1. <code>begin_doc</code>
2. <code>find_equations</code>
3. <code>find_commands</code>
4. <code>convert_commands</code>
5. <code>alt_commands</code>
6. <code>multi_replace</code>
7. <code>convert_symbols</code>
8. <code>alt_symbols</code>
9. <code>check_brackets</code>
10. <code>next_bracket</code>
11. <code>flatten</code>
12. <code>nested_brackets</code>
13. <code>tabular</code>
14. <code>make_string</code>
15. <code>eqn_tokenise</code>
16. <code>tokenise</code>



## 1. <code>begin_doc</code>
    Function to insert the todo package statement into the LaTeX document

        Parameters:
            original_doc (list) : List of lines within the original LaTeX document

        Returns:
            latex_doc (str) : Edited LaTeX document as a single string

This function is able to search for an existing ['todo' package](http://tug.ctan.org/macros/latex/contrib/todonotes/todonotes.pdf) statement within the document, and will otherwise append this package. The default parameters for this package are:
- color = white
- bordercolor = black\
Alternative options can be found in the link above. The main statement structure must stay the same to be compatible with [LaTeX](https://www.overleaf.com/learn).

### Potential Issues:
An anticipated issue may be that the 'todo' package already exists within the document with different parameters to those that are desired. This will likely have to be edited manually in the LaTeX typset file to produce the appropriate results.

<ins>Issues with 'todo' Package:</ins> 
There is an issue when figures are involved - if there is math text at the bottom of a page, and a figure at the start of the next page, the alt text will come after the figure and its caption. Also, while the width of the alt text box is adjusted to be smaller for subfigures, if there are many figures in a subfigure, the alt text for the cation will go off the end of the page, hence not being visable or readable. A suggestion, outside the scope of this project, is to creata a LaTeX package with this functionality, allowing more freedom in customisation of the alt text. This would also aid in reading equation numbers.


## 2. <code>find_equations</code>
    Function to find the math text within the given delimiters

        Parameters:
            token (str) : Token of text from LaTeX document
            delimiters (list) : Math text characters to search between

        Returns:
            equation (str) : Math text found between the delimiters (returns None if no delimiters are found)

This function uses ['Regular Expression'](https://python.readthedocs.io/en/stable/library/re.html) searches within the text for common LaTeX typset delimiters. These delimiters include:
- \\$...\\$
- \\$\\$...\\$\\$
- \\(...\\)
- \\[...\\]
- \begin{math}...\end{math}
- \begin{equation}...\end{equation}
- \begin{align}...\end{align}
To search for a wider range of delimiters, some of which are shown below, simply add them to the <code>delimiters</code> list in <code>main</code> with the appropriate Regular Expression formatting.

### Potential Issues:
There are other LaTeX typset delimiters that have not been implemented into the code yet. Known examples include:
- \begin{displaymath}...\end{displaymath}
- \begin{equation*}...\end{equation*}
- \begin{align*}...\end{align*}
- \begin{gather}...\end{gather}
- \begin{gather*}...\end{gather*}
- \begin{eqnarray}...\end{eqnarray}
- \begin{eqnarray*}...\end{eqnarray*}


## 3. <code>find_commands</code>
    Function to identify '\' LaTeX commands within math text

        Parameters:
            equation (str) : Equation within math text

        Returns:
            commands (list) : List of identified commands within 'equation'

This function finds commands by searching for [letters](https://docs.python.org/3/library/string.html) after the backslash symbol, excepting either an <code>IndexError</code> or <code>ValueError</code> otherwise. Currently, this function looks for word commands (e.g. '\Psi', '\frac', etc.) and punctuation commands (e.g. '\{', '\:', etc.) separately.


## 4. <code>convert_commands</code>
    Function to convert the commands found in the math text to alt text

    Paramters:
        commands (list) : List of identified commands within the equation
        symbols (list) : List of LaTeX symbols in csv file
        converted_symbols (list) : List of alt text versions of 'symbols'

    Returns:
        converted (dict) : Dictionary of 'commands' with their alt text

This function takes the commands found from the previous function to convert them into alt text using 'LaTeX_Symbols'. To aid in debugging, the function returns <code>(command) not in CSV file</code> for commands that currently have no alt text, or include a typo or similar.


## 5. <code>alt_commands</code>
    Function to convert the commands to alt text

    Parameters:
        arg (str) : Math text within brackets
        commands (list) : List of identified commands within the equation
        symbols (list) : List of LaTeX symbols in csv file
        converted_symbols (list) : List of alt text versions of 'symbols'
        special_symbols (dict) : Dictionary of math symbols to be replaced

    Returns:
        alt_equation (list) : Alt text of 'arg'

This function uses the previous function to replace the commands with their alt text counterparts. The backslash before each command is also removed here. There are some special cases of commands that are dealt with here. 

<ins>Miscellaneous Commands:</ins>

As these commands do not add anything "visible" to the equation, they are skipped over in this function. These commands cannot be ignored in <code>find_commands</code>, for example, due to needing to deal with an associated equation element in a specific way - e.g. '\label' needs to be considered to know to skip over the equation's label given between '{...}' (see <code>eqn_tokenise</code> function).
This method applies to:
- 'left'
- 'right'
- 'rm'
- 'text'
- ':'
- ','

Other commands wanting to be skipped over can also be added to the list in this function.

<ins>Trigonometric Commands:</ins>

Assigned to each command in 'LaTeX_Symbols' is the most likely phrasing or formal symbol name. In the case of trigonometric functions, the alt text phrase involves the formal name of the trig function, followed by 'of'. However, in some cases, this will not be the most ideal phrasing. The case considered in this function is when the trig function is raised to a power. In which case, 'of' is removed from the alt text to produce 'sine superscript 2 ( x )', for example.
This method applies to:
- 'cos'
- 'sin'
- 'tan'
- 'arccos'
- 'arcsin'
- 'arctan'
- 'cosh'
- 'sinh'
- 'tanh'
- 'cot'
- 'sec'
- 'coth'


### Potential Issues:
There may be cases where a command that has not been included in the list of exceptions is included in the alt text. There may also be some other commands that require alternative treatment that may need to be added here. Also, it was noted that occasionally, the removal of 'of' from the alt text didn't work, the reason of which is unknown.


## 6. <code>multi_replace</code>
    Function to replace multiple substrings within 'equation'

    Parameters:
        equation (str) : Equation within math text
        replace_dict (dict) : Dictionary of substrings to be replaced

    Returns:
        replaced_eqn (str) : 'equation' with replaced commands and symbols

This function takes the dictionaries from the previous functions to convert the original math text into its alt text version. This involes a simple list comprehension, the <code>.replace()</code> method, and the <code>.sub()</code> function. Backslashes from commands are also removed here in the unlikely case they are not removed in the previous function.

### Potential Issues:
Issues will only arise in this function (e.g. raising an error if the <code>replace_dict</code> variable is an empty dictionary) if there are issues in the previous functions. Therefore, there are no known issues.


## 7. <code>convert_symbols</code>
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

Within this function is where most of the symbol alt text wording exceptions are made. This includes:
- When the previous command is one of 'sum', 'int', or 'prod':
    - if the symbol is '^' and it was not the last symbol to be used, then 'to' is added to the alt text, otherwise 'superscript' is added.
    - if the symbol is '_' and '^' is not present in this part of the equation, then 'over' is added to the alt text, otherwise 'from' is added.
- When the next command is 'prime':
    - if the symbol is '^', a single space is added to the alt text.
- When the previous command is 'log':
    - if the symbol is '_', 'base' is added to the alt text.
- When the symbol is '|':
    - if the next symbol is '_', 'evaluated at' is added to the alt text.

Otherwise, the symbols are converted with their formal names, shown in the list <code>special_symbols</code>, using  the previous functions.

### Potential Issues:
There is currently an issue with the first point above. Most of the time, the alt text that is returned, for example, is 'integral from x superscript y...'. Removing these statements and changing this alt text phrasing to 'integral subscript x superscript y...' would be a simpler solution, but leaves more interpretation up to the reader. This issue is due to the global list <code>symbol</code>, which is used to track if either '^' or '_' have been used yet. Making this a local variable leads to the result, for example, of 'integral from a to b x to 2' if the math text is '\int_a^b x^2'. There is also the issue of there being no limits at all, producing alt text similar to the example given here.

The other statements within this function rely on the LaTeX typeset being written in a particular way - e.g. without spacing between characters. In the case where the previous/next symbol is not found correctly, the returned alt text will include the formal symbol command names, likely leading to some inconsistency in phrasing throughout the document.


## 8. <code>alt_symbols</code>
    Function to convert all of the special symbols within 'equation'

    Parameters:
        equation (str) : Equation within math text
        track_commands (list) : List of previous commands found in math text
        special_symbols (dict) : Dictionary of math symbols to be replaced

    Returns:
        alt_equation (str) : Equation string with all special symbols
            converted

This function takes the whole equation string to find all of the special symbols and pass them through the previous function. Otherwise, the character is added back into it's place in the equation.


## 9. <code>check_brackets</code>
    Function to check for open and closed parentheses in 'equation'

    Parameters:
        equation (str) : Equation within math text

    Returns:
        True - if 'equation' is valid; else False

This function checks for fully closed brackets - '{' and '}' - in the equation string. This is paired with the next function, <code>next_bracket</code>, to return the string with "complete" brackets. This function can be edited to look for multiple types of brackets, given in the variable <code>par_dict</code>. It is currently set up to only check for '{' and '}' as these brackers are used with commands - i.e. '\frac{...}{...}'. The function only returns <code>True</code> if it contains "complete" brackets.


## 10. <code>next_bracket</code>
    Function to find the equation string with complete brackets

    Parameters:
        equation (str) : Equation within math text
        index (int) : Index of the start bracket (or the index for the end of
            '\\frac' in the case of searching for fractions)

    Returns:
        complete (tup) : Tuple where the first element is the equation string
            containing complete brackets and the second element is the index
            of the closed bracket

This function is paired with the previous function to incrementally add characters from the original equation string and pass it through <code>check_brackets</code> until it returns <code>True</code>.


## 11. <code>flatten</code>
    Function to 'flatten' a list of strings and lists into one list of strings

    Parameters:
        eqn_list (list) : List of strings and strings within lists

    Returns:
        flattened (list) : List of items in 'eqn_list' as single list entries

Due to all of the steps within the code producing alt text at different points, the result is often a list of lists of strings. This function "flattens" these lists out to create one list with only strings as its entries.

### Potential Issues:
There may be issues arising if there are further lists within lists, however these should be fixed due to the function being called within itself. Therefore, there are no known issues.


## 12. <code>nested_brackets</code>
    Function to find the elements within nested brackets

    Parameters:
        equation (str) : Equation within math text
        symbols (list) : List of LaTeX symbols in csv file
        converted_symbols (list) : List of alt text versions of 'symbols'
        special_symbols (dict) : Dictionary of math symbols to be replaced

    Returns:
        alt_equation (list) : List of alt text components within the brackets

This function takes the string with "complete" brackets from the previous functions to split the elements up within it. There are some symbol/command exceptions that are dealt with here. Also, '\left' and '\right' are removed here. 

<ins>Subscripts and Superscripts:</ins>

When the symbols '^' or '_' are found, if the length of the next <code>part</code> (i.e. the argument that is in the subscript or superscript) is more than 2, then parentheses are added around the argument. This is to ensure that it is clear when the subscript/superscript ends. This is not applied to arguments that are less than 2 characters as this might cause confusion between powers and index notation, for example.

#### Potential Issues:
There are some cases where there are brackets added around a single index subscript/superscript. One such case is when the writer adds these brackets themselves - i.e. 'x^{m}' produces 'x superscript ( m )'. However, within context, the user could be able to determine whether a subscript/superscript is intended to be a power or an index.

<ins>Roots:</ins>

With similar reasons to the previous point, brackets are added around the argument of the root to indicate the end of the root. 

<ins>Fractions:</ins>

If the fraction command is found, it is known that the next two elements in <code>parts</code> will be the numerator and denominator respectively (due to the way in which the expression is separated at each bracket). If both the numerator and denominator are less than 3 characters long, then the fraction is worded as 'x over y end fraction'. Otherwise, it has the usual wording of 'fraction with numerator x and denominator y'. The 'end fraction' is added in both cases to be excplicit as to where the fraction ends - e.g. '\frac{x}{yz}' and '\frac{x}{y}z' both produce 'x over y z' if the 'end fraction' phrasing is not added.

The rest of this function involves using the previous functions to convert the remaining commands and symbols to their alt text counterparts. There is also a statement to add 'uppercase' to the alt text for capital letters.


### Potential Issues:
In LaTeX typeset, when the argument of the superscript/subscript is an index, parantheses are sometimes added around these characters by the writer. This would then make the argument at least 3 characters long, leading the code to add another set of parentheses around it.
The code also currently is not set up to deal with different powered roots - i.e. '\sqrt[3]{xyz}'. This will likely return 'root of ( [3] ) xyz' as the square and curly brackets will be separate elements in <code>parts</code>.
Only fractions within fractions can be converted correctly here. If there is a further fraction within either of the arguments, or similarly more braces, this function does not work.
Lastly, combinations of uppercase and lowercase letters that are in the same <code>part</code> will not get recognised in the last conversion statement for capital letters. For example, '\frac{dY}{dX}' in some cases (e.g. inside nested brackets) will produce the alt text 'dY over dX end fraction', instead of the desired output 'd uppercase Y over d uppercase X end fraction'.


## 13. <code>tabular</code>
    Function to create alt text for a table in the LaTeX document

    Parameters:
        table (str) : String of text within the tabular environment
        delimiters (list) : Math text characters to search between
        symbols (list) : List of LaTeX symbols in csv file
        converted_symbols (list) : List of alt text versions of 'symbols'
        special_symbols (dict) : Dictionary of math symbols to be replaced

    Returns:
        alt_tab (str) : Alt text version of 'table'

This function deals exclusively with tables, both with and without math text contained within. This is due to tables being a common feature in scientific papers, and are usually not interpreted well by screen readers.

<ins>Columns and Rows:</ins>

This function takes the first set of braces (curly brackets) after '\begin{tabular}' where the amount of columns and line formatting are specified. The amount of columns is determined by counting the number of 'c's in this first brace, and the number of rows by counting the number of newline commands - '\\\\'. The alt text then starts by stating the amount of columns and rows - e.g. 'Table with x columns and y rows'.

<ins>'And's and 'Newline's:</ins>

To find where each element within a row and where each row is separated, the function starts by finding '\hline' on each row of the table. The index of the newline command - '\\' - is then found, which determines the entire string for that row. Within this row, the indices for the '&' commands are found and added to <code>and_indices</code>. Between each element, separated by '&', the phrase 'and' is added to alt text. And between each row, 'next row' is added to alt text.

<ins>Element Alt Text:</ins>

The last step involves converting the table elements to alt text. For elements that do not include any math text, including the alt text already added, they are simply added to the alt text without any changes. For elements including math text, a new set of delimiters are defined, where the delimiter symbol itself is included in the Regular Expression. This allows alt text for the math text _within_ the delimiters to be found, and then the whole expression, including the delimiters, to be replaced in the original string. This allows both standard and math text to be present within the same element.

### Potential Issues:
This function requires the table typeset to be given in a particular way. In the column specification, each column should be indicated by 'c', with or without '|' separating them. Cases where the columns are specified in an alternative way - e.g. adding a width specification - will not be recognised. 
It also requires rows to be separated by '\hline' in order to determine where each row starts and ends.
Lastly, using the newline command within a cell will lead to misinterpretations of where each row starts/ends. This therefore produces the incorrect amount of rows at the start of the alt text, and incorrect alt text throughout the table. 


## 15. <code>eqn_tokenise</code>
    Function to tokenise an equation within the LaTeX document

    Parameters:
        equation (str) : Equation within math text
        symbols (list) : List of LaTeX symbols in csv file
        converted_symbols (list) : List of alt text versions of 'symbols'
        special_symbols (dict) : Dictionary of math symbols to be replaced

    Returns:
        alt_equation (str) : Alt text version of 'equation'

This function takes the expressions found between the math text delimiters and deals with each element separately. The elements are sorted into one of 14 types, as defined in <code>token_specification</code>. The order in which these token types are called is important.

<ins><code>NUMBER</code>:<ins>

This Regular Expression searches for any integer or decimal. When found, it will be appended to the alt text as a string. It must be a string so that the alt text can be formatted correctly, otherwise a <code>TypeError</code> is called when using the 'flatten' function.

<ins><code>ID</code>:<ins>

This Regular Expression searches for words or combinations of letters - both uppercase and lowercase. As the code is set up to search for commands by searching for a single backslash, the command word itself will be identified here. Hence, a statement checking if the word is in <code>track_commands</code> allows such words to be skipped. This is also where a single uppercase character will be given the alt text phrasing 'uppercase X', for example. One extra instance that is specified here is if these uppercase characters are in a superscript. All other words are appeneded to the alt text as their original value.

#### Potential Issues:
A further addition to the code would be to apply this uppercase condition to other expressions - e.g. '\frac{dX}{dY}' - as mentioned in <code>nested_brackets</code> above. Also, separating each character, for a sequence of characters that do not make up a word, would be useful in allowing the screen reader to interpret the alt text correctly

<ins><code>SYMBOL</code>:<ins>

This Regular Expression searches for the characters listed in <code>special_symbols</code>: '_', '^', '>', '<', '-', '/', '!', and '|'. Each symbol that is found is added to <code>track_symbols</code> in order to determine the phrasing for other elements within the expression. The symbol is converted using <code>convert_symbols</code> and appended to the alt text. The only exception that is dealt with here is skipping over converting '_' if the previous symbol was 'lim'.

#### Potential Issues:
The only issues that would arise here are if extra symbols are added with the incorrect Regular Expression, or errors are occuring in one of the other functions that deal with converting symbols. The <code>IndexError</code> is avoided here due to the <code>track_commands</code> list starting with an empty string as it's first element.

<ins><code>OPEN_BRAC</code>:<ins>

This Regular Expression searches for the open brace command. This brace, along with its backslash, are simply added to the alt text to ensure that it is visible in the compiled LaTeX typeset version.

<ins><code>CLOSE_BRAC</code>:<ins>

This Regular Expression searches for the close brace command. As with <code>OPEN_BRAC</code>, this symbol is added to the alt text. Both <code>OPEN_BRAC</code> and <code>CLOSE_BRAC</code> need to be searched for separately (and before <code>BRACE</code> below) so that they are not considered in <code>BRACE</code>.

<ins><code>COLON</code>:<ins>

This Regular Expression searches for the colon command. When this token type is found, it is skipped over. This is because it only adds a single space between expression components. Other commands - e.g. '\quad', '\hspace', etc - that add multiple spaces to an expression, and are usually used to separate individual expressions, have the wording '(text spacing)'. This is to ensure that separate equations within the same math text delimiters are not confused with one equation. 

<ins><code>BRACKET</code>:<ins>

This Regular Expression searches for sets of open and close parentheses: '(', ')', '[', and ']'. These symbols are added to the alt text, as they can be read by the screen reader.

<ins><code>FRACTION</code>:<ins>

This Regular Expression searches for tbe '\frac' command. Firstly, 'frac' is added to the <code>track_commands</code> list. Each argument of the fraction - i.e. the numerator and denominator - is converted to alt text using the <code>next_bracket</code> and <code>nested_brackets</code> functions. This ensures that the expressions are found between "complete" brackets (see <code>BRACE</code> below). Here, the alt text phrasing for the fraction, depending on its complexity, is added to the alt text. If the length of both of the arguments are less than 3 characters long, then the phrasing 'x over y end fraction' is used. Otherwise, the usual phrasing 'fraction with numerator x and denominator y end fraction' is used. As this token only finds the '\frac' command itself, the code would otherwise continue through each character of the fraction arguments to convert it to alt text. Therefore, each index between the end index of '\frac' and the index of the close brace of the denominator argument are added to <code>duplicates</code> in order to be skipped over.

#### Potential Issues:
There may be some inconsistency with phrasing for fractions, as this section only applies to fractions that are outside of brackets. Hence, fractions that are within multiple brackets, or other fractions, may not be converted correctly (see <code>nested_brackets</code>).

<ins><code>DFRACTION</code>:<ins>

This Regular Expression searches for the '\dfrac' command. This command is dealt with in the same way as <code>FRACTION</code>.

<ins><code>BRACE</code>:<ins>

This Regular Expression searches for text between braces, including the delimiters themselves. There are some conditions here in which the rest of this loop is skipped over. This applies if the expression within the braces is 'equation', or if the previous command was 'label' or 'hspace'. The rest of this function then involves dealing with some specific cases, including:
- The expression within the braces is 'array':
    - If the previous command is 'end', indicating that the array environment has been closed, then 'End array environment' is added to the alt text and the rest of the loop is skipped.
    - 'array' is then added to the <code>track_environ</code> list to deal with other elements within this environment in a specific way.
    - 'Begin array environment' is then added to the alt text, once it has been determined that this brace is the start of the array environment.
- The previous character is '^' or '_', or the previous command is 'sqrt':
    - '(' is added to the alt text. This is due to the current expression, i.e. the argument of the subscript, superscript, or root, being within the braces, indicating that it is more than one character long. 
    - The same statement is also added at the end of this section to add ')' to the alt text, after all of the conversion within the braces has been added.
- There is a '{' within the expression contained within the braces delimiters:
    - This indicates that there are nexted brackets. Hence the "complete" brackets are found and converted to alt text using the <code>next_bracket</code> and <code>nested_brackets</code> functions.
    - The range of indices between the end index of this brace and the index of the close brace that "completes" the brackets is then added to <code>duplicates</code> to skip over in this function.
- There is no '{' within the expression contained within the braces delimiters:
    - Firstly, the commands within this expression are found, converted, and replaced in the original argument.
    - If 'dot', 'ddot', or 'hat' are amongst these commands, then the alt text for these commands are added after the next expression element - i.e. '\dot{y}' has the alt text 'y dot'. Otherwise, the commands and symbols are replaced with their appropriate alt text using <code>multi_replace</code>. 

#### Potential Issues:
Many of the issues that are experienced come from this section of the function, but usually arise in the earlier functions. Following the debugging advice in the 'README' document will allow for the exact area in which the issue is occuring to be found.

<ins><code>AND</code>:<ins>

This Regular Expression searches for the ampersand command. If 'array' is the last element in <code>track_environ</code>, then 'for' is added to the alt text. This is because the code is designed to only treat expression within the array environment as piecewise functions (see 'Examples').

#### Potential Issues:
An edit that could be made to the code is to deal with a variety of uses for the array environment. For example, if this environment is being used to create a table in math mode, then the above wording may not be appropriate.

<ins><code>NEWLINE</code>:<ins>

This Regular Expression searches for the newline command - double backslash. Similar to the reasoning above, as the code treats expressions within the array environment as piecewise functions only, 'and' is added to the alt text when the newline command is identified. Otherwise, '\n\n newline' is added. This ensures that cases where this newline command is found outside the array environment are still considered. 

<ins><code>COMMAND</code>:<ins>

This Regular Expression searches for the backslash symbol indicating the start of a command. Within this section, the command is found using <code>find_commands</code> and added to <code>track_commands</code>. Commands that are not needed within the alt text are then skipped over. This applies to:
- 'left'
- 'right'
- 'rm'
- 'label'
- 'begin'
- 'end',
- 'text'
- 'nonumber'
- ','
- 'quad'

As mentioned previously, it is important to do this step after they have been added to <code>track_commands</code>, as subsequent expression elements may need to be treated in a different way. Another exception here is if the command is 'prime' and the final element in the <code>track_symbols</code> list is '^'. This will then remove the 'superscript' already added to the alt text in order to produce, for example, 'y prime' instead of 'y superscript prime'. <code>track_symbols</code> also has its first element as an empty string in order to avoid <code>IndexError</code>. Otherwise, all of the commands are converted to their counterpart in 'LaTeX_Symbols' and added to the alt text.

#### Potential Issues:
If there are unwanted commands that are added to the alt text, it is likely that they are not being skipped over. For example, 'left' and 'right' sometimes appear in the alt text, particularly when within nested brackets. A solution to this could be to change the alt text within 'LaTeX_Symbols' to a space, ensuring that if the command is not skipped over, it only adds a single space to the alt text. These spaces have no effect on the compiled version of the LaTeX typeset as a built-in feature of LaTeX is to treat multiple spaces as a single space.

Another issue are commands, such as '\polylongdiv', that produce math text only in the compiled version of the LaTeX typeset, and not the typeset itself. There is currently no way for the code to interpret these cases, except by giving an explanation of the command functionality as its alt text. For this example of '\polylongdiv', a separate function could be created to take its two arguments and determine the calculations, and hence produce some form of alt text.    

<ins><code>MISMATCH</code>:<ins>

This Regular Expression searches for any other character. Most of the characters found within the equation will fit into one of the categories above. Characters, such as punctionation, spaces, etc, are added to the alt text, unless the character is in <code>track_commands</code>. This is to avoid any characters that have already been dealt with. Most screen readers, with correct settings, will be able to read the punctionation added here - i.e. 'f ( x, y )' is read as 'f open parentheses x comma y close paraentheses'.

#### Potential Issues:
There may be some characters that have not been considered yet that would also need to be skipped over here. In which case, another statement could be added here to ensure this. Further, it may be easier to also give punctuation alt text to ensure all screen readers can interpret the alt text correctly. In the example above, the alt text could instead be 'f ( x comma y)'.


## 16. <code>tokenise</code>
    Function to tokenise the LaTeX document

    Parameters:
        latex_doc (str) : LaTeX document (all as a single string)
        delimiters (list) : Math text characters to search between
        symbols (list) : List of LaTeX symbols in csv file
        converted_symbols (list) : List of alt text versions of 'symbols'
        special_symbols (dict) : Dictionary of math symbols to be replaced

    Returns:
        altex_doc (str) : Alt text verions of 'latex_doc'

This is the main function for this code, which takes the whole LaTeX document, with the 'todo' statement already added from <code>begin_doc</code>. As with the previous function, each element within this string is considered separately, by being sorted into one of 16 types, as defined in <code>token_specification</code>. Again, the order in which these token types are called is important.

<ins><code>NUMBER</code>/<code>NEWLINE</code>/<code>SKIP</code>/<code>ID</code>:<ins>

These Regular Expressions search for: integers or decimal numbers, newlines, spaces or tabs, and words or consecutive characters respectively. Each character found matching one of these categories is added to the alt text.

<ins><code>EQN_1</code>/<code>EQN_2</code>/<code>EQN_3</code>/<code>EQN_4</code>/<code>EQN_5</code>:<ins>

These Regular Expressions search for the delimiters: '\$\$...\$\$', '\$...\$', '\begin{math}...\end{math}', '\(...\)', '\[...\]' respectively. Firstly, the expression within these delimiters is found using <code>find_equations</code>. In the case that numbers are the only elements within this expression, no alt text is needed, so it is added to the alt text - i.e. without a 'todo' statement. This is because the screen reader can recognise the numbers without an alt text statement. Otherwise, the math text is passed through <code>eqn_tokenise</code>, and added back into the document string with its alt text. This is where the 'todo' statement is added around the alt text string. This includes 'begin alt text' and 'end alt text' at the start and end of the string respectively. Some indication is needed to signal to the user where the alt text starts and ends due to the screen reader likely attempting to read the formatted equation. If it is more desirable that the alt text be presented in a different format, the string can either be edited here, or in <code>begin_doc</code>.

#### Potential Issues:
When adding further delimiters, examples of which are given in <code>find_equations</code> above, the order must be considered. For example, double dollar signs must be searched for before single dollar signs, otherwise the double dollar sign will be mistakenly recognised as a delimiter with no equation between it. Also, delimiters that are likely to start and end on different lines will need to be treated similarly to <code>EQN_6</code> below.

Another issue may be dollar signs included in the LaTeX typeset that are not being used as delimiters. Due to the way in which equations are found with Regular Expression, these dollar sign commands will be treated as an equation delimiter.

<ins><code>EQN_6</code>:<ins>

This Regular Expression searches for the start delimiter '\begin{equation}'. Firstly, the index for the '\end{equation}' statement is found here, so that the expression between these statements can be found and passed through <code>eqn_tokenise</code> as one string. This '\begin{equation}' statement is then added back into the alt text. The rest of the math text, up to '\end{equation}', does not need to be added to <code>duplicates</code> as it still needs to be added back into the document to appear in the compiled version of the LaTeX typeset. 

<ins><code>END_EQN</code>:<ins>

This Regular Expression searches for the end delimiter '\end{equation}'. This statement is firstly added to the alt text to close the math environment. As there would be no other math environment called between '\begin{equation}' and '\end{equation}', the previous <code>alt_text</code> variable still has its value as the alt text for this delimiter. Hence, it is then added to the document, with the 'todo' statement around it.

<ins><code>EQN_7</code>:<ins>

This Regular Expression searches for the start delimiter '\begin{align}'. This section has the same funtion as <code>EQN_6</code>, instead searching for the align environment. 

<ins><code>END_ALIGN</code>:<ins>

This Regular Expression searches for the end delimiter '\end{align}'. This section has the same function as <code>END_EQN</code>, instead searching for the align environment.

<ins><code>BEGIN_TAB</code>:<ins>

This Regular Expression searches for the statement '\begin{tabular}'. This will create alt text for all tables, whether they include math text or not. The index for '\end{tabular}' is found so that the whole expression between these two statements is passed through the <code>tabular</code> function. The LaTeX typeset for this table is then added to the document. The indices between these two statements are added to <code>duplicates</code>, as if there is math text present within the table, one of the other <code>token_specification</code> categories will also convert it to alt text. Hence, it should be skipped over.

#### Potential Issues:
This section only works for tables that are specified with the '\begin{tabular}' and '\end{tabular}' statements. Other methods of creating a table - e.g. '\begin{table}', '\begin{array}', etc - will not work with this function

<ins><code>END_TAB</code>:<ins>

This Regular Expression searches for the statement '\end{tabular}'. This section has the same function as <code>END_EQN</code>, instead searching for the tabular environment.

<ins><code>MISMATCH</code>:<ins>

This Regular Expression searches for any other character. These characters are added to the alt text document. 

#### Potential Issues:
There may be some characters that have not been considered yet that would also need to be skipped over here. In which case, another statement could be added here to ensure this.


## LaTeX_Symbols
This file includes the list of math-mode commands and their alt text versions. The most common symbols used in physics fields from a [comprehesive list](https://texdoc.org/serve/symbols-a4.pdf/0) were selected. Most symbols use their formal names - e.g. '|' has 'vertical bar' as the alt text, instead of 'evaluated at' or 'absolute value' etc. - with alternatives included in the code for exceptions.

### Adding to LaTeX_Symbols:
The first column includes the symbol as used in LaTeX typset. The new command should be added to the appropriate section (section headings in column 5) or to the miscellaneous section. The second column incluses the symbols' alt text. Add the alt text for the new symbol with a space at the start and end - this ensures that words are separated in the final document alt text. If a command has no alt text - e.g. similar to '\left', '\label', etc - a single space can be added in this column instead.
