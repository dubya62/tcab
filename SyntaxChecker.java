/**
 * This class should check the syntax of a list of tokens and add
 * relevant errors where needed
 */

import java.util.ArrayList;

public class SyntaxChecker{
    public boolean threwErrors = false;

    public SyntaxChecker(ArrayList<Token> tokens){
        Main.debug("Starting the SyntaxChecker...");

        // check class headers
        ClassHeaderSyntax classHeaderSyntax = new ClassHeaderSyntax(tokens);
        if (classHeaderSyntax.threwErrors){
            this.threwErrors = true;
        }

        // check function headers

        // check all variable names (to make sure they follow the rules)

        // make sure all (, {, and [ are matched properly



        Main.debug("SyntaxChecker finished!");
    }



}
