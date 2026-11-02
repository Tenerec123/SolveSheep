Objective: Refresh SolveSheep with the approved warm-workshop visual system, dark mode, problem-status/skill surfaces, and a contained native-masonry enhancement.
Branch: `feature/workshop-ui-refresh` | Delivery: `feature-branch-chain` | Forecast: ~550 authored changed lines; slice work into reviewable commits on this feature branch.
Runner: `python manage.py test` (PostgreSQL with pgvector and project environment required; availability to be checked).

## Specs

### S1 — Warm workshop and dark theme
User direction: “me gusta el taller calido, pero quiero que haya dark mode, donde podria entrar el modo observatorio o si eso es jodido haz sencillamente taller dark.”
Theme requirements: “Use a persistent theme toggle with the OS setting as the default and honor reduced-motion preferences; keep keyboard access.” Dark/light appearance must not change login behavior, search behavior, or authentication logic. Keep the login form and auth flows untouched. Persist only the theme preference locally; default to the OS color preference when no saved choice exists.
Checks: theme toggle is keyboard operable and announces its state; saved selection survives reload; unsaved selection follows `prefers-color-scheme`; reduced-motion is respected.

### S2 — Native masonry, only if contained
User instruction: “Migrate to native CSS masonry only if the change stays contained; if it would alter layout behavior app-wide, skip it and tell me why.”
Apply native CSS Grid Lanes only inside the existing card-grid component and only with a graceful fallback preserving usable ordered cards in unsupported browsers. If this cannot be contained to card-grid presentation, leave current masonry behavior in place and record why.
Checks: supported and fallback layouts keep all cards visible, responsive, and usable with keyboard navigation; MathJax/image height changes do not break the fallback.

### S3 — Status and skill surfaces without fabricated progress
User instruction: “Add the problem-status and profile-skill views to the interface, reusing current difficulty/topic tags; don't create new backend taxonomy or database migrations.”
Use the already existing difficulty and topic tags. Do not add models or migrations. Display only progress/skill information that existing persisted data can substantiate; use a truthful empty/limited-data presentation for untracked attempts and accuracy rather than inventing per-user outcomes.
Checks: accepted authored solutions can be distinguished using existing data; untracked pending/abandoned states and skill accuracy are not presented as persisted facts.

### S4 — Training intent and hints scope
Original user request: “Tambien en training cambiarlo, un sistema de pedir un problema. se queda en pending hasta que lo resuelvas o te rindas. tambien en training los bundles de hasta ahora, pero tipo creados automaticos segun tags internas especificas.”
The interface should present the active-problem/pending idea and existing training bundles using current tags. Hints remain future work: “vi la solucion podria ir en el futuro cuando metamos hints, tpo ir de hint en hint y cuando ya no queden le preguntas al usuario si entiende la solucion, si ni siquiera la entiende es que era too much, pero eso en un futuro”. Do not imply state is persisted where the current data layer cannot persist it.

### S5 — Search semantics and untouched auth
User instructions: “Please keep auth flows untouched.” “Keep search semantics unchanged.” “Dark/light mode can affect appearance but should not change login behavior, search behavior, or auth logic.” Preserve existing search controls, GET parameter names, and filtering behavior; do not edit authentication behavior or forms.
Checks: compare the existing search form/filter names and route flow before/after; login/register/activation routes and view behavior remain unchanged.

## Tasks
- T1 — Create and mirror this feature plan; link S1–S5; inline; done; commit: none.
- T2 — Implement shared theme tokens/toggle and contained native-masonry enhancement in the shared card grid; S1, S2, S5; theme writer plus parent inline on disjoint surfaces; in_progress; commit: pending.
- T3 — Evaluate native masonry separately; S2; inline; dropped because its scoped implementation is part of T2's shared card-grid presentation; commit: none.
- T4 — Restyle training/profile/status/skill surfaces using available data only; S3, S4; inline; pending; commit: pending.
- T5 — Preserve search/auth behavior and run applicable tests plus responsive/accessibility checks; S1–S5; inline; pending; commit: pending.

