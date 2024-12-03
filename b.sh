#!/bin/bash

# Comando a ser executado
COMMAND="python3 -m main tests/OBSERVAVEL_balke_pearl.txt"

# Loop para executar o comando 10 vezes
for i in {1..5}
do
    echo "Execução $i:"
    $COMMAND
done

