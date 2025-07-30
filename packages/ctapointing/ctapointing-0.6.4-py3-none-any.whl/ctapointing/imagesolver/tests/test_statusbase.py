import pytest

from ctapointing.imagesolver.registration import StatusBase, Status


def test_statusbase():
    # test for DEFAULT status
    s = StatusBase()
    assert s.has_status(Status.DEFAULT)

    # set all possible flags
    for x in Status:
        if x is not Status.DEFAULT:
            s.set_status(x)

    # test for all flags to be set
    for x in Status:
        if x is not Status.DEFAULT:
            assert s.has_status(x)


def test_statusbase_fails():
    with pytest.raises(AttributeError):
        not_implemented_flag = Status.NOTIMPLEMENTED
        s = StatusBase(not_implemented_flag)

    not_implemented_flag = "some_string"
    with pytest.raises(AttributeError or TypeError):
        s = StatusBase(not_implemented_flag)
