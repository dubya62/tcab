public class CompilerVariable{
    String name;
    String type;
    String value;

    public CompilerVariable(String name, String value){
        this.name = name;
        this.value = value;

        this.type = inferType(this.value);

    }

    public static CompilerVariable parseDefinition(String definition){
        // should be name, =, value
        int i;
        for (i=0; i<definition.length(); i++){
            if (definition.charAt(i) == '='){
                break;
            }
        }
        // throw an error if there was no equal sign
        if (i >= definition.length()-1){
            System.out.println("Compiler definitions must contain '='...");
            Main.exit();
        }

        String variableName = definition.substring(0, i);
        String variableValue = definition.substring(i+1);

        return new CompilerVariable(variableName, variableValue);
    }


    public static String inferType(String value){
        // type will be float, int, bool, String, or void

        // if it is true or false, boolean
        if (value.equals("true") || value.equals("false")){
            return "bool";
        }

        // if it has " or ' at the end and beginning, it is a string
        if (value.length() > 0 && (value.charAt(0) == '"' || value.charAt(0) == '\'') && (value.charAt(value.length()-1) == '"' || value.charAt(value.length()-1) == '\'')){
            return "String";
        }

        // if it is a single integer, it is an int
        try{
            Integer.parseInt(value);
            return "int";
        } catch (Exception e){
        }

        // if it has a . that separates two integers, it is a float
        try{
            Float.parseFloat(value);
            return "float";
        } catch (Exception e){
        }

        System.out.println("The type of '" + value + "' could not be inferred...");
        Main.exit();
        return "void";
    }

    public String toString(){
        return this.name + ":" + this.type + "=" + this.value;
    }

}
