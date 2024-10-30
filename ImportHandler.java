/** 
 * This file deals with importing files and preprocessing them
 *
 */

import java.util.ArrayList;
import java.util.Set;

public class ImportHandler{
    public ArrayList<Token> tokens;

    public ImportHandler(CliArgs cliArgs){
        if (cliArgs.filename.equals("")){
            System.out.println("Please supply a filename to compile...");
            Main.exit();
        }
        this.tokens = Main.preprocessFile(cliArgs, cliArgs.filename);

        Main.debug("Starting the Import Handler on file " + cliArgs.filename + " ...");

        // recursively handle imports

        Main.debug("Import Handler has finished!");

    }
}
