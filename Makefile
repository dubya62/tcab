

CLASSES := Main.class Lexer.class Preprocessor.class Token.class Normalizer.class ConditionalCompiler.class CliArgs.class CompilerVariable.class ImportHandler.class ImportStatement.class SyntaxChecker.class AccessChecker.class ClassHeaderSyntax.class TestFunctionConverter.class Deabstractor.class

all: $(CLASSES)
	java Main -d debug=true test.tcab


$(CLASSES): %.class: %.java
	javac $^
	
clean:
	rm -rf *.class
