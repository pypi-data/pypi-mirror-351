import pytest
from orco_nmr.core import assign_spin, assign_spin_probs, SENTINEL
from orco_nmr.stats import load_stats

# load once
stats = load_stats()

def find_valid_spin(dims=("N", "CA", "CO", "CB")):
    """
    Find a residue that has all dims in its reference.
    Returns (res1, ref_dict).
    """
    for (res1, ss), ref in stats.items():
        if all(d in ref for d in dims):
            return res1, ref
    pytest.skip(f"No stats entry with dims {dims}")

def test_assign_spin_probs_valid_input():
    # pick a real residue/ref that contains N,CA,CO,CB
    res1, ref = find_valid_spin()
    spin = {
        "N":  ref["N"][0],
        "CA": ref["CA"][0],
        "CO": ref["CO"][0],
        "CX": [ ref["CB"][0] ],  # one optional dim
    }

    result = assign_spin_probs(spin, stats)
    assert isinstance(result, dict)
    assert result, "Expected non‐empty probability dict"
    assert abs(sum(result.values()) - 1.0) < 1e-6

    # the picked residue must be top‐1
    top1 = max(result.items(), key=lambda kv: kv[1])[0]
    assert top1 == res1

def test_assign_spin_probs_missing_CA():
    spin = {"N": 120.0, "CA": SENTINEL, "CO": 175.0, "CX": [20.0]}
    assert assign_spin_probs(spin, stats) == {}

def test_assign_spin_print_output(capsys):
    res1, ref = find_valid_spin()
    spin = {
        "N":  ref["N"][0],
        "CA": ref["CA"][0],
        "CO": ref["CO"][0],
        "CX": [ ref["CB"][0] ],
    }

    assign_spin(spin, stats)
    out = capsys.readouterr().out

    # header + our residue
    assert "Res" in out
    assert "Total" in out
    assert any(ss in out for ss in ("Coil", "Helix", "Sheet"))
    assert res1 in out

def test_assign_spin_error_on_missing_backbone(capsys):
    spin = {"N": SENTINEL, "CA": SENTINEL, "CO": SENTINEL, "CX": []}
    assign_spin(spin, stats)
    out = capsys.readouterr().out
    assert "must supply N, CA and CO" in out
