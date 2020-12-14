"""Run test with hypothesis - in the exemple below we let pytest discover and run the test but we could also run the test explicitly ourselfs or  done it
as unitest. More info here: https://hypothesis.readthedocs.io/en/latest/quickstart.html#an-example """

from hypothesis import given, example, assume
import hypothesis.strategies as st
from math import isnan #to remove nan from test

def encode(input_string):

    if not input_string:
        return []

    count = 1
    prev = ""
    lst = []
    for character in input_string:
        if character != prev:
            if prev:
                entry = (prev, count)
                lst.append(entry)
            count = 1
            prev = character
        else:
            count += 1
    entry = (character, count)
    lst.append(entry)
    return lst


def decode(lst):
    q = ""
    for character, count in lst:
        q += character * count
    return q

@given(st.text()) #specifies how to provide the arguments
@example("") #to check edge cases - we add here the test that we always want to perform
def test_decode_inverts_encode(s):
    assert decode(encode(s)) == s

@given(st.integers(), st.integers())
def test_ints_are_commutative(x, y):
    assert x + y == y + x


@given(x=st.integers(), y=st.integers())
def test_ints_cancel(x, y):
    assert (x + y) - y == x


@given(st.lists(st.integers()))
def test_reversing_twice_gives_same_list(xs):
    # This will generate lists of arbitrary length (usually between 0 and
    # 100 elements) whose elements are integers.
    ys = list(xs)
    ys.reverse()
    ys.reverse()
    assert xs == ys


@given(st.tuples(st.booleans(), st.text()))
def test_look_tuples_work_too(t):
    # A tuple is generated as the one you provided, with the corresponding
    # types in those positions.
    assert len(t) == 2
    assert isinstance(t[0], bool)
    assert isinstance(t[1], str)

@given(st.floats())
def test_negation_is_self_inverse_for_non_nan(x):
    assume(not isnan(x))
    assert x == -(-x)
