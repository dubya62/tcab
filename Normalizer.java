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
    public ArrayList<Token> tokens;

    public Normalizer(ArrayList<Token> tokens){
        Main.debug("Starting the Normalizer...");

        this.tokens = tokens;

        // ignore comments, multi-line comments, and documentation blocks
        this.tokens = this.ignoreComments(this.tokens);

        // remove all semicolons and fix newlines
        this.tokens = this.removeSemicolons(this.tokens);

        // remove all duplicate newlines
        this.tokens = this.removeDuplicateNewlines(this.tokens);
        
        // handle lines broken with \
        this.tokens = this.combineBrokenLines(this.tokens);

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
            } else if (tokens.get(i).equals("\n")){
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
        ArrayList<Token> result = new ArrayList<>();

        // iterate through the tokens and only add
        // a token to the result if it is not in a comment
        int i = 0;
        int quotes = 0;
        int comment = 0;
        int opens = 0;
        while (i < tokens.size()){
            // toggle whether or not we are in quotes if we hit a quote char
            if (tokens.get(i).equals("\"")){
                if (comment == 0){
                    quotes ^= 1;
                    quotes &= 1;
                }
            } else if (tokens.get(i).equals("&")){
                i++;
                while (i < tokens.size() && tokens.get(i).equals("\n")){
                    i++;
                }
                if (i < tokens.size() && tokens.get(i).equals("{")){
                    // we are in a comment if not in a string
                    if (quotes == 0){
                        comment ^= 1;
                        comment &= 1;
                    }
                }
                opens++;
            } else if (tokens.get(i).equals("}")){
                opens--;
                if (opens == 0){
                    comment = 0;
                    i++;
                    continue;
                }
            } 

            // add the current token if not in a comment
            if (comment == 0){
                result.add(tokens.get(i));
            }

            i++;
        }
        Main.debug("Finished Ignoring Documentation Blocks!");
        return result;
    }

    /**
     * Replace all semicolons with newline characters
     */
    private ArrayList<Token> removeSemicolons(ArrayList<Token> tokens){
        Main.debug("Replacing all semicolons with newlines...");
        ArrayList<Token> result = new ArrayList<>();

        for (int i=0; i<tokens.size(); i++){
            if (tokens.get(i).token.equals(";")){
                tokens.get(i).token = "\n";
            } 
            result.add(tokens.get(i));
        }


        Main.debug("Finished replacing semicolons!");
        return result;
    }

    /**
     * If there are mutliple adjacent newlines,
     * remove until there is only one
     */
    private ArrayList<Token> removeDuplicateNewlines(ArrayList<Token> tokens){
        Main.debug("Removing all duplicate newlines...");
        ArrayList<Token> result = new ArrayList<>();

        boolean lastWasNewline = true;
        for (int i=0; i<tokens.size(); i++){
            // ignore duplicate newlines
            if (tokens.get(i).token.equals("\n")){
                if (lastWasNewline){
                    continue;
                }
                // replace with a semicolon as a separator
                tokens.get(i).token = ";";
                lastWasNewline = true;
            } else {
                lastWasNewline = false;
            }

            result.add(tokens.get(i));
        }

        Main.debug("Finished removing duplicate newlines!");
        return result;
    }


    /**
     * Combine lines broken with ;
     */
    private ArrayList<Token> combineBrokenLines(ArrayList<Token> tokens){
        Main.debug("Combining Lines that end with \\...");
        ArrayList<Token> result = new ArrayList<>();

        // look for \ with ; directly after it. 
        // once found, ignore both \ and ;
        int continues = 0;
        for (int i=0; i<tokens.size(); i++){
            if (continues > 0){
                continues--;
                continue;
            }

            if (tokens.get(i).token.equals("\\")){
                if (i + 1 < tokens.size()){
                    if (tokens.get(i+1).token.equals(";")){
                        continues += 1;
                        continue;
                    }
                }
            }

            result.add(tokens.get(i));

        }

        Main.debug("Finished combining Lines that end with \\!");
        return result;
    }


    /**
     */
    public String toString(){
        return this.tokens.toString();
    }
}



