import re
from .exceptions import ValidationError

def _get_password_errors(password: str,
                         min_length: int = 8,
                         max_length: int = 50,
                         require_upper: bool = True,
                         require_lower: bool = True,
                         require_digit: bool = True,
                         require_special: bool = True) -> list[str]:
    errors = []

    if not isinstance(password, str):
        errors.append("Password must be a string.")
        return errors

    if ' ' in password:
        errors.append("Password should not contain spaces.")
    if len(password) < min_length:
        errors.append(f"Must be at least {min_length} characters.")
    if len(password) > max_length:
        errors.append(f"Must be at most {max_length} characters.")
    if require_upper and not re.search(r'[A-Z]', password):
        errors.append("Must include at least one uppercase letter.")
    if require_lower and not re.search(r'[a-z]', password):
        errors.append("Must include at least one lowercase letter.")
    if require_digit and not re.search(r'\d', password):
        errors.append("Must include at least one digit.")
    if require_special and not re.search(r'[\W_]', password):
        errors.append("Must include at least one special character.")

    return errors

def is_valid_password(password: str,
                      min_length: int = 8,
                      max_length: int = 50,
                      require_upper: bool = True,
                      require_lower: bool = True,
                      require_digit: bool = True,
                      require_special: bool = True) -> bool:
    return not _get_password_errors(
        password,
        min_length,
        max_length,
        require_upper,
        require_lower,
        require_digit,
        require_special
    )

def validate_password(password: str,
                      min_length: int = 8,
                      max_length: int = 50,
                      require_upper: bool = True,
                      require_lower: bool = True,
                      require_digit: bool = True,
                      require_special: bool = True) -> None:
    errors = _get_password_errors(
        password,
        min_length,
        max_length,
        require_upper,
        require_lower,
        require_digit,
        require_special
    )

    if errors:
        formatted_message = "\n- " + "\n- ".join(errors)
        raise ValidationError(
            f"Password validation failed due to the following reasons:{formatted_message}"
        )
