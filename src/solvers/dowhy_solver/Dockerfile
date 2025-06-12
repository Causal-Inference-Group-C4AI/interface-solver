FROM python:3.10-slim

WORKDIR /app

COPY src/solvers/dowhy_solver/requirements_dowhy.txt .

RUN pip install --no-cache-dir -r requirements_dowhy.txt

COPY src/solvers/dowhy_solver/dowhy_solver.py .

COPY utils ./utils

EXPOSE 5003

CMD ["python", "dowhy_solver.py"]