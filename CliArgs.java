
import java.util.ArrayList;

public class CliArgs{
    public boolean fastmath;
    public boolean verbose;
    public boolean help;
    public String filename;
    public ArrayList<CompilerVariable> compilerVariables;

    public CliArgs(String[] args){
        // -f = fastmath
        // -v = verbose
        // -h = help
        // -d = define variables
        this.fastmath = false;
        this.verbose = false;
        this.help = false;
        this.filename = "";
        this.compilerVariables = new ArrayList<>();

        for (int i=0; i<args.length; i++){
            if (args[i].equals("-f")){
                this.fastmath = true;
            } else if(args[i].equals("-v")){
                this.verbose = true;
            } else if (args[i].equals("-h")){
                this.help = true;
            } else if (args[i].equals("-d")){
                // this is before defining a variable
                // print an error message if there is nothing after this
                if (i+1 == args.length){
                    System.out.println("Expected a variable definition after '-d'...");
                    Main.exit();
                }
                compilerVariables.add(CompilerVariable.parseDefinition(args[i+1]));
                i++;
            } else {
                this.filename = args[i];
            }

        }
        
    }

    public String toString(){
        return this.compilerVariables.toString();
    }

}
