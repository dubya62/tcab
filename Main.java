/**
 * This is the main Compiler program
 * It will deal with things such as the user supplied CLI args
 * as well as calling necessary functions in other modules
 */

import java.util.ArrayList;

public class Main{
    // whether or not to print debug information
    static boolean DEBUG = true;

    public static void main(String[] args){
        // perform tokenization
        Lexer lexer = new Lexer("test.tcab");
        ArrayList<Token> tokens = lexer.getTokens();

        // perform normalization (removing comments etc.)
        Normalizer normalizer = new Normalizer(tokens);
        tokens = normalizer.tokens;
        
        // handle conditional compilation
        
        // recursively add imports
        
        // perform syntax error checking

        // perform access error checking

        // perform deabstraction (converting methods into a serial program)
        
        // preprocess based on the target platform
        
        // optimize based on the target platform
        
        // write the output code to the correct file type

    }

    /**
     * print debug information
     */
    public static void debug(String message){
        if (Main.DEBUG){
            System.out.println(message);
        }
    }



}


