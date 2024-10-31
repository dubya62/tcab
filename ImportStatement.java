
import java.util.ArrayList;

public class ImportStatement{
    public ArrayList<Token> tokens;
    public String filename;

    public ImportStatement(ArrayList<Token> tokens, String filename){
        this.tokens = tokens;
        this.filename = parseFilename(this.tokens, filename);
    }

    private static String parseFilename(ArrayList<Token> importStatementTokens, String filepath){
        if (importStatementTokens.size() < 2){
            Error theError = new Error("SYNTAX", "Expected a file after 'import'...","Reference a file directly after 'import'.");
            theError.setErrorToken(importStatementTokens.get(0));
            Main.addError(theError);
            Main.exit();
        }

        // split the filename at slashes and keep everything before the last element
        String[] splitted = filepath.split("/", 0);
        int splittedElements = splitted.length-1;

        String result = "";
        
        // for each dot at the start, add ../

        boolean stillGoingBack = true;

        for (int i=1; i<importStatementTokens.size(); i++){
            if (importStatementTokens.get(i).token.equals(".")){
                if (stillGoingBack){
                    if (splittedElements > 1){
                        splittedElements--;
                    } else {
                        result += "../";
                    }
                } else {
                    result += "/";
                }
            } else {
                stillGoingBack = false;
                result += importStatementTokens.get(i).token;
            }
            System.out.println(result.toString());
        }
        String finalResult = "";
        for (int i=0; i<splittedElements; i++){
            finalResult += splitted[i] + "/";
        }
        finalResult += result;

        finalResult += ".tcab";

        Main.debug("Import file path " + finalResult);

        return finalResult;
    }
}
