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
    public ConditionalCompiler(ArrayList<Token> tokens, CliArgs cliArgs){
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

                        expressionResult = evaluateExpression(cliArgs, expression);
                        Main.debug("Expression " + expression.toString() + " evaluated to " + expressionResult);
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
                        // if last if opened was true, start ignoring
                        boolean lastIf = ifsWereOpened.pop();
                        ifsWereOpened.push(lastIf);
                        if (lastIf){
                            ignoring = true;
                            i++;
                            continue;
                        } else {
                            ignoring = false;
                        }

                        // evaluate expression

                        expression = new ArrayList<>();
                        i++;
                        i++;
                        while (i < n && !tokens.get(i).equals(";")){
                            expression.add(tokens.get(i));
                            i++;
                        }

                        expressionResult = evaluateExpression(cliArgs, expression);
                        Main.debug("Expression " + expression.toString() + " evaluated to " + expressionResult);
                        if (expressionResult){
                            ifsWereOpened.pop();
                            ifsWereOpened.push(true);
                        }

                        if (!ignoring){
                            ignoring = !expressionResult;
                        }

                        i++;
                        continue;
                    } else if (tokens.get(i+1).equals("else")){
                        // make sure the last #if didn't happen
                        if (ifsWereOpened.isEmpty()){
                            Error theError = new Error("SYNTAX", "Cannot have #else directive without an #if directive before it...", "Use an #if directive here.");
                            theError.setErrorToken(tokens.get(i+1));
                            Main.addError(theError);
                            Main.exit();
                        }
                        // if last if opened was true, start ignoring
                        boolean lastIf = ifsWereOpened.pop();
                        ifsWereOpened.push(lastIf);
                        if (lastIf){
                            ignoring = true;
                            i++;
                            continue;
                        } else {
                            ignoring = false;
                        }

                        i += 3;
                        continue;
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
    private boolean evaluateExpression(CliArgs cliArgs, ArrayList<Token> expression){
        // expression should be in this form
        // [variable] [comparison operator] [value]
        // conditional operators:
        // ==, <=, >=, <, >, !=
        if (expression.size() < 3){
            Error theError = new Error("SYNTAX", "Expected expression in the form '[variable] [comparison operator] [value]'...", "Fix it...");
            theError.setErrorToken(expression.get(0));
            Main.addError(theError);
            Main.exit();
        }


        // if the variable name is not defined in the cliArgs, return false
        boolean variableIsDefined = false;
        CompilerVariable commandLineVariable = null;
        for (int i=0; i<cliArgs.compilerVariables.size(); i++){
            if (cliArgs.compilerVariables.get(i).name.equals(expression.get(0).token)){
                variableIsDefined = true;
                commandLineVariable = cliArgs.compilerVariables.get(i);
            }
        }
        if (!variableIsDefined){
            return false;
        }


        // find the comparison operator
        String comparisonOperator = "";
        int valueStart = 0;
        if (expression.get(1).equals("=")){
            if (expression.get(2).equals("=")){
                comparisonOperator = "==";
                valueStart = 3;
            }
        } else if (expression.get(1).equals("<")){
            if (expression.get(2).equals("=")){
                comparisonOperator = "<=";
                valueStart = 3;
            } else {
                comparisonOperator = "<";
                valueStart = 2;
            }
        } else if (expression.get(1).equals(">")){
            if (expression.get(2).equals("=")){
                comparisonOperator = ">=";
                valueStart = 3;
            } else {
                comparisonOperator = ">";
                valueStart = 2;
            }
        } else if (expression.get(1).equals("!")){
            if (expression.get(2).equals("=")){
                comparisonOperator = "!=";
                valueStart = 3;
            }
        }
        if (comparisonOperator.equals("")){
            Error theError = new Error("SYNTAX", "Invalid Comparison Operator...", "Use a valid comparison operator...");
            theError.setErrorToken(expression.get(1));
            Main.addError(theError);
            return false;
        }

        // concatenate the rest of the expression and infer its type
        String totalValue = "";
        for (int i=valueStart; i<expression.size(); i++){
            totalValue += expression.get(i).token;
        }
        // if empty, throw an error
        if (totalValue.equals("")){
            Error theError = new Error("SYNTAX", "Expected a value after the comparison operator...", "Use a valid value...");
            theError.setErrorToken(expression.get(1));
            Main.addError(theError);
        }

        // infer the variable's type
        String valueType = CompilerVariable.inferType(totalValue);

        // see if the types are compatible for the operation
        if (!valueType.equals(commandLineVariable.type)){
            // if they are not the same, throw an error
            Error theError = new Error("COMPILER", "The type of '" + commandLineVariable.name + "' does not match this type...", "Use a valid value...");
            theError.setErrorToken(expression.get(valueStart));
            Main.addError(theError);
            return false;
        }

        // the types are compatible. Compare them to determine the final outcome
        if (comparisonOperator.equals("==")){
            if (valueType.equals("int")){
                return Integer.parseInt(totalValue) == Integer.parseInt(commandLineVariable.value);
            } else if(valueType.equals("float")){
                return Float.parseFloat(totalValue) == Float.parseFloat(commandLineVariable.value);
            } else if (valueType.equals("bool")){
                return totalValue.equals(commandLineVariable.value);
            } else if (valueType.equals("String")){
                return totalValue.equals(commandLineVariable.value);
            }
        } else if (comparisonOperator.equals("!=")){
            if (valueType.equals("int")){
                return Integer.parseInt(totalValue) != Integer.parseInt(commandLineVariable.value);
            } else if(valueType.equals("float")){
                return Float.parseFloat(totalValue) != Float.parseFloat(commandLineVariable.value);
            } else if (valueType.equals("bool")){
                return !totalValue.equals(commandLineVariable.value);
            } else if (valueType.equals("String")){
                return !totalValue.equals(commandLineVariable.value);
            }
        } else if (comparisonOperator.equals("<")){
            if (valueType.equals("int")){
                return Integer.parseInt(commandLineVariable.value) < Integer.parseInt(totalValue);
            } else if(valueType.equals("float")){
                return Float.parseFloat(commandLineVariable.value) < Float.parseFloat(totalValue);
            } else if (valueType.equals("bool")){
                Error theError = new Error("COMPILER", "Cannot compare bool with bool using '" + comparisonOperator + "'...", "Use a valid comparison operator...");
                theError.setErrorToken(expression.get(valueStart-1));
                Main.addError(theError);
                return false;
            } else if (valueType.equals("String")){
                Error theError = new Error("COMPILER", "Cannot compare String with String using '" + comparisonOperator + "'...", "Use a valid comparison operator...");
                theError.setErrorToken(expression.get(valueStart-1));
                Main.addError(theError);
                return false;
            }
        } else if (comparisonOperator.equals("<=")){
            if (valueType.equals("int")){
                return Integer.parseInt(commandLineVariable.value) <= Integer.parseInt(totalValue);
            } else if(valueType.equals("float")){
                return Float.parseFloat(commandLineVariable.value) <= Float.parseFloat(totalValue);
            } else if (valueType.equals("bool")){
                Error theError = new Error("COMPILER", "Cannot compare bool with bool using '" + comparisonOperator + "'...", "Use a valid comparison operator...");
                theError.setErrorToken(expression.get(valueStart-1));
                Main.addError(theError);
                return false;
            } else if (valueType.equals("String")){
                Error theError = new Error("COMPILER", "Cannot compare String with String using '" + comparisonOperator + "'...", "Use a valid comparison operator...");
                theError.setErrorToken(expression.get(valueStart-1));
                Main.addError(theError);
                return false;
            }

        } else if (comparisonOperator.equals(">")){
            if (valueType.equals("int")){
                return Integer.parseInt(commandLineVariable.value) > Integer.parseInt(totalValue);
            } else if(valueType.equals("float")){
                return Float.parseFloat(commandLineVariable.value) > Float.parseFloat(totalValue);
            } else if (valueType.equals("bool")){
                Error theError = new Error("COMPILER", "Cannot compare bool with bool using '" + comparisonOperator + "'...", "Use a valid comparison operator...");
                theError.setErrorToken(expression.get(valueStart-1));
                Main.addError(theError);
                return false;
            } else if (valueType.equals("String")){
                Error theError = new Error("COMPILER", "Cannot compare String with String using '" + comparisonOperator + "'...", "Use a valid comparison operator...");
                theError.setErrorToken(expression.get(valueStart-1));
                Main.addError(theError);
                return false;
            }
        } else if (comparisonOperator.equals(">=")){
            if (valueType.equals("int")){
                return Integer.parseInt(commandLineVariable.value) >= Integer.parseInt(totalValue);
            } else if(valueType.equals("float")){
                return Float.parseFloat(commandLineVariable.value) >= Float.parseFloat(totalValue);
            } else if (valueType.equals("bool")){
                Error theError = new Error("COMPILER", "Cannot compare bool with bool using '" + comparisonOperator + "'...", "Use a valid comparison operator...");
                theError.setErrorToken(expression.get(valueStart-1));
                Main.addError(theError);
                return false;
            } else if (valueType.equals("String")){
                Error theError = new Error("COMPILER", "Cannot compare String with String using '" + comparisonOperator + "'...", "Use a valid comparison operator...");
                theError.setErrorToken(expression.get(valueStart-1));
                Main.addError(theError);
                return false;
            }
        }


        return false;
    }

    public String toString(){
        return this.tokens.toString();
    }

}

