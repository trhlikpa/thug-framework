class DatabaseRecordError(Exception):
    """
    Raised when mongodb document has wrong format or does not exists
    """
    pass


class UserAgentNotFoundError(Exception):
    """
    Raised when mongodb document does not contain user agent
    """
    pass


class UrlNotFoundError(Exception):
    """
    Raised when mongodb document does not contain url
    """
    pass


class UrlFormatError(Exception):
    """
    Raised when domain cannot be parsed from url
    """
    pass


class UrlNotReachedError(Exception):
    """
    Raised when url is unreachable
    """
    pass
