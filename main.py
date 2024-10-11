"""
The purpose of this program is to transpile mkt scripts into highly efficient, platform independent c (or cuda) scripts
The user can then compile the C/Cuda script into machine code

The idea behind the compiler is that all checks are done at compile time, meaning there
are no runtime errors (unless using inline assembly)

The compiler will also apply heavy optimizations to the program, including algorithmic optimization

"""

DEBUG = True

def debug(message:str):
    if DEBUG:
        print(message)

# keep a list of exceptions to display just before writing the output
class ErrorMessage:
    def __init__(self):
        self.type = "N/A"
        self.line_number = "0"
        self.line = ""
        self.cause = "The cause is unkown..."
        self.suggestions = "Good Luck!"

    def __str__(self):
        result = "-" * 80
        result += "\n"
        result += f"ERROR: ({self.type}) in line {self.line_number}:\n"
        result += f"LINE: \n\t{self.line}\n"
        result += f"CAUSE: \n\t{self.cause}\n"
        result += f"SUGGESTIONS: \n\t{self.suggestions}\n"
        return result


RESERVED_WORDS = set(["int", "bool", "float", "short", "long", "double", "char", "void", "class", "public", "private", "protected", "extends", "return", "if", "for", "while", "import", "as", "use", "try", "catch", "switch", "case", "else", "new", "asm", "static", "extends"])


class Line:
    """
    A single line of code.
    """
    def __init__(self, tokens: list[str]):
        self.tokens = tokens

    def __str__(self):
        return self.tokens.__str__()


class Block:
    """
    A simple block of code.
    contains its own scope and is enclosed in {}
    """
    def __init__(self, lines:list[str]):
        self.lines = lines

    def print(self):
        for line in self.lines:
            print(line)
        print()

    def __str__(self):
        return self.lines.__str__()


class Class(Block):
    """
    A class.
    """
    def __init__(self, class_name:str, parents:list[str], lines:list[str]):
        Block.__init__(self, lines)
        self.name = class_name
        self.parents = parents
        self.subclasses = []

    def print(self):
        print(self.__str__())
        print(f"extends: {self.parents}")
        Block.print(self)

    def __str__(self):
        return f"class {self.name} ({len(self.lines)} lines)"


class Function(Block):
    """
    A single function.
    """
    def __init__(self, function_name:str, lines:list[str]):
        Block.__init__(self, lines)
        self.name = function_name


