# Interface Solver (WIP)

## How to run
1. Setup Docker containers:

     ```bash
     docker compose build
     ```

3. Run main code
    ```bash
    docker compose run main_interface tests/test-simples.txt
    ```
4. Stop containers and remove orphans
   ```bash
    docker compose down --remove-orphans
    ```

