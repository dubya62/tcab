/**
 * Check accesses and throw related errors when an invalid access is made
 * (when the code violates an access specifier)
 */

import java.util.ArrayList;

public class AccessChecker{
    public boolean threwErrors = false;

    public AccessChecker(ArrayList<Token> tokens){
        Main.debug("Starting the AccessChecker...");

        // check each reference to each variable and make sure that the 
        // identifier both exists and is accessible


        Main.debug("AccessChecker finished!");
    }
}
