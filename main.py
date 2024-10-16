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
        self.file = ""
        self.type = "N/A"
        self.line_number = "0"
        self.line = ""
        self.cause = "The cause is unkown..."
        self.suggestions = "Good Luck!"

    def __str__(self):
        result = "-" * 80
        result += "\n"
        result += f"FILE: {self.file}\n"
        result += f"ERROR: ({self.type}) in line {self.line_number}:\n"
        result += f"LINE: \n\t{self.line}\n"
        result += f"CAUSE: \n\t{self.cause}\n"
        result += f"SUGGESTIONS: \n\t{self.suggestions}\n"
        return result


RESERVED_WORDS = set(["int", "bool", "float", "short", "long", "double", "char", "void", "class", "public", "private", "protected", "extends", "return", "if", "for", "while", "import", "as", "use", "try", "catch", "switch", "case", "else", "new", "asm", "static", "extends"])


class Directive:
    """
    A compiler directive
    """
    def __init__(self, tokens: list[str]):
        self.tokens = tokens

class Use:
    """
    A use (as) statement
    use System.out.println;
    or
    use System.out.println as print;
    """
    def __init__(self, tokens: list[str]):
        self.tokens = tokens
        self.parse()

    def parse(self):
        use_index = self.tokens.index("use")
        if "as" in self.tokens:
            as_index = self.tokens.index("as")

            self.first = self.tokens[use_index+1:as_index]
            self.second = self.tokens[as_index+1:]
        else:
            self.first = self.tokens[use_index+1:]
            self.second = self.tokens[-1]


class Line:
    """
    A single line of code.
    """
    def __init__(self, tokens: list[str]):
        self.tokens = tokens
        self.is_declaration = False

    def __str__(self):
        return self.tokens.__str__()


class Block:
    """
    A simple block of code.
    contains its own scope and is enclosed in {}
    """
    def __init__(self, lines:list[str]):
        self.lines = lines
        self.is_declaration = False

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
        self.functions = []
        self.directives = []
        self.uses = []
        self.file = ""
        self.is_global = True

    def get_scope(self):
        # check the first line of this classes' definition
        if len(self.lines) < 1:
            return "private"
        if len(self.lines[0].tokens) < 1:
            return "private"

        match (self.lines[0].tokens[0]):
            case "private":
                return "private"
            case "public":
                return "public"
            case "protected":
                return "protected"
            case default:
                return "private"


    def print(self):
        print(self.__str__())
        print(f"extends: {self.parents}")
        print(f"subclasses: {[str(x) for x in self.subclasses]}")
        Block.print(self)

    def __str__(self):
        return f"class {self.name} ({len(self.lines)} lines)"


class Function(Block):
    """
    A single function.
    """
    def __init__(self, function_name:str, params:list[str], return_type:list[str], access:str, lines:list[str]):
        Block.__init__(self, lines)
        self.name = function_name
        self.params = params
        self.return_type = return_type
        self.access = access
        self.directives = []