class Compiler:
    def __init__(self, filename:str):
        self.EXCEPTIONS = []

        self.data = self.open_file(filename)
        self.tokens = self.tokenize(self.data)
        self.handle_broken_lines()
        self.remove_semicolons()
        self.preprocess()

    def open_file(self, filename:str):
        debug("Attempting to open the file...")
        try:
            with open(filename, 'r') as f:
                data = f.read()
        except:
            print(f"Error opening file {filename}")
        debug("Finished reading file!")
        return data 


    def add_error(self, line: Line, error_type: str, cause: str, suggestions: str):
        # TODO: implement different types of errors
        result = ErrorMessage()
        result.type = error_type
        result.line_number = self.parse_line_number(line)
        if result.line_number == "0":
            result.line = "ERROR while fetching line"
        else:
            try:
                result.line = self.data.split("\n")[int(result.line_number)]
            except:
                result.line = "ERROR while fetching line"
        result.cause = cause
        result.suggestions = suggestions
        self.EXCEPTIONS.append(result)

    def parse_line_number(self, line: Line):
        if len(line.tokens) > 0:
            if len(line.tokens[0]) > 0 and line.tokens[0][0] == '`':
                return line.tokens[0][1:]
        return "0"

    def tokenize(self, lines:list[str]):
        debug("Tokenizing the source file...")

        break_tokens = ["\n", "*", "$", "#", ".", ",", "[", "]", "<", ">", "&", "|", "\t", " ", "~", "^", "(", ")", "@", "%", "/", "=", "+", "-", ";", "'", '"', "{", "}"]
        break_tokens = set(break_tokens)

        result = []
        current_token = ""
        quotes = 0
        comment = 0
        multi = 0
        doc = 0

        current_line = 1

        for i in range(len(lines)):
            if lines[i] in break_tokens:


                # toggle whether or not we are in quotes
                if lines[i] == '"':
                    isChar = False
                    if len(lines) > i+1 and i > 0:
                        if lines[i-1] == "'" and lines[i+1] == "'":
                            isChar = True

                    if not isChar:
                        quotes ^= 1
                        quotes &= 1


                if not quotes:
                    # toggle whether or not we are in a comment
                    if lines[i] == "/":
                        if len(lines) > i+1:
                            if lines[i+1] == "*":
                                if comment == 0:
                                    multi = 1
                                comment = 1
                        if i > 0:
                            if lines[i-1] == "*":
                                if multi:
                                    comment = 0
                                    multi = 0
                                    continue
                            elif lines[i-1] == "/":
                                if not multi:
                                    comment = 1
                                    multi = 0
                    if lines[i] == "@":
                        if len(lines) > i + 1:
                            if comment == 0:
                                multi = 1
                            comment = 1
                            doc = 1

                # you found the end of a documentation block
                if lines[i] == "}":
                    if doc:
                        multi = 0
                        comment = 0
                        doc = 0
                        continue

                
                if quotes:
                    current_token += lines[i]
                else:
                    if len(current_token) > 0:
                        if lines[i] == '"':
                            current_token += '"'
                        if not comment:
                            result.append(current_token)

                    match (lines[i]):
                        case '"':
                            pass
                        case " ":
                            pass
                        case "\t":
                            pass
                        case "\n":
                            if comment:
                                if not multi:
                                    comment = 0
                                    del result[-1]
                                    result.append(lines[i])
                            else:
                                result.append(lines[i])
                        case default:
                            if not comment:
                                result.append(lines[i])

                    current_token = ""

                # save the line number for error messages
                if lines[i] == "\n":
                    result.append(f"`{current_line}")
                    current_line += 1

            else:
                current_token += lines[i]

        if current_token != "":
            result.append(current_token)
        
        debug("Comments are now removed!")
        debug("Finished tokenizing!")

        return result


    def handle_broken_lines(self):
        # handle lines that are broken
        # onto multiple lines using \
        # at the end of a line
        
        debug("Handling lines broken with \\ ...")
        # do this by finding "//" token directly before \n token
        quotes = 0

        i = 0
        n = len(self.tokens)
        while i < n:
            if self.tokens[i] == '"':
                quotes ^= 1
                quotes &= 1
            if self.tokens[i] == '\n' and i > 0:
                if self.tokens[i-1] == '\\':
                    del self.tokens[i-1]
                    del self.tokens[i-1]
                    i -= 1
                    n -= 2
                    continue
            i += 1
        debug("Broken lines have been handled!")


    def remove_semicolons(self):
        # remove all semicolons.
        # can ignore whether or not we are in quotes since
        # strings are tokenized together
        debug("Removing semicolons...")
        i = 0
        n = len(self.tokens)
        while i < n:
            if self.tokens[i] == ";":
                if n > i + 1:
                    # if the semicolon separates two statements
                    if self.tokens[i+1] != "\n":
                        self.tokens[i] = "\n"
                        i += 1
                        continue
                # otherwise, just remove the semicolon
                del self.tokens[i]
                i -= 1
                n -= 1
            i += 1
        debug("Semicolons have been removed!")

    
    def check_variable_name(self, line:Line, var_name:str):
        # check to make sure that a variable name follows naming standards
        
        pass



    def preprocess(self):
        # The tokens are currently an abstracted blob.
        # create a similar level of abstraction here and check the syntax
        # warn the programmer if there are any errors
        # after preprocessing, we can focus on optimizing
        
        # the first thing we will do is iterate through each line and convert it to the correct class
        debug("Preprocessing...")

        result = []

        i = 0
        n = len(self.tokens)

        curr_line = []
        while i < n:
            if self.tokens[i] == "\n":
                # ignore lines with nothing on them (except for the line number)
                if len(curr_line) == 1 and len(curr_line[0]) > 0 and curr_line[0][0] == "`":
                    pass
                else:
                    if len(curr_line) != 0:
                        result.append(Line(curr_line))
                curr_line = []
            else:
                curr_line.append(self.tokens[i])

            i += 1
        
        # we should now have a list of Line objects (and no more newlines in our tokens)

        self.classes = []

        global_scope = [1] * len(result)

        # now we should convert some of those lines into classes
        i = 0
        n = len(result)
        while i < n:
            # first, remove all saved line numbers
            curr = result[i].tokens.copy()
            j = 0
            while j < len(curr):
                if len(curr[j]) > 0:
                    if curr[j][0] == '`':
                        del curr[j]
                        j -= 1
                j += 1

            print(curr)

            m = len(curr)
            if m > 0:
                # check if this is a class definition
                match (curr[0]):
                    case "public":
                        # check if this is a class definition
                        if "class" in curr:
                            # if the next token is not the "class" keyword, throw an error
                            if curr[1] != "class":
                                # handle different cases 
                                handled = 0
                                if "static" in curr:
                                    self.add_error(result[i], "SYNTAX", "Classes cannot be defined as static...", "Remove the keyword static from this line.")
                                    handled = 1
                                if "private" in curr:
                                    self.add_error(result[i], "SYNTAX", "You cannot define a class as both public and private...", "Remove access modifiers until \n\tthere are less than two of them...")
                                    handled = 1
                                if "protected" in curr:
                                    self.add_error(result[i], "SYNTAX", "You cannot define a class as both public and protected...", "Remove access modifiers until \n\tthere are less than two of them...")
                                    handled = 1

                                # put at least some error message
                                if handled == 0:
                                    self.add_error(result[i], "SYNTAX", "Incorrect syntax...\n\tExpected 'class' after 'public'...", "Fix it or something?")


                            else: # the next token is class
                                # the next token should be the name of the class
                                if m < 3:
                                    self.add_error(result[i], "SYNTAX", "Incorrect syntax...\n\tExpected a class name after 'class'...", "Add a unique name for this scope.")
                                else:
                                    class_name = curr[2]
                                    
                                    # throw an error if the class is not named correctly
                                    self.check_variable_name(curr, class_name)

                                    # the next token should be extends or {
                                    if m < 4:
                                        self.add_error(result[i], "SYNTAX", "Incorrect syntax...\n\tExpected either '{' or 'extends' after class name...", "Fix it...")
                                    else:
                                        # this is the end of the class definition
                                        if curr[3] == "{":
                                            # TODO: act as though anything else on this line is on the next line

                                            # for now, just start gathering lines into a class block
                                            # iterate through each token, trying to find the matching }
                                            inner_lines = []

                                            j = i + 1
                                            number_of_lines = len(result)
                                            opens = 1
                                            # iterate through lines until the end of the file
                                            while j < number_of_lines:
                                                k = 0
                                                tokens_len = len(result[j].tokens)
                                                while k < tokens_len:
                                                    if result[j].tokens[k] == "{":
                                                        opens += 1
                                                    elif result[j].tokens[k] == "}":
                                                        opens -= 1

                                                    if opens == 0:
                                                        break
                                                    k += 1
                                                if opens == 0:
                                                    break
                                                j += 1

                                            # if the class definition was never closed
                                            if opens != 0:
                                                self.add_error(result[i], "SYNTAX", "'{' was never closed...", "Find the appropriate place to close it and put '}'")
                                            
                                            inner_lines = result[i:j+1]

                                            new_class = Class(class_name, [], inner_lines)

                                            # update the global scope
                                            for k in range(i, j+1):
                                                global_scope[k] = 0


                                            debug(f"Class {class_name} found!")

                                            self.classes.append(new_class)
                                            
                                        elif curr[3] == "extends":
                                            # get all parent classes
                                            if m < 5:
                                                self.add_error(result[i], "SYNTAX", "Expected one or more parent classes after 'extends'...", "Put the appropriate parent class(es)...\n\tSeparate each parent class with a ','")

                                            j = 4
                                            while j < m:
                                                if curr[j] == "{":
                                                    break
                                                j += 1
                                            parent_classes = curr[4:j]
                                            
                                            # TODO: act as though anything else on this line is on the next line

                                            # for now, just start gathering lines into a class block
                                            # iterate through each token, trying to find the matching }
                                            inner_lines = []

                                            j = i + 1
                                            number_of_lines = len(result)
                                            opens = 1
                                            # iterate through lines until the end of the file
                                            while j < number_of_lines:
                                                k = 0
                                                tokens_len = len(result[j].tokens)
                                                while k < tokens_len:
                                                    if result[j].tokens[k] == "{":
                                                        opens += 1
                                                    elif result[j].tokens[k] == "}":
                                                        opens -= 1

                                                    if opens == 0:
                                                        break
                                                    k += 1
                                                if opens == 0:
                                                    break
                                                j += 1

                                            # if the class definition was never closed
                                            if opens != 0:
                                                self.add_error(result[i], "SYNTAX", "'{' was never closed...", "Find the appropriate place to close it and put '}'")
                                            
                                            inner_lines = result[i:j+1]

                                            new_class = Class(class_name, parent_classes, inner_lines)

                                            # update the global scope
                                            for k in range(i, j+1):
                                                global_scope[k] = 0


                                            debug(f"Class {class_name} found!")

                                            self.classes.append(new_class)
                                            

                                        
                                        else:
                                            # throw an error if it neither extends nor 
                                            self.add_error(result[i], "SYNTAX", "Incorrect syntax...\n\tExpected either '{' or 'extends' after class name...", "Fix it...")
                                    

                    case "private":
                        # check if this is a class definition
                        if "class" in curr:
                            # if the next token is not the "class" keyword, throw an error
                            if curr[1] != "class":
                                # handle different cases 
                                handled = 0
                                if "static" in curr:
                                    self.add_error(result[i], "SYNTAX", "Classes cannot be defined as static...", "Remove the keyword static from this line.")
                                    handled = 1
                                if "public" in curr:
                                    self.add_error(result[i], "SYNTAX", "You cannot define a class as both private and public...", "Remove access modifiers until \n\tthere are less than two of them...")
                                    handled = 1
                                if "protected" in curr:
                                    self.add_error(result[i], "SYNTAX", "You cannot define a class as protected...", "Remove 'protected'.")
                                    handled = 1

                                # put at least some error message
                                if handled == 0:
                                    self.add_error(result[i], "SYNTAX", "Incorrect syntax...\n\tExpected 'class' after 'private'...", "Fix it or something?")


                            else: # the next token is class
                                # the next token should be the name of the class
                                if m < 3:
                                    self.add_error(result[i], "SYNTAX", "Incorrect syntax...\n\tExpected a class name after 'class'...", "Add a unique name for this scope.")
                                else:
                                    class_name = curr[2]
                                    
                                    # throw an error if the class is not named correctly
                                    self.check_variable_name(curr, class_name)

                                    # the next token should be extends or {
                                    if m < 4:
                                        self.add_error(result[i], "SYNTAX", "Incorrect syntax...\n\tExpected either '{' or 'extends' after class name...", "Fix it...")
                                    else:
                                        # this is the end of the class definition
                                        if curr[3] == "{":
                                            # TODO: act as though anything else on this line is on the next line

                                            # for now, just start gathering lines into a class block
                                            # iterate through each token, trying to find the matching }
                                            inner_lines = []

                                            j = i + 1
                                            number_of_lines = len(result)
                                            opens = 1
                                            # iterate through lines until the end of the file
                                            while j < number_of_lines:
                                                k = 0
                                                tokens_len = len(result[j].tokens)
                                                while k < tokens_len:
                                                    if result[j].tokens[k] == "{":
                                                        opens += 1
                                                    elif result[j].tokens[k] == "}":
                                                        opens -= 1

                                                    if opens == 0:
                                                        break
                                                    k += 1
                                                if opens == 0:
                                                    break
                                                j += 1

                                            # if the class definition was never closed
                                            if opens != 0:
                                                self.add_error(result[i], "SYNTAX", "'{' was never closed...", "Find the appropriate place to close it and put '}'")
                                            
                                            inner_lines = result[i:j+1]

                                            new_class = Class(class_name, [], inner_lines)

                                            # update the global scope
                                            for k in range(i, j+1):
                                                global_scope[k] = 0

                                            debug(f"Class {class_name} found!")

                                            self.classes.append(new_class)
                                            
                                        elif curr[3] == "extends":
                                            # get all parent classes
                                            if m < 5:
                                                self.add_error(result[i], "SYNTAX", "Expected one or more parent classes after 'extends'...", "Put the appropriate parent class(es)...\n\tSeparate each parent class with a ','")

                                            j = 4
                                            while j < m:
                                                if curr[j] == "{":
                                                    break
                                                j += 1
                                            parent_classes = curr[4:j]
                                            
                                            # TODO: act as though anything else on this line is on the next line

                                            # for now, just start gathering lines into a class block
                                            # iterate through each token, trying to find the matching }
                                            inner_lines = []

                                            j = i + 1
                                            number_of_lines = len(result)
                                            opens = 1
                                            # iterate through lines until the end of the file
                                            while j < number_of_lines:
                                                k = 0
                                                tokens_len = len(result[j].tokens)
                                                while k < tokens_len:
                                                    if result[j].tokens[k] == "{":
                                                        opens += 1
                                                    elif result[j].tokens[k] == "}":
                                                        opens -= 1

                                                    if opens == 0:
                                                        break
                                                    k += 1
                                                if opens == 0:
                                                    break
                                                j += 1

                                            # if the class definition was never closed
                                            if opens != 0:
                                                self.add_error(result[i], "SYNTAX", "'{' was never closed...", "Find the appropriate place to close it and put '}'")
                                            
                                            inner_lines = result[i:j+1]

                                            new_class = Class(class_name, parent_classes, inner_lines)

                                            # update the global scope
                                            for k in range(i, j+1):
                                                global_scope[k] = 0

                                            debug(f"Class {class_name} found!")

                                            self.classes.append(new_class)
                                            

                                        
                                        else:
                                            # throw an error if it neither extends nor 
                                            self.add_error(result[i], "SYNTAX", "Incorrect syntax...\n\tExpected either '{' or 'extends' after class name...", "Fix it...")

                    case "class":
                        # check if this is a class definition
                        if "class" in curr:
                            # if the next token is not the "class" keyword, throw an error
                            if curr[0] != "class":
                                # handle different cases 
                                handled = 0
                                if "static" in curr:
                                    self.add_error(result[i], "SYNTAX", "Classes cannot be defined as static...", "Remove the keyword static from this line.")
                                    handled = 1
                                if "public" in curr:
                                    self.add_error(result[i], "SYNTAX", "Keyword 'public' should go before 'class'", "Either change the order or remove 'public'.")
                                    handled = 1
                                if "private" in curr:
                                    self.add_error(result[i], "SYNTAX", "Keyword 'private' should go before 'class'", "Either change the order or remove 'private'.")
                                    handled = 1
                                if "protected" in curr:
                                    self.add_error(result[i], "SYNTAX", "You cannot define a class as protected...", "Remove 'protected'.")
                                    handled = 1

                                # put at least some error message
                                if handled == 0:
                                    self.add_error(result[i], "SYNTAX", "Incorrect syntax...\n\tExpected 'class <ClassName> {'", "Fix it or something?")


                            else: # the next token is class
                                # the next token should be the name of the class
                                if m < 2:
                                    self.add_error(result[i], "SYNTAX", "Incorrect syntax...\n\tExpected a class name after 'class'...", "Add a unique name for this scope.")
                                else:
                                    class_name = curr[1]
                                    
                                    # throw an error if the class is not named correctly
                                    self.check_variable_name(curr, class_name)

                                    # the next token should be extends or {
                                    if m < 3:
                                        self.add_error(result[i], "SYNTAX", "Incorrect syntax...\n\tExpected either '{' or 'extends' after class name...", "Fix it...")
                                    else:
                                        # this is the end of the class definition
                                        if curr[2] == "{":
                                            # TODO: act as though anything else on this line is on the next line

                                            # for now, just start gathering lines into a class block
                                            # iterate through each token, trying to find the matching }
                                            inner_lines = []

                                            j = i + 1
                                            number_of_lines = len(result)
                                            opens = 1
                                            # iterate through lines until the end of the file
                                            while j < number_of_lines:
                                                k = 0
                                                tokens_len = len(result[j].tokens)
                                                while k < tokens_len:
                                                    if result[j].tokens[k] == "{":
                                                        opens += 1
                                                    elif result[j].tokens[k] == "}":
                                                        opens -= 1

                                                    if opens == 0:
                                                        break
                                                    k += 1
                                                if opens == 0:
                                                    break
                                                j += 1

                                            # if the class definition was never closed
                                            if opens != 0:
                                                self.add_error(result[i], "SYNTAX", "'{' was never closed...", "Find the appropriate place to close it and put '}'")
                                            
                                            inner_lines = result[i:j+1]

                                            new_class = Class(class_name, [], inner_lines)

                                            # update the global scope
                                            for k in range(i, j+1):
                                                global_scope[k] = 0

                                            debug(f"Class {class_name} found!")

                                            self.classes.append(new_class)
                                            
                                        elif curr[2] == "extends":
                                            # get all parent classes
                                            if m < 4:
                                                self.add_error(result[i], "SYNTAX", "Expected one or more parent classes after 'extends'...", "Put the appropriate parent class(es)...\n\tSeparate each parent class with a ','")

                                            j = 3
                                            while j < m:
                                                if curr[j] == "{":
                                                    break
                                                j += 1
                                            parent_classes = curr[3:j]
                                            
                                            # TODO: act as though anything else on this line is on the next line

                                            # for now, just start gathering lines into a class block
                                            # iterate through each token, trying to find the matching }
                                            inner_lines = []

                                            j = i + 1
                                            number_of_lines = len(result)
                                            opens = 1
                                            # iterate through lines until the end of the file
                                            while j < number_of_lines:
                                                k = 0
                                                tokens_len = len(result[j].tokens)
                                                while k < tokens_len:
                                                    if result[j].tokens[k] == "{":
                                                        opens += 1
                                                    elif result[j].tokens[k] == "}":
                                                        opens -= 1

                                                    if opens == 0:
                                                        break
                                                    k += 1
                                                if opens == 0:
                                                    break
                                                j += 1

                                            # if the class definition was never closed
                                            if opens != 0:
                                                self.add_error(result[i], "SYNTAX", "'{' was never closed...", "Find the appropriate place to close it and put '}'")
                                            
                                            inner_lines = result[i:j+1]

                                            new_class = Class(class_name, parent_classes, inner_lines)

                                            # update the global scope
                                            for k in range(i, j+1):
                                                global_scope[k] = 0


                                            debug(f"Class {class_name} found!")

                                            self.classes.append(new_class)
                                            

                                        
                                        else:
                                            # throw an error if it neither extends nor 
                                            self.add_error(result[i], "SYNTAX", "Incorrect syntax...\n\tExpected either '{' or 'extends' after class name...", "Fix it...")


                    case "protected":
                        # throw an error if you define a class as protected
                        if "class" in curr:
                            self.add_error(result[i], "SYNTAX", "Classes cannot be defined as protected...", "Remove the keyword static from this line.")

                            
                    case default:
                        pass
            i += 1
            
        # the classes should now all be gathered
        # now make sure that everything is inside of a class (except for imports and compiler directives)
        remaining_lines = []

        for i in range(len(global_scope)):
            # check each line in the global scope to make sure it is 
            # either an import or compiler directive
            if global_scope[i]:
                curr = result[i].tokens.copy()
                j = 0
                while j < len(curr):
                    if len(curr[j]) > 0:
                        if curr[j][0] == '`':
                            del curr[j]
                            j -= 1
                    j += 1

                n = len(curr)
                if n < 1:
                    self.add_error(result[i], "SYNTAX", "Stray token found in global scope...", "Remove it.")

                else:
                    if curr[0] == "import" or curr[0] == "#":
                        remaining_lines.append(result[i])
                    else:
                        self.add_error(result[i], "SYNTAX", "Only classes, import statments, or compiler directives are allowed in the global scope...", "Remove the offending statement or put it in a class.")

        # we now have all global lines
        # and all classes put into an array
        # now we can further block each class
        self.block_classes()

        print("REMAINING LINES:")
        [print(x) for x in remaining_lines]

    
    def remove_subclass_lines(self, the_class:Class) -> Class:
        if len(the_class.subclasses) == 0:
            return the_class


    def handle_subclasses(self):
        ends = []
        classes = []
        is_subclasses = []
        for i in range(len(self.classes)):
            start = int(self.parse_line_number(self.classes[i].lines[0]))
            
            is_subclass = 0

            # iterate backwards through the possible superclasses
            for j in range(len(classes)-1, -1, -1):
                if start < ends[j]:
                    classes[j].subclasses.append(self.classes[i])
                    print(f"{classes[j]} has subclass {self.classes[i]}") 
                    is_subclass = 1

                    # FIXME: use the distance instead of the line number
                    super_start = int(self.parse_line_number(classes[j].lines[0]))
                    subclass_start = start - super_start - 1
                    subclass_end = subclass_start + len(self.classes[i].lines) - 1
                    print("HERE")
                    print(subclass_start, subclass_end)
                    [print(x) for x in classes[j].lines]
                    
                    classes[j].lines = classes[j].lines[0:subclass_start] + classes[j].lines[subclass_end+1:]

                    break

            end = int(self.parse_line_number(self.classes[i].lines[-1]))
            ends.append(end)
            classes.append(self.classes[i])
            is_subclasses.append(is_subclass)

        # remove classes from the global scope if they are subclasses
        self.classes = [classes[x] for x in range(len(classes)) if is_subclasses[x] == 0]

        # now recursively remove the lines that subclasses take up since they are in a subclass array
        for i in range(len(self.classes)):
            #self.classes[i] = self.remove_subclass_lines(self.classes[i])
            pass


    def block_classes(self):
        # first, figure out which classes are subclasses of others
        self.handle_subclasses()

        
        # use the found class objects and break
        # them up into normal lines and functions

        """
        for i in range(len(self.classes)):
            curr = self.classes[i]

            # iterate through the tokens inside the class
            # gather the functions and remaining statements
            n = len(curr.lines)
            j = 1
            while j < n:
                # check if the current line is a function header
                curr_line = curr.lines[i].tokens.copy()
                k = 0
                while k < len(curr_line):
                    if len(curr_line[k]) > 0:
                        if curr_line[k][0] == '`':
                            del curr_line[k]
                            k -= 1
                    k += 1

                m = len(curr_line)

                # function headers should start with public, private, or a return type
                if m < 1:
                    # this line has nothing on it
                    pass
                else:
                    if curr_line[0] == "public":
                        pass
                    elif curr_line[0] == "private":
                        pass
                    else:
                        # try to figure out what this line is.
                        # it could be a function, a variable, or a use statement.
                        pass



                j += 1
        """



            


if __name__ == '__main__':
    compiler = Compiler("test.mkt")

    [print(x) for x in compiler.EXCEPTIONS]
    print()
    [x.print() for x in compiler.classes]

    




