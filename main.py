#!/usr/bin/env python3
"""
main.py

Este script:
 - Carga distribuciones desde archivos.
 - Invoca la simulación Fortran para generar time_evolution.dat.
 - Lee los resultados.
 - Llama al módulo de graficado.
"""

import ctypes
import logging
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from numpy.ctypeslib import ndpointer

from plotting import plot_simulation

# -------------------------------------------------------------------
# Configuración de logging
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# -------------------------------------------------------------------
# Constantes de rutas
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"
LIB_PATH = BASE_DIR / "lib" / "libepidemic.so"

TIME_EVOLUTION = RESULTS_DIR / "time_evolution.dat"

# -------------------------------------------------------------------
# Tipos
# -------------------------------------------------------------------
Array1D = ndpointer(ctypes.c_double, flags="C_CONTIGUOUS")

# -------------------------------------------------------------------
# Funciones
# -------------------------------------------------------------------
def load_distributions(nt: int) -> Tuple[np.ndarray, np.ndarray]:
    """Carga los vectores G y P desde archivos y comprueba su longitud."""
    G = np.loadtxt(DATA_DIR / "time_generation.dat")
    P = np.loadtxt(DATA_DIR / "incubation_period.dat")

    if G.size != nt + 1 or P.size != nt + 1:
        raise ValueError(f"Se esperaban {nt+1} valores en las distribuciones, "
                         f"pero se obtuvieron {G.size} y {P.size}.")
    logging.info("Distribuciones cargadas correctamente.")
    return G, P

def init_fortran(lib_path: Path) -> ctypes.CDLL:
    """Carga la librería Fortran y ajusta tipos de la rutina."""
    lib = ctypes.CDLL(str(lib_path))
    lib.simulate_and_write.argtypes = [Array1D, Array1D]
    lib.simulate_and_write.restype = None
    logging.info("Librería Fortran cargada desde %s", lib_path)
    return lib

def run_simulation(lib: ctypes.CDLL, G: np.ndarray, P: np.ndarray) -> None:
    """Llama a la subrutina Fortran para generar time_evolution.dat."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    logging.info("Iniciando simulación Fortran...")
    lib.simulate_and_write(G, P)
    logging.info("Simulación completada y archivo generado: %s", TIME_EVOLUTION)

def main() -> None:
    NT = 20
    G, P = load_distributions(NT)
    lib = init_fortran(LIB_PATH)
    run_simulation(lib, G, P)
    plot_simulation(TIME_EVOLUTION)

if __name__ == "__main__":
    main()