class Compiler:
    def __init__(self, filename:str, imports:list[str]=[], relation:str=""):
        self.EXCEPTIONS = []
        self.imports = imports
        self.relation = relation

        if filename[:2] != "./":
            filename = "./" + filename
        self.imports.append(filename)
        self.filename = filename
        self.data = self.open_file(self.filename)
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
            print(f"Please make sure this file exists or download any required dependencies first.")
            exit()
        debug("Finished reading file!")
        return data 


    def add_error(self, file:str, line: Line, error_type: str, cause: str, suggestions: str):
        result = ErrorMessage()
        result.file = file
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

        break_tokens = ["\n", "*", "$", "#", ".", ",", "[", "]", "<", ">", "&", "|", "\t", " ", "~", "^", "(", ")", "@", "%", "/", "=", "+", "-", ";", "'", '"', "{", "}", ":"]
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
                        case "{":
                            if not comment:
                                result.append(lines[i])
                                result.append("\n")
                                result.append(f"`{current_line}")
                        case "}":
                            if not comment:
                                result.append(lines[i])
                                result.append("\n")
                                result.append(f"`{current_line}")

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
                                    self.add_error(self.filename, result[i], "SYNTAX", "Classes cannot be defined as static...", "Remove the keyword static from this line.")
                                    handled = 1
                                if "private" in curr:
                                    self.add_error(self.filename, result[i], "SYNTAX", "You cannot define a class as both public and private...", "Remove access modifiers until \n\tthere are less than two of them...")
                                    handled = 1
                                if "protected" in curr:
                                    self.add_error(self.filename, result[i], "SYNTAX", "You cannot define a class as both public and protected...", "Remove access modifiers until \n\tthere are less than two of them...")
                                    handled = 1

                                # put at least some error message
                                if handled == 0:
                                    self.add_error(self.filename, result[i], "SYNTAX", "Incorrect syntax...\n\tExpected 'class' after 'public'...", "Fix it or something?")


                            else: # the next token is class
                                # the next token should be the name of the class
                                if m < 3:
                                    self.add_error(self.filename, result[i], "SYNTAX", "Incorrect syntax...\n\tExpected a class name after 'class'...", "Add a unique name for this scope.")
                                else:
                                    class_name = curr[2]
                                    
                                    # throw an error if the class is not named correctly
                                    self.check_variable_name(curr, class_name)

                                    # the next token should be extends or {
                                    if m < 4:
                                        self.add_error(self.filename, result[i], "SYNTAX", "Incorrect syntax...\n\tExpected either '{' or 'extends' after class name...", "Fix it...")
                                    else:
                                        # this is the end of the class definition
                                        if curr[3] == "{":

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
                                                self.add_error(self.filename, result[i], "SYNTAX", "'{' was never closed...", "Find the appropriate place to close it and put '}'")
                                            
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
                                                self.add_error(self.filename, result[i], "SYNTAX", "Expected one or more parent classes after 'extends'...", "Put the appropriate parent class(es)...\n\tSeparate each parent class with a ','")

                                            j = 4
                                            while j < m:
                                                if curr[j] == "{":
                                                    break
                                                j += 1
                                            parent_classes = curr[4:j]
                                            

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
                                                self.add_error(self.filename, result[i], "SYNTAX", "'{' was never closed...", "Find the appropriate place to close it and put '}'")
                                            
                                            inner_lines = result[i:j+1]

                                            new_class = Class(class_name, parent_classes, inner_lines)

                                            # update the global scope
                                            for k in range(i, j+1):
                                                global_scope[k] = 0


                                            debug(f"Class {class_name} found!")

                                            self.classes.append(new_class)
                                            

                                        
                                        else:
                                            # throw an error if it neither extends nor 
                                            self.add_error(self.filename, result[i], "SYNTAX", "Incorrect syntax...\n\tExpected either '{' or 'extends' after class name...", "Fix it...")
                                    

                    case "private":
                        # check if this is a class definition
                        if "class" in curr:
                            # if the next token is not the "class" keyword, throw an error
                            if curr[1] != "class":
                                # handle different cases 
                                handled = 0
                                if "static" in curr:
                                    self.add_error(self.filename, result[i], "SYNTAX", "Classes cannot be defined as static...", "Remove the keyword static from this line.")
                                    handled = 1
                                if "public" in curr:
                                    self.add_error(self.filename, result[i], "SYNTAX", "You cannot define a class as both private and public...", "Remove access modifiers until \n\tthere are less than two of them...")
                                    handled = 1
                                if "protected" in curr:
                                    self.add_error(self.filename, result[i], "SYNTAX", "You cannot define a class as protected...", "Remove 'protected'.")
                                    handled = 1

                                # put at least some error message
                                if handled == 0:
                                    self.add_error(self.filename, result[i], "SYNTAX", "Incorrect syntax...\n\tExpected 'class' after 'private'...", "Fix it or something?")


                            else: # the next token is class
                                # the next token should be the name of the class
                                if m < 3:
                                    self.add_error(self.filename, result[i], "SYNTAX", "Incorrect syntax...\n\tExpected a class name after 'class'...", "Add a unique name for this scope.")
                                else:
                                    class_name = curr[2]
                                    
                                    # throw an error if the class is not named correctly
                                    self.check_variable_name(curr, class_name)

                                    # the next token should be extends or {
                                    if m < 4:
                                        self.add_error(self.filename, result[i], "SYNTAX", "Incorrect syntax...\n\tExpected either '{' or 'extends' after class name...", "Fix it...")
                                    else:
                                        # this is the end of the class definition
                                        if curr[3] == "{":

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
                                                self.add_error(self.filename, result[i], "SYNTAX", "'{' was never closed...", "Find the appropriate place to close it and put '}'")
                                            
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
                                                self.add_error(self.filename, result[i], "SYNTAX", "Expected one or more parent classes after 'extends'...", "Put the appropriate parent class(es)...\n\tSeparate each parent class with a ','")

                                            j = 4
                                            while j < m:
                                                if curr[j] == "{":
                                                    break
                                                j += 1
                                            parent_classes = curr[4:j]
                                            

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
                                                self.add_error(self.filename, result[i], "SYNTAX", "'{' was never closed...", "Find the appropriate place to close it and put '}'")
                                            
                                            inner_lines = result[i:j+1]

                                            new_class = Class(class_name, parent_classes, inner_lines)

                                            # update the global scope
                                            for k in range(i, j+1):
                                                global_scope[k] = 0

                                            debug(f"Class {class_name} found!")

                                            self.classes.append(new_class)
                                            

                                        
                                        else:
                                            # throw an error if it neither extends nor 
                                            self.add_error(self.filename, result[i], "SYNTAX", "Incorrect syntax...\n\tExpected either '{' or 'extends' after class name...", "Fix it...")

                    case "class":
                        # check if this is a class definition
                        if "class" in curr:
                            # if the next token is not the "class" keyword, throw an error
                            if curr[0] != "class":
                                # handle different cases 
                                handled = 0
                                if "static" in curr:
                                    self.add_error(self.filename, result[i], "SYNTAX", "Classes cannot be defined as static...", "Remove the keyword static from this line.")
                                    handled = 1
                                if "public" in curr:
                                    self.add_error(self.filename, result[i], "SYNTAX", "Keyword 'public' should go before 'class'", "Either change the order or remove 'public'.")
                                    handled = 1
                                if "private" in curr:
                                    self.add_error(self.filename, result[i], "SYNTAX", "Keyword 'private' should go before 'class'", "Either change the order or remove 'private'.")
                                    handled = 1
                                if "protected" in curr:
                                    self.add_error(self.filename, result[i], "SYNTAX", "You cannot define a class as protected...", "Remove 'protected'.")
                                    handled = 1

                                # put at least some error message
                                if handled == 0:
                                    self.add_error(self.filename, result[i], "SYNTAX", "Incorrect syntax...\n\tExpected 'class <ClassName> {'", "Fix it or something?")


                            else: # the next token is class
                                # the next token should be the name of the class
                                if m < 2:
                                    self.add_error(self.filename, result[i], "SYNTAX", "Incorrect syntax...\n\tExpected a class name after 'class'...", "Add a unique name for this scope.")
                                else:
                                    class_name = curr[1]
                                    
                                    # throw an error if the class is not named correctly
                                    self.check_variable_name(curr, class_name)

                                    # the next token should be extends or {
                                    if m < 3:
                                        self.add_error(self.filename, result[i], "SYNTAX", "Incorrect syntax...\n\tExpected either '{' or 'extends' after class name...", "Fix it...")
                                    else:
                                        # this is the end of the class definition
                                        if curr[2] == "{":

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
                                                self.add_error(self.filename, result[i], "SYNTAX", "'{' was never closed...", "Find the appropriate place to close it and put '}'")
                                            
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
                                                self.add_error(self.filename, result[i], "SYNTAX", "Expected one or more parent classes after 'extends'...", "Put the appropriate parent class(es)...\n\tSeparate each parent class with a ','")

                                            j = 3
                                            while j < m:
                                                if curr[j] == "{":
                                                    break
                                                j += 1
                                            parent_classes = curr[3:j]
                                            

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
                                                self.add_error(self.filename, result[i], "SYNTAX", "'{' was never closed...", "Find the appropriate place to close it and put '}'")
                                            
                                            inner_lines = result[i:j+1]

                                            new_class = Class(class_name, parent_classes, inner_lines)

                                            # update the global scope
                                            for k in range(i, j+1):
                                                global_scope[k] = 0


                                            debug(f"Class {class_name} found!")

                                            self.classes.append(new_class)
                                            

                                        
                                        else:
                                            # throw an error if it neither extends nor 
                                            self.add_error(self.filename, result[i], "SYNTAX", "Incorrect syntax...\n\tExpected either '{' or 'extends' after class name...", "Fix it...")


                    case "protected":
                        # throw an error if you define a class as protected
                        if "class" in curr:
                            self.add_error(self.filename, result[i], "SYNTAX", "Classes cannot be defined as protected...", "Remove the keyword static from this line.")

                            
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
                    self.add_error(self.filename, result[i], "SYNTAX", "Stray token found in global scope...", "Remove it.")

                else:
                    if curr[0] == "import" or curr[0] == "#":
                        remaining_lines.append(result[i])
                    else:
                        self.add_error(self.filename, result[i], "SYNTAX", "Only classes, import statments, or compiler directives are allowed in the global scope...", "Remove the offending statement or put it in a class.")

        for x in self.classes:
            x.file = self.filename

        # we now have all global lines
        # and all classes put into an array
        # now we can further block each class
        self.handle_subclasses()

        print("REMAINING LINES:")
        [print(x) for x in remaining_lines]

        # now we need to handle import statements.
        # all import statements must be in the global scope
        self.handle_imports(remaining_lines)

    
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

                    subclass_start = 0
                    subclass_line_number = int(self.parse_line_number(self.classes[i].lines[0]))
                    for x in classes[j].lines:
                        curr_line_number = int(self.parse_line_number(x))
                        if curr_line_number == subclass_line_number:
                            break
                        subclass_start += 1

                    subclass_end = subclass_start + len(self.classes[i].lines) - 1
                    
                    classes[j].lines = classes[j].lines[0:subclass_start] + classes[j].lines[subclass_end+1:]

                    break

            end = int(self.parse_line_number(self.classes[i].lines[-1]))
            ends.append(end)
            classes.append(self.classes[i])
            is_subclasses.append(is_subclass)

        # remove classes from the global scope if they are subclasses
        self.classes = [classes[x] for x in range(len(classes)) if is_subclasses[x] == 0]


    def handle_imports(self, remaining:list[Line]):
        # To handle imports, simply include all of the code from that file
        # instead of just putting the code at the top, put it all in a class
        # with the same name as the file it is imported from
        result = []

        # rather than getting stuck in an infinite loop during a circular import,
        # only import each unique filename once
        i = 0
        n = len(remaining)
        while i < n:
            # check each line to see if it is an import
            curr = remaining[i].tokens.copy()
            j = 0
            while j < len(curr):
                if len(curr[j]) > 0:
                    if curr[j][0] == '`':
                        del curr[j]
                        j -= 1
                j += 1

            m = len(curr)

            if m > 0:
                if curr[0] == "import":
                    # remove the import statement from remaining tokens
                    del remaining[i]
                    i -= 1
                    n -= 1

                    debug("Handling import statement.")
                    # if this is an import statement

                    # first, see how many .'s prepend the first directory/file
                    the_path = curr[1:]

                    dots = 0
                    for x in the_path:
                        if x == '.':
                            dots += 1
                        else:
                            break
                    path_start = dots

                    this_path = self.filename.split("/")[:-1]
                    while this_path[-1] not in [".", ".."] and dots > 0:
                        del this_path[-1]
                        dots -= 1

                    for x in range(dots):
                        this_path.append("..")

                    for j in range(path_start, len(the_path)):
                        this_path.append(the_path[j])

                    # join the path back
                    j = 0
                    while j < len(this_path):
                        if this_path[j] == ".":
                            del this_path[j]
                            j -= 1
                        j += 1
                    this_path = "/".join(this_path)
                    this_path += ".tcab"

                    # this path should represent a file.
                    # try to open the file in a new compiler object
                    if "./" + this_path not in self.imports:
                        debug(f"Creating new compiler object for {this_path}")
                        new_compiler = Compiler(this_path, self.imports, the_path)
                        # update your imports
                        self.imports = new_compiler.imports
                        result.append(new_compiler)

                        # make imported classes not global (for access protection later)
                        for x in range(len(new_compiler.classes)):
                            new_compiler.classes[x].is_global = False
                    else:
                        debug("This file has already been imported... ignoring")


            i += 1

        # encase all imports with relative paths starting with a . in private class . {}
        for i in range(len(result)):
            last = None
            for j in range(len(result[i].relation)):
                new_class = Class(result[i].relation[j], [], [])
                new_class.is_global = False
                if last == None:
                    new_class.lines = [Line(["protected", "class", new_class.name, "{"]), Line(["}"])]
                    self.classes.append(new_class)
                    pass
                else:
                    last.subclasses.append(new_class)
                last = new_class

                if j == len(result[i].relation) - 1:
                    specifier = "public"
                    if len(result[i].relation) == 0:
                        specifier = "protected"
                    new_class.lines = [Line([specifier, "class", new_class.name, "{"])] + result[i].remaining_lines + [Line(["}"])]
                    new_class.subclasses = result[i].classes


        self.remaining_lines = remaining


        debug("All imports have been preprocessed!")
        return result



