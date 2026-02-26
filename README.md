# ∑ Mathematischer Ausdrucksgenerator

Streamlit-Demo: https://math-expression-generator.streamlit.app/

Streamlit-App zur Generierung zufälliger mathematischer Ausdrücke mit Ableitung, Integral und farbigem Term-Highlighting.

## Starten

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Features

- **Konzepte** – Polynom, Wurzel, Trigonometrie, Logarithmus, Exponential, Rational, Brüche
- **Komplexität** – Anzahl der Terme per Slider (1–7)
- **Erweiterte Einstellungen** – Koeffizientenbereich, Multiplikation von Termen, Verschachtelungen
- **Ableitungen** – Erste und zweite Ableitung (SymPy)
- **Integral** – Unbestimmtes Integral + C
- **Term-Highlighting** – Jeden Summanden in eigener Farbe; Ableitungen/Integral übernehmen dieselben Farben

## Stack

- [Streamlit](https://streamlit.io) – UI
- [SymPy](https://www.sympy.org) – Symbolisches Rechnen
- [KaTeX](https://katex.org) – LaTeX-Rendering (via Streamlit)



@Constantin Wilharm Feb. 2026
MIT