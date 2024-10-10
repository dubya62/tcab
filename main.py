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
                # ignore lines with nothing on them
                if len(curr_line) == 0:
                    pass
                else:
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
            if len(result[i]) > 0:
                # check if this is a class definition
                match (result[i][0]):
                    case "public":
                        pass
                    case "private":
                        pass
                    case "protected":
                        pass
                    case "class":
                        pass
            



if __name__ == '__main__':
    compiler = Compiler("example.mkt")

    




