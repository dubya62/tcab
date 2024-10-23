/**
 * The purpose of this file is to keep track of a single token
 * it will handle the file name and line number for syntax error handling
 */

public class Token{
    public String filename;
    public int lineNumber;
    public String token;

    public Token(String filename, int lineNumber, String token){
        this.filename = filename;
        this.lineNumber = lineNumber;
        this.token = token;
    }

    public boolean equals(String other){
        return this.token.equals(other);
    }

    public boolean equals(Token other){
        return this.token.equals(other.token);
    }

    public String toString(){
        return this.token;
    }

}
