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

    public static void main(String[] args){

        // parse the cliArgs
        ArrayList<String> cliVariables = new ArrayList<>();
        cliVariables.add("test=true");
        cliVariables.add("testing=5.4");


        // perform tokenization
        Lexer lexer = new Lexer("test.tcab");
        ArrayList<Token> tokens = lexer.getTokens();

        // perform normalization (removing comments etc.)
        Normalizer normalizer = new Normalizer(tokens);
        tokens = normalizer.tokens;
        
        // handle conditional compilation
        ConditionalCompiler conditionalCompiler = new ConditionalCompiler(tokens, cliVariables);
        tokens = conditionalCompiler.tokens;
        
        // recursively add imports
        
        // perform syntax error checking

        // perform access error checking

        // perform deabstraction (converting methods into a serial program)
        
        // preprocess based on the target platform
        
        // optimize based on the target platform

        // write compiler errors to stdout
        

        // write the output code to the correct file type

    }

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


