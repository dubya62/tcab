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
    public ArrayList<Token> tokens;

    public ClassHeaderSyntax(ArrayList<Token> tokens){
        Main.debug("Checking the syntax of class headers...");
            
        tokens = checkHeaders(tokens);

        Main.debug("Finished checking the syntax of class headers!");

        this.tokens = tokens;
    }

    private ArrayList<Token> checkHeaders(ArrayList<Token> fileTokens){

        int n = fileTokens.size();
        int i=0;
        while (i < n) {
            // when a class is found
            if (fileTokens.get(i).token.equals("class")){
                if (i > 0){
                    String wordBefore = fileTokens.get(i-1).token;
                    // make sure the word before class is public, private, protected, or ;
                    switch(wordBefore){
                        case ";":
                            if (i > 1){
                                boolean breaking = false;
                                switch(fileTokens.get(i-2).token){
                                    case "public":
                                    case "private":
                                    case "protected":
                                        // delete the extra semicolon
                                        fileTokens.remove(i-1);
                                        i--;
                                        n--;
                                        breaking = true;
                                }
                                if (breaking){
                                    break;
                                }
                            }
                        case "public":
                        case "private":
                        case "protected":
                            break;
                        default:
                            Error theError = new Error("SYNTAX", "Unexcepted token '" + wordBefore + "' before class definition...", "Remove/fix the offending token.");
                            theError.setErrorToken(fileTokens.get(i-1));
                            Main.addError(theError);
                            this.threwErrors = true;
                    }
                }

                // remove extra semicolons after
                while (i+1 < n && fileTokens.get(i+1).token.equals(";")){
                    fileTokens.remove(i+1);
                    n--;
                }

                // make sure the words after are a name
                if (i < n){
                    String nextToken = fileTokens.get(i+1).token;
                    if (nextToken.equals("{")){
                        Error theError = new Error("SYNTAX", "Expected a class name after the class keyword...", "Give this class a proper name.");
                        theError.setErrorToken(fileTokens.get(i));
                        Main.addError(theError);
                        this.threwErrors = true;
                    }
                    // TODO: make sure the words after the name are either { or extends

                } else {
                    Error theError = new Error("SYNTAX", "Expected a class name after the class keyword...", "Give this class a proper name.");
                    theError.setErrorToken(fileTokens.get(i));
                    Main.addError(theError);
                    this.threwErrors = true;
                }

            }

            i++;
        }


        return fileTokens; 
    }
}
