/** 
 * This file deals with importing files and preprocessing them
 *
 */

import java.util.ArrayList;
import java.util.Set;
import java.util.HashSet;

public class ImportHandler{
    public ArrayList<Token> tokens;

    public ImportHandler(CliArgs cliArgs){
        if (cliArgs.filename.equals("")){
            System.out.println("Please supply a filename to compile...");
            Main.exit();
        }

        Main.debug("Starting the Import Handler...");

        Set<String> alreadyImported = new HashSet<>();


        this.tokens = handleFile(cliArgs, cliArgs.filename, alreadyImported);


        // recursively handle imports


        Main.debug("Import Handler finished!");
        Main.debug("Import Handler output:");
        Main.debug(this.tokens.toString());

    }

    /**
     * Handle a single file's imports
     */
    private ArrayList<Token> handleFile(CliArgs cliArgs, String filename, Set alreadyImported){
        if (alreadyImported.contains(filename)){
            Main.debug("File " + filename + " has already been imported. Ignoring...");
            return new ArrayList<Token>();
        }
        alreadyImported.add(filename);
        Main.debug("Preprocessing file " + filename + "...");
        ArrayList<Token> result = Main.preprocessFile(cliArgs, cliArgs.filename);

        // look for import statements in this file
        ArrayList<ImportStatement> importStatements = gatherImportStatements(result);


        Main.debug("Finished preprocessing file " + filename + "...");
        return result;
    }

    /**
     * Generate list of all import statements
     */
    private ArrayList<ImportStatement> gatherImportStatements(ArrayList<Token> fileTokens){
        ArrayList<ImportStatement> result = new ArrayList<>();

        // get the tokens of the statement and instantiate an ImportStatement with them
        for (int i=0; i<fileTokens.size(); i++){
            if (fileTokens.get(i).equals("import")){
                Main.debug("Found an import statement.");
                ArrayList<Token> statementTokens = new ArrayList<>();

                while (!fileTokens.get(i).equals(";")){
                    statementTokens.add(fileTokens.get(i));
                    i++;
                }

                ImportStatement theStatement = new ImportStatement(statementTokens);

            }
        }

        return result;
    }

}

