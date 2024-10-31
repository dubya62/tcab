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
        Main.debug("Imported files:");
        Main.debug(alreadyImported.toString());
        if (alreadyImported.contains(filename)){
            Main.debug("File " + filename + " has already been imported. Ignoring...");
            return new ArrayList<Token>();
        }
        if (filename.length() < 2 || !filename.substring(0,2).equals("./")){
            filename = "./" + filename;
        }
        alreadyImported.add(filename);
        Main.debug("Preprocessing file " + filename + "...");
        ArrayList<Token> result = Main.preprocessFile(cliArgs, filename);

        // look for import statements in this file
        ArrayList<ImportStatement> importStatements = gatherImportStatements(result, filename);

        // remove the import statements from the file
        result = removeImportStatements(result);

        // handle each file in the import statements
        ArrayList<Token> finalResult = new ArrayList<>();
        for (int i=0; i < importStatements.size(); i++){
            // put this into a class that corresponds to the filename
            ArrayList<Token> currentFile = handleFile(cliArgs, importStatements.get(i).filename, alreadyImported);
            String[] splittedFilename = importStatements.get(i).filename.split("/", 0);
            // remove .tcab from the end if needed
            if (splittedFilename.length > 0){
                String lastPart = splittedFilename[splittedFilename.length-1];
                if(lastPart.length() > 4){
                    if (lastPart.substring(lastPart.length()-5).equals(".tcab")){
                        splittedFilename[splittedFilename.length-1] = lastPart.substring(0, lastPart.length()-5);
                    }
                }
            }
            if (currentFile.size() > 0){
                for (int j=1; j<splittedFilename.length; j++){
                    finalResult.add(new Token(importStatements.get(i).filename, 0, "protected"));
                    finalResult.add(new Token(importStatements.get(i).filename, 0, "class"));
                    finalResult.add(new Token(importStatements.get(i).filename, 0, splittedFilename[j]));
                    finalResult.add(new Token(importStatements.get(i).filename, 0, "{"));
                    finalResult.add(new Token(importStatements.get(i).filename, 0, ";"));
                }
                finalResult.addAll(currentFile);
                for (int j=1; j<splittedFilename.length; j++){
                    finalResult.add(new Token(importStatements.get(i).filename, 0, "}"));
                    finalResult.add(new Token(importStatements.get(i).filename, 0, ";"));
                }
            }
        }
        finalResult.addAll(result);

        Main.debug("Finished preprocessing file " + filename + "...");
        return finalResult;
    }

    /**
     * Generate list of all import statements
     */
    private ArrayList<ImportStatement> gatherImportStatements(ArrayList<Token> fileTokens, String filename){
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

                ImportStatement theStatement = new ImportStatement(statementTokens, filename);

                result.add(theStatement);
            }
        }

        return result;
    }

    /**
     * Remove the import statements from the file
     */
    private ArrayList<Token> removeImportStatements(ArrayList<Token> fileTokens){
        ArrayList<Token> result = new ArrayList<>();

        boolean added = false;
        for (int i=0; i < fileTokens.size(); i++){
            if (fileTokens.get(i).token.equals("import")){
                while (i < fileTokens.size() && !fileTokens.get(i).equals(";")){
                    i++;
                }
                added = true;
            }
            if (!added){
                result.add(fileTokens.get(i));
            } else {
                added = false;
            }
        }

        return result;
    }

}

