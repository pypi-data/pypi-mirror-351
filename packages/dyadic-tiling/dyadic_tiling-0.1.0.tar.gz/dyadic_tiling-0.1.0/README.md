# DyadicTiling

> **Morton encoded dyadic cubes and points for efficient space decomposition.**

DyadicTiling is a lightweight Python package for tiling spaces of arbitrary dimension with dyadic cubes. Points are organised using Morton encodings, dyadic cubes are points with a truncation level, and tilings are collections of dyadic cubes. The natural ordering from the Morton encoding allows for efficient operations, even in high-dimensions.

---

## ✨ Features

* **Pure‑Python**: Only one light-weight dependency, `sortedcontainers`.
* **Arbitrary dimension**: The same code works from 1‑D to 17‑D and beyond.
* **PointSet & DyadicCubeSet**: Membership operations in *O(log n)*.
* **Stopping Times**: Define a (consistent) rule τ(x) that assigns a level to each point and automatically get a disjoint set of dyadic cubes.
* **Fully tested**: 100% coverage across 100+ unit tests.

---

## 🚀 Installation

```bash
pip install dyadic-tiling            # From PyPI (recommended)
# or
pip install git+https://github.com/Benjamin-Walker/DyadicTiling.git
```

Requires Python ⩾ 3.8 and sortedcontainers ⩾ 2.4.

---

## ⚡ Quick‑start

```python
from DyadicTiling.point import Point
from DyadicTiling.dyadic_cube import DyadicCube

# 1. Encode any point in [range[0][0], range[0][1]] x [range[1][0], range[1][1]]
range = [[-3, -1], [1.1, 1.3]]
p = Point([-2.3, 1.2], coordinate_ranges=range)
print(p.get_morton_string(4))      # → '00110111' (morton code at level 4)

# 2. Grab the dyadic cube that contains it at level k
cube = p.get_containing_cube(level=2)
print(cube)                        # DyadicCube(dim=2, level=2, morton_code=0011)

# 3. Slice a PointSet by cube
from DyadicTiling.point_set import PointSet
cloud = PointSet([p, Point([-2.5, 1.18], coordinate_ranges=range), Point([-1.1, 1.28], coordinate_ranges=range)])
print(cloud.in_cube(cube))         # Only points inside that square

# 4. Build a stopping using DyadicCubes
from DyadicTiling.stopping_time import DyadicCubeSetStoppingTime
rule = DyadicCubeSetStoppingTime()
rule.add(cube)
print(rule(p))                     # 2  (the level for the point p)
```

---


## 📄 License

DyadicTiling is distributed under the MIT license — see `LICENSE` for details.

---

## ✏️ Citation

If this package saved you some time, please cite it:

```bibtex
@software{dyadictiling,
  author       = {Benjamin Walker},
  title        = {DyadicTiling: Morton encoded dyadic cubes and points for efficient space decomposition.},
  year         = {2025},
  url          = {https://github.com/Benjamin-Walker/DyadicTiling},
  license      = {MIT}
}
```