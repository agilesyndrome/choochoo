
from re import compile

'''
A parser generator takes a string as input and returns a generator that yields successive parses.
A parse is a (result, string) tuple where result is always a list and string is the remaining string (possibly empty).
'''


def literal(target):
    def _parser(string):
        if string.startswith(target):
            yield [target], string[len(target):]
    return _parser


def transform(parser, transform=lambda l: l):
    def _parser(string):
        for result, rest in parser(string):
            try:
                yield transform(result), rest
            except:  # allow filtering of inconsistent results (eg parse int)
                pass
    return _parser


def drop(parser):
    return transform(parser, lambda l: [])


# breadth first (depth first is inefficient)
def sequence(*parsers):
    def _recurse(parsers, results, string):
        if parsers:
            parser, parsers = parsers[0], parsers[1:]
            for result, rest in parser(string):
                yield from _recurse(parsers, results + result, rest)
        else:
            yield results, string
    def _parser(string):
        yield from _recurse(parsers, [], string)
    return _parser


def choice(*parsers):
    def _parser(string):
        for parser in parsers:
            yield from parser(string)
    return _parser


# only returns matching groups
def pattern(regexp):
    r = compile(regexp)
    def _parser(string):
        m = r.match(string)
        if m:
            yield list(m.groups()), string[m.end():]
    return _parser


class Recursive:

    def __init__(self):
        self._parser = None

    def __call__(self, *args, **kwargs):
        yield from self._parser(*args, **kwargs)

    def calls(self, parser):
        self._parser = parser


def exhaustive(parser):
    def _parser(string):
        for result, rest in parser(string):
            if not rest:
                yield result
    return _parser