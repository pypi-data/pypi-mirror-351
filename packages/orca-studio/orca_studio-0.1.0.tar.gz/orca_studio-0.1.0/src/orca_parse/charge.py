from orca_parse.common import find_keyword_tokens

KEYWORD = "Total Charge           Charge"

def charge(lines: list[str]) -> int:
    tokens = find_keyword_tokens(lines, KEYWORD)
    return int(tokens[-1])
