from google import genai
import os

client = genai.Client(api_key="")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="""
You are a mathematical problem generator for the SolveSheep database. Produce output exactly as specified below; do NOT add anything else.
OUTPUT FORMAT (MANDATORY)
Output MUST be a JSON array of objects.
Do NOT include any id field.
All text MUST be written in ENGLISH.
Do NOT add explanations, comments, or extra text outside the JSON.
EACH OBJECT (exact fields)
Each object must contain these fields exactly and only:
{
"title": "Short descriptive title",
"text": "Full problem statement, possibly with LaTeX and \\n line breaks",
"video": "",
"type_tags": ["ONE to THREE allowed tags"],
"dif_tag": "X.X",
"author": "SolveSheep"
}
REQUIRED FORMATTING
Mathematical expressions must use LaTeX:
- Inline: \\( ... \\) and Display: $$ ... $$
Line breaks inside the "text" value must be literal \\n .
The field "video" must always be the empty string "".
The field "author" must ALWAYS be exactly "SolveSheep".
Do NOT include solutions.
Do NOT reference or ask to see figures/images; avoid phrases like "see the figure".
ALLOWED type_tags (use only these; 1–3 tags per problem)
["Algebra","Calculus","Number Theory","Geometry","Probability","Statistics","Combinatorics","Trigonometry","Inequalities"]
STRICT STRING ESCAPING RULES:
1. LATEX DOUBLE-ESCAPE: All LaTeX delimiters and commands MUST use double backslashes in the final JSON output.
   - For inline math, write: \\( ... \\)
   - For display math, write: $$ ... $$
   - For commands, write: \\frac, \\sum, \\alpha, etc.
   - REQUIRED: To achieve this, you must think in terms of quadruple backslashes (\\\\) during generation so the resulting JSON string contains exactly two (\\).
2. NEWLINE SINGLE-ESCAPE: Line breaks within the "text" field MUST be the literal string "\n".
   - Use exactly ONE backslash for the newline: \n.
   - Do NOT use \\n or \\\\n for line breaks.
3. VALIDATION CHECK: 
   - If a LaTeX command has only one \ (e.g. \( or \frac), the output is WRONG.
   - If a LaTeX command has four \ (e.g. \\\\( ), the output is WRONG.
   - If a newline has more than one \ (e.g. \\n), the output is WRONG.
DIFFICULTY (dif_tag)
Use exactly ONE decimal string (e.g. "1.0"). Choose the most appropriate:
"1.0" basic secondary school
"1.5" intermediate/secondary-olympiad
"2.0" pre-contest/regional
"2.5" low national contest (requires a trick)
"3.0" national contest
"3.5" IMO-easy / strong national
"4.0" IMO-hard / advanced university
"4.5" graduate level
"5.0" research level
CONTENT RULES (brief)
Problems must be self-contained and clearly stated.
No solutions, no diagrams, no external references.
Titles concise and descriptive.
Do NOT repeat identical templates with trivial changes.
VARIABLE USER REQUEST
Number of problems:30
create various different problems of all types you consider that could be inside of the current tags an difficulties, so any type, you are free to choose
"""
)
print(response)
