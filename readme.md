# Programming language

## Idea
-   This will be a high level, object oriented programming language
-   It will be compiled and optimized to the corresponding C code

## syntax
-   semicolons are optional
-   strings are mutable
-   primitves are passed by copy, objects passed by reference. Use .copy() on an object to pass it by copy (may be compiled out anyway)
-   Main class is required
-   every class inherits from a base object
-   allow overloading based on argument types
-   allow keyword arguments
-   if, while, and for-each do not require parenthesis
-   "garbage collection" handled at compile time
-   allow compile time multithreading, simt, and gpu setup
-   allow list (dynamic array) and array as built-in types
-   Compiler will complain if you change the size of a non-dynamic type
-   allow inline assembly
-   allow different possible arguments with |
-   allow use statements to shorten names
-   use $ to denote a test (should return true or false as to whether or not the test passed)
-   use @ to denote documentation should contain documentation for the function/class
-   allow multiple inheritance
-   use # to denote a compiler directive (will be important for writing low level)


## reserved words
-   int
-   bool
-   float
-   short
-   long
-   double
-   char
-   void
-   class
-   public
-   private
-   protected
-   extends
-   return
-   if
-   for
-   while
-   import
-   as
-   use
-   switch
-   case
-   else
-   new
-   asm
-   static
-   default


## Some ideas
-   Multiplying an array/list by an integer uses python's method of return that many multiples of the list concatenated
```
// list/array declaration
*[*] test1 = [4, 5, 6, 2.33];
*[*] test2 = [4] * 10; // a dynamic array of 10 4's
```
-   Allow overloading the access operator in classes
```
* example = new Example();
System.out.println(example[0]);
```
-   The generate C code should compile conditionally for linux, max, windows, web, ios, and android (as well as different architectures)
-   Allow the use of the compiler directive # for certain tasks
    - conditional compilation
    - telling the compiler that a function produces external output (e.g. println, socket.write(), socket.read(), pipe.read(), pipe.write())

## Compiler Options
-   fastmath - allow float and double operations to be commutative

## more ideas
-   allow defining a class inside a class

## Compiler directives
-   conditional compilation 
    - platform
    - whether or not a certain variable was passed to the compiler in the cli args
    - compiler directive functions
        - type() = returns the type of a variable as a String
        - 
-   constrain
    - the acceptable values/types for a variable
-   A method where a library writer can put responsibility on the user to perform error checking
-   whether or not a function provides human output
-   the cost of a specific function
```
#if [condition]
#elif [condition]
#else
#endif

#constrain [condition] : <Reason for constraint> : <Suggestions>

#output 

#cycles <number of cycles>

#print <Message>

type() = return type of given variable as a String

PLATFORM 
ARCHITECTURE

```


## Pattern matching
-   Allow for more advanced pattern matching than a simple switch-case statement
    - probably use ML as a model
```
// any function can be a pattern matching function
public int test(String arg1){
    case (""){}
    case ("Hello"){
        return -1;
    }
    case ("World"){
        return 0;
    }
    case (_){
        return 1;
    }
}


// a normal switch case statment
** result = int (String var1, int var2) {
    case ("test", _){
        return 1;
    }
    case ("hello", _){} // falls through
    case (_, -1){
        return 10;
    }
    case (_, _){
        return 0;
    }
}("test", 10);

result = 1;



```

## More Ideas
-   case pattern matching (like ml)
    - cons
    - instance variables of classes (like prolog)
    - elements of tuples
    - exclusive matching
    - arguments to the function itself are optional, but can be used within the statments if needed
-   f strings
-   default argument values
-   built-in regex class that is equal to strings that match it (and vice versa)
-   ability to create functions for a different class (only for the current scope) (implement/reimplement)
-   list/array slicing
-   threaded keyword to make all calls to this function create a new thread
-   ability to serialize/deserialize objects
-   ... as final arg for any number of extra args










