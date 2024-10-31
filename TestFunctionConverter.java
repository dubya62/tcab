/**
 * Converts $ test functions into actual functions 
 * (with the same properties as the original function)
 */

import java.util.ArrayList;
import java.util.Stack;

public class TestFunctionConverter{
    public ArrayList<Token> tokens;

    public TestFunctionConverter(ArrayList<Token> tokens){
        Main.debug("Converting $ test functions into normal functions...");

        this.tokens = convertTestFunctions(tokens);


        Main.debug("Finished converting $ test functions into normal functions!");
        Main.debug("TestFunctionConverter output:");
        Main.debug(this.tokens.toString());

    }

    public ArrayList<Token> convertTestFunctions(ArrayList<Token> fileTokens){
        // look for '$' then '{' to denote a test function
        ArrayList<Token> result = new ArrayList<>();

        int n = fileTokens.size();
        int i = 0;
        while (i < n){
            if (fileTokens.get(i).equals("$")){
                if (i+1 < n){
                    if (fileTokens.get(i+1).equals("{")){
                        // find the function that this is attached to and replicate it
                        while (i > 0 && fileTokens.get(i-1).equals(";")){
                            fileTokens.remove(i-1);
                            result.remove(i-1);
                            i--;
                            n--;
                        }

                        int returnSpot = i;

                        // we should now be at the }. need to match it
                        Stack<Integer> stack = new Stack<>();
                        while (i > 0){
                            if (fileTokens.get(i).equals("}")){
                                stack.push(1);
                            } else if (fileTokens.get(i).equals("{")){
                                if (stack.size() > 0){
                                    stack.pop();
                                }
                                if (stack.size() == 0){
                                    // this is the matching spot
                                    break;
                                }
                            }
                            i--;
                        }

                        // collect tokens to the previous ;
                        ArrayList<Token> originalFunction = new ArrayList<>();
                        int startingBrace = i;
                        Integer openParenthesis = null;
                        Stack<Integer> parenthesisStack = new Stack<>();
                        while (i > 0 && !fileTokens.get(i).equals(";")){
                            if (fileTokens.get(i).equals(")")){
                                parenthesisStack.push(1);
                            } else if (parenthesisStack.size() > 0 && fileTokens.get(i).equals("(")){
                                parenthesisStack.pop();
                                if (parenthesisStack.size() == 0){
                                    openParenthesis = i; 
                                }
                            }
                            i--;
                        }
                        i++;
                        int functionBeginning = i;

                        while (i < startingBrace){
                            originalFunction.add(fileTokens.get(i));
                            i++;
                        }

                        i = returnSpot;

                        // find the location where the $ should go
                        if (openParenthesis == null){
                            Error theError = new Error("SYNTAX", "You cannot make a test function of a test function...", "Remove one of the test functions.");
                            theError.setErrorToken(fileTokens.get(i));
                            Main.addError(theError);
                            i++;
                            continue;
                        }
                        int dollarSignSpot = openParenthesis - functionBeginning - 1;

                        result.add(new Token(fileTokens.get(i).filename, fileTokens.get(i).lineNumber, ";"));

                        for (int j=0; j<originalFunction.size(); j++){
                            if (j == dollarSignSpot){
                                // put the $ in the correct spot
                                result.add(new Token(fileTokens.get(i).filename, fileTokens.get(i).lineNumber, "$"));
                            }
                            result.add(originalFunction.get(j));
                        }

                    }
                }
            } else {
                result.add(fileTokens.get(i));
            }


            i++;
        }

        return result;
    }

}
