import streamlit as st
import sympy as sp
import random

# ─────────────────────────────────────────────
# Seitenkonfiguration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Mathematischer Ausdrucksgenerator",
    page_icon="∑",
    layout="wide",
)

# CSS – alle Latex-Elemente werden über data-testid="stLatex" gestylt,
# da st.markdown()-Blöcke kein echtes DOM-Wrapping um benachbarte st.latex()-Elemente erzeugen.
st.markdown(
    """
<style>
/* ── alle LaTeX-Boxen ── */
[data-testid="stLatex"] {
    background: #1e1e2e;
    border: 1px solid #44475a;
    border-radius: 10px;
    padding: 22px 20px;
    margin: 6px 0 10px;
    text-align: center;
}
[data-testid="stLatex"] .katex {
    color: #f8f8f2 !important;
    font-size: 1.6rem !important;
}

/* ── Hauptausdruck: etwas größer ── */
.main-expr-label {
    font-size: 1.05rem;
    color: #888;
    margin-bottom: 2px;
}
.main-expr [data-testid="stLatex"] {
    border-color: #6272a4;
    border-width: 2px;
}
.main-expr [data-testid="stLatex"] .katex {
    font-size: 2.1rem !important;
}

/* ── Abschnittsüberschriften ── */
.sec-header {
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: .04em;
    margin: 20px 0 4px;
    padding: 5px 14px;
    border-radius: 6px;
    display: inline-block;
}
.sec-header.abl  { background:#1c3a28; color:#50fa7b; }
.sec-header.int  { background:#3a1c31; color:#ff79c6; }
.sec-header.loes { background:#3a2c1c; color:#ffb86c; }

/* ── LaTeX-Boxen je Abschnitt einfärben ── */
.abl-block  [data-testid="stLatex"] { border-left: 4px solid #50fa7b; }
.int-block  [data-testid="stLatex"] { border-left: 4px solid #ff79c6; }
.loes-block [data-testid="stLatex"] { border-left: 4px solid #ffb86c; }
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# Symbolische Variable
# ─────────────────────────────────────────────
x = sp.Symbol("x", real=True)

# ─────────────────────────────────────────────
# Konzept-Katalog
# ─────────────────────────────────────────────
KONZEPTE = {
    "Polynom  xⁿ": {
        "key": "poly",
        "default": True,
        "emoji": "📈",
        "help": "Terme wie 3x², −x³, 5x",
    },
    "Quadratwurzel  √x": {
        "key": "sqrt",
        "default": True,
        "emoji": "√",
        "help": "√x, 2√x",
    },
    "n-te Wurzel  ⁿ√x": {
        "key": "nthroot",
        "default": False,
        "emoji": "∛",
        "help": "Kubikwurzel, 4. Wurzel, …",
    },
    "Trigonometrisch": {
        "key": "trig",
        "default": True,
        "emoji": "〜",
        "help": "sin(x), cos(x), tan(x)",
    },
    "Logarithmus": {
        "key": "log",
        "default": True,
        "emoji": "㏒",
        "help": "ln(x), log₁₀(x), log₂(x)",
    },
    "Exponential  eˣ": {
        "key": "exp",
        "default": True,
        "emoji": "eˣ",
        "help": "eˣ, 2ˣ, e^(2x)",
    },
    "Rational  1/xⁿ": {
        "key": "rational",
        "default": False,
        "emoji": "½",
        "help": "1/x, 2/x², …",
    },
    "Betrag  |x|": {
        "key": "absval",
        "default": False,
        "emoji": "|·|",
        "help": "|x|, |2x−1|",
    },
    "Hyperbolisch  sinh/cosh": {
        "key": "hyp",
        "default": False,
        "emoji": "ℍ",
        "help": "sinh(x), cosh(x)",
    },
    "Brüche  (a·x+b)/(c·x+d)": {
        "key": "bruch",
        "default": False,
        "emoji": "⅟",
        "help": "Rationale Ausdrücke wie (2x+1)/(x−3), 5/(x²+4), (x²+2)/(x+1)",
    },
}


# ─────────────────────────────────────────────
# Ausdrucksgenerator
# ─────────────────────────────────────────────
_DEFAULT_ADV: dict = {
    "koeff_min": -4,
    "koeff_max": 4,
    "multiplikation": False,
    "verschachteln": False,
}


def _koeff(adv_cfg: dict) -> sp.Integer:
    min_k = adv_cfg.get("koeff_min", -4)
    max_k = adv_cfg.get("koeff_max", 4)
    bereich = [i for i in range(min_k, max_k + 1) if i != 0]
    return sp.Integer(random.choice(bereich or [-1, 1]))


def _inner_arg(konzepte: set, adv_cfg: dict) -> sp.Expr:
    """Nicht-triviales inneres Argument für Verschachtelungen.
    Schließt 'linear' aus → sichtbares Nesting wie sin(x²), ln(√x), e^(cos x)."""
    pool: list[str] = []
    sicher = konzepte & {"poly", "sqrt", "trig"}
    if not sicher:
        sicher = {"poly"}
    if "poly" in sicher:
        pool += ["quadratic", "cubic"]  # kein "linear"!
    if "sqrt" in sicher:
        pool += ["sqrt"]
    if "trig" in sicher:
        pool += ["sin", "cos"]
    if not pool:
        pool = ["quadratic"]

    w = random.choice(pool)
    a = sp.Integer(random.choice([1, 2]))
    match w:
        case "quadratic":
            return x**2  # positiv → sicher als sqrt/log-Inneres
        case "cubic":
            return x**3
        case "sqrt":
            return sp.sqrt(x)
        case "sin":
            return sp.sin(a * x)
        case "cos":
            return sp.cos(a * x)
        case _:
            return x**2


def _inner_arg_fuer_poly(konzepte: set, adv_cfg: dict) -> sp.Expr:
    """Inneres Argument speziell für Poly-Nesting.
    Bevorzugt Funktionen (trig/sqrt), damit (sin x)² statt (x²)² entsteht."""
    funk = konzepte & {"trig", "sqrt", "hyp"}
    if funk:
        return _inner_arg(funk, adv_cfg)
    return _inner_arg(konzepte, adv_cfg)


def _term_bauen(konzepte: set, adv_cfg: dict, tiefe: int = 0) -> sp.Expr:
    pool: list[str] = []
    if "poly" in konzepte:
        pool += ["linear", "quadratic", "cubic", "quartic"]
    if "sqrt" in konzepte:
        pool += ["sqrt", "sqrt"]
    if "nthroot" in konzepte:
        pool += ["cbrt", "viertwurzel"]
    if "trig" in konzepte:
        pool += ["sin", "cos"] + (["tan"] if random.random() > 0.6 else [])
    if "log" in konzepte:
        pool += ["ln", "log10", "log2"]
    if "exp" in konzepte:
        pool += ["exp", "exp2"]
    if "rational" in konzepte:
        pool += ["inv1", "inv2"]
    if "absval" in konzepte:
        pool += ["abs"]
    if "hyp" in konzepte:
        pool += ["sinh", "cosh"]
    if "bruch" in konzepte:
        pool += ["bruch_lin_lin", "bruch_konst_quad", "bruch_quad_lin"]
    if not pool:
        return x

    c = _koeff(adv_cfg)
    w = random.choice(pool)
    a = sp.Integer(random.choice([1, 2, 3]))

    nest = adv_cfg.get("verschachteln", False) and tiefe == 0

    # Inneres Argument für funktionale Terme (sin/log/sqrt/…)
    def arg() -> sp.Expr:
        return _inner_arg(konzepte, adv_cfg) if nest else a * x

    match w:
        # ── Polynome: Nesting über (inner)^n ──────────────────────────────────
        case "linear":
            if nest:
                return c * _inner_arg_fuer_poly(konzepte, adv_cfg)
            return c * x
        case "quadratic":
            if nest:
                return c * _inner_arg_fuer_poly(konzepte, adv_cfg) ** 2
            return c * x**2
        case "cubic":
            if nest:
                return c * _inner_arg_fuer_poly(konzepte, adv_cfg) ** 3
            return c * x**3
        case "quartic":
            if nest:
                return c * _inner_arg_fuer_poly(konzepte, adv_cfg) ** 4
            return c * x**4
        # ── Funktionale Terme: Nesting über arg() ─────────────────────────────
        case "sqrt":
            return c * sp.sqrt(arg())
        case "cbrt":
            return c * sp.cbrt(arg())
        case "viertwurzel":
            return c * sp.root(arg(), 4)
        case "sin":
            return c * sp.sin(arg())
        case "cos":
            return c * sp.cos(arg())
        case "tan":
            return c * sp.tan(arg())
        case "ln":
            return c * sp.log(arg())
        case "log10":
            return c * sp.log(arg(), 10)
        case "log2":
            return c * sp.log(arg(), 2)
        case "exp":
            return c * sp.exp(arg())
        case "exp2":
            return c * sp.exp(2 * arg())
        case "inv1":
            return c / x
        case "inv2":
            return c / x**2
        case "abs":
            return c * sp.Abs(x)
        case "sinh":
            return c * sp.sinh(arg())
        case "cosh":
            return c * sp.cosh(arg())
        # ── Brüche ────────────────────────────────────────────────────────────
        case "bruch_lin_lin":
            b1 = sp.Integer(random.randint(-5, 5))
            b2 = sp.Integer(random.choice([-3, -2, -1, 1, 2, 3]))
            return (_koeff(adv_cfg) * x + b1) / (c * x + b2)
        case "bruch_konst_quad":
            zaehler = sp.Integer(random.randint(1, 6))
            k = sp.Integer(random.randint(1, 9))
            return zaehler / (x**2 + k)
        case "bruch_quad_lin":
            b = sp.Integer(random.choice([-3, -2, -1, 1, 2, 3]))
            return (c * x**2 + sp.Integer(random.randint(1, 5))) / (x + b)
        case _:
            return x


def ausdruck_generieren(
    konzepte: set, n_terme: int = 3, adv_cfg: dict | None = None
) -> sp.Expr:
    if adv_cfg is None:
        adv_cfg = _DEFAULT_ADV
    if not konzepte:
        return x**2 + 2 * x - 3

    terme: list[sp.Expr] = []
    versuche = 0
    while len(terme) < n_terme and versuche < 80:
        t = _term_bauen(konzepte, adv_cfg)
        if str(t) not in [str(tt) for tt in terme]:
            terme.append(t)
        versuche += 1
    if not terme:
        terme = [x**2]

    # Optionale Konstante
    if random.random() > 0.4:
        terme.append(sp.Integer(random.randint(-9, 9)))

    # Multiplikation: JEDES aufeinanderfolgende Paar wird zwingend multipliziert
    if adv_cfg.get("multiplikation", False) and len(terme) >= 2:
        random.shuffle(terme)
        neue: list[sp.Expr] = []
        i = 0
        while i < len(terme):
            if i + 1 < len(terme):
                neue.append(terme[i] * terme[i + 1])
                i += 2
            else:
                neue.append(terme[i])  # letzter Term bei ungerader Anzahl
                i += 1
        terme = neue

    return sp.Add(*terme, evaluate=True)


# ─────────────────────────────────────────────
# Rechner-Hilfsfunktionen
# ─────────────────────────────────────────────
def sichere_ableitung(ausdruck: sp.Expr, ordnung: int, vereinfachen: bool = True):
    try:
        result = sp.diff(ausdruck, x, ordnung)
        return (sp.simplify(result) if vereinfachen else result), None
    except Exception as e:
        return None, str(e)


def sicheres_integral(ausdruck: sp.Expr, vereinfachen: bool = True):
    try:
        result = sp.integrate(ausdruck, x)
        return (sp.simplify(result) if vereinfachen else result), None
    except Exception as e:
        return None, str(e)


# ─────────────────────────────────────────────
# Term-Highlighting
# ─────────────────────────────────────────────
# KaTeX unterstützt NUR benannte Farben in \textcolor, keine Hex-Werte.
# Für die HTML-Legende wird eine eigene Hex-Tabelle geführt.
# Diese Namen sind sowohl in KaTeX (\textcolor) als auch als CSS-Farbnamen gültig.
# Dadurch stimmen Legende (HTML) und Ausdruck (KaTeX) in der Farbe exakt überein.
HIGHLIGHT_FARBEN = [
    "blue",
    "orange",
    "green",
    "violet",
    "cyan",
    "teal",
    "red",
    "magenta",
]
_INNEN = "gray"  # innere Argumente (1. Ebene) → grau / dezent
_INNEN2 = "yellow"  # innere Argumente (2. Ebene) → gold


def _ist_neg(e: sp.Expr) -> bool:
    if isinstance(e, sp.Mul):
        return any(a.is_number and float(a) < 0 for a in e.args)
    if isinstance(e, (sp.Integer, sp.Rational, sp.Float)):
        return float(e) < 0
    return False


def _tc(farbe: str, s: str) -> str:
    return rf"\textcolor{{{farbe}}}{{{s}}}"


def _func_tex(cls) -> str:
    return {
        sp.sin: r"\sin",
        sp.cos: r"\cos",
        sp.tan: r"\tan",
        sp.asin: r"\arcsin",
        sp.acos: r"\arccos",
        sp.atan: r"\arctan",
        sp.sinh: r"\sinh",
        sp.cosh: r"\cosh",
        sp.log: r"\ln",
        sp.exp: r"\exp",
        sp.Abs: r"\left|\cdot\right|",
    }.get(cls, rf"\operatorname{{{cls.__name__}}}")


def _color_kern(kern: sp.Expr, farbe: str) -> str:
    """Baut farbiges LaTeX für einen Kern-Ausdruck (ohne Vorzeichen)."""

    # ── Atom ────────────────────────────────────────────────────────────────
    if kern.is_symbol or kern.is_number:
        return _tc(farbe, sp.latex(kern))

    # ── Potenz / Wurzel ─────────────────────────────────────────────────────
    if isinstance(kern, sp.Pow):
        b, e = kern.args
        b_l = sp.latex(b)
        if e == sp.Rational(1, 2):
            return _tc(farbe, r"\sqrt{" + _tc(_INNEN, b_l) + r"}")
        if e == sp.Rational(1, 3):
            return _tc(farbe, r"\sqrt[3]{" + _tc(_INNEN, b_l) + r"}")
        if e == sp.Rational(1, 4):
            return _tc(farbe, r"\sqrt[4]{" + _tc(_INNEN, b_l) + r"}")
        return _tc(farbe, sp.latex(kern))  # allgemeine Potenz: Ganzes einfärben

    # ── Zusammengesetzte Funktion ────────────────────────────────────────────
    if isinstance(kern, sp.Function):
        cls = type(kern)
        args = kern.args

        # exp(u) → e^{u}
        if cls is sp.exp and len(args) == 1:
            inner_l = _tc(_INNEN, sp.latex(args[0]))
            return _tc(farbe, r"e^{" + inner_l + r"}")

        # Abs(u) → |u|
        if cls is sp.Abs and len(args) == 1:
            inner_l = _tc(_INNEN, sp.latex(args[0]))
            return _tc(farbe, r"\left|" + inner_l + r"\right|")

        # log(x, Basis) → log_b(x)
        if cls is sp.log and len(args) == 2:
            inner_l = _tc(_INNEN, sp.latex(args[0]))
            b_l = sp.latex(args[1])
            # \left( und \right) MÜSSEN im selben \textcolor-Block sein
            return _tc(farbe, rf"\log_{{{b_l}}}\!\left(" + inner_l + r"\right)")

        # Alle anderen Funktionen mit einem Argument
        if len(args) == 1:
            inner = args[0]
            tex = _func_tex(cls)
            # 2-fach verschachtelt → gold
            inner_l = (
                _tc(_INNEN2, sp.latex(inner))
                if isinstance(inner, sp.Function)
                else _tc(_INNEN, sp.latex(inner))
            )
            # \left( und \right) MÜSSEN im selben \textcolor-Block sein
            return _tc(farbe, tex + r"\!\left(" + inner_l + r"\right)")

        return _tc(farbe, sp.latex(kern))

    # ── Produkt aus zwei Nicht-Zahlen ────────────────────────────────────────
    if isinstance(kern, sp.Mul):
        zahlen = [a for a in kern.args if a.is_number]
        andere = [a for a in kern.args if not a.is_number]
        if len(andere) == 1:
            return _color_kern(andere[0], farbe)
        if len(andere) == 2:
            return (
                _color_kern(andere[0], farbe)
                + r"\cdot "
                + _color_kern(andere[1], _INNEN)
            )
        return _tc(farbe, sp.latex(kern))  # >2 Faktoren: Fallback

    return _tc(farbe, sp.latex(kern))


def _color_addend(addend: sp.Expr, farbe: str) -> str:
    """Vollständig gefärbter Summand (Vorzeichen extern behandeln)."""
    kern = -addend if _ist_neg(addend) else addend

    # Koeffizient abspalten
    if isinstance(kern, sp.Mul):
        zahlen = [a for a in kern.args if a.is_number]
        andere = [a for a in kern.args if not a.is_number]
        if zahlen and andere:
            k = sp.Mul(*zahlen)
            k_abs = abs(k)
            rest = sp.Mul(*andere) if len(andere) > 1 else andere[0]
            col = _color_kern(rest, farbe)
            return col if k_abs == 1 else _tc(farbe, sp.latex(k_abs)) + r"\," + col
    return _color_kern(kern, farbe)


def _struktur(addend: sp.Expr) -> dict:
    """Erkennt äußere/innere Struktur eines Summanden für die Legende."""
    kern = -addend if _ist_neg(addend) else addend
    if isinstance(kern, sp.Mul):
        andere = [a for a in kern.args if not a.is_number]
        kern = andere[0] if len(andere) == 1 else (sp.Mul(*andere) if andere else kern)

    if isinstance(kern, sp.exp):
        inner = kern.args[0]
        return {"typ": "funktion", "name": "exp", "innen": sp.latex(inner)}

    if isinstance(kern, sp.Function):
        inner = kern.args[0]
        d = {"typ": "funktion", "name": type(kern).__name__, "innen": sp.latex(inner)}
        if isinstance(inner, sp.Function):
            d["typ"] = "verschachtelt"
            d["innen_name"] = type(inner).__name__
            d["innen2"] = sp.latex(inner.args[0]) if inner.args else "?"
        return d

    if isinstance(kern, sp.Pow):
        b, e = kern.args
        for frac, label in [
            (sp.Rational(1, 2), "Quadratwurzel"),
            (sp.Rational(1, 3), "Kubikwurzel"),
            (sp.Rational(1, 4), "4. Wurzel"),
        ]:
            if e == frac:
                return {"typ": "wurzel", "label": label, "innen": sp.latex(b)}
        return {"typ": "potenz", "basis": sp.latex(b), "exp": sp.latex(e)}

    if isinstance(kern, sp.Mul):
        funcs = [a for a in kern.args if isinstance(a, sp.Function)]
        if len(funcs) >= 2:
            return {"typ": "produkt", "faktoren": [sp.latex(f) for f in funcs]}

    return {"typ": "einfach"}


def highlighting(expr: sp.Expr) -> tuple[str, list[dict]]:
    """Gibt (farbiges LaTeX, Legende) zurück."""
    addends = list(sp.Add.make_args(expr))
    # Positive zuerst
    addends = sorted(addends, key=lambda a: 1 if _ist_neg(a) else 0)

    teile: list[str] = []
    legende: list[dict] = []

    for i, addend in enumerate(addends):
        farbe = HIGHLIGHT_FARBEN[i % len(HIGHLIGHT_FARBEN)]
        ist_neg = _ist_neg(addend)
        farbig = _color_addend(addend, farbe)
        sign = (
            (r"-\," if ist_neg else "") if i == 0 else (r"-\," if ist_neg else r"+\,")
        )
        teile.append(sign + farbig)
        legende.append(
            {
                "farbe": farbe,
                "latex": sp.latex(addend),
                "info": _struktur(addend),
            }
        )

    return " ".join(teile), legende


def _zerlegt_farbig(ausdruck: sp.Expr, op_func, vereinfachen: bool) -> str:
    """Wendet op_func term-für-term auf ausdruck an und färbt jedes Ergebnis
    in der Farbe des jeweiligen Ursprungs-Summanden (wie in highlighting())."""
    addends = sorted(sp.Add.make_args(ausdruck), key=lambda a: 1 if _ist_neg(a) else 0)
    teile: list[str] = []
    for i, addend in enumerate(addends):
        farbe = HIGHLIGHT_FARBEN[i % len(HIGHLIGHT_FARBEN)]
        try:
            result = op_func(addend)
            if vereinfachen:
                result = sp.simplify(result)
        except Exception:
            continue
        if result == 0:
            continue
        ist_neg = _ist_neg(result)
        abs_result = -result if ist_neg else result
        colored = _tc(farbe, sp.latex(abs_result))
        sign = (
            (r"-\," if ist_neg else "")
            if not teile
            else (r"-\," if ist_neg else r"+\,")
        )
        teile.append(sign + colored)
    return " ".join(teile) if teile else _tc("gray", "0")


# ─────────────────────────────────────────────
# UI – Seitenleiste
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Konfiguration")
    st.markdown("### Mathematische Konzepte")
    st.caption("Wähle die Bausteine, die im Ausdruck vorkommen dürfen.")

    ausgewaehlt: set = set()
    for bezeichnung, meta in KONZEPTE.items():
        if st.checkbox(
            f"{meta['emoji']}  {bezeichnung}",
            value=meta["default"],
            help=meta["help"],
            key=f"cb_{meta['key']}",
        ):
            ausgewaehlt.add(meta["key"])

    st.markdown("---")
    st.markdown("### Komplexität")
    n_terme = st.slider(
        "Anzahl der Terme",
        min_value=1,
        max_value=7,
        value=3,
        help="Wie viele unterschiedliche Terme der Ausdruck enthalten darf.",
    )

    st.markdown("---")
    with st.expander("🔬 Erweiterte Einstellungen (Advanced)", expanded=False):
        st.caption("Für komplexere Ausdrücke und mehr Kontrolle.")

        koeff_bereich = st.slider(
            "Koeffizientenbereich",
            min_value=-20,
            max_value=20,
            value=(-4, 4),
            help="Wertebereich für zufällige Koeffizienten. 0 wird stets ausgeschlossen.",
        )

        st.markdown("**Kombinationsregeln**")
        multiplikation = st.checkbox(
            "✖️ Multiplikation von Termen",
            value=False,
            help="Einzelne Terme können miteinander multipliziert werden, z. B. x² · sin(x).",
        )
        verschachteln = st.checkbox(
            "🪆 Verschachtelungen",
            value=False,
            help="Funktionsargumente werden durch Unterausdrücke ersetzt, z. B. sin(√x), ln(x²+1).",
        )

    adv_cfg: dict = {
        "koeff_min": koeff_bereich[0],
        "koeff_max": koeff_bereich[1],
        "multiplikation": multiplikation,
        "verschachteln": verschachteln,
    }

    st.markdown("---")
    st.caption("Erstellt mit SymPy · Streamlit")

# ─────────────────────────────────────────────
# UI – Hauptbereich: Kopfzeile
# ─────────────────────────────────────────────
st.markdown("# ∑ Mathematischer Ausdrucksgenerator")
st.markdown(
    "Konfiguriere die Konzepte in der Seitenleiste und klicke auf **Generieren**, "
    "um einen zufälligen mathematischen Ausdruck zu erstellen. "
    "Ableitung und Integral lassen sich unten einblenden."
)

_, col_btn = st.columns([5, 1])
with col_btn:
    generieren = st.button("🎲 Generieren", type="primary", use_container_width=True)

# ─────────────────────────────────────────────
# Session-State – Ausdruck bleibt beim Neuzeichnen erhalten
# ─────────────────────────────────────────────
if "ausdruck" not in st.session_state:
    st.session_state.ausdruck = ausdruck_generieren(ausgewaehlt, n_terme, adv_cfg)

if generieren:
    if not ausgewaehlt:
        st.warning("Bitte wähle mindestens ein Konzept in der Seitenleiste aus.")
    else:
        st.session_state.ausdruck = ausdruck_generieren(ausgewaehlt, n_terme, adv_cfg)

ausdruck: sp.Expr = st.session_state.ausdruck

# Highlighting-Flag früh lesen (Checkbox kommt erst nach dem Ausdruck)
zeige_highlight: bool = st.session_state.get("zeige_highlight", False)

# ─────────────────────────────────────────────
# Ausdruck anzeigen
# ─────────────────────────────────────────────
st.markdown("### Generierter Ausdruck")

if zeige_highlight:
    try:
        hl_latex, hl_legende = highlighting(ausdruck)
        st.latex(r"f(x) \;=\; " + hl_latex)
        # ── Kompakte Legende ────────────────────────────────────────────────
        teile = []
        for i, item in enumerate(hl_legende):
            # KaTeX-Farbnamen sind auch gültige CSS-Farbnamen → exakte Übereinstimmung
            html_col = item["farbe"]
            typ = item["info"].get("typ", "einfach")
            name = item["info"].get("name", "")

            # Menschenlesbare Unicode-Labels (kein LaTeX – wird in HTML angezeigt)
            _SUP = {"2": "²", "3": "³", "4": "⁴", "5": "⁵", "-1": "⁻¹", "-2": "⁻²"}
            _FN = {
                "log": "ln",
                "exp": "exp",
                "sin": "sin",
                "cos": "cos",
                "tan": "tan",
                "sinh": "sinh",
                "cosh": "cosh",
                "sqrt": "√",
                "Abs": "|·|",
                "asin": "arcsin",
                "acos": "arccos",
                "atan": "arctan",
            }
            fn = _FN.get(name, name)
            if typ == "funktion":
                label = (
                    "eˣ"
                    if name == "exp"
                    else (
                        "√(…)"
                        if name == "sqrt"
                        else "|…|" if name == "Abs" else f"{fn}(…)"
                    )
                )
            elif typ == "verschachtelt":
                i_name = item["info"].get("innen_name", "g")
                i_fn = _FN.get(i_name, i_name)
                label = f"{fn}({i_fn}(…))"
            elif typ == "wurzel":
                label = item["info"].get("label", "Wurzel")
            elif typ == "potenz":
                exp_s = str(item["info"].get("exp", "n"))
                label = "x" + _SUP.get(exp_s, f"^{exp_s}")
            elif typ == "produkt":
                label = "Produkt"
            else:
                label = "Polynom / Konst."
            teile.append(
                f'<span style="color:{html_col}; font-weight:600;">■ {label}</span>'
            )
        teile.append('<span style="color:#888;">▪ grau = inneres Arg.</span>')
        st.markdown(
            '<div style="font-size:0.8rem; margin:-6px 0 8px; line-height:2;">'
            + " &nbsp; ".join(teile)
            + "</div>",
            unsafe_allow_html=True,
        )
    except Exception as err:
        st.latex(r"f(x) \;=\; " + sp.latex(ausdruck))
        st.caption(f"Highlighting-Fehler: {err}")
else:
    st.latex(r"f(x) \;=\; " + sp.latex(ausdruck))

st.markdown("---")

# ─────────────────────────────────────────────
# Aufklapp-Schalter
# ─────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
zeige_abl = c1.checkbox("📐 Ableitungen anzeigen", value=False)
zeige_int = c2.checkbox("∫  Integral anzeigen", value=False)
vereinfachen = c3.checkbox(
    "✨ Vereinfachen",
    value=True,
    help="Wendet sp.simplify() an – kürzt Brüche, fasst Terme zusammen und vereinfacht Ausdrücke algebraisch.",
)
st.checkbox(
    "🎨 Term-Highlighting",
    value=False,
    key="zeige_highlight",
    help="Färbt jeden Summanden im Ausdruck oben in einer eigenen Farbe; innere Funktionsargumente erscheinen grau.",
)

# ─────────────────────────────────────────────
# Ableitungen
# ─────────────────────────────────────────────
if zeige_abl:
    st.markdown(
        '<span class="sec-header abl">📐 Ableitungen</span>',
        unsafe_allow_html=True,
    )

    abl1, err1 = sichere_ableitung(ausdruck, 1, vereinfachen)
    abl2, err2 = sichere_ableitung(ausdruck, 2, vereinfachen)

    st.markdown('<div class="abl-block">', unsafe_allow_html=True)

    st.markdown("**Erste Ableitung — f ′(x)**")
    if abl1 is not None:
        if zeige_highlight:
            try:
                tex1 = _zerlegt_farbig(
                    ausdruck, lambda t: sp.diff(t, x, 1), vereinfachen
                )
                st.latex(r"f'(x) \;=\; " + tex1)
            except Exception:
                st.latex(r"f'(x) \;=\; " + sp.latex(abl1))
        else:
            st.latex(r"f'(x) \;=\; " + sp.latex(abl1))
    else:
        st.error(f"f ′(x) konnte nicht berechnet werden: {err1}")

    st.markdown("**Zweite Ableitung — f ″(x)**")
    if abl2 is not None:
        if zeige_highlight:
            try:
                tex2 = _zerlegt_farbig(
                    ausdruck, lambda t: sp.diff(t, x, 2), vereinfachen
                )
                st.latex(r"f''(x) \;=\; " + tex2)
            except Exception:
                st.latex(r"f''(x) \;=\; " + sp.latex(abl2))
        else:
            st.latex(r"f''(x) \;=\; " + sp.latex(abl2))
    else:
        st.error(f"f ″(x) konnte nicht berechnet werden: {err2}")

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Integral
# ─────────────────────────────────────────────
if zeige_int:
    st.markdown(
        '<span class="sec-header int">∫ Unbestimmtes Integral</span>',
        unsafe_allow_html=True,
    )

    integral, err_int = sicheres_integral(ausdruck, vereinfachen)

    st.markdown('<div class="int-block">', unsafe_allow_html=True)
    if integral is not None:
        if zeige_highlight:
            try:
                tex_int = _zerlegt_farbig(
                    ausdruck, lambda t: sp.integrate(t, x), vereinfachen
                )
                st.latex(r"\int f(x)\, dx \;=\; " + tex_int + r" \;+\; C")
            except Exception:
                st.latex(r"\int f(x)\, dx \;=\; " + sp.latex(integral) + r" \;+\; C")
        else:
            st.latex(r"\int f(x)\, dx \;=\; " + sp.latex(integral) + r" \;+\; C")
    else:
        st.error(
            f"SymPy konnte keine geschlossene Stammfunktion finden. {err_int or ''}"
        )
    st.markdown("</div>", unsafe_allow_html=True)
