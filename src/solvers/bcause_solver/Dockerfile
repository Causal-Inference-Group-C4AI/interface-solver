FROM python:3.10-slim

WORKDIR /app

COPY src/solvers/bcause_solver/requirements_bcause.txt .

RUN pip install --no-cache-dir -r requirements_bcause.txt

COPY src/solvers/bcause_solver/bcause_solver.py .

COPY utils ./utils

EXPOSE 5003

CMD ["python", "bcause_solver.py"]