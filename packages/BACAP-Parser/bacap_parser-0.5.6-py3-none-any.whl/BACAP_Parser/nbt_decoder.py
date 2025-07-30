import re

from .ExtendedDict import ExtendedDict
from .utils import cut_namespace


def is_decimal(num):
    pattern = re.compile(r"^-?\d+$")
    return re.search(pattern, num)


def nbt_decoder(input_str: str):
    """
    Translate nbt to python types.
    :param input_str: nbt.
    :return: Some python type (depends on input).
    """
    signature = {"'": "'", "\"": "\"", "{": "}", "[": "]"}

    def strip_key(key: str) -> str:
        return key.strip("'").strip("\"")

    def remove_escaping_in_string(string: str):
        return "\\".join((x.replace("\\", "") for x in string.split(r"\\")))

    def convert_type(value: str) -> dict | list | bool | int | float | str:
        if len(value) == 0:
            return ""
        if value.startswith("[") and value.endswith("]"):
            return parse_list(value)
        elif value.startswith("{") and value.endswith("}"):
            return parse_nbt(value)
        elif (value.startswith("'") and value.endswith("'")) or (value.startswith("\"") and value.endswith("\"")):
            value = value[1:-1]
            try:
                if value.startswith("{") and value.endswith("}"):
                    return parse_nbt(remove_escaping_in_string(value))
                elif value.startswith("[") and value.endswith("]"):
                    return parse_list(remove_escaping_in_string(value))
            except ValueError:
                pass
            return remove_escaping_in_string(value)
        elif value.endswith("b"):
            return bool(int(value[:-1]))
        elif value.lower() in {"false", "true"}:
            return value == "true"
        elif value[-1] in {"f", "d"}:
            return float(value[:-1])
        elif value[-1] == "s":
            return int(value[:-1])
        elif is_decimal(value):
            return int(value)
        else:
            raise ValueError(f"Undefined type: {value}")

    def parse_nbt(input_nbt):
        input_nbt = input_nbt[1:-1]
        result = ExtendedDict()
        current_key = ''
        current_value = ''
        in_key = True
        in_value = False
        brace_counter = 0
        current_quote = None
        is_escaping = False
        i = 0
        while i < len(input_nbt):
            char = input_nbt[i]
            if in_key:
                if char in signature.keys() and current_quote is None:
                    current_quote = char
                    brace_counter += 1
                    current_key += char
                elif char == signature.get(current_quote):
                    brace_counter -= 1
                    current_key += char
                    if brace_counter == 0:
                        current_quote = None
                elif char == ':' and current_quote is None:
                    current_key = cut_namespace(current_key)
                    in_key = False
                    in_value = True
                elif current_quote:
                    current_key += char
                elif char not in [",", " "]:
                    current_key += char
            elif in_value:
                if is_escaping:
                    current_value += char
                    is_escaping = False
                elif char == "\\":
                    current_value += char
                    is_escaping = True
                elif current_quote is None:
                    if char == " ":
                        pass
                    elif char == ",":
                        current_key = strip_key(current_key)
                        result[current_key] = convert_type(current_value)
                        current_key = ''
                        current_value = ''
                        in_key = True
                        in_value = False
                        current_quote = None
                    elif char in signature.keys():
                        current_quote = char
                        current_value += char
                        brace_counter += 1
                    else:
                        current_value += char
                elif char == signature[current_quote]:
                    current_value += char
                    brace_counter -= 1
                    if brace_counter == 0:
                        current_key = strip_key(current_key)
                        result[current_key] = convert_type(current_value)
                        current_key = ''
                        current_value = ''
                        in_key = True
                        in_value = False
                        current_quote = None
                elif char == current_quote:
                    current_value += char
                    brace_counter += 1
                else:
                    current_value += char
            i += 1
        if current_key:
            current_key = strip_key(current_key)
            result[current_key] = convert_type(current_value)
        return result

    def parse_list(value: str) -> list:
        value = value[1:-1]
        if not value:
            return []
        if value[1] == ";":
            value = value.partition(";")[2]
        result = []
        current_value = ''
        brace_counter = 0
        current_quote = None
        is_escaping = False
        i = 0
        while i < len(value):
            char = value[i]
            if is_escaping:
                current_value += char
                is_escaping = False
            elif char == "\\":
                current_value += char
                is_escaping = True
            elif current_quote is None:
                if char in signature.keys():
                    current_quote = char
                    brace_counter += 1
                    current_value += char
                elif char == "," and brace_counter == 0:
                    result.append(convert_type(current_value))
                    current_value = ''
                elif char not in [" ", ","]:
                    current_value += char
            elif char == signature[current_quote]:
                current_value += char
                brace_counter -= 1
                if brace_counter == 0:
                    current_quote = None
            elif char == current_quote:
                current_value += char
                brace_counter += 1
            else:
                current_value += char
            i += 1
        if current_value:
            result.append(convert_type(current_value))
        return result

    return convert_type(input_str)