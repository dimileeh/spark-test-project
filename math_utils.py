"""Math utilities module providing basic arithmetic operations."""


def add(a: float, b: float) -> float:
    """Return the sum of two numbers.

    Args:
        a: The first operand.
        b: The second operand.

    Returns:
        The result of a + b.

    Examples:
        >>> add(2, 3)
        5
        >>> add(-1, 1)
        0
    """
    return a + b


def subtract(a: float, b: float) -> float:
    """Return the difference of two numbers.

    Args:
        a: The minuend.
        b: The subtrahend.

    Returns:
        The result of a - b.

    Examples:
        >>> subtract(10, 4)
        6
        >>> subtract(0, 5)
        -5
    """
    return a - b


def multiply(a: float, b: float) -> float:
    """Return the product of two numbers.

    Args:
        a: The first factor.
        b: The second factor.

    Returns:
        The result of a * b.

    Examples:
        >>> multiply(3, 4)
        12
        >>> multiply(-2, 5)
        -10
    """
    return a * b


def divide(a: float, b: float) -> float:
    """Return the quotient of two numbers.

    Args:
        a: The dividend.
        b: The divisor.

    Returns:
        The result of a / b.

    Raises:
        ValueError: If b is zero (division by zero is not allowed).

    Examples:
        >>> divide(10, 2)
        5.0
        >>> divide(7, 2)
        3.5
    """
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b


if __name__ == "__main__":
    print("Math Utilities — Quick Test")
    print("=" * 35)

    a, b = 10, 3

    print(f"add({a}, {b})       = {add(a, b)}")
    print(f"subtract({a}, {b})  = {subtract(a, b)}")
    print(f"multiply({a}, {b})  = {multiply(a, b)}")
    print(f"divide({a}, {b})    = {divide(a, b):.4f}")

    print()
    print("Division by zero handling:")
    try:
        divide(5, 0)
    except ValueError as e:
        print(f"  divide(5, 0) → ValueError: {e}")
