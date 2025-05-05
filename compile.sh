#!/bin/bash
mkdir -p lib
mkdir -p results
gfortran -shared -fPIC -o lib/libepidemic.so epidemic_simulation.f90
echo "✅ Compilación exitosa: lib/libepidemic.so"
