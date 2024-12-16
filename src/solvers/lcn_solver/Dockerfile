FROM python:3.10-slim

WORKDIR /app

COPY src/solvers/lcn_solver/requirements_lcn.txt .

RUN pip install --no-cache-dir -r requirements_lcn.txt

COPY src/solvers/lcn_solver/lcn_solver.py .

COPY utils ./utils

COPY lcn ./lcn

EXPOSE 5004

CMD ["python", "lcn_solver.py"]