class PsonoException(Exception):
    '''Psono Errors'''

class PsonoPermissionDeniedOrNotExistException(PsonoException):
    '''Psono Errors'''

class PsonoLoginException(PsonoException):
    '''Psono Login Failure'''

class PsonoPathNotFoundException(PsonoException):
    ''''Psono path not found'''

class PsonoIDNotFoundException(PsonoException):
    '''Raise when you can't find the an ID'''