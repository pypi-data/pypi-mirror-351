# tests/test_qbitnum.py

import pytest
from qbitnum.qbitnum import QBitNum

def test_normalization():
    q = QBitNum([(1, 2), (2, 2)])
    # total weight 4 → normalized to 0.5 each
    assert pytest.approx(q.states[1]) == 0.5
    assert pytest.approx(q.states[2]) == 0.5

def test_addition_and_collapse():
    q1 = QBitNum([(1, 0.5), (2, 0.5)])
    q2 = QBitNum([(3, 0.7), (4, 0.3)])
    q3 = q1 + q2
    # expected distribution: {4:0.35, 5:0.5, 6:0.15}
    assert pytest.approx(q3.states[4], rel=1e-3) == 0.35
    assert pytest.approx(q3.states[5], rel=1e-3) == 0.50
    assert pytest.approx(q3.states[6], rel=1e-3) == 0.15
    assert pytest.approx(q3.collapse('mean'), rel=1e-3) == 4.8
    assert q3.collapse('max') == 5

def test_sub_mul_div():
    q1 = QBitNum([(2, 1.0)])
    q2 = QBitNum([(3, 1.0)])
    assert (q1 - q2).collapse('mean') == -1
    assert (q1 * q2).collapse('mean') == 6
    assert (q2 // q1).collapse('mean') == 1

def test_sample_mode():
    q = QBitNum([(1, 0.8), (2, 0.2)])
    # run many samples to check distribution roughly
    samples = [q.collapse('sample') for _ in range(1000)]
    # ensure both values appear
    assert 1 in samples and 2 in samples

