"""String utilities module providing common string manipulation functions."""


def reverse_string(s: str) -> str:
    """Return the reverse of the given string.

    Args:
        s: The input string to reverse.

    Returns:
        A new string with characters in reverse order.

    Examples:
        >>> reverse_string("hello")
        'olleh'
        >>> reverse_string("Python")
        'nohtyP'
        >>> reverse_string("")
        ''
    """
    return s[::-1]


def capitalize_words(s: str) -> str:
    """Return the string with the first letter of each word capitalised.

    Words are delimited by whitespace. This is equivalent to Python's
    built-in ``str.title()`` but applied uniformly to every word.

    Args:
        s: The input string.

    Returns:
        A new string where every word starts with an uppercase letter and
        the remaining characters are lowercased.

    Examples:
        >>> capitalize_words("hello world")
        'Hello World'
        >>> capitalize_words("the quick brown fox")
        'The Quick Brown Fox'
        >>> capitalize_words("")
        ''
    """
    return s.title()


def count_vowels(s: str) -> int:
    """Return the number of vowel characters in the given string.

    Both uppercase and lowercase vowels (a, e, i, o, u) are counted.

    Args:
        s: The input string.

    Returns:
        An integer representing the total count of vowels found in *s*.

    Examples:
        >>> count_vowels("hello")
        2
        >>> count_vowels("Python")
        1
        >>> count_vowels("rhythm")
        0
        >>> count_vowels("")
        0
    """
    return sum(1 for ch in s if ch.lower() in "aeiou")


def is_palindrome(s: str) -> bool:
    """Return True if the string reads the same forwards and backwards.

    The check is case-insensitive and ignores non-alphanumeric characters,
    so phrases like ``"A man a plan a canal Panama"`` are considered
    palindromes.

    Args:
        s: The input string to test.

    Returns:
        ``True`` if *s* is a palindrome, ``False`` otherwise.

    Examples:
        >>> is_palindrome("racecar")
        True
        >>> is_palindrome("hello")
        False
        >>> is_palindrome("A man a plan a canal Panama")
        True
        >>> is_palindrome("")
        True
    """
    cleaned = "".join(ch.lower() for ch in s if ch.isalnum())
    return cleaned == cleaned[::-1]