## Log
- L1 — User's original request: “hola, ya tengo mas o menos la web en mvp, funcionar funciona, pero le falta rating y otras cosillas. hay info de engram de eso. primero ideemos la interfaz. el estilo ahora es tipo bootstrab normalorro en blanco, que no es feo del todo pero es algo soso. Se me ocurre que hay que cambiar algunas cosas. Te digo: los problemas deberian estar clasificados para cada usuario en resueltos, no resueltos, pendkentes o mire la solucion/me rendi. segun eso un color de la ui. en el profile deberia haber la tipica telaraña de habilidad dependiendo de la dificultad y accuracy para resolver problemas de ciertos tipos/skills de mates tipo abstraccion, generalizacion, invariante etc. Tambien en training cambiarlo, un sistema de pedir un problema. se queda en pending hasta que lo resuelvas o te rindas. tambien en training los bundles de hasta ahora, pero tipo creados automaticos segun tags internas especificas. login y eso igual y el searcher tambien igual creo. Por ahora solo ui. Con rsto y engram cuestioname estas ideas si algo no te cuadra y cuando lo tengamos organizamos el desarrollo”
- L2 — User correction, 2026-11-02: “vi la solucion podria ir en el futuro cuando metamos hints, tpo ir de hint en hint y cuando ya no queden le preguntas al usuario si entiende la solucion, si ni siquiera la entiende es que era too much, pero eso en un futuro, como dices esta ok. lo demas estoy de acuerdo, antes de que te pongas dime el estilo visual que podriamos poner, que xolores, que diseño? eso es igual de importante”
- L3 — User visual direction, 2026-11-02: “me gusta el taller calido, pero quiero que haya dark mode, donde podria entrar el modo observatorio o si eso es jodido haz sencillamente taller dark. Por coerto, las cards de problemas usan masonry, han metido masonry nativo, las puedes migrar. ya te puedes poner a ello?”
- L4 — User implementation constraints, 2026-11-02: “Sounds good; you're free to choose between a dark observatory variant or warm-workshop dark mode. Please keep auth flows untouched. After opening the design, inspect templates and existing styles, and determine whether the requested front-end work is small or broad. If small, implement it inline. If broad, track it with your standard plan before code changes.

Migrate to native CSS masonry only if the change stays contained; if it would alter layout behavior app-wide, skip it and tell me why. Add the problem-status and profile-skill views to the interface, reusing current difficulty/topic tags; don't create new backend taxonomy or database migrations. Keep search semantics unchanged. Dark/light mode can affect appearance but should not change login behavior, search behavior, or auth logic.

Use a persistent theme toggle with the OS setting as the default and honor reduced-motion preferences; keep keyboard access.

While you work, check that the visible todo list still matches and update it if it doesn't. Tell me if the work stays small or needs tracking and show the current plan.”
- L5 — Exploration: this is broad, not small. Global style rules are inline in `MainApp/templates/base.html`; card masonry is shared through `MainApp/templates/masonry_grid_system.html` and `MainApp/templates/grid_display.html`. `Problem` has `type_tags` and `dif_tag`; `Solution` has `accepted` and `author`, but there is no per-attempt state, rejection/pending distinction, or skill-accuracy record. Profile heatmap currently uses random client-side values. Therefore derive only accepted-solution signals and show an honest no-data state for untracked statuses/accuracy; no migrations or fake counts.
- L6 — Design artifact: `design/solvesheep-workshop/` contains three concept boards and a manifest. The canvas URL is available, but the environment could not launch the browser because `xdg-open` is unavailable. User approved proceeding from the direction. The initial feature-size estimate exceeds 400 authored lines; the delivery-slice choice is recorded in L13.
- L7 — User authorized production UI work on 2026-11-02 with auth flows and search semantics unchanged, no new taxonomy or migrations, local persistent theme preference defaulting to OS preference, keyboard access, and reduced-motion support. Branch `feature/workshop-ui-refresh` was created from `main` before source edits. Exploration confirms the work is broad and must be tracked.
- L8 — Gentle Design handoff selected `design/solvesheep-workshop/01-training.html` as the implementation's visual reference; profile and search boards are companion page compositions in the same system. The handoff requires mapping the artboard to existing Django components (not copying its standalone HTML).
- L9 — Native masonry is being isolated to Search results only via a template context flag, since the existing wrapper also serves home, training, bundle, and profile grids. Other pages must retain their exact prior measured-JS behavior; Search uses the native `@supports (display: grid-lanes)` path only when available and otherwise keeps the legacy fallback.
- L10 — Updated all concept-board theme controls to default to the OS preference and persist manual selection in local storage, matching the newly authorized theme behavior. Canvas refresh returned the same URL; automatic browser launch still fails because `xdg-open` is unavailable.
- L11 — Theme writer completed the shared shell, semantic tokens, local/OS theme selection, accessible toggle, and reduced-motion CSS on its allowed files. RED was observed for the new public-template wiring test; GREEN and the preserved removed-endpoint test both passed with `.venv/bin/python manage.py test MainApp.tests.ThemeFoundationTests MainApp.tests.RemovedEndpointsTests -v 2` (2 tests). Parent review found the native-masonry fallback must remain unchanged for all non-Search consumers.
- L12 — Parent aligned production tokens to the artboards, limited native Grid Lanes to Search via `native_masonry=True`, restored the original measured-JS fallback for every other grid (and Search when unsupported), converted existing tag chips to theme-aware accessible pills, and ran `git diff --check` plus the same two focused Django tests successfully. Feature forecast remains above 400 authored changed lines; T2's implementation is ready for its work-unit boundary.
- L13 — User selected `feature-branch-chain` on 2026-11-02. Work-unit commits may be sliced on `feature/workshop-ui-refresh`; this does not authorize push, PR creation, or merge.
