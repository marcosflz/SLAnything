"""Genera los diagramas propios (en español) del capítulo 1.

Uso:
    uv run --with matplotlib python tools/make_ch01_assets.py
"""
from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).resolve().parents[1] / "notebooks" / "assets" / "ch01"
OUT.mkdir(parents=True, exist_ok=True)

AZUL = "#2F6FEB"
AZUL_CLARO = "#E8F0FE"
VERDE = "#1F9D6B"
VERDE_CLARO = "#E6F6EF"
AMBAR = "#C77800"
AMBAR_CLARO = "#FFF4DE"
GRIS = "#5B6472"
GRIS_CLARO = "#F2F4F7"
TINTA = "#1B2430"


def caja(ax, x, y, w, h, titulo, subtitulo="", fc="white", ec=AZUL,
         tc=TINTA, fs=12, sub_fs=9.5, lw=1.6, radio=0.035):
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.012,rounding_size={radio}",
        linewidth=lw, edgecolor=ec, facecolor=fc, zorder=2,
    )
    ax.add_patch(p)
    if subtitulo:
        ax.text(x + w/2, y + h*0.64, titulo, ha="center", va="center",
                fontsize=fs, fontweight="bold", color=tc, zorder=3)
        ax.text(x + w/2, y + h*0.30, subtitulo, ha="center", va="center",
                fontsize=sub_fs, color=GRIS, zorder=3, linespacing=1.25)
    else:
        ax.text(x + w/2, y + h/2, titulo, ha="center", va="center",
                fontsize=fs, fontweight="bold", color=tc, zorder=3,
                linespacing=1.25)


def flecha(ax, x1, y1, x2, y2, color=GRIS, lw=2.0, rad=0.0):
    a = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>", mutation_scale=18, linewidth=lw,
        color=color, connectionstyle=f"arc3,rad={rad}", zorder=1,
    )
    ax.add_patch(a)


def diagrama_etapas():
    fig, ax = plt.subplots(figsize=(13.2, 5.6))
    ax.set_xlim(0, 13.2); ax.set_ylim(0, 5.6); ax.axis("off")

    ax.text(0.25, 5.28, "Las dos etapas de un LLM", fontsize=19,
            fontweight="bold", color=TINTA, va="top")
    ax.text(0.25, 4.92, "Primero aprende el idioma con texto sin etiquetar; después se especializa con datos etiquetados.",
            fontsize=11.5, color=GRIS, va="top")

    # Pretraining
    caja(ax, 0.30, 2.95, 2.35, 1.25, "Texto sin etiquetar",
         "web · libros · Wikipedia\nmiles de millones de tokens",
         fc=GRIS_CLARO, ec=GRIS, fs=11.5, sub_fs=9)
    caja(ax, 3.05, 2.95, 3.05, 1.25, "PRETRAINING",
         "predecir la siguiente palabra\nlas etiquetas salen del texto",
         fc=AZUL_CLARO, ec=AZUL, tc=AZUL, fs=12.5, sub_fs=9.0)
    caja(ax, 6.55, 2.95, 2.15, 1.25, "Modelo base",
         "foundation model\ncapacidad general\ndel idioma",
         fc="white", ec=AZUL, fs=11.5, sub_fs=9)
    flecha(ax, 2.68, 3.57, 3.02, 3.57)
    flecha(ax, 6.13, 3.57, 6.52, 3.57)

    ax.text(0.30, 2.55, "Etapa 1 · aprender el idioma", fontsize=10,
            color=AZUL, fontweight="bold")

    # Finetuning
    caja(ax, 0.30, 0.55, 2.35, 1.15, "Datos etiquetados",
         "instrucción → respuesta\no texto → clase",
         fc=VERDE_CLARO, ec=VERDE, fs=11, sub_fs=9)
    caja(ax, 3.05, 0.55, 3.05, 1.15, "FINETUNING",
         "especializar el modelo base\ncon ejemplos etiquetados",
         fc=VERDE_CLARO, ec=VERDE, tc=VERDE, fs=12.5, sub_fs=9.0)
    caja(ax, 6.55, 0.90, 2.15, 0.95, "Asistente",
         "sigue instrucciones", fc="white", ec=VERDE, fs=11, sub_fs=9)
    caja(ax, 6.55, 0.05, 2.15, 0.72, "Clasificador",
         "spam / no spam,\nsentimiento…", fc="white", ec=VERDE, fs=10.5, sub_fs=8.5)
    flecha(ax, 2.68, 1.12, 3.02, 1.12)
    flecha(ax, 6.13, 1.12, 6.50, 1.32)
    flecha(ax, 6.13, 1.12, 6.50, 0.45)

    # Flecha vertical del modelo base al finetuning
    flecha(ax, 7.62, 2.92, 7.62, 1.90, color=GRIS, lw=2.2, rad=0.0)
    ax.text(7.78, 2.40, "reutilizamos\nlos pesos", fontsize=9, color=GRIS, va="center")

    # Etapa 3 target
    caja(ax, 9.20, 0.55, 3.55, 1.60,
         "LLM final",
         "Asistente conversacional (ChatGPT)\no modelo especializado en una tarea",
         fc=AMBAR_CLARO, ec=AMBAR, fs=12.5, sub_fs=9.5)
    flecha(ax, 8.73, 1.37, 9.17, 1.37, color=AMBAR)
    ax.text(9.20, 0.28, "Etapa 3 · especializar", fontsize=10,
            color=AMBAR, fontweight="bold")

    ax.text(9.20, 2.55, "El mismo modelo base sirve\npara tareas muy distintas.",
            fontsize=9.5, color=GRIS, style="italic", linespacing=1.3)

    fig.savefig(OUT / "fig_es_etapas.png", dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)


