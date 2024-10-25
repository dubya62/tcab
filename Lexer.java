/**
 * This program will deal with breaking the file into tokens at certain characters
 */

import java.io.File;
import java.util.Scanner;
import java.util.ArrayList;
import java.util.Set;
import java.util.HashSet;
import java.util.Arrays;

public class Lexer{

    public String filename;
    private ArrayList<ArrayList<String>> fileData;
    public ArrayList<Token> tokens;

    /**
     * Supply a filename to start
     * return the broken up tokens
     */
    public Lexer(String filename){
        Main.debug("Starting the Lexer");
        this.filename = filename;

        this.fileData = new ArrayList<>();

        // read the file's data into the data array
        this.fileData = readFile(filename);

        // break into tokens
        this.tokens = breakIntoTokens(this.fileData);

        Main.debug("Lexer is finished! Lexer output:");
        Main.debug(this.toString());
    }

    /**
     * Return the tokens of the file
     */
    public ArrayList<Token> getTokens(){
        return this.tokens;
    }

    /**
     * read the file's lines
     * break at newlines
     */
    private ArrayList<ArrayList<String>> readFile(String filename){
        // open the file
        File file = new File(filename);
        Scanner scanner = null;
        try {
            scanner = new Scanner(file);
        } catch (Exception e) {
            System.out.println("ERROR: Could not open file: " + filename);
            System.exit(1);
        }

        // read the lines of the file (breaking at newlines)
        int i=0;
        while (scanner.hasNextLine()){
            this.fileData.add(new ArrayList<>());

            this.fileData.get(i).add(scanner.nextLine() + "\n");

            i++;
        }

        return this.fileData;
    }

    /**
     * Use a list of breaking characters to convert the file into tokens
     */
    private ArrayList<Token> breakIntoTokens(ArrayList<ArrayList<String>> fileLines){
        // create a hashset with all of the breaking tokens in it
        Set<Character> breakChars = new HashSet<>();
        
        breakChars.addAll(Arrays.asList('\n', '*', '$', '.', '#', ',', '[', ']', '<', '>', '&', '|', '\t', ' ', '^', '(', ')', '@', '%', '/', '=', '+', '-', ';', '\'', '"', '{', '}', ':', '\\'));
        
        ArrayList<Token> result = new ArrayList<>();

        // keeping track of what level of comments we are in 
        int comment = 0;
        int multiLineComments = 0;
        int documentation = 0;

        int opens = 0;

        int quotes = 0;

        // if you are inside quotes, dont break
        for (int i=0; i<fileLines.size(); i++){
            // the entire line is the only String in this Array.
            // iterate through it and break at tokens
            String currentLine = fileLines.get(i).get(0);
            fileLines.set(i, new ArrayList<>());
            String currentToken = "";
            // iterate through the string itself
            for (int j=0; j<currentLine.length(); j++){
                if (breakChars.contains(currentLine.charAt(j))){
                    // this is a break char

                    // if this is a quote, toggle quotes
                    if (currentLine.charAt(j) == '"'){
                        // only start quotes if not in a comment
                        if (quotes == 1 || comment == 0){
                            quotes ^= 1;
                            quotes &= 1;
                        }
                        
                        // this was an end quote
                        if (quotes == 0 && comment == 0){
                            result.get(result.size()-1).token += currentToken + currentLine.charAt(j);
                            currentToken = "";
                            continue;
                        } 
                    } else if (quotes == 1){
                        result.get(result.size()-1).token += currentToken + currentLine.charAt(j);
                        currentToken = "";
                        continue;
                    }

                    if (quotes == 0){
                        // handle whether or not we are in a comment
                        if (currentLine.charAt(j) == '/'){
                            if (j > 0){
                                // close a multiLine comment if needed
                                if (currentLine.charAt(j-1) == '*'){
                                    if (comment == 1 && multiLineComments == 1 && documentation == 0){
                                        comment = 0;
                                        multiLineComments = 0;
                                    }
                                }

                            }

                            if (j < currentLine.length()){
                                // a normal single line comment
                                if (currentLine.charAt(j+1) == '/'){
                                    if (comment == 0){
                                        comment = 1;
                                    }
                                } else if (currentLine.charAt(j+1) == '*'){
                                    // start a multi-line comment
                                    if (comment == 0){
                                        comment = 1;
                                        multiLineComments = 1;
                                    }
                                }
                            } 
                        } else if (currentLine.charAt(j) == '{'){
                            if (result.size() > 0){
                                // this is a doc comment
                                if (result.get(result.size()-1).token.equals("&")){
                                    if (comment == 0){
                                        comment = 1;
                                        multiLineComments = 1;
                                        documentation = 1;
                                        opens = 0;
                                    } 
                                }
                            }
                            opens++;

                        } else if (currentLine.charAt(j) == '}'){
                            if (opens > 0){
                                opens--;
                                if (opens == 0){
                                    if (documentation == 1){
                                        comment = 0;
                                        multiLineComments = 0;
                                        documentation = 0;
                                    }
                                }
                            }
                        }
                    }

                    // do not add empty tokens
                    if (currentToken.length() != 0){
                        // create a new token object
                        result.add(new Token(this.filename, i + 1, currentToken));
                    }

                    // do not add spaces
                    switch (currentLine.charAt(j)){
                        case '\n':
                            if (comment == 1 && multiLineComments == 0){
                                comment = 0;
                            }
                            result.add(new Token(this.filename, i + 1, "\n"));
                            break;
                        case '\t':
                            result.add(new Token(this.filename, i + 1, "\t"));
                            break;
                        default:
                            if (currentLine.charAt(j) != ' '){
                                result.add(new Token(this.filename, i + 1, Character.toString(currentLine.charAt(j))));
                            } 
                            break;
                    }

                    currentToken = "";
                } else {
                    // this is not a break char
                    currentToken += currentLine.charAt(j);
                }
            }
            if (currentToken.length() > 0){
                result.add(new Token(this.filename, i + 1, currentToken));
            }
            
        }

        return result;
    }

    /**
     */
    public String toString(){
        return this.tokens.toString();
    }

}





