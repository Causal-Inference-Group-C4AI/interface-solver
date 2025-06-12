# Interface Solver

Interface Solver is a modular framework for causal inference and probabilistic graphical models.
It offers a streamlined pipeline for executing and comparing causal inference algorithms in a reproducible, containerized environment.
The framework supports seamless integration and benchmarking of multiple packages—including [DoWhy](https://github.com/py-why/dowhy), [bcause](https://github.com/PGM-Lab/bcause), [lcn](https://github.com/IBM/LCN), and [autobounds](https://www.tandfonline.com/doi/full/10.1080/01621459.2023.2216909) (with source code access)—enabling direct comparison of their performance.
The primary goal of this project is to evaluate and compare the effectiveness of different tools when working with partially identifiable causal graphs.

This project was carried out with the support of IBM and of Itaú Unibanco S.A., through the Itaú Scholarship Program (PBI).


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
## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