def diagrama_roadmap():
    fig, ax = plt.subplots(figsize=(13.2, 4.5))
    ax.set_xlim(0, 13.2); ax.set_ylim(0, 4.5); ax.axis("off")

    ax.text(0.25, 4.22, "El plan del libro: tres etapas, un LLM", fontsize=18,
            fontweight="bold", color=TINTA, va="top")
    ax.text(0.25, 3.90, "Cada etapa produce algo que puedes ejecutar y examinar.",
            fontsize=11, color=GRIS, va="top")

    etapas = [
        ("ETAPA 1", "Construir los cimientos", "caps. 2–4",
         ["Datos y tokenización", "Mecanismo de atención", "Arquitectura GPT"], AZUL, AZUL_CLARO),
        ("ETAPA 2", "Preentrenar", "caps. 5–6",
         ["Bucle de entrenamiento", "Evaluación del modelo", "Cargar pesos abiertos"], VERDE, VERDE_CLARO),
        ("ETAPA 3", "Especializar", "cap. 7",
         ["Instruction tuning", "Clasificación", "Asistente personal"], AMBAR, AMBAR_CLARO),
    ]
    x = 0.35
    for i, (etapa, titulo, caps, items, color, claro) in enumerate(etapas):
        w = 3.85
        caja(ax, x, 0.55, w, 2.75, "", fc="white", ec=color, lw=1.8)
        ax.add_patch(FancyBboxPatch((x, 2.22), w, 1.08,
                     boxstyle="round,pad=0.012,rounding_size=0.03",
                     linewidth=0, facecolor=claro, zorder=3))
        ax.text(x + 0.22, 3.02, etapa, fontsize=9.5, color=color,
                fontweight="bold", zorder=4)
        ax.text(x + 0.22, 2.72, titulo, fontsize=14, color=TINTA,
                fontweight="bold", zorder=4)
        ax.text(x + w - 0.20, 3.02, caps, fontsize=9.5, color=GRIS,
                ha="right", zorder=4)
        for j, item in enumerate(items):
            yy = 1.78 - j * 0.42
            ax.text(x + 0.22, yy, "•", fontsize=12, color=color, zorder=4)
            ax.text(x + 0.42, yy, item, fontsize=10.2, color=TINTA, zorder=4)
        if i < 2:
            flecha(ax, x + w + 0.05, 1.92, x + w + 0.43, 1.92, color=GRIS, lw=2.0)
        x += w + 0.48

    ax.text(0.35, 0.18, "En este cuaderno recorremos la etapa 0: entender qué vamos a construir y por qué.",
            fontsize=9.5, color=GRIS, style="italic")

    fig.savefig(OUT / "fig_es_roadmap.png", dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    diagrama_etapas()
    diagrama_roadmap()
    print("Listo:", OUT)
