import pytest

from destiny.main.bdd.models import Players, Matches
from destiny.main.bdd.connexion import Session
from destiny.main.etl.extract import extract_summoners, extract_matches


@pytest.fixture
def p_session():
    return Session


def test_extract_summoners(p_session):
    nb_sum_needed = 5
    sums = extract_summoners(p_session, nb_sum_needed)
    assert all(type(s) == Players for s in sums)
    assert len(sums) == nb_sum_needed


def test_extract_matches(p_session):
    nb_match_needed = 5
    matches = extract_matches(p_session, nb_match_needed)
    assert all(type(m) == Matches for m in matches)
    assert len(matches) == nb_match_needed

# testing: do this after the implementation of the mcd
def test_extract_timelines(p_session):
    assert False

