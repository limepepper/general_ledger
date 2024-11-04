from colorama import Fore, Style

from rich import inspect

import hashlib
from rich.style import Style as RichStyle
import functools
from loguru import logger


# logger = logger.opt(colors=True)

def logger_wraps(*, entry=True, exit=True, level="DEBUG"):
    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(
                    level, "Entering '{}' (args={}, kwargs={})", name, args, kwargs
                )
            result = func(*args, **kwargs)
            if exit:
                logger_.log(level, "Exiting '{}' (result={})", name, result)
            return result

        return wrapped

    return wrapper


def logger_init(*, entry=True, exit=True, level="DEBUG"):
    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(
                    level,
                    "Entering '{}' (args={}, kwargs={})",
                    name,
                    args,
                    kwargs,
                )
            result = func(*args, **kwargs)
            if exit:
                logger_.log(level, "Exiting '{}' (result={})", name, result)
            return result

        return wrapped

    return wrapper


def is_iterable(obj):
    """Check if an object is iterable. except strings"""
    if isinstance(obj, str):
        return False
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def bool_colorize(match):
    content = match.group(1)
    if str_to_bool(content):
        return f"{Fore.GREEN}{content}{Style.RESET_ALL}"  # Green for True
    elif content == "False":
        return f"{Fore.RED}{content}{Style.RESET_ALL}"  # Red for False
    return content  # Just in case there's something unexpected


def b(content):
    """Decorator to colorize boolean values in the output."""
    if str_to_bool(content):
        return f"{Fore.GREEN}{content} {Style.RESET_ALL}"  # Green for True
    elif not str_to_bool(content):
        return f"{Fore.RED}{content}{Style.RESET_ALL}"
    raise ValueError(f"Cannot interpret '{content}' as a boolean")


def str_to_bool(value):
    """Converts a string to its truthy or falsy boolean equivalent."""
    if value is True or value is False:
        return value
    truthy_values = {"true", "1", "yes", "y", "on"}
    falsy_values = {"false", "0", "no", "n", "off"}

    value_lower = value.strip().lower()  # Normalize the input

    if value_lower in truthy_values:
        return True
    elif value_lower in falsy_values:
        return False
    else:
        raise ValueError(f"Cannot interpret '{value}' as a boolean")


max_transition_len = 18


def log_change(
    logger,
    transition,
    accumulated,
    node,
    context,
):
    global max_transition_len
    max_transition_len = min(max(max_transition_len, len(transition)), 18)
    logger.trace(
        "{:<{max_transition_len}.{max_transition_len}}: <g>{:14.14}</g> [<y>{:>6}:{:>6}</y>] {} {} {} {} sub:{}",
        node.label,
        transition,
        node.value,
        accumulated,
        b(node.is_leaf),
        b(node.is_visible),
        context.current_level,
        "{:<4}".format(node.meta.operation.name),
        context.get_current_total(),
        max_transition_len=max_transition_len,
    )


max_message_len = 18


def visit_logger(
    logger,
    message,
    node,
    current_level,
    logger_level="INFO",
):
    global max_message_len
    logger_ = logger.opt(depth=1, colors=True)
    max_message_len = min(max(max_message_len, len(message)), 18)
    logger_.log(
        logger_level,
        "<g>{:18.18}</g> [<y>{:>6}</y>] {} {} {} {message!r}",
        node.label,
        node.value,
        b(node.is_leaf),
        current_level,
        "{:<4}".format(node.meta.operation.name),
        message=message,
        max_message_len=max_message_len,
    )


def string_to_color(input_string: str) -> RichStyle:
    # Create a hash of the input string
    hash_object = hashlib.md5(input_string.encode())
    hash_hex = hash_object.hexdigest()

    # Use the first 6 characters of the hash to create a color
    r = int(hash_hex[:2], 16) % 64 + 192  # Ensure the value is in the range 192-255
    g = int(hash_hex[2:4], 16) % 64 + 192
    b = int(hash_hex[4:6], 16) % 64 + 192
    color_code = f"#{r:02x}{g:02x}{b:02x}"

    # Create a rich Style with the generated color
    style = RichStyle(bgcolor=color_code)
    return style


def slugu(text, sep="_"):
    """
    Convert a string to a slug.
    """
    chars_to_replace = [" ", ".", ",", "-"]
    for char in chars_to_replace:
        text = text.replace(char, sep)
    return text.lower()


def raiseu():
    raise ValueError("This error thrown by raiseu() function")
