<div align="center">



<p align="center"><img src="https://github.com/user-attachments/assets/1cad2a1e-ca87-474e-96de-fd6b02560771" width=100px /></p>

# Twocan

*A Bayesian optimization framework for multimodal registration of highly multiplexed single-cell spatial proteomics data*

[![Documentation Status](https://readthedocs.org/projects/twocan/badge/?version=latest)](https://twocan.readthedocs.io/en/latest/?badge=latest)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![PyPI version](https://badge.fury.io/py/twocan.svg)](https://badge.fury.io/py/twocan)

</div>

## Overview

Twocan automatically finds optimal parameters for registering images from different spatial proteomics technologies using Bayesian optimization. Instead of manually tuning preprocessing and registration parameters, Twocan efficiently explores the parameter space to find the best registration for your data.

**Key Features:**
- 🔧 Automated parameter optimization for image registration
- 🧠 Bayesian optimization via Optuna for efficient search
- 🔬 Support for multiple spatial proteomics modalities (IF, IMC, FISH, IMS)
- 📊 Built-in quality metrics and visualization tools
- 🎯 Extensible framework for custom objectives and preprocessors

## Quick Start

### Installation

```bash
# Install from PyPI
pip install twocan

# Or install from source
git clone https://github.com/camlab-bioml/twocan.git
cd twocan
pip install .
```

### Basic Usage

```python
import twocan as tc

# Load your images
moving_img = tc.read_image("moving.tif") 
fixed_img = tc.read_image("fixed.tif")

# Create estimator and optimize
estimator = tc.RegEstimator(moving_img, fixed_img)
study = estimator.optimize(n_trials=100)

# Get best transformation
best_transform = tc.pick_best_registration(study)
```

## Documentation

📚 **[Full Documentation](https://twocan.readthedocs.io/)**

## Examples & Notebooks

Check out the `notebooks/` directory for comprehensive examples:
- Basic registration with default settings
- Custom preprocessing for different modalities  
- Advanced optimization strategies
- Saving and loading registration results

## Citation

If you use Twocan in your research, please cite:

```bibtex
@software{harrigan2024twocan,
  title={Twocan: A Bayesian optimization framework for multimodal registration},
  author={Harrigan, Caitlin F.},
  year={2024},
  url={https://github.com/camlab-bioml/twocan}
}
```

## License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 **Documentation**: [twocan.readthedocs.io](https://twocan.readthedocs.io/)
- 📧 **Contact**: kierancampbell@lunenfeld.ca
- 🐛 **Issues**: [GitHub Issues](https://github.com/camlab-bioml/twocan/issues)
