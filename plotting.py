#!/usr/bin/env python3
"""
plotting.py

Funciones para leer datos de simulación epidemiológica desde un archivo .dat
y generar un gráfico guardado en PNG.
"""

import logging
from pathlib import Path
from typing import Union, List

import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------------------------
# Configuración de logging
# -------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

# -------------------------------------------------------------------
# Constantes de gráfico
# -------------------------------------------------------------------
DEFAULT_VARIABLES: List[str] = ["S", "I", "Q", "R", "D"]
DEFAULT_COLORS: List[str] = [
    "tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"
]
FIG_SIZE = (12, 7)
DPI = 300

# -------------------------------------------------------------------
# Funciones
# -------------------------------------------------------------------
def read_simulation_data(file_dat: Union[str, Path]) -> pd.DataFrame:
    """
    Lee un archivo .dat generado por Fortran y devuelve un DataFrame con
    columnas ['T', 'D', 'R', 'I', 'Q', 'S'].

    Args:
        file_dat: Ruta al archivo .dat

    Raises:
        FileNotFoundError: Si el archivo no existe.
    """
    file_path = Path(file_dat)
    if not file_path.is_file():
        logger.error("Archivo de datos no encontrado: %s", file_path)
        raise FileNotFoundError(f"{file_path} no existe")

    df = pd.read_csv(
        file_path,
        comment="#",
        sep=r"\s+",
        engine="python",
        header=None,
        names=["T", "D", "R", "I", "Q", "S"],
    )
    logger.info("Datos leídos correctamente desde %s", file_path)
    return df

def plot_simulation(
    file_dat: Union[str, Path],
    output_path: Union[str, Path] = Path("results") / "simulation_plot.png",
    variables: List[str] = DEFAULT_VARIABLES,
    colors: List[str] = DEFAULT_COLORS,
) -> None:
    """
    Genera un gráfico de la simulación epidemiológica y lo guarda en PNG.

    Args:
        file_dat: Ruta al archivo .dat con columnas T, D, R, I, Q, S.
        output_path: Ruta de salida para el archivo PNG.
        variables: Lista de variables a graficar (columnas del DataFrame).
        colors: Lista de colores para cada variable.
    """
    # Leer datos
    df = read_simulation_data(file_dat)

    # Preparar carpeta de salida
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Crear figura y eje
    fig, ax = plt.subplots(figsize=FIG_SIZE)

    # Graficar cada variable
    for var, color in zip(variables, colors):
        ax.plot(df["T"], df[var], label=var, color=color)

    # Etiquetas y estilo
    ax.set_xlabel("Tiempo (días)")
    ax.set_ylabel("Proporción")
    ax.set_title("Evolución de las variables epidemiológicas")
    ax.legend()
    ax.grid(True)

    # Ajuste y guardado
    fig.tight_layout()
    fig.savefig(out_path, dpi=DPI)
    plt.close(fig)

    logger.info("Gráfico guardado en: %s", out_path.resolve())  
