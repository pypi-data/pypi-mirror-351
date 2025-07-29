"""
Module implements some basic functions involving regular expressions.
"""

import re


def extract_protocol(url: str) -> str | None:
    """
    Extract the protocol portion from a database connection URL.

    The extract_protocol function takes a database connection URL string as input and extracts the protocol portion
    (the part before "://"). This function is useful for identifying the database type from connection strings.

    :param url: The url from which the protocol will be extracted.
    :type url: str
    :return: The protocol or None, if the extraction failed
    :rtype: str | None
    """
    pattern = r'^([a-z0-9_\-+.]+)://'
    match = re.match(pattern, url)
    if match:
        return match.group(1)
    return None


def normalize_sql_spaces(sql_string: str) -> str:
    """
    Normalize multiple consecutive spaces in SQL string to single spaces.
    Only handles spaces, preserves other whitespace characters.

    :param sql_string: The SQL string for space normalization.
    :type sql_string: str
    :return: The normalized SQL command.
    :rtype: str
    """
    return re.sub(r' +', ' ', sql_string.strip())
