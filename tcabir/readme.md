# TCABIR
-   Tcab internal representation

# Purpose
-   The purpose of this internal representation is to provide:
    - heavy optimization
    - parallelism
    - platform independence

# Syntax
-   All variables are global
-   All variables are in the form #{varnum}
-   Only one mathematical/comparison operation is allowed per line
-   All array accesses are converted to variables
-   #3[2] = #{3+2} or #5
-   each variable is 1 byte, but will later be converted to 4 byte int
-   literals are allowed, but only numbers in the range `[0, 255]` inclusive
-   low level (platform independent system) calls are allowed (all arguments must be variables)
-   while loops are allowed
-   each variable should have a type and remaining size attached
```
#1 = 223
#2 = 12
#3 = 0
#4 = 1
#5 = 2
write(#4, #1, #5)
#6 = #2 - #4
#7 = #6 / #1




```
