FROM python:3.10-slim

WORKDIR /app

COPY src/solvers/lcn_solver/requirements_lcn.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc g++ gfortran git cmake liblapack-dev libblas-dev pkg-config \
        curl make ca-certificates bash patch unzip autoconf automake libtool locales && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://raw.githubusercontent.com/coin-or/coinbrew/master/coinbrew -o /usr/local/bin/coinbrew && \
    chmod +x /usr/local/bin/coinbrew

RUN bash -c "/usr/local/bin/coinbrew fetch Ipopt --no-prompt"
RUN bash -c "/usr/local/bin/coinbrew build Ipopt --prefix=/usr/local/ipopt --test --no-prompt"
RUN bash -c "/usr/local/bin/coinbrew install Ipopt --no-prompt"

ENV LD_LIBRARY_PATH=/usr/local/ipopt/lib:$LD_LIBRARY_PATH
ENV PATH=/usr/local/ipopt/bin:$PATH

RUN pip install --no-cache-dir -r requirements_lcn.txt

COPY src/solvers/lcn_solver/lcn_solver.py .

COPY utils ./utils

COPY lcn ./lcn

EXPOSE 5004

CMD ["python", "lcn_solver.py"]