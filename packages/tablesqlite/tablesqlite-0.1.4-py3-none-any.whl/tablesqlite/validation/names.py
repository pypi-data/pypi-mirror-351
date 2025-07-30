

def is_number(name: str) -> bool:
    """
    Check if the given name is a number.
    
    Args:
        name (str): The name to check.
    
    Returns:
        bool: True if the name is a number, False otherwise.
    """
    try:
        float(name)
        return True
    except ValueError:
        return False

keywords = {
        "select", "from", "where", "table", "insert", "update", "delete",
        "create", "drop", "alter", "join", "on", "as", "and", "or", "not",
        "in", "is", "null", "values", "set", "group", "by", "order", "having",
        "limit", "offset", "distinct"
    }

def validate_name(
    name: str, *, 
    validate_chars: bool = True, 
    validate_words: bool = True, 
    validate_len: bool = True,
    allow_dot: bool = True,
    allow_dollar: bool = False,
    max_len: int = 255,
    forgiven_chars = None,
    allow_number: bool = False,
) -> None:
    
    forgiven_chars = forgiven_chars or set()

    if not isinstance(name, str):
        raise TypeError("Name must be a string.")

    if is_number(name) and not allow_number:
        raise ValueError("Name as number not allowed. if you want to use a number, set allow_number=True.")
    elif name[0].isdigit():
        raise ValueError("Name cannot start with a digit.")
    if len(name) == 0:
        raise ValueError("Column name cannot be empty.")

    if validate_len and len(name) > max_len:
        raise ValueError("Column name is too long. Maximum length is 255 characters.")


    
    if validate_chars:
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
        allowed.update(forgiven_chars)
        if allow_dot:
            allowed.add('.')
        if allow_dollar:
            allowed.add('$')
        
        bad_chars = [c for c in name if c not in allowed]
        if bad_chars:
            raise ValueError(f"Column name contains forbidden characters: {bad_chars}")

        if allow_dot:
            # Extra check: make sure dots are only separating valid parts
            parts = name.split('.')
            for part in parts:
                if not part:
                    raise ValueError("Column name has consecutive dots or leading/trailing dot.")
                if part[0].isdigit():
                    raise ValueError(f"Each part of a dotted name must not start with a digit: {part}")

    if validate_words:
        found = next((word for word in keywords if word == name.casefold()), None)
        if found:
            raise ValueError(f"Name contains forbidden words: {found}")
        
def standard_column_validation(
    name: str, *,
    validate_chars: bool = True,
    validate_words: bool = True,
    validate_len: bool = True,
    allow_dot: bool = False,
    allow_dollar: bool = False,
    max_len: int = 255,
    forgiven_chars = None,
    allow_number: bool = False,
) -> None:
    """
    Validate a column name according to various criteria.
    
    Args:
        name (str): The column name to validate.
        validate_chars (bool): Whether to validate characters in the name.
        validate_words (bool): Whether to validate against reserved words.
        validate_len (bool): Whether to validate the length of the name.
        allow_dot (bool): Whether to allow dots in the name.
        allow_dollar (bool): Whether to allow dollar signs in the name.
        max_len (int): The maximum allowed length for the name.
        forgiven_chars (set): A set of additional characters that are allowed.
        allow_number (bool): Whether to allow numbers in the name.
    
    Raises:
        TypeError: If the name is not a string.
        ValueError: If the name does not meet the validation criteria.
    """
    validate_name(
        name, 
        validate_chars=validate_chars, 
        validate_words=validate_words, 
        validate_len=validate_len,
        allow_dot=allow_dot,
        allow_dollar=allow_dollar,
        max_len=max_len,
        forgiven_chars=forgiven_chars,
        allow_number=allow_number
    )

def standard_table_validation(
    name: str, *,
    validate_chars: bool = True,
    validate_words: bool = True,
    validate_len: bool = True,
    allow_dot: bool = False,
    allow_dollar: bool = False,
    max_len: int = 255,
    forgiven_chars = None,
    allow_number: bool = False,
) -> None:
    """
    Validate a table name according to various criteria.
    
    Args:
        name (str): The table name to validate.
        validate_chars (bool): Whether to validate characters in the name.
        validate_words (bool): Whether to validate against reserved words.
        validate_len (bool): Whether to validate the length of the name.
        allow_dot (bool): Whether to allow dots in the name.
        allow_dollar (bool): Whether to allow dollar signs in the name.
        max_len (int): The maximum allowed length for the name.
        forgiven_chars (set): A set of additional characters that are allowed.
        allow_number (bool): Whether to allow numbers in the name.
    
    Raises:
        TypeError: If the name is not a string.
        ValueError: If the name does not meet the validation criteria.
    """
    validate_name(
        name, 
        validate_chars=validate_chars, 
        validate_words=validate_words, 
        validate_len=validate_len,
        allow_dot=allow_dot,
        allow_dollar=allow_dollar,
        max_len=max_len,
        forgiven_chars=forgiven_chars,
        allow_number=allow_number
    )