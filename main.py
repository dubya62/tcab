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

    def __str__(self):
        return self.lines.__str__()


class Class(Block):
    """
    A class.
    """
    def __init__(self, lines:list[str]):
        Block.__init__(lines)

class Function(Block):
    """
    A single function.
    """
    def __init__(self, lines:list[str]):
        Block.__init__(lines)


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


    def add_error(self, line: Line, cause: str, suggestions: str):
        # TODO: implement different types of errors
        result = ErrorMessage()
        result.type = "N/A"
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
        [print(x) for x in result]

        # now we should convert some of those lines into classes
        i = 0
        n = len(result)
        while i < n:
            m = len(result[i].tokens)
            if m > 1:
                # check if this is a class definition
                match (result[i].tokens[1]):
                    case "public":
                        if "static" in result[i].tokens:
                            self.add_error(result[i], "idk", 'idk')

                    case "private":
                        pass
                    case "protected":
                        pass
                    case "static":
                        pass
                    case "class":
                        pass
                    case default:
                        pass
            i += 1
            



if __name__ == '__main__':
    compiler = Compiler("example.mkt")

    [print(x) for x in compiler.EXCEPTIONS]

    




