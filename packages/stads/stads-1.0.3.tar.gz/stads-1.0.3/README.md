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
│   ├── config.py
│   ├── evaluation.py
│   ├── image_processing.py
│   ├── interpolator.py
│   ├── microscope.py
│   ├── random_sampler.py
│   ├── read_images.py
│   ├── stads.py
│   ├── stads_helpers.py
│   ├── stratified_sampler.py
│   ├── stratified_sampler_helpers.py
│   └── utility_functions.py
├── tests/
│   ├── test_laboratory_instruments.py
│   ├── test_random_sampler.py
│   ├── test_stads_helpers.py
│   ├── test_stratified_sampler.py
│   └── test_stratified_sampler_helpers.py
├── setup.py
├── README.md
└── requirements.txt
</pre>

---

## Installation

### Install from PyPI

```bash
pip install stads_sampler
```

### Install from Source (Development Mode)

```bash
git clone https://github.com/bharadwajakarsh/stads_adaptive_sampler.git
cd stads_sampler
pip install -e .
```

---

## Usage

### 1. Running Laboratory Experiments

#### Adaptive Sampler Test

```python
from laboratory.laboratory_instruments import LaboratoryInstrument

myInstrument = LaboratoryInstrument((1080, 1080), 10)  # Initialize instrument
myInstrument.run_experiment1()  # Run adaptive sampling experiment
```

---

### 2. Running Individual Samplers

#### Uniform Sampler

```python
from src.random_sampler import RandomSampler

mySampler = RandomSampler((1080, 1080), 10)
mySampler.get_coordinates()()
```

#### Stratified Sampler

```python
from src.stratified_sampler import StratifiedSampler

mySampler = StratifiedSampler((1080, 1080), 10)
mySampler.get_coordinates()
```

---

### 3. Running Full Adaptive Sampling Experiment

```python
from src.stads import AdaptiveSampler

mySampler = AdaptiveSampler(
    (1080, 1080),        # Frame size
    'stratified',        # Initial sampler: 'uniform' or 'stratified'
    'linear',            # Sampling strategy: 'linear', 'exponential', etc.
    50,                  # Total sample budget
    10                   # Initial sampling rate
)

reconstructed_frames, PSNRs, SSIMs = mySampler.run()
```

---

## License

This project is licensed under the OPINCHARGE. See the [LICENSE](LICENSE) file for details.

---

## Contact

**Author:** Akarsh Bharadwaj  
**Email:** akarsh_sudheendra.bharadwaj@dfki.de  
**Repository:** [github.com/bharadwajakarsh/stads_adaptive_sampler](https://github.com/bharadwajakarsh/stads_adaptive_sampler)
