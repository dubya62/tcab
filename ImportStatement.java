
import java.util.ArrayList;

public class ImportStatement{
    public ArrayList<Token> tokens;
    public String filename;

    public ImportStatement(ArrayList<Token> tokens){
        this.tokens = tokens;
        this.filename = parseFilename(this.tokens);
    }

    private static String parseFilename(ArrayList<Token> importStatementTokens){
        return "hello";
    }
}
