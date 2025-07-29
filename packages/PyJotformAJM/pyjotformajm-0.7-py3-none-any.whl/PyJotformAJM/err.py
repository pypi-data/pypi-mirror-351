from urllib.error import HTTPError


class JotFormAuthenticationError(HTTPError):
    ...


class NoJotformClientError(Exception):
    ...


class InvalidJotformSubmissionID(Exception):
    ...


class SignatureFileError(Exception):
    ...


class FieldTableMapNotLoaded(FileNotFoundError):
    ...
