# Adaptive Sampling Algorithm for FIB-SEM and SIMS Imaging

## Abstract

We present an initial prototype of an adaptive sampling algorithm designed for sparse and adaptive scanning in Focused Ion Beam Scanning Electron Microscopy (FIB-SEM) and Secondary Ion Mass Spectrometry (SIMS) imaging. The algorithm leverages temporal coherence in time-dependent secondary electron imaging and spatial/spectral redundancy in hyperspectral imaging to enable efficient image acquisition.

Our approach aims to mitigate beam-induced damage by enabling lower dwell-time (resulting in noisy images) or sparse sampling with post-reconstruction. We evaluate random sampling techniques, including uniform and stratified methods, and compare interpolation strategies—cubic, linear, and nearest neighbour—based on reconstruction fidelity and structural similarity metrics.

---

## Project Structure

<pre>
STADS/
├── data/
├── figures/
├── plots/
├── laboratory/
│   └── laboratory_instruments.py
├── src/
│   └── stads/
│       ├── __init__.py
│       ├── config.py
│       ├── evaluation.py
│       ├── image_processing.py
│       ├── interpolator.py
│       ├── microscope.py
│       ├── random_sampler.py
│       ├── read_images.py
│       ├── stads.py
│       ├── stads_helpers.py
│       ├── stratified_sampler.py
│       ├── stratified_sampler_helpers.py
│       └── utility_functions.py
├── tests/
│   ├── test_laboratory_instruments.py
│   ├── test_random_sampler.py
│   ├── test_stads_helpers.py
│   ├── test_stratified_sampler.py
│   └── test_stratified_sampler_helpers.py
├── setup.py
├── pyproject.toml
├── README.md
└── requirements.txt
</pre>

---

## Installation

### Install from PyPI

```bash
pip install stads
