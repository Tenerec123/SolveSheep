import re
from django import template

register = template.Library()


# Captura bloques latex: $...$, $$...$$, \(...\), \[...\]
LATEX_PATTERN = re.compile(
    r"(\${1,2}.*?\${1,2}|\\\(.*?\\\)|\\\[.*?\\\])",
    re.DOTALL
)

@register.filter
def latex_truncate(text, max_words=30):
    if not text:
        return ""

    # 1. Extraer bloques LaTeX
    blocks = LATEX_PATTERN.findall(text)

    # Insertamos marcadores temporales
    clean_text = LATEX_PATTERN.sub("<<<LATEX>>>", text)

    # 2. Truncar solo texto plano
    words = clean_text.split()
    if len(words) <= int(max_words):
        return text  # no truncar

    truncated = " ".join(words[:int(max_words)]) + " …"

    # 3. Restaurar bloques LaTeX uno por uno
    for block in blocks:
        truncated = truncated.replace("<<<LATEX>>>", block, 1)

    return truncated
