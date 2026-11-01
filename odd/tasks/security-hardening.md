# Security hardening (post-audit) — fix/security-hardening

Audit found public write endpoints, broken signup, email-triggered moderation, CSRF bypasses and racy counters. User approved the six security fixes, removal of public problem/solution creation, and removal of the Gemini generation feature for now.

## Specs

- S1: "por ahora bloquea al publico la creacion de problemas y de soluciones" — no anonymous request may create Problem or Solution rows. The `/json/` import endpoint is removed entirely ("quitamos el problema").
- S2: "haz el commit de limpieza" — normalize line endings, untrack staticfiles/ and media/.
- S3: "crea el venv" — project has no local Python environment (was developed on another machine); create `.venv` and install requirements.txt + sentence-transformers (missing from requirements).
- S4: signup activation: `is_active=False` users currently can never activate (token unused, mail sent to the admin). Add email-to-user activation with expiring signed token.
- S5: moderation: accept/reject of solutions moves from emailed GET links to Django admin actions; the email becomes notification-only (email preview clients auto-follow GET links and trigger unintended accept/delete).
- S6: solution submissions gain login + rate limit (cache-based, noted per-process limitation).
- S7: `@csrf_exempt` removed from Like/toggle endpoints (templates already send the X-CSRFToken header).
- S8: `likes_count` increments become atomic with `F()` expressions.
- S9: "la ia de gemini haciendo problemas no... lo puedes quitar por ahora, no lo usare, esto en otro commit" — remove Gemini problem generation (Training views, admin AI button, geminitest.py, google-genai dependency), keep the rest of Training.

## Tasks

- T1 (S2) cleanup commit — done: 85b1f20
- T2 (S1) Fix 1: remove `/json/` view + route — commit: (pending)
- T3 (S4) Fix 2: email activation for signup — commit: (pending)
- T4 (S5) Fix 3: moderation actions in admin, notification-only email — commit: (pending)
- T5 (S6) Fix 4: login_required + rate limit on solution submit — commit: (pending)
- T6 (S7) Fix 5: remove csrf_exempt — commit: (pending)
- T7 (S8) Fix 6: atomic likes_count — commit: (pending)
- T8 (S9) Fix 7: remove Gemini generation — done: 15239d9 (Training rewritten without AI views/routes, ai_button.html + geminitest.py deleted, google-genai/GEMINI_API_KEY dropped). Leftover commented Create_Problem mention in bundle_interface.html is inside a broken HTML comment, inert.
- T9 (S3) venv + verification — done: .venv ready with requirements + sentence-transformers + pillow (pinned, commit 96bb192 incl. menus/treebeard removal); manage.py check clean. manage.py test still blocked: no local Postgres at localhost (connection refused), no Docker daemon on this machine.

## Log

- L1 (user): "haz un audit al proyecto y busca fallos. la idea es cambiarlo para que sea un sistema abierto y gratis para practicar problem solving en matematicas. cero anuncios y mierdas, pwro primero el audit"
- L2 (user): "ok, lo fix de seguridad me parecen bien. primero dine esto: el worktree esta limpio? y explicame e ... y explicame los fixes, que el codigo es mio pero hace un año casi que no lobtoco"
- L3 (user): "haz el commit de limpieza, crea dl venv, que no tengo aqui, yo antos programaba en otra maquina y haz los fixes. por ahora bloquea al publico la creacion de problemas y de soluciones, quitamos el problema y ya se hara algo cuando sepamos la difeccion que quiero gomar con el proyecto vale?"
- L4 (user): "otra cosa, la ia de gemini haciendo problemas no, seguramente acabe usando algo de openrouter con openai sdk, lo puedes quitar por ahora, no lo usare, esto en otro commit"
