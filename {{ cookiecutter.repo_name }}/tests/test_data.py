"""
Sample test for data

------
This sample demostrates using a pandas DataFrame object and
follows common pandas convertions

"""

import pytest
import pandas as pd
import datatest as dt
from hypothesis import given, example, assume
import hypothesis.strategies as st
from math import isnan #to remove nan from test


@pytest.fixture(scope='module')
@dt.working_directory(__file__)
def df():
    return pd.read_csv('example.csv')


def test_column_names(df):
    """
    Check that your data has the required columns
    """
    required_names = {'A', 'B', 'C'}
    dt.validate(df.columns, required_names)


def test_column(df):
    """
    Check that your dataframe has the columns in the order specified in a list
    """
    required_columns = ['A', 'B', 'C']
    dt.validate(df.columns, required_columns)


def test_a(df):
    """
    Check that a column has especific values
    """
    data = df['A'].values
    requirement = {'x', 'y', 'z'}
    dt.validate(data, requirement)


def test_max_value():
    """Validates values within a list"""
    data = [60, 200, 18, 99, 105]

    def max200(x):
        if x <= 200:
            return True
        return dt.Deviation(x - 200, 200)

    def test_sum():
        assert sum(data) == 482

    # ... add more functions here

    dt.validate(data, max200)


# validate data types


def test_float_types():
    data = [0.0, 1.0, 2.0]

    dt.validate(data, float)


# validate format - we can add json schema

# ...add more tests here...

if __name__ == '__main__':
    import sys
    sys.exit(pytest.main([__file__]))

#test with hypothesis: https://hypothesis.readthedocs.io/en/latest/quickstart.html

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




@st.composite
def distinct_strings_with_common_characters(draw):
    x = draw(st.text(min_size=1))
    y = draw(st.text(alphabet=x))
    assume(x != y)
    return (x, y)

@given(s1=distinct_strings_with_common_characters(), s2= distinct_strings_with_common_characters()) #call the composite function
def test_substraction(s1, s2):
    print(s1, s2)

#hypothesis for geojsons

@st.composite
def positions(draw, dims=2):
    """
    https://tools.ietf.org/html/rfc7946#section-3.1.1
    Questions
    ---------
    * should the elevation/altitude component be bounded?
    * is it valid to mix dimensionality of positions within a geometry?
    """
    if dims is None:
        dims = draw(st.sampled_from([2, 3]))

    if dims == 2:
        pos = draw(
            st.tuples(
                st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False),
                st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False)))
    elif dims == 3:
        pos = draw(
            st.tuples(
                st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False),
                st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
                st.floats(allow_nan=False, allow_infinity=False)))
    else:
        raise ValueError("Position must be 2 or 3 dims")

    return pos


@st.composite
def bboxes(draw, dims=2):
    """
    https://tools.ietf.org/html/rfc7946#section-5
    """
    if dims is None:
        dims = draw(st.sampled_from([2, 3]))

    # Use 3 dim positions even if we only need 2
    pos1 = draw(positions(dims=3))
    pos2 = draw(positions(dims=3))
    lons, lats, zs = zip(pos1, pos2)

    if dims == 2:
        bbox = (min(lons), min(lats), max(lons), max(lats))
    elif dims == 3:
        bbox = (min(lons), min(lats), min(zs), max(lons), max(lats), max(zs))
    else:
        raise ValueError("dims must be 2 or 3")

    return bbox


@st.composite
def linestrings(draw):
    """
    https://tools.ietf.org/html/rfc7946#section-3.1.4
    """
    return draw(st.lists(positions(), min_size=2))


@st.composite
def linear_rings(draw, assert_validity=False):
    """
    https://tools.ietf.org/html/rfc7946#section-3.1.6
    """
    coords = draw(st.lists(positions(), min_size=4))
    coords.append(coords[0])
    if assert_validity:
        raise NotImplementedError('assert_validity not available yet')
    return coords


@st.composite
def geometries(draw, geom_types=None):
    """
    Questions
    ---------
    * When coordinates are composed of arrays of something,
    can those arrays be empty? Assume NO here (e.g.,
    MultiPoint is an array of *at least one* position.)
    * Need to add bbox and foreign members
    """
    if geom_types is None:
        # default to all
        geom_types = [
            'Point', 'LineString', 'Polygon',
            'MultiPoint', 'MultiLineString', 'MultiPolygon']

    geom_type = draw(st.sampled_from(geom_types))

    if geom_type == 'Point':
        coords = draw(positions())
    elif geom_type == 'LineString':
        coords = draw(linestrings())
    elif geom_type == 'Polygon':
        coords = draw(st.lists(linear_rings(), min_size=1))
    elif geom_type == 'MultiPoint':
        coords = draw(st.lists(positions(), min_size=1))
    elif geom_type == 'MultiLineString':
        coords = draw(st.lists(linestrings(), min_size=1))
    elif geom_type == 'MultiPolygon':
        coords = draw(st.lists(st.lists(linear_rings(), min_size=1), min_size=1))
    else:
        raise NotImplementedError(geom_type)

    return {
        'type': geom_type,
        'coordinates': coords}


@st.composite
def geometry_collection(draw):
    """
    To Do
    -----
    * bbox and foreign members
    """
    geoms = draw(st.lists(geometries()))  # can be empty
    assume(len(geoms) != 1)  # avoid single geom
    return {
        'type': 'GeometryCollection',
        'geometries': geoms}


@st.composite
def properties(draw):
    return draw(st.dictionaries(
        keys=st.one_of(st.text(), st.integers()),
        values=st.one_of(
            st.text(),
            st.integers(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.none())))


@st.composite
def features(draw):
    feature = {
        'type': 'Feature',
        'geometry': draw(st.one_of(geometries(), geometry_collection(), st.none())),
        'properties': draw(st.one_of(properties(), st.none()))}

    if draw(st.booleans()):
        feature['id'] = draw(st.one_of(
            st.integers(), st.text(), st.floats(allow_nan=False, allow_infinity=False)))

    if draw(st.booleans()):
        feature['bbox'] = draw(bboxes())

    # foreign members
    if draw(st.booleans()):
        key = draw(st.one_of(
            st.integers(), st.text(), st.floats(allow_nan=False, allow_infinity=False)))
        value = draw(st.one_of(
            st.integers(), st.text(), st.none(), st.floats(allow_nan=False, allow_infinity=False)))
        feature[key] = value

    return feature


# @st.composite
# def feature_collection(draw):
#     """
#     To do
#     -----
#     Foreign Members and bbox
#     """
#     features = draw(st.lists(features()))
#     return {
#         'type': 'FeatureCollection',
#         'features': features}

def find_name(feature):
    """This function checks a geojson-like feature
    for the `name` property.

    This assumes that feature['properties']
    is always a dictionary or mapping. But the GeoJSON spec
    allows for `null` (becomes a python `None`) and causes this
    to fail on otherwise valid geojson objects.

    Would you think to test that? Hypothesis does.
    """
    # Get name property or default to empty string
    return feature['properties'].get('name', '')


# To use the hypothesis GeoJSON strategy,
# decorate the test with the @given(feautures())
@given(features())
def test_find_name(feature):
    find_name(feature)
