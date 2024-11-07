# interface-solver
Interface para rodar softwares que calculam bounds de efeito causal. 

## How to run
On root repository:
```python
python3 automatic_interface tests/test-name.txt
```


# Causal Inference Interface

This project provides a unified interface to run and compare four different software tools for causal inference analysis: **LCN**, **Autobounds**, **Bcause**, and **DoWhy**.
The interface simplifies setting up and executing causal inference models, making it easier to switch between tools and benchmark their performance and results.

## Overview

Causal inference is an area in data science and statistical analysis, focusing on understanding and identifying cause-effect relationships in data, often under conditions of uncertainty or limited information.
In many real-world scenarios, causal relationships cannot be fully identified due to missing data, unobserved confounding, or other limitations.
This is where partial identifiability comes into play—an approach that allows for estimating causal effects in such limited scenarios, providing bounds or ranges for causal effects instead of exact values.

This project integrates four distinct causal inference libraries, each offering unique methods for handling (or not handling) partial identifiability.
Users can compare and contrast these approaches, exploring how each library handles the challenge of uncertainty in causal modeling, and evaluate their outputs and efficiency in a straightforward, scriptable environment.


### Supported Libraries


### Key Features


## Installation

### Requirements

The following Python packages are required (recommended versions are noted):

- `matplotlib==3.9.2`
- `networkx==2.8.5`
- `pyscipopt==5.1.1`
- `numpy==1.24.4`
- `pandas==2.1.3`
- `pgmpy==0.1.17`
- `tqdm`
- `setuptools`
- `wheel`
- `plotnine`
- `sympy`
- `scipy`
- `dowhy`
- `bcause`

To install these dependencies, run:

```bash
pip install -r requirements.txt
```

### Installing the Interface
Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/yourusername/causal-inference-interface.git
cd causal-inference-interface
```

Then install the package:

```bash
python setup.py install
```

## Usage
### Basic example
1. Import the main interface class:

```bash
from causal_inference_interface import CausalInferenceInterface
```

2. Initialize the interface with a dataset:

```bash
interface = CausalInferenceInterface(data_path="data/your_data.csv")
```

3. Run a specific software package:

```bash
results_lcn = interface.run_lcn()
results_autobounds = interface.run_autobounds()
results_bcause = interface.run_bcause()
results_dowhy = interface.run_dowhy()
```

4. Compare results across the different libraries:

```bash
interface.compare_results([results_lcn, results_autobounds, results_bcause, results_dowhy])
```

### Error Handling
If an invalid path or unsupported data format is provided, the interface will raise a custom error message detailing the issue.

## Folder Structure

```bash
project-root/
├── data/                # Directory for data files
├── causal_inference_interface/
│   ├── __init__.py      # Main interface code
│   └── ...              # Additional module files
├── README.md
└── requirements.txt
```

## Contributing
1. Fork the repository.
2. Create a feature branch (git checkout -b feature-branch).
3. Commit your changes (git commit -m 'Add feature').
4. Push to the branch (git push origin feature-branch).
5. Open a Pull Request.


## License
This project is licensed under the MIT License. See LICENSE for more details.

## Acknowledgements
This interface integrates with open-source libraries, and we appreciate the developers of LCN, Autobounds, Bcause, and DoWhy for their contributions to causal inference.

## Contact
For questions or issues, please contact [Daniel](A.COM).