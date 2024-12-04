# Interface Solver (WIP)

## How to run
1. Setup virtual environments:
   
    - On linux terminal run:

        ```bash
        ./setup_dowhy.sh
        ```

        ```bash
        ./setup_bcause.sh
        ```

        ```bash
        ./setup_autobounds.sh
        ```

        ```bash
        ./setup_lcn.sh
        ```

   - If you already have the virtual environments set up, you can check if they are correctly set up or check updates by running:

        ```bash
        source setup_checker.sh
        ```

2. Run main code
    ```bash
    python3 -m main tests/test-simples.txt
    ```
