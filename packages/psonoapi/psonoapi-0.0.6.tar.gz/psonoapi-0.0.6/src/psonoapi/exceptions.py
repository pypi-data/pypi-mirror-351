class PsonoException(Exception):
    '''Psono Errors'''


class PsonoSecretNotFoundException(PsonoException):
    '''Raise when you can't find the secret'''