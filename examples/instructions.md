You are an expert python coder. Return only valid python source code.
Place all train of thought and summaries in triple-quoted string comments.
Also place doctests in all relevant functions and classes.

You will write a class called Calculator that is a simple desk calculator.
Calculations will be done through the __call__(self, expr) method that returns the value
of the (str) expr as a number, either float or int.
You can assign to simple variables (which can consist of at least one underscore or letter ahd
zero or more letters, underscores, or numbers) with '=' and use those simple variables in
later calculations.

both int and float constants are allowed.

The following operators, in order of precedence (highest to lowest) are available:
* unary minus (-)
* exponentiation (**)
* integer division (//), modulo (%), division(/), or multiplication (*)
* addition (+), subtraction (-)
* comparisons (<, <=,>, >=)
* equality comparisons (==, !=)
* unary logical not (!)
* logical and (&&)
* logical or (||)

The comparison and logical operators will return a value of 0 when false and 1 when true.

The __call__() method should raise SyntaxError when there is a syntax error.
The __call__() method should raise ZeroDivisionError when division by zero is attempted.
