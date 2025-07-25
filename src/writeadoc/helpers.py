import re


RX_WIDONT = re.compile(r"\s+(\S+\s*)$")


def widont(value):
    """
    Adds an HTML non-breaking space between the final two words of the string to
    avoid "widowed" words.

    Examples:

    >>> widont('Test   me   out')
    'Test   me&nbsp;out'

    >>> widont('It works with trailing spaces too  ')
    'It works with trailing spaces&nbsp;too  '

    >>> widont('no-effect')
    'no-effect'

    """

    def replace(matchobj):
        return f"&nbsp;{matchobj.group(1)}"

    return RX_WIDONT.sub(replace, str(value))
