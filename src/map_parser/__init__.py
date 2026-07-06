from .classes import Map, Zone, Connection
from .errors import LexingError, ParsingError, ValidationError
from .lexer import Lexer
from .parser import Parser
from .validator import Validator


def load_map(file_path: str) -> Map:
    try:
        with open(file_path, "r") as f:
            file_lines = f.readlines()
    except FileNotFoundError:
        raise ValueError(f"File Not Found - '{file_path}'")
    except NotADirectoryError:
        raise ValueError(f"Not A Directory - '{file_path}'")
    except IsADirectoryError:
        raise ValueError(f"Is A Directory - '{file_path}'")
    except PermissionError:
        raise ValueError(f"Permission Error - '{file_path}'")
    except OSError:
        raise ValueError(f"Can't Read File - '{file_path}'")

    tokens = Lexer(file_lines, file_path).evaluate()
    nb_drones, zones, connections = Parser(tokens).parse()
    return Validator(nb_drones, zones, connections).validate()


__all__ = [
    "Map",
    "Zone",
    "Connection",
    "LexingError",
    "ParsingError",
    "ValidationError",
    "load_map",
]
