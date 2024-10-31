/**
 * This class should check the syntax of a list of tokens and add
 * relevant errors where needed
 */

import java.util.ArrayList;
import java.util.Stack;

public class SyntaxChecker{
    public boolean threwErrors = false;
    public ArrayList<Token> tokens;

    public SyntaxChecker(ArrayList<Token> tokens){
        Main.debug("Starting the SyntaxChecker...");

        // check class headers
        ClassHeaderSyntax classHeaderSyntax = new ClassHeaderSyntax(tokens);
        if (classHeaderSyntax.threwErrors){
            this.threwErrors = true;
        }
        this.tokens = classHeaderSyntax.tokens;

        // check function headers

        // check all variable names (to make sure they follow the rules)

        // make sure all (, {, and [ are matched properly
        findUnmatchedBlocks(this.tokens);

        // make sure $ test functions are only after functions


        Main.debug("SyntaxChecker finished!");
        Main.debug("SyntaxChecker output:");
        Main.debug(tokens.toString());

    }


    public void findUnmatchedBlocks(ArrayList<Token> fileTokens){
        Stack<Token> stack = new Stack<>();
        for (int i=0; i<fileTokens.size(); i++){
            switch(fileTokens.get(i).token){
                case "(":
                case "{":
                case "[":
                    stack.push(fileTokens.get(i));
                    break;
                case ")":
                case "}":
                case "]":
                    if (stack.size() < 1){
                        Error theError = new Error("SYNTAX", "Unmatched '" + fileTokens.get(i).token + "'...", "Match it with the correct opener.");
                        theError.setErrorToken(fileTokens.get(i));
                        Main.addError(theError);
                        this.threwErrors = true;
                    } else {
                        Token currToken = stack.pop();
                        if (currToken.token.equals("(") && !fileTokens.get(i).token.equals(")")){
                            Error theError = new Error("SYNTAX", "Unmatched '" + currToken.token + "'...", "Match it with the correct opener.");
                            theError.setErrorToken(currToken);
                            Main.addError(theError);
                            this.threwErrors = true;
                        } 
                        else if (currToken.token.equals("[") && !fileTokens.get(i).token.equals("]")){
                            Error theError = new Error("SYNTAX", "Unmatched '" + currToken.token + "'...", "Match it with the correct opener.");
                            theError.setErrorToken(currToken);
                            Main.addError(theError);
                            this.threwErrors = true;
                        } 
                        else if (currToken.token.equals("{") && !fileTokens.get(i).token.equals("}")){
                            Error theError = new Error("SYNTAX", "Unmatched '" + currToken.token + "'...", "Match it with the correct opener.");
                            theError.setErrorToken(currToken);
                            Main.addError(theError);
                            this.threwErrors = true;
                        } 
                    }
                    break;

            }
        }
        while (stack.size() > 0){
            Token currToken = stack.pop();
            Error theError = new Error("SYNTAX", "Unmatched '" + currToken.token + "'...", "Match it with the correct closer.");
            theError.setErrorToken(currToken);
            Main.addError(theError);
            this.threwErrors = true;
        }


    }



}
