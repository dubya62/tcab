

all: Main.class Lexer.class Syntax.class Preprocessor.class Token.class Normalizer.class
	java Main

%.class: %.java
	javac $^
	
clean:
	rm -rf *.class
