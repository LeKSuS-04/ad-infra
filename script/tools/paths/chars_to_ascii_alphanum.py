from string import ascii_letters, digits

_MAPPING = {
    "$": "S",
    "-": "_",
    "@": "a",
    "_": "",
    " ": "_",
    "а": "a",  # noqa: RUF001
    "б": "b",  # noqa: RUF001
    "в": "v",
    "г": "g",  # noqa: RUF001
    "д": "d",
    "е": "e",  # noqa: RUF001
    "ё": "yo",
    "ж": "j",
    "з": "z",
    "и": "i",
    "й": "j",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",  # noqa: RUF001
    "п": "p",
    "р": "r",  # noqa: RUF001
    "с": "s",  # noqa: RUF001
    "т": "t",
    "у": "u",  # noqa: RUF001
    "ф": "f",
    "x": "h",
    "ц": "c",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ъ": "y",
    "ы": "y",
    "ь": "Y",
    "э": "e",
    "ю": "yu",
    "я": "ya",
    "А": "A",  # noqa: RUF001
    "Б": "B",
    "В": "V",  # noqa: RUF001
    "Г": "G",
    "Д": "D",
    "Е": "E",  # noqa: RUF001
    "Ё": "Yo",
    "Ж": "J",
    "З": "Z",  # noqa: RUF001
    "И": "I",
    "Й": "J",
    "К": "K",  # noqa: RUF001
    "Л": "L",
    "М": "M",  # noqa: RUF001
    "Н": "N",  # noqa: RUF001
    "О": "O",  # noqa: RUF001
    "П": "P",
    "Р": "R",  # noqa: RUF001
    "С": "S",  # noqa: RUF001
    "Т": "T",  # noqa: RUF001
    "У": "U",  # noqa: RUF001
    "Ф": "F",
    "Х": "H",  # noqa: RUF001
    "Ц": "C",
    "Ч": "Ch",
    "Ш": "Sh",
    "Щ": "Shch",
    "Ъ": "Y",
    "Ы": "Y",
    "Ь": "Y",  # noqa: RUF001
    "Э": "E",
    "Ю": "Yu",
    "Я": "Ya",
}


def normalize_char(char: str) -> str:
    if char in ascii_letters + digits:
        return char
    if char in _MAPPING.keys():
        return _MAPPING[char]
    return "."