class Parser:
    """
    Takes control after the Compiler has handled all imports and classes
    """

    def __init__(self, remaining_lines:list[Line], classes:list[Class]):
        self.EXCEPTIONS = []

        self.remaining_lines = remaining_lines
        self.classes = classes

        # handle function blocks
        for x in range(len(self.classes)):
            self.classes[x] = self.handle_inside_class(self.classes[x])

        # now we can handle compiler directives
        debug("Parsing Compiler Directives...")
        self.directives = []
        self.handle_directives()

        debug("Finished Parsing Compiler Directives!")

        # the only remaining tokens should be as follows:
        # in class scopes:
        #   use statements
        #   attributes (instance variables)
        #
        # in function scopes:
        #   local variables
        #   function calls
        #   return
        #   if, for, while, switch, case
        #   

        # if there are any more lines in the global scope, add an exception for each
        for line in self.remaining_lines:
            self.add_exception(line, "SYNTAX", "Invalid line declared in global scope...\n\tOnly compiler directives and import statments are allowed...", "Remove/alter the offending statement.")

        # handle use (as) statements by adding them to Class objects
        for i in range(len(self.classes)):
            self.classes[x] = self.handle_use_statements(self.classes[x])

        # we should be able to start rearranging lines of code
        # and applying the compiler directives so that we have a sequential program
        # we should be able to catch any syntax errors while do this

    def parse_line_number(self, line: Line):
        if len(line.tokens) > 0:
            if len(line.tokens[0]) > 0 and line.tokens[0][0] == '`':
                return line.tokens[0][1:]
        return "0"


    def add_error(self, file: str, line: Line, error_type: str, cause: str, suggestions: str):
        debug(f"Added error message... ({cause})")
        result = ErrorMessage()
        result.file = file
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



    def handle_inside_class(self, the_class:Class):
        # handle potential compiler directives, functions, statements inside of functions, declarations, and use statements within a class
        # we will ignore compiler directives until the end
        # we should have enough information to start gathering functions and variable declarations
        
        
        i = 0
        n = len(the_class.lines)

        if n > 1:
            # remove the first and last lines
            del the_class.lines[0]
            del the_class.lines[-1]

        n = len(the_class.lines)

        while i < n:
            # iterate through the lines. 

            # right now, just separate functions from the rest of the statements
            # functions are in this form:
            # public static void main(float | String test){
            # void main(* test){
            curr = the_class.lines[i].tokens.copy()
            j = 0
            while j < len(curr):
                if len(curr[j]) > 0:
                    if curr[j][0] == '`':
                        del curr[j]
                        j -= 1
                j += 1

            m = len(curr)

            if m > 0:
                # this should be a function definition
                if curr[-1] == "{":
                    debug("Found function defintion")
                    
                    # parse the line and try to create the function
                    is_static = 0
                    return_type_start = 0
                    access = "private"
                    if curr[0] == "public":
                        access = "public"
                        return_type_start = 1
                        if m > 1:
                            if curr[1] == "static":
                                is_static = 1
                                return_type_start = 2
                    elif curr[0] == "static":
                        is_static = 1
                        access = "private"
                        return_type_start = 1
                    elif curr[0] == "protected":
                        access = "protected"
                        return_type_start = 1
                        if m > 1:
                            if curr[1] == "static":
                                is_static = 1
                                return_type_start = 2
                    elif curr[0] == "private":
                        return_type_start = 1
                        if m > 1:
                            if curr[1] == "static":
                                is_static = 1
                                return_type_start = 2
                    else:
                        # if none of the other cases happened, the first tokens are the return type
                        return_type_start = 0
                    
                    # we now have the access specifier, whether or not it is static, and where the return type starts
                    # we expect a return type, a name, and parameters inside of (), then {
                    # work backwards to find the name (directly before the last close parenthesis were opened
                    if m > 1:
                        if curr[-2] != ")":
                            self.add_error(the_class.file, the_class.lines[i], "SYNTAX", "Expected ')' at end of parameters...", "Put a ')' directly before the '{'.")
                        else:
                            # work backwards until finding the opening of that parenthesis
                            j = m - 3
                            opens = 1
                            while j >= 0:
                                if curr[j] == ")":
                                    opens += 1
                                elif curr[j] == "(":
                                    opens -= 1

                                if opens == 0:
                                    break
                                j -= 1

                            # the opener was never found
                            if j < 0:
                                self.add_error(the_class.file, the_class.lines[i], "SYNTAX", "Expected '(' before list of parameters...", "Enclose parameters in '(' and ')'.")
                            else:
                                if j == 0:
                                    self.add_error(the_class.file, the_class.lines[i], "SYNTAX", "Expected function name before '('...", "Name the function.")
                                else:
                                    params = curr[j+1:-2]

                                    function_name = curr[j-1]

                                    # everything from return_type_start to the name is the return type
                                    return_type = curr[return_type_start:j-1]

                                    debug(f"Function parsed: name - {function_name}\treturn_type - {return_type}\tparams - {params}")

                                    # now start on the next line and get the contents of this function,
                                    # breaking at the closing line
                                    opens = 1
                                    j = i + 1
                                    while j < n:
                                        for x in the_class.lines[j].tokens:
                                            if x == "{":
                                                opens += 1
                                            elif x == "}":
                                                opens -= 1
                                            if opens == 0:
                                                break
                                        if opens == 0:
                                            break
                                        j += 1

                                    if j == n:
                                        self.add_error(the_class.file, the_class.lines[i], "SYNTAX", "Function {function_name} was never closed", "Put a '}' where it should be closed.")
                                    else:
                                        function_lines = the_class.lines[i+1:j]
                                        new_function = Function(function_name, params, return_type, access, function_lines)
                                        test_function = None

                                        if j != n - 1:
                                            # check if there is a $ method
                                            if len(the_class.lines[j+1].tokens) > 1:
                                                if the_class.lines[j+1].tokens[1] == "$":
                                                    # create another function that returns bool with same params
                                                    # with the same name, but starting with $

                                                    # now gather the lines for the test_function
                                                    if len(the_class.lines[j+1].tokens) < 2:
                                                        self.add_error(the_class.file, the_class.lines[i], "SYNTAX", "Expected '{' after '$'...", "Put '{' after '$'.")
                                                    else:
                                                        if the_class.lines[j+1].tokens[2] != "{":
                                                            self.add_error(the_class.file, the_class.lines[i], "SYNTAX", "Expected '{' after '$'...", "Put '{' after '$'.")
                                                        else:
                                                            opens = 1
                                                            test_function_lines_start = j
                                                            j = j + 2
                                                            while j < n:
                                                                for x in the_class.lines[j].tokens:
                                                                    if x == "{":
                                                                        opens += 1
                                                                    elif x == "}":
                                                                        opens -= 1
                                                                    if opens == 0:
                                                                        break
                                                                if opens == 0:
                                                                    break
                                                                j += 1
                                                            if j == n:
                                                                self.add_error(the_class.file, the_class.lines[i], "SYNTAX", "Function ${function_name} was never closed", "Put a '}' where it should be closed.")
                                                            else:
                                                                test_function_lines = the_class.lines[test_function_lines_start+1:j]

                                                                test_function = Function("$" + function_name, params, "bool", access, test_function_lines)
                                                                debug(f"Test Function parsed: name - ${function_name}\treturn_type - bool\tparams - {params}")

                                                                

                                        
                                        the_class.functions.append(new_function)
                                        if test_function != None:
                                            the_class.functions.append(test_function)

                                        the_class.lines = the_class.lines[0:i] + the_class.lines[j+1:]
                                        i -= 1
                                        n -= j - i

            i += 1

        # now recursively handle each of the subclasses to this class
        for i in range(len(the_class.subclasses)):
            the_class.subclasses[i] = self.handle_inside_class(the_class.subclasses[i])


        return the_class


    def handle_directives(self):
        # find compiler directive in each scope (including global)
        # and add them to the proper block
        
        # look through the remaining lines first
        i = 0
        n = len(self.remaining_lines)
        while i < n:
            curr = self.remaining_lines[i].tokens.copy()
            j = 0
            while j < len(curr):
                if len(curr[j]) > 0:
                    if curr[j][0] == '`':
                        del curr[j]
                        j -= 1
                j += 1

            m = len(curr)

            if m > 0:
                if curr[0] == "#":
                    # this is a directive
                    debug(f"Found compiler directive in global scope : {curr}")
                    self.directives.append(Directive(self.remaining_lines[i]))
                    del self.remaining_lines[i]
                    i -= 1
                    n -= 1

            i += 1


        # now handle classes
        for i in range(len(self.classes)):
            self.classes[i] = self.handle_class_directives(self.classes[i])


    def handle_function_directives(self, the_function:Function):
        # handle directives in the function's body
        i = 0
        n = len(the_function.lines)
        while i < n:
            curr = the_function.lines[i].tokens.copy()
            j = 0
            while j < len(curr):
                if len(curr[j]) > 0:
                    if curr[j][0] == '`':
                        del curr[j]
                        j -= 1
                j += 1

            m = len(curr)

            if m > 0:
                if curr[0] == "#":
                    # this is a directive
                    debug(f"Found compiler directive in function {the_function.name} : {curr}")
                    the_function.directives.append(Directive(the_function.lines[i]))
                    del the_function.lines[i]
                    i -= 1
                    n -= 1
            i += 1

        return the_function


    def handle_class_directives(self, the_class:Class):
        # handle directives in the remaining section
        i = 0
        n = len(the_class.lines)
        while i < n:
            curr = the_class.lines[i].tokens.copy()
            j = 0
            while j < len(curr):
                if len(curr[j]) > 0:
                    if curr[j][0] == '`':
                        del curr[j]
                        j -= 1
                j += 1

            m = len(curr)

            if m > 0:
                if curr[0] == "#":
                    # this is a directive
                    debug(f"Found compiler directive in {str(the_class)} : {curr}")
                    the_class.directives.append(Directive(the_class.lines[i]))
                    del the_class.lines[i]
                    i -= 1
                    n -= 1
            i += 1
        

        # handle directives in functions
        for i in range(len(the_class.functions)):
            the_class.functions[i] = self.handle_function_directives(the_class.functions[i])

        # handle directives in subclasses (recursively)
        for i in range(len(the_class.subclasses)):
            the_class.subclasses[i] = self.handle_class_directives(the_class.subclasses[i])

        return the_class


    def handle_use_statements(self, the_class: Class):
        # first, iterate through the lines of the class
        # and look for the use

        i = 0
        n = len(the_class.lines)
        while i < n:
            curr = the_class.lines[i].tokens.copy()
            j = 0
            while j < len(curr):
                if len(curr[j]) > 0:
                    if curr[j][0] == '`':
                        del curr[j]
                        j -= 1
                j += 1

            m = len(curr)

            if m > 0:
                if curr[0] == "use":
                    # this is a use statement
                    the_class.uses.append(Use(the_class.lines[i].tokens))
                    del the_class.lines[i]
                    i -= 1
                    n -= 1
            i += 1

        # call recursively on all subclasses
        for i in range(len(the_class.subclasses)):
            the_class.subclasses[i] = self.handle_use_statements(the_class.subclasses[i])

        return the_class


