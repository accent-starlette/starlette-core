import datetime


def bad_input_variable(today=None):
    return today or datetime.datetime.now()


def another_bad_input_variable(today=datetime.datetime.now()):
    return today
