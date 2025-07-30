from fastmcp import FastMCP

mcp = FastMCP("SimpleCalculator")

@mcp.tool()
def add(a: int, b: int) -> int:
    """
    Add two numbers

    Args:
        a: The first number
        b: The second number

    Returns:
        The sum of the two numbers
    """
    return a + b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """
    Subtract two numbers

    Args:
        a: The first number
        b: The second number

    Returns:
        The difference of the two numbers
    """
    return a - b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """
    Multiply two numbers

    Args:
        a: The first number
        b: The second number

    Returns:
        The product of the two numbers
    """
    return a * b

@mcp.tool()
def divide(a: int, b: int) -> float:
    """
    Divide two numbers

    Args:
        a: The first number
        b: The second number

    Returns:
        The quotient of the two numbers
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

if __name__ == "__main__":
    mcp.run()
