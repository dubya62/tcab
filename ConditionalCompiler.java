/**
 * Handle conditional compilation by ignoring needed tokens
 * This should remove any compiler directives dealing with conditional compilation
 */

import java.util.ArrayList;
import java.util.Stack;

public class ConditionalCompiler{
    public ArrayList<Token> tokens;

    /**
     * Take in a list of cliVariables and make compilation decisions based on them
     */
    public ConditionalCompiler(ArrayList<Token> tokens, ArrayList<String> cliVariables){
        Main.debug("Starting the conditional compiler...");

        // conditional compilation directives start with #
        // #if 
        // #elif
        // #else
        // #endif
        //
        // The directives can either use built-in compiler variables or 
        // cliVariables supplied at the compiler's runtime
        // _PLATFORM:
        //     windows
        //     mac
        //     linux
        //     web
        //     ios
        //     android
        //
        // _ARCHITECTURE:
        //     x86_64
        //     i386
        //     arm64
        //     arm32
        //
        //  _DEBUG:
        //     true/false
        //
       
        // TODO: if platform or architecture is not supplied in the cliArgs, 
        // assume them to be whatever the compiler is running on
        
        this.tokens = tokens;

        // in a conditional compilation directive, you can use #if, #elif, #else, or #endif
        // after these should be tokens that evaluate to a boolean true or false
        // if the condition is true, include that code; otherwise, ignore it
        ArrayList<Token> result = new ArrayList<>();
        ArrayList<Token> expression;

        int i = 0;
        int n = tokens.size();
        boolean ignoring = false;
        boolean expressionResult;
        int opens = 0;

        Stack<Boolean> ifsWereOpened = new Stack<>();
        
        while (i < n){
            // we are looking for # and then one of the keywords
            if (tokens.get(i).equals("#")){
                if (i+1 < n){
                    if (tokens.get(i+1).equals("if")){
                        // evaluate expression
                        expression = new ArrayList<>();
                        i++;
                        i++;
                        while (i < n && !tokens.get(i).equals(";")){
                            expression.add(tokens.get(i));
                            i++;
                        }

                        expressionResult = evaluateExpression(cliVariables, expression);
                        // save whether or not it was opened
                        ifsWereOpened.push(expressionResult);

                        if (!ignoring){
                            ignoring = !expressionResult;
                            opens = 0;
                        }

                        opens++;
                        i++;
                        continue;
                    } else if (tokens.get(i+1).equals("elif")){
                        // make sure the last #if didn't happen
                        if (ifsWereOpened.isEmpty()){
                            Error theError = new Error("SYNTAX", "Cannot have #elif directive without an #if directive before it...", "Use an #if directive here.");
                            theError.setErrorToken(tokens.get(i+1));
                            Main.addError(theError);
                            Main.exit();
                        }


                        // evaluate expression

                        expression = new ArrayList<>();
                        i++;
                        i++;
                        while (i < n && !tokens.get(i).equals(";")){
                            expression.add(tokens.get(i));
                            i++;
                        }

                        expressionResult = evaluateExpression(cliVariables, expression);

                    } else if (tokens.get(i+1).equals("else")){
                        // evaluate expression
                        expression = new ArrayList<>();
                        i++;
                        i++;
                        while (i < n && !tokens.get(i).equals(";")){
                            expression.add(tokens.get(i));
                            i++;
                        }

                        expressionResult = evaluateExpression(cliVariables, expression);

                    } else if (tokens.get(i+1).equals("endif")){
                        if (ifsWereOpened.isEmpty()){
                            Error theError = new Error("SYNTAX", "Missing matching #if to #endif...", "Either delete this #endif or create the matching #if.");
                            theError.setErrorToken(tokens.get(i+1));
                            Main.addError(theError);
                            Main.exit();
                        }
                        ifsWereOpened.pop();
                        opens--;
                        if (opens == 0){
                            ignoring = false;
                        }
                        i += 3;
                        continue;

                    } 
                }

            }

            if (!ignoring){
                result.add(tokens.get(i));
            }

            i++;
        }


        this.tokens = result;

        Main.debug("Conditional compiler finished!");
        Main.debug("Conditional compiler output:");
        Main.debug(this.toString());
    }


    /**
     * Evaluate a conditional compiler directive expression based on the cliArgs
     */
    private boolean evaluateExpression(ArrayList<String> cliArgs, ArrayList<Token> expression){
        System.out.println(expression.toString());
        return false;
    }

    public String toString(){
        return this.tokens.toString();
    }

}

