# coding=UTF-8
# ex:ts=4:sw=4:et=on

# Copyright (c) 2013, Mathijs Dumon
# All rights reserved.
# Complete license can be found in the LICENSE file.

import re
from fractions import Fraction

###############################
# Some convenience functions: #
###############################
def _handle_customs(text):
    text = text.decode('utf-8')

    if r"\larger" in text:
        fontsize = 20
    elif r"\large" in text:
        fontsize = 15
    else:
        fontsize = 10

    replacers = [
        (r"²", r"$^{2}$"),
        (r"³", r"$^{3}$"),
        (r"α", r"$\alpha$"),
        (r"β", r"$\beta$"),
        (r"γ", r"$\gamma$"),
        (r"δ", r"$\delta$"),
        (r"γ", r"$\digamma$"),
        (r"η", r"$\eta$"),
        (r"ι", r"$\iota$"),
        (r"κ", r"$\kappa$"),
        (r"λ", r"$\lambda$"),
        (r"μ", r"$\mu$"),
        (r"ω", r"$\omega$"),
        (r"φ", r"$\phi$"),
        (r"π", r"$\pi$"),
        (r"ψ", r"$\psi$"),
        (r"ρ", r"$\rho$"),
        (r"σ", r"$\sigma$"),
        (r"τ", r"$\tau$"),
        (r"θ", r"$\theta$"),
        (r"υ", r"$\upsilon$"),
        (r"ξ", r"$\xi$"),
        (r"ζ", r"$\zeta$"),
        (r"\larger", r""),
        (r"\large", r""),
        (r"\newline", r"$\newline$"),
    ]
    for val, rep in replacers:
        text = text.replace(val, rep)

    parts = text.replace("$$", "").split(r"\newline")
    while "$$" in parts: parts.remove("$$")
    return parts, fontsize

def mt_frac(val):
    val = Fraction(val).limit_denominator()
    if val.denominator > 1:
        return r"\frac{%d}{%d}" % (val.numerator, val.denominator)
    else:
        return r"%d" % val.numerator

def mt_range(lower, name, upper):
    return r"\left({ %s \leq %s \leq %s }\right)" % (mt_frac(lower), name, mt_frac(upper))

def get_plot_safe(expression):
    return r"".join(_handle_customs(expression)[0])

def get_string_safe(expression):

    replacers = [
        (r"$", r""),
        (r"\larger", r""),
        (r"\left", r""),
        (r"\right", r""),
        (r"\leq", r"≤"),
        (r"\geq", r"≥"),
        (r"\large", r""),
        (r"\newline", "\n"),
    ]
    for val, rep in replacers:
        expression = expression.replace(val, rep)

    regex_replacers = [
        (r"\\sum_\{(\S+)\}\^\{(\S+)\}", r"Σ(\1->\2)"),
        (r"(\S+)_(?:\{(\S+)\})", r"\1\2"),
        (r"(\S+)_(\S+)", r"\1\2"),
        (r"\\frac\{([^}])\}\{([^}])\}", r"\1\\\2"), # single characters
        (r"\\frac\{(.+)\}\{(.+)\}", r"(\1)\\(\2)"), # multi charachters
        (r"\(\{([^})]+)\}\)", r"(\1)")
    ]
    for regexpr, sub in regex_replacers:
        pattern = re.compile(regexpr)
        expression = pattern.sub(sub, expression)

    return expression





