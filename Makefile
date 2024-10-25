

CLASSES := Main.class Lexer.class Syntax.class Preprocessor.class Token.class Normalizer.class ConditionalCompiler.class

all: $(CLASSES)
	java Main



$(CLASSES): %.class: %.java
	javac $^
	
clean:
	rm -rf *.class
