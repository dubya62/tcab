/**
 * This is the main Compiler program
 * It will deal with things such as the user supplied CLI args
 * as well as calling necessary functions in other modules
 */

import java.util.ArrayList;

public class Main{
    // whether or not to print debug information
    static boolean DEBUG = true;
    static ArrayList<Error> errors = new ArrayList<>();

    public static ArrayList<Token> preprocessFile(CliArgs cliArgs, String filename){
        // perform tokenization
        Lexer lexer = new Lexer(filename);
        ArrayList<Token> tokens = lexer.getTokens();

        // perform normalization (removing comments etc.)
        Normalizer normalizer = new Normalizer(tokens);
        tokens = normalizer.tokens;
        
        // handle conditional compilation
        ConditionalCompiler conditionalCompiler = new ConditionalCompiler(tokens, cliArgs);
        tokens = conditionalCompiler.tokens;

        return tokens;
    }

    public static void main(String[] args){
        // parse the cliArgs
        CliArgs cliArgs = parseCliArgs(args);
        Main.debug("Command Line Arguments:");
        Main.debug(cliArgs.toString());
        
        // recursively add imports
        ImportHandler importHandler = new ImportHandler(cliArgs);
        ArrayList<Token> tokens = importHandler.tokens;
        
        // perform syntax error checking (on this file and all imports)
        SyntaxChecker syntaxChecker = new SyntaxChecker(tokens);
        tokens = syntaxChecker.tokens;

        // convert $ test functions to actual functions
        TestFunctionConverter testFunctionConverter = new TestFunctionConverter(tokens);
        tokens = testFunctionConverter.tokens;

        // perform access error checking (on this file and all imports)
        AccessChecker accessChecker = new AccessChecker(tokens);

        // display errors if one was encountered
        if (Main.errors.size() > 0){
            Main.exit();
        }

        // perform deabstraction (converting methods into a serial program)
        Deabstractor deabstractor = new Deabstractor(tokens);
        tokens = deabstractor.tokens;
        
        // pretranslate based on the target platform
        
        // optimize based on the target platform

        // write compiler errors to stdout
        

        // write the output code to the correct file type

    }

    /**
     */
    public static CliArgs parseCliArgs(String[] args){
        CliArgs result = new CliArgs(args);
        return result;
    }

    /**
     */
    public static void addError(Error error){
        Main.errors.add(error);
    }

    /**
     * print debug information
     */
    public static void debug(String message){
        if (Main.DEBUG){
            System.out.println(message);
        }
    }

    /**
     * Print out all compiler errors and exit the program
     */
    public static void exit(){
        for (int i=0; i<errors.size(); i++){
            System.out.println(errors.get(i).toString());
        }
        System.exit(1);
    }



}


