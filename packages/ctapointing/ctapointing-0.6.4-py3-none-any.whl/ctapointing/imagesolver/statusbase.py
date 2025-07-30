from enum import IntFlag

import logging

log = logging.getLogger(__name__)


class Status(IntFlag):
    """
    Status flags used during spot extraction, matching
    and fitting.
    """

    USED = 1
    PRESELECTED = 2
    SELECTED = 4
    MATCHED = 8
    SIMFITTED = 16
    FIELDMATCHED = 32
    BESTMATCH = 64
    SOLVED = 128
    OUTLIER = 256
    DEFAULT = 0


class StatusBase:
    """
    Class storing a combination of various status flags.

    Available flags are those defined in the Status class.
    """

    def __init__(self, status=Status.DEFAULT):
        if not isinstance(status, Status):
            raise AttributeError

        self.__status = status

    def has_status(self, status):
        """
        Check if object has status 'status'.
        Returns True if this is the case, False otherwise.

        :param status: Status class flag to test
        """
        return (self.__status & status) == status

    def is_used(self):
        return self.has_status(Status.USED)

    def is_preselected(self):
        return self.has_status(Status.PRESELECTED)

    def is_selected(self):
        return self.has_status(Status.SELECTED)

    def is_matched(self):
        return self.has_status(Status.MATCHED)

    def is_simfitted(self):
        return self.has_status(Status.SIMFITTED)

    def is_fieldmatched(self):
        return self.has_status(Status.FIELDMATCHED)

    def is_bestmatch(self):
        return self.has_status(Status.BESTMATCH)

    def is_solved(self):
        return self.has_status(Status.SOLVED)

    def set_status(self, status, combine=True):
        """
        Sets a status flag for this object.

        :param status: the status flag to be set
        :param combine: if True, add status flag to other existing flags
                        if False, set this status flag as the only one
        """
        if status not in Status:
            raise AttributeError

        if status is Status.DEFAULT:
            self.__status = Status.DEFAULT
        elif combine:
            self.__status |= status
        else:
            self.__status = status

    def unset_status(self, status):
        if status not in Status:
            raise AttributeError

        if status is Status.DEFAULT:
            self.__status = Status.DEFAULT
        else:
            self.__status &= ~status

    @property
    def status(self):
        """
        Returns combined set of status flags for this object.

        :returns Status: (combined set of) status flags.
        """
        return self.__status

    def __repr__(self):
        return repr(self.__status)

    def __str__(self):
        return str(self.__status)
