/**
 * This class should deal with converting the entire program into a 
 * serial line of instructions
 * This means removing all functions and classes and converting variables into
 * unique identifiers
 */

import java.util.ArrayList;

public class Deabstractor{
    public ArrayList<Token> tokens;

    public Deabstractor(ArrayList<Token> tokens){
        Main.debug("Starting the Deabstractor...");

        this.tokens = tokens;

        // start with finding the main function
        this.tokens = deabstractMain(this.tokens);

        Main.debug("Deabstractor finished!");
        Main.debug("Deabstractor output:");
        Main.debug(this.tokens.toString());
        
    }

    public ArrayList<Token> deabstractMain(ArrayList<Token> fileTokens){




        return fileTokens;
    }

}
