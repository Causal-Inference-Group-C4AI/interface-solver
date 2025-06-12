# Interface Solver

Interface Solver is a modular framework for causal inference and probabilistic graphical models.
It offers a streamlined pipeline for executing and comparing causal inference algorithms in a reproducible, containerized environment.
The framework supports seamless integration and benchmarking of multiple packages—including [DoWhy](https://github.com/py-why/dowhy), [bcause](https://github.com/PGM-Lab/bcause), [lcn](https://github.com/IBM/LCN), and [autobounds](https://www.tandfonline.com/doi/full/10.1080/01621459.2023.2216909) (with source code access)—enabling direct comparison of their performance.

This project was supported by IBM through its Scholarship Program and by Itaú Unibanco S.A. through the Itaú Scholarship Program (PBI).

## Overview

Causal inference is an area in data science and statistical analysis, focusing on understanding and identifying cause-effect relationships in data, often under conditions of uncertainty or limited information.
In many real-world scenarios, causal relationships cannot be fully identified due to missing data, unobserved confounding, or other limitations.
This is where partial identifiability comes into play—an approach that allows for estimating causal effects in such limited scenarios, providing bounds or ranges for causal effects instead of exact values.

This project integrates four distinct causal inference libraries, each offering unique methods for handling (or not handling) partial identifiability.
Users can compare and contrast these approaches, exploring how each library handles the challenge of uncertainty in causal modeling, and evaluate their outputs and efficiency in a reproducible, containerized environment.


## Features

- **Causal Model Parsing:** Supports parsing of UAI files and other network formats.
- **Network Generation:** Tools for generating canonical and relaxed network representations.
- **Mechanism Definition:** Automated mechanism generation for nodes in causal graphs.
- **Containerized Execution:** Docker-based setup for reproducible experiments.
- **Extensible Architecture:** Modular codebase for easy integration of new solvers and utilities.

## Getting Started
### How to run
1. **Build Docker Containers:**
    ```bash
    docker compose build
    ```

2. **Run Main Interface:**
    ```bash
    docker compose run main_interface tests/test-simples.txt
    ```

3. **Stop Containers:**
    ```bash
    docker compose down --remove-orphans
    ```

### Running BRACIS tests
In linux environment:

1. **Make it executable**:
    ```bash
    chmod +x run_all_bracis_tests.sh
    ```

2. **Run**:
    ```bash
    ./run_all_bracis_tests.sh
    ```

## Contributing
1. Fork the repository.
2. Create a feature branch (git checkout -b feature-branch).
3. Commit your changes (git commit -m 'Add feature').
4. Push to the branch (git push origin feature-branch).
5. Open a Pull Request.

## Acknowledgements
This interface integrates with open-source libraries, and we appreciate the researchers and developers of LCN, Autobounds, Bcause, and DoWhy for their contributions to causal inference.

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.

## Contact
For questions or issues, please contact [Daniel](daniel.lawand@gmail.com).