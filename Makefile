

CLASSES := Main.class Lexer.class Syntax.class Preprocessor.class Token.class Normalizer.class

all: $(CLASSES)
	java Main



$(CLASSES): %.class: %.java
	javac $^
	
clean:
	rm -rf *.class
