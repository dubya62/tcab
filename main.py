"""
The purpose of this program is to transpile mkt scripts into highly efficient, platform independent c (or cuda) scripts
The user can then compile the C/Cuda script into machine code

The idea behind the compiler is that all checks are done at compile time, meaning there
are no runtime errors (unless using inline assembly)

The compiler will also apply heavy optimizations to the program, including algorithmic optimization

"""

class Compiler:
    def __init__(self, filename:str):
        self.data = self.open_file(filename)
        self.tokens = self.tokenize(self.data)


    def open_file(self, filename:str):
        try:
            with open(filename, 'r') as f:
                data = f.read()
        except:
            print(f"Error opening file {filename}")
        return data 


    def tokenize(self, lines:list[str]):
        break_tokens = ["\n", "*", "$", "#", ".", ",", "[", "]", "<", ">", "&", "|", "\t", " ", "~", "^", "(", ")", "@", "%", "/", "=", "+", "-"]
        break_tokens = set(break_tokens)

        return result



if __name__ == '__main__':
    compiler = Compiler("example.mkt")
    




