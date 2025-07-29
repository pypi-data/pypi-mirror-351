# tests/test_core_equal_stats.py

import pytest
from orco_nmr.core import assign_spin_probs
from orco_nmr.core import SENTINEL

def make_equal_stats():
    """Stats where ALA and GLY share identical backbone (no SS needed)."""
    common = {'N': (1.0, 1.0), 'CA': (2.0, 1.0), 'CO': (3.0, 1.0)}
    return {
        ('ALA', ''): common,
        ('GLY', ''): common,
    }

def test_single_residue_probability():
    stats = {('ALA', ''): {'N': (1.0,1.0), 'CA': (2.0,1.0), 'CO': (3.0,1.0)}}
    spin  = {'N': 1.0, 'CA': 2.0, 'CO': 3.0, 'CX': []}
    probs = assign_spin_probs(spin, stats)
    assert probs == {'A': 1.0}

def test_two_equal_residues_split_evenly():
    stats = make_equal_stats()
    spin  = {'N': 1.0, 'CA': 2.0, 'CO': 3.0, 'CX': []}
    probs = assign_spin_probs(spin, stats)
    assert pytest.approx(probs['A'], rel=1e-6) == 0.5
    assert pytest.approx(probs['G'], rel=1e-6) == 0.5

def test_missing_mandatory_atom_returns_empty():
    stats = make_equal_stats()
    spin  = {'N': SENTINEL, 'CA': 2.0, 'CO': 3.0, 'CX': []}
    assert assign_spin_probs(spin, stats) == {}

def test_with_one_sidechain_dimension():
    stats = {
        ('ALA',''): {'N': (1.0,1.0), 'CA': (2.0,1.0), 'CO': (3.0,1.0), 'CB': (4.0,1.0)},
        ('GLY',''): {'N': (1.0,1.0), 'CA': (2.0,1.0), 'CO': (3.0,1.0), 'CB': (4.0,1.0)},
    }
    spin  = {'N': 1.0, 'CA': 2.0, 'CO': 3.0, 'CX': [4.0]}
    probs = assign_spin_probs(spin, stats)
    assert pytest.approx(probs['A'], rel=1e-6) == 0.5
    assert pytest.approx(probs['G'], rel=1e-6) == 0.5
