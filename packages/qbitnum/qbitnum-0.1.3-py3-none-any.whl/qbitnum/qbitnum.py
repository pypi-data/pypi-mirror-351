# qbitnum/qbitnum.py

from collections import defaultdict
import random

class QBitNum:
    """
    Quantum‐inspired numeric type: holds a distribution of (value, probability) states.
    Supports +, -, *, //, and collapse().
    """

    def __init__(self, states):
        self.states = defaultdict(float)
        total = 0.0
        for val, prob in states:
            self.states[val] += prob
            total += prob
        # normalize
        if abs(total - 1.0) > 1e-8 and total > 0:
            for v in self.states:
                self.states[v] /= total

    def __add__(self, other):
        result = defaultdict(float)
        for v1, p1 in self.states.items():
            for v2, p2 in other.states.items():
                result[v1 + v2] += p1 * p2
        return QBitNum(list(result.items()))

    def __sub__(self, other):
        result = defaultdict(float)
        for v1, p1 in self.states.items():
            for v2, p2 in other.states.items():
                result[v1 - v2] += p1 * p2
        return QBitNum(list(result.items()))

    def __mul__(self, other):
        result = defaultdict(float)
        for v1, p1 in self.states.items():
            for v2, p2 in other.states.items():
                result[v1 * v2] += p1 * p2
        return QBitNum(list(result.items()))

    def __floordiv__(self, other):
        result = defaultdict(float)
        for v1, p1 in self.states.items():
            for v2, p2 in other.states.items():
                if v2 != 0:
                    result[v1 // v2] += p1 * p2
        return QBitNum(list(result.items()))

    def collapse(self, mode='mean'):
        """Collapse distribution to a single number."""
        if mode == 'mean':
            return sum(v * p for v, p in self.states.items())
        elif mode == 'max':
            return max(self.states.items(), key=lambda x: x[1])[0]
        elif mode == 'sample':
            r = random.random()
            cum = 0.0
            for v, p in sorted(self.states.items()):
                cum += p
                if r < cum:
                    return v
            # fallback
            return v
        else:
            raise ValueError(f"Unknown collapse mode: {mode}")

    def __repr__(self):
        return f"QBitNum({{ {', '.join(f'{v}: {p:.3f}' for v, p in self.states.items())} }})"

