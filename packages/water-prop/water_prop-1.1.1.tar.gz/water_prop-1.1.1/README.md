# water_prop

This package provides vapor pressure (in bar) and specific gravity of water at different temperatures (°C).

## Installation

```bash
pip install .
```

## Usage

```python
from water_prop import get_sg, get_vp

print(get_sg(30))  # Specific Gravity
print(get_vp(30))  # Vapor Pressure (bar)
```
