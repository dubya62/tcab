

CLASSES := Main.class Lexer.class Syntax.class Preprocessor.class Token.class Normalizer.class ConditionalCompiler.class CliArgs.class CompilerVariable.class ImportHandler.class ImportStatement.class

all: $(CLASSES)
	java Main -d debug=true test.tcab


$(CLASSES): %.class: %.java
	javac $^
	
clean:
	rm -rf *.class
