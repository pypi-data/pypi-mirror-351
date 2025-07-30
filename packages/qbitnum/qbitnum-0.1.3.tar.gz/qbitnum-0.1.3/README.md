# qbitnum

**Quantum‐Inspired Numeric Data Type for Classical Python**

`qbitnum` provides a `QBitNum` class that simulates qubit‑like superposition for integer/float values, letting you perform probabilistic arithmetic in pure Python.

## Features

- Store distributions of possible values with associated probabilities  
- Support `+`, `-`, `*`, `//` (and extendable) operations over superposed states  
- Post‑operation “collapse” in three modes:
  - **mean**: expected value  
  - **max**: most likely value  
  - **sample**: random draw by probability  

## Installation

```bash
pip install qbitnum

from qbitnum import QBitNum

# Create superposed values
q1 = QBitNum([(1, 0.5), (2, 0.5)])
q2 = QBitNum([(3, 0.7), (4, 0.3)])

# Add them
q3 = q1 + q2
print(q3)  
# QBitNum({4: 0.35, 5: 0.5, 6: 0.15})

# Collapse to a single value:
print(q3.collapse('mean'))   # 4.8
print(q3.collapse('max'))    # 5
print(q3.collapse('sample')) # 4 or 5 or 6 (random)

class QBitNum:
    def __init__(self, states: List[Tuple[Number, float]]):
        """
        states: list of (value, probability), probabilities need not sum to 1.
        """
    def __add__(self, other: QBitNum) -> QBitNum:  # likewise -, *, //
    def collapse(self, mode: str = 'mean') -> Number
        """
        mode in {'mean', 'max', 'sample'}
        """

