FROM python:3.10-slim

WORKDIR /app

COPY src/solvers/autobounds_solver/requirements_autobounds.txt .

RUN pip install --no-cache-dir -r requirements_autobounds.txt

COPY src/solvers/autobounds_solver/autobounds_solver.py .

COPY utils ./utils

COPY autobounds ./autobounds

EXPOSE 5001

CMD ["python", "autobounds_solver.py"]