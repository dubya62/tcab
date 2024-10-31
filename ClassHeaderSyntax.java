/**
 * Make sure that all class headers are in the correct format
 * <> = optional
 * [] = required
 *
 * <access specifier> class [ClassName] <extends> <parent1><,> <parent2> {
 *
 */

import java.util.ArrayList;

class ClassHeaderSyntax{
    public boolean threwErrors = false;

    public ClassHeaderSyntax(ArrayList<Token> tokens){
        Main.debug("Checking the syntax of class headers...");
            
        checkHeaders(tokens);

        Main.debug("Finished checking the syntax of class headers!");
    }

    private void checkHeaders(ArrayList<Token> fileTokens){
    }
}
