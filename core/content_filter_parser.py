import re
from models.content_model import Content


def is_valid_filter(filter_str):
    """Returns True if the filter string is non-empty and can be parsed without error."""
    if not filter_str or not filter_str.strip():
        return False
    try:
        ContentFilterParser(filter_str)
        return True
    except Exception:
        return False


class ContentFilterParser:
    def __init__(self, filter_text: str):
        self.filter_text = filter_text.strip()

    def match(self, content: Content) -> bool:
        if not self.filter_text:
            return True

        expr = self._parse_expression(self.filter_text)
        return expr(content)

    def _parse_expression(self, text: str):
        # Tokenisierung
        tokens = re.findall(r'\w+\s*=\s*"[^"]*"|AND|OR|NOT', text)

        def parse_token(token: str):
            if "=" in token:
                key, val = token.split("=")
                key = key.strip()
                val = val.strip().strip('"')
                return lambda c: str(c.metadata.get(key, "")).strip() == val
            elif token == "NOT":
                return "NOT"
            elif token == "AND":
                return "AND"
            elif token == "OR":
                return "OR"
            return None

        # Einfacher Evaluierungsstack (ohne Klammern)
        stack = []
        for tok in tokens:
            op = parse_token(tok)
            if callable(op):
                stack.append(op)
            elif op == "NOT":
                prev = stack.pop()
                stack.append(lambda c, p=prev: not p(c))
            elif op == "AND":
                right = stack.pop()
                left = stack.pop()
                stack.append(lambda c, left_func=left,
                             r=right: left_func(c) and r(c))
            elif op == "OR":
                right = stack.pop()
                left = stack.pop()
                stack.append(lambda c, left_func=left,
                             r=right: left_func(c) or r(c))

        return stack[-1] if stack else lambda c: True
