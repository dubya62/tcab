/**
 * This file deals with normalizing the tokens into an easier form to deal with
 * 
 * This includes:
 *     Ignoring comments, multi-line comments, and documentation blocks
 *     Combining strings into single tokens
 *     Removing all semicolons (and fixing newlines)
 *     Handling lines broken with \
 *
 */

import java.util.ArrayList;


public class Normalizer{
    ArrayList<Token> tokens;

    public Normalizer(ArrayList<Token> tokens){
        Main.debug("Starting the Normalizer...");

        this.tokens = tokens;

        // ignore comments, multi-line comments, and documentation blocks
        this.tokens = this.ignoreComments(this.tokens);

        Main.debug("Finished Normalizing!");
        Main.debug("Normalizer Output:");
        Main.debug(this.toString());

    }

    /**
     * remove all comments, multi-line comments, and documentation blocks
     */
    private ArrayList<Token> ignoreComments(ArrayList<Token> tokens){
        Main.debug("Ignoring All Comments...");

        tokens = ignoreSingleLineComments(tokens);
        tokens = ignoreMultiLineComments(tokens);
        tokens = ignoreDocumentationBlocks(tokens);

        Main.debug("Finished Ignoring All Comments!");

        return tokens;
    }

    /**
     */
    private ArrayList<Token> ignoreSingleLineComments(ArrayList<Token> tokens){
        Main.debug("Ignoring Single Line Comments...");

        ArrayList<Token> result = new ArrayList<>();

        // iterate through the tokens and only add
        // a token to the result if it is not in a comment
        int i = 0;
        int quotes = 0;
        int comment = 0;
        while (i < tokens.size()){
            // toggle whether or not we are in quotes if we hit a quote char
            if (tokens.get(i).equals("\"")){
                if (comment == 0){
                    quotes ^= 1;
                    quotes &= 1;
                }
            } else if (tokens.get(i).equals("/")){
                if (i > 0 && tokens.get(i-1).equals("/")){
                    // we are in a comment if not in a string
                    if (quotes == 0){
                        comment ^= 1;
                        comment &= 1;
                        // remove the previous / since it is part of a comment
                        if (result.size() > 0){
                            result.remove(result.size() - 1);
                        }
                    }
                }
            } else if (tokens.get(i).equals("\\n")){
                comment = 0;
            }

            // add the current token if not in a comment
            if (comment == 0){
                result.add(tokens.get(i));
            }

            i++;
        }

        Main.debug("Finished Ignoring Single Line Comments!");
        return result;
    }

    /**
     */
    private ArrayList<Token> ignoreMultiLineComments(ArrayList<Token> tokens){
        Main.debug("Ignoring Multi Line Comments");
        ArrayList<Token> result = new ArrayList<>();

        // iterate through the tokens and only add
        // a token to the result if it is not in a comment
        int i = 0;
        int quotes = 0;
        int comment = 0;
        while (i < tokens.size()){
            // toggle whether or not we are in quotes if we hit a quote char
            if (tokens.get(i).equals("\"")){
                if (comment == 0){
                    quotes ^= 1;
                    quotes &= 1;
                }
            } else if (tokens.get(i).equals("*")){
                if (i > 0 && tokens.get(i-1).equals("/")){
                    // we are in a comment if not in a string
                    if (quotes == 0){
                        comment ^= 1;
                        comment &= 1;
                        // remove the previous / since it is part of a comment
                        if (result.size() > 0){
                            result.remove(result.size() - 1);
                        }
                    }
                }
            } else if (tokens.get(i).equals("/")){
                // close the comment if you reach */ not in quotes
                if (i > 0 && tokens.get(i-1).equals("*")){
                    if (quotes == 0){
                        comment = 0;
                        i++;
                        continue;
                    }
                }
            } else if (tokens.get(i).equals("\\n")){
                comment = 0;
            }

            // add the current token if not in a comment
            if (comment == 0){
                result.add(tokens.get(i));
            }

            i++;
        }
        Main.debug("Finished Ignoring Multi Line Comments!");
        return result;
    }

    /**
     */
    private ArrayList<Token> ignoreDocumentationBlocks(ArrayList<Token> tokens){
        Main.debug("Ignoring Documentation Blocks!");
        Main.debug("Finished Ignoring Documentation Blocks!");
        return tokens;
    }

    /**
     */
    public String toString(){
        return this.tokens.toString();
    }
}