class Sequencer:
    """
    This class will deal with laying out the program in a sequential manner.
    This means it will have to handle errors in access specifiers and whether or not 
    variables/functions/classes are defined.
    It will also have to take compiler directives into account
    """
    def __init__(self, classes:list[Class], directives:list[Directive]):
        self.classes = classes
        self.directives = directives
        self.EXCEPTIONS = []

        self.trace()

    def parse_line_number(self, line: Line):
        if len(line.tokens) > 0:
            if len(line.tokens[0]) > 0 and line.tokens[0][0] == '`':
                return line.tokens[0][1:]
        return "0"

    def add_error(self, file: str, line: Line, error_type: str, cause: str, suggestions: str):
        result = ErrorMessage()
        result.file = file
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


    def find_main_function(self):
        # start static analysis of the trace of the code. This will start
        # at the Main class in the global scope and execute the main method
        
        # first, make sure that there is a Main class
        main_class_found = 0
        main_class = None
        for x in self.classes:
            if x.name == "Main":
                main_class_found = 1
                main_class = x

        if not main_class_found:
            self.add_error("*", Line(["`-1"]), "SYNTAX", "A class named Main is required in the global context...", "Add a Main class to this file or use a different file as the global scope.")
        else:
            # now, make sure that there is a main method in that class
            # the main method should either accept no args or a single String[] arg
            main_function_found = 0
            main_function = None
            for x in main_class.functions:
                if x.name == 'main':
                    main_function_found = 1
                    main_function = x
            if not main_function_found:
                self.add_error("*", Line(["`-1"]), "SYNTAX", "A function named main is required in a class named Main within the global context...", "Add a main function.")
            else:
                return main_class, main_function
        return None, None


    def convert_operation_equals(self, the_function: Function):
        # convert an operation and then equal sign to
        # its equivalent simple operation
        # i += 1
        # => i = i + 1

        i = 0
        n = len(the_function.lines)
        while i < n:
            # search through each line of the function
            curr = the_function.lines[i].tokens.copy()
            m = len(curr)
            line_number = []

            if m > 0:
                if len(curr[0]) > 0:
                    if curr[0][0] == "`":
                        line_number.append(curr[0])
                        del curr[0]
                        m -= 1

            j = 0
            while j < m:
                # if this token is an = sign, 
                # we should check if the token before
                # is an operator
                if curr[j] == "=":
                    if j > 0:
                        match(curr[j-1]):
                            case "+":
                                del curr[j-1]
                                m -= 1
                                j -= 1
                                curr = line_number + curr[0:j+1] + curr[0:j] + ["+", "("] + curr[j+1:] + [")"]
                                the_function.lines[i].tokens = curr
                            case "-":
                                del curr[j-1]
                                m -= 1
                                j -= 1
                                curr = line_number + curr[0:j+1] + curr[0:j] + ["-", "("] + curr[j+1:] + [")"]
                                the_function.lines[i].tokens = curr
                            case "*":
                                del curr[j-1]
                                m -= 1
                                j -= 1
                                curr = line_number + curr[0:j+1] + curr[0:j] + ["*", "("] + curr[j+1:] + [")"]
                                the_function.lines[i].tokens = curr
                            case "/":
                                del curr[j-1]
                                m -= 1
                                j -= 1
                                curr = line_number + curr[0:j+1] + curr[0:j] + ["/", "("] + curr[j+1:] + [")"]
                                the_function.lines[i].tokens = curr
                            case "%":
                                del curr[j-1]
                                m -= 1
                                j -= 1
                                curr = line_number + curr[0:j+1] + curr[0:j] + ["%", "("] + curr[j+1:] + [")"]
                                the_function.lines[i].tokens = curr
                            case "|":
                                # check if ||
                                if j-1 > 0:
                                    if curr[j-2] == "|":
                                        del curr[j-1]
                                        m -= 1
                                        j -= 1
                                        del curr[j-1]
                                        m -= 1
                                        j -= 1
                                        curr = line_number + curr[0:j+1] + curr[0:j] + ["|", "|", "("] + curr[j+1:] + [")"]
                                        the_function.lines[i].tokens = curr
                                    else:
                                        del curr[j-1]
                                        m -= 1
                                        j -= 1
                                        curr = line_number + curr[0:j+1] + curr[0:j] + ["|", "("] + curr[j+1:] + [")"]
                                        the_function.lines[i].tokens = curr
                                else:
                                    del curr[j-1]
                                    m -= 1
                                    j -= 1
                                    curr = line_number + curr[0:j+1] + curr[0:j] + ["|", "("] + curr[j+1:] + [")"]
                                    the_function.lines[i].tokens = curr
                            case "&":
                                # check if &&
                                if j-1 > 0:
                                    if curr[j-2] == "&":
                                        del curr[j-1]
                                        m -= 1
                                        j -= 1
                                        del curr[j-1]
                                        m -= 1
                                        j -= 1
                                        curr = line_number + curr[0:j+1] + curr[0:j] + ["&", "&", "("] + curr[j+1:] + [")"]
                                        the_function.lines[i].tokens = curr
                                    else:
                                        del curr[j-1]
                                        m -= 1
                                        j -= 1
                                        curr = line_number + curr[0:j+1] + curr[0:j] + ["&", "("] + curr[j+1:] + [")"]
                                        the_function.lines[i].tokens = curr
                                else:
                                    del curr[j-1]
                                    m -= 1
                                    j -= 1
                                    curr = line_number + curr[0:j+1] + curr[0:j] + ["&", "("] + curr[j+1:] + [")"]
                                    the_function.lines[i].tokens = curr
                j += 1
            
            i += 1

        return the_function
        

    def break_declarations(self, the_function:Function):
        # declarations can be in these two forms
        # int test = 4;
        # int test; test = 4;
        
        # function calls can use kwargs, but they must be inside parenthesis
        # look for an equal sign outside of parenthesis
        # after that, look for two strings (where neither is ".") to see what part is the name and what part is the declaration
        # if there is no two tokens together, then this line just sets the variable
        # the type can end in a word, *, or ]

        i = 0
        n = len(the_function.lines)
        while i < n:
            curr = the_function.lines[i].tokens.copy()
            m = len(curr)
            j = 0

            inside = 0
            line_number = ""
            while j < m:
                # iterate through this line, looking for an equal sign
                
                # get rid of the line number
                if len(curr[j]) > 0:
                    if curr[j][0] == '`':
                        line_number = curr[j]
                        del curr[j]
                        m -= 1
                        continue

                # look for an equal sign that is not inside of parenthesis
                if curr[j] == "(":
                    inside += 1
                elif curr[j] == ")":
                    inside -= 1
                elif curr[j] == "=":
                    if inside == 0:
                        is_normal = 1
                        # make sure the token before was not !, >, or <
                        # make sure the token after is not =
                        if j > 0:
                            if curr[j-1] in ["!", "<", ">"]:
                                is_normal = 0
                        if j < m - 1:
                            if curr[j+1] == "=":
                                is_normal = 0
                                j += 1

                        if is_normal:
                            # now we need to see if this is just setting or a declaration
                            # if it is a declaration, there will be a type that ends with ], *, or a word
                            # followed by a name that starts with a word
                            is_declaration = False

                            the_equal = j
                            j = 0
                            words = 0
                            while j < the_equal:
                                # look for *, ], or a word followed by a word other than .
                                if curr[j] == "*":
                                    # next can be either *, a word, [, or ]
                                    words = 0
                                    if j + 1 < the_equal:
                                        if curr[j+1] not in ["*", "[", "]"]:
                                            is_declaration = True
                                            break
                                elif curr[j] == "[":
                                    # skip until "]"
                                    words = 0
                                    while j < the_equal and curr[j] != "]":
                                        j += 1
                                    j -= 1
                                elif curr[j] == "]":
                                    # next can be [, =, or another word
                                    words = 0
                                    if j + 1 < the_equal:
                                        if curr[j+1] not in ["[", "="]:
                                            is_declaration = True
                                            break
                                elif curr[j] not in [".", "[", "]", "*"]:
                                    # this is a word
                                    words += 1
                                else:
                                    # reset word counter
                                    words = 0

                                j += 1
                                
                                if words == 2:
                                    is_declaration = True
                                    break


                            if is_declaration:
                                new_line = Line(the_function.lines[i].tokens[:the_equal+1])
                                new_line.is_declaration = True
                                the_function.lines.insert(i, new_line)
                                i += 1
                                n += 1

                                this_line = []
                                if line_number != "":
                                    this_line.append(line_number)

                                the_function.lines[i].tokens = this_line + curr[j-1:]

                            break

                j += 1
            
            i += 1
            
        return the_function


    def convert_operations(self, the_function: Function):
        # convert operations (+, -, *, /, ==, >, <, ~, |, &, [], %, ^, !, &&, ||)
        # into function calls for the entire function
        # + - plus
        # - - minus
        # - - negative
        # * - times 
        # / - dividedBy
        # == - equals
        # != - doesNotEqual
        # > - isGreaterThan
        # < - isLessThan
        # >= - isGreaterThanOrEqualTo
        # <= - isLessThanOrEqualTo
        # ~ - not
        # | - or 
        # & - and
        # [] - getElement 
        # % - mod
        # ^ - xor
        # ! - logicalNot
        # && - logicalNot
        # || - logicalOr
        # [x:y] - splice
        # << - leftShift
        # >> - rightShift

        operators = set(["+", "-", "*", "/", "==", "!=", ">", "<", ">=", "<=", "~", "|", "&", "%", "^", "!", "&&", "||", ">>", "<<"])

        # convert lines like i += 1 to i = i + 1
        the_function = self.convert_operation_equals(the_function)

        #  break declarations into multiple lines if assigned
        the_function = self.break_declarations(the_function)

        i = 0
        n = len(the_function.lines)
        while i < n:
            curr = the_function.lines[i].tokens
            j = 0
            m = len(curr)
            while j < m:
                if j + 1 < m:
                    match(curr[j]):
                        case "=":
                            if curr[j+1] == "=":
                                curr[j] = "=="
                                del curr[j+1]
                        case "<":
                            if curr[j+1] == "=":
                                curr[j] = "<="
                                del curr[j+1]
                            elif curr[j+1] == "<":
                                curr[j] = "<<"
                                del curr[j+1]
                        case ">":
                            if curr[j+1] == "=":
                                curr[j] = ">="
                                del curr[j+1]
                            elif curr[j+1] == ">":
                                curr[j] = ">>"
                                del curr[j+1]
                        case "<<":
                            if curr[j+1] == "=":
                                curr[j] = "<<="
                                del curr[j+1]
                        case ">>":
                            if curr[j+1] == "=":
                                curr[j] = ">>="
                                del curr[j+1]
                        case "&":
                            if curr[j+1] == "&":
                                curr[j] = "&&"
                                del curr[j+1]
                            pass
                        case "|":
                            if curr[j+1] == "|":
                                curr[j] = "||"
                                del curr[j+1]
                        case "!":
                            if curr[j+1] == "=":
                                curr[j] = "!="
                                del curr[j+1]

                j += 1
            i += 1

        # handle negations, bitwise not, and logical not
        i = 0
        n = len(the_function.lines)
        while i < n:
            curr = the_function.lines[i].tokens
            m = len(curr)
            j = 0
            while j < m:
                # handle bitwise not and logical not
                if curr[j] == "~" or curr[j] == "!":
                    curr.insert(j, 0)
                elif curr[j] == "-":
                    # this is a negation if there is an operator, =, [, or ( directly before
                    if j > 0:
                        if curr[j-1] in operators or curr[j-1] in ["=", "[", "(", ",", ":"]:
                            # convert to .negate()
                            curr[j] = "("
                            # the end of the negation will be directly before EOL or any operator
                            while j < m:
                                if curr[j] in operators or curr[j] in [")", "}", "]", "="]:
                                    break

                                j += 1
                            curr.insert(j, ")")
                            j += 1
                            curr.insert(j, ".")
                            j += 1
                            curr.insert(j, "negate")
                            j += 1
                            curr.insert(j, "(")
                            j += 1
                            curr.insert(j, ")")

                j += 1

            i += 1


        # convert array accesses/splices
        i = 0
        n = len(the_function.lines)
        while i < n:
            curr = the_function.lines[i].tokens
            m = len(curr)
            j = 0

            # only change this on lines that are not declarations
            if the_function.lines[i].is_declaration == False:
                while j < m:
                    # look for [ and ]
                    if curr[j] == "[":
                        starti = i
                        startj = j
                        is_splice = False
                        splicei = -1
                        splicej = -1
                        opens = 0
                        while i < n:
                            curr = the_function.lines[i].tokens
                            m = len(curr)
                            while j < m:
                                # find the end of the access
                                if curr[j] == "[":
                                    opens += 1
                                if curr[j] == "]":
                                    opens -= 1
                                if opens == 0:
                                    break
                                if opens == 1:
                                    if curr[j] == ":":
                                        is_splice = True
                                        splicei = i 
                                        splicej = j
                                j += 1
                            if opens == 0:
                                break
                            j = 0
                            i += 1
                        # found either the closing bracket or the end of the function
                        if i == n and j == m:
                            self.add_error("*", the_function.lines[starti], "SYNTAX", "'[' was unmatched...", "Add matching ']'.")
                        else:
                            # this can be an access, a splice, or an array declaration
                            # if it is an access or a slice, there will be a word, ), or ] before it
                            curr = the_function.lines[starti].tokens
                            m = len(curr)
                            is_splice_or_access = False
                            if startj > 0:
                                if curr[startj-1] != "=" and (curr[startj-1] not in operators or curr[startj-1] in [")", "]"]):
                                    # this is a slice or access
                                    is_splice_or_access = True

                                    if is_splice:
                                        # replace : with ,
                                        # replace [ with ( and ] with )
                                        # put splice before (
                                        the_function.lines[splicei].tokens[splicej] = ","
                                        the_function.lines[starti].tokens[startj] = "("
                                        the_function.lines[i].tokens[j] = ")"
                                        the_function.lines[starti].tokens.insert(startj, "splice")
                                        the_function.lines[starti].tokens.insert(startj, ".")
                                        startj += 2
                                        splicej += 2
                                        j += 2
                                        m += 2

                                        # set the arguments of splice to 0 if not present
                                        if splicei == starti and splicej - startj == 1:
                                            print("HERE1")
                                            the_function.lines[splicei].tokens.insert(splicej, "0")
                                            m += 1
                                            splicej += 1
                                            j += 1
                                        if i == splicei and j - splicej == 1:
                                            print("HERE2")
                                            the_function.lines[i].tokens.insert(splicej+1, "0")
                                            m += 1
                                            j += 1

                                        i = starti
                                    else:
                                        # a simple access
                                        the_function.lines[starti].tokens[startj] = "("
                                        the_function.lines[i].tokens[j] = ")"
                                        the_function.lines[starti].tokens.insert(startj, "getElement")
                                        the_function.lines[starti].tokens.insert(startj, ".")

                                        m += 2
                                        i = starti
                                        j = startj + 2
                            
                            if not is_splice_or_access:
                                # this is a declaration. join this onto one line
                                while i > starti:
                                    the_function.lines[i-1].tokens += the_function.lines[i].tokens
                                    del the_function.lines[i]
                                    i -= 1
                                    n -= 1

                                i = starti
                                j = startj
                        

                    j += 1

            i += 1
        


        # negations, array accesses, and unary operators are now taken care of

        # operator:precedence
        operator_functions = {
                ")":")",

                "||":"logicalOr",
                "&&":"logicalAnd",
                "|":"or",
                "^":"xor",
                "&":"and",

                "==":"equals",
                "!=":"doesNotEqual",

                ">":"isGreaterThan",
                ">=":"isGreaterThanOrEqualTo",
                "<":"isLessThan",
                "<=":"isLessThanOrEqualTo",

                "<<":"leftShift",
                ">>":"rightShift",

                "+":"plus",
                "-":"minus",

                "%":"mod",
                "*":"times",
                "/":"dividedBy",

                "~":"not",
                "!":"logicalNot",

                "(":"(",

                }
        operators = {
                ",":-2,
                ")":-1,

                "||":0,
                "&&":1,
                "|":2,
                "^":3,
                "&":4,

                "==":5,
                "!=":5,

                ">":6,
                ">=":6,
                "<":6,
                "<=":6,

                "<<":7,
                ">>":7,

                "+":8,
                "-":8,

                "%":9,
                "*":9,
                "/":9,

                "~":10,
                "!":10,

                "(":11,

                }

        #operators = set(["+", "-", "*", "/", "==", "!=", ">", "<", ">=", "<=", "~", "|", "&", "%", "^", "!", "&&", "||", ">>", "<<"])

        # x = 2 + 4 * 5
        # x = 2.plus(4.times(5))

        # x = (2 + 4) * 5
        # x = 2.plus(4).times(5)

        op_stack = []

        i = 0
        n = len(the_function.lines)
        while i < n:
            # search through the lines of the function for these operators
            curr = the_function.lines[i].tokens
            m = len(curr)

            j = 0
            last_was_op = False
            while j < m:
                # search through a single line for these operators
                if curr[j] in operators:
                    # we found an operator
                    if len(op_stack) == 0:
                        op_stack.append(curr[j])
                        if curr[j] != "(":
                            curr.insert(j, ".")
                            j += 1
                            m += 1
                            curr.insert(j, operator_functions[curr[j]])
                            j += 1
                            m += 1
                        curr[j] = "("
                    elif operators[curr[j]] > operators[op_stack[-1]]:
                        # if you find an operator with higher precendence, 
                        # start this operator and continue the one before
                        op_stack.append(curr[j])
                        if curr[j] != "(":
                            curr.insert(j, ".")
                            j += 1
                            m += 1
                            curr.insert(j, operator_functions[curr[j]])
                            j += 1
                            m += 1
                        curr[j] = "("

                    else:
                        # while this operator has lower or equal precedence,
                        # close the top operator and pop it
                        # then open this operator
                        if curr[j] != "(":
                            if curr[j] == ")":
                                # pop from the stack until reaching (
                                while len(op_stack) > 0 and op_stack[-1] != "(":
                                    curr.insert(j, ")")
                                    j += 1
                                    m += 1
                                    op_stack.pop()

                                j += 1
                                if len(op_stack) > 0:
                                    op_stack.pop()
                                

                            elif curr[j] == ",":
                                # pop from the stack until reaching (
                                while len(op_stack) > 0 and op_stack[-1] != "(":
                                    curr.insert(j, ")")
                                    j += 1
                                    m += 1
                                    op_stack.pop()
                            else:

                                while len(op_stack) > 0 and operators[curr[j]] <= operators[op_stack[-1]] and op_stack[-1] != "(":
                                    curr.insert(j, ")")
                                    j += 1
                                    m += 1
                                    op_stack.pop()
                                op_stack.append(curr[j])
                                curr.insert(j, ".")
                                j += 1
                                m += 1
                                curr.insert(j, operator_functions[curr[j]])
                                j += 1
                                m += 1

                                curr[j] = "("

                    last_was_op = True
                else:
                    last_was_op = False
                
                j += 1

            while len(op_stack) > 0:
                curr.append(")")
                op_stack.pop()
                
                
            i += 1


        # all operators have now been correctly converted into function calls

        return the_function


    def number_variables(self, the_function:Function, starting_number:int=0):
        # each line in the function should be one of the following:
        #   a variable declaration
        #   a function call
        #   a control flow statement (if, for, while, switch)

        # should perform access checking to make sure that nothing defies access specifiers
        
        builtins = ["int", "bool", "float", "short", "long", "double", "char", "void", "if", "(", ")", "{", "}", "[", "]", ",", "while", "for", "switch", "case", "return", "="]
        builtins = set(builtins)

        types = set(["int", "bool", "float", "short", "long", "double", "char", "void", "*"])





        # "name":"#<varnum>"
        found = {}
        # "#<varnum>":"name"
        reverse = {}

        i = 0
        n = len(the_function.lines)
        # iterate through the lines of the function
        line_number = []
        while i < n:
            curr = the_function.lines[i].tokens.copy()
            j = 0
            while j < len(curr):
                # get rid of line number tokens
                if len(curr[j]) > 0:
                    if curr[j][0] == '`':
                        line_number = [curr[j]]
                        del curr[j]
                        j -= 1

                # combine all $ with the token after them
                if curr[j] == "$":
                    if m > j + 1:
                        curr[j] = curr[j] + curr[j + 1]
                        del curr[j+1]
                        m -= 1

                j += 1
            j = 0
            m = len(curr)

            # iterate through the tokens in this line
            while j < m:
                if curr[j] != "(":
                    # if the next token is . 
                    # keep combining tokens until it is not
                    added = ""
                    while j + 1 < m and (added == "." or curr[j+1] == "."):
                        added = curr[j+1]
                        curr[j] = curr[j] + curr[j+1]
                        del curr[j+1]
                        m -= 1

                    # check if the combined token was found
                    if curr[j] not in builtins:
                        if curr[j] not in found:
                            debug(f"Found new variable: {curr[j]}")
                            varnum = f"#{starting_number}"
                            found[curr[j]] = varnum
                            reverse[varnum] = curr[j]
                            starting_number += 1

                            # TODO
                            # check to make sure that the new variable
                            # does not violate access specifiers
                            # we first need to know the type of each thing
                            # built-ins such as 2, 2.3, "hello", or 'c' can be treated as global
                            

                    if curr[j] in found:
                        curr[j] = found[curr[j]]
                        
                j += 1

            # recreate the line with the changes
            the_function.lines[i].tokens = line_number + curr

            i += 1

        print(found)

        return the_function



    def trace_function(self, the_function:Function):
        current_number = 0

        the_function = self.convert_operations(the_function)

        the_function = self.number_variables(the_function, current_number)

        # need to keep track of which functions call which so that recursive functions are not infinitely defined

        return the_function


    def trace(self):

        debug("Tracing...")

        # get the main class and function
        main_class, main_function = self.find_main_function()

        # kill the program and show the user that they need
        # a main class and function if they do not have one
        if main_class == None or main_function == None:
            [print(x) for x in self.EXCEPTIONS]
            exit()

        main_function = self.trace_function(main_function)

        [print(x) for x in main_function.lines]



class Variable:
    def __init__(self, num:int):
        self.num = num
        self.type = "void"



if __name__ == '__main__':
    all_exceptions = []

    compiler = Compiler("test.tcab")

    all_exceptions += compiler.EXCEPTIONS


    # the compiler now has a massive tree of classes and all imports handled
    # the only remaining tokens should be compiler directives, functions, statements inside of functions, declarations, and use statements
    parser = Parser(compiler.remaining_lines, compiler.classes)


    all_exceptions += parser.EXCEPTIONS

    sequencer = Sequencer(parser.classes, parser.directives)

    all_exceptions += sequencer.EXCEPTIONS

    print()
    print("EXCEPTIONS:")
    [print(x) for x in all_exceptions]




