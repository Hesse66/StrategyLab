---
name: codex-design
description: Use this workflow when a project needs a distinctive real frontend generated directly from a backend-first brief, either for a new app with no frontend or for an existing app whose frontend should be replaced without breaking backend contracts.
version: 1.1
---

# Codex Design Workflow

This process separates backend truth from frontend design execution.

Use it when Codex can build, inspect, or preserve the backend, but a frontier design model such as Gemini or Opus should create the strongest possible interface direction. The goal is not to ask a model to "make the UI better." The goal is to give it a backend-only product brief, production-quality reference screenshots, and have it produce the real frontend files while preserving every working contract.

## When To Use

Use this workflow for:

- A new backend-first app where the frontend is empty, placeholder, or intentionally thin.
- An existing app with working backend/state/API logic but a weak, generic, confusing, or overgrown frontend.
- A product where the frontend should feel like the product's world or tool, not like an LLM chat, SaaS dashboard, or template.
- A project where preserving event handlers, state shape, storage, routes, API calls, tests, and backend behavior matters more than preserving current markup.

Avoid this workflow when the user only needs a small component patch, a style tweak, or a direct bug fix.

## Core Principle

The design model gets creative freedom over experience, hierarchy, composition, typography, interaction feel, and visual language.

Codex keeps ownership of production correctness: contracts, state wiring, tests, server routes, persistence, accessibility checks, scrolling, responsive behavior, and integration repairs.

Do not let a creative frontend pass silently rewrite backend semantics. Treat the backend as the truth unless the user explicitly asks to change it.

## Roles

Codex should:

- Extract the backend-only product brief.
- Identify contracts that must survive.
- Generate or curate reference screenshots for the most important screens when image generation is available.
- Prepare prompts for the design model.
- Integrate the returned files into the real codebase.
- Run tests and browser smoke checks.
- Repair integration seams.
- Remove machine-facing language from normal user surfaces.

The design model should:

- Produce a distinctive interface concept.
- Organize the full user experience, not just isolated screens.
- Use the reference screenshots as production-quality direction, not as rigid pixel-perfect targets.
- Create complete production frontend files for the requested app.
- Preserve declared contracts during the integration pass.
- Avoid generic "clean modern" defaults unless the project specifically calls for them.

## Phase 1: Build Or Extract The Backend Brief

For a new project, implement or define the backend first. Keep the frontend empty, minimal, or deliberately throwaway. The backend can be actual code, API documentation, state schemas, domain objects, or a precise technical plan.

For an existing project, inspect the app and ignore the current frontend's visual choices unless the user says a specific piece must remain. Extract what the app does, what state exists, what actions users can take, what screens are required, and what contracts the frontend must call.

Keep all design-related source-of-truth files in a dedicated `design/` folder inside the app file system. Prefer one canonical `design/DESIGN.MD` that follows the DESIGN.md format over scattered files.

Create a backend-only brief with this structure:

```md
# ONLY-BACKEND

## Product
- App name:
- One-sentence purpose:
- Primary users:
- Core user loop:
- What this must feel like:
- What this must not feel like:

## Domain Concepts
- Main entities:
- State objects:
- Lifecycle or phases:
- Success/failure conditions:
- External services or files:

## Screens / Modes
1. Screen name
   - Purpose:
   - State shown:
   - User actions:
   - Backend calls/events:
   - Empty/loading/error states:

## Contracts To Preserve
- Routes:
- API endpoints:
- Storage keys:
- Event attributes or handlers:
- Form/input identifiers:
- Component props:
- Data schemas:
- Functions that must not be removed:

## UX Rules
- What the user should always know:
- What should be hidden from normal users:
- What is optional vs primary:
- What must happen automatically:
- What requires confirmation:

## Visual North Star
- Physical or emotional metaphor:
- Palette:
- Typography:
- Texture/material:
- Motion:
- Layout constraints:
- Accessibility constraints:

## Non-Goals
- Do not build:
- Do not expose:
- Do not imitate:
```

For apps powered by LLMs, explicitly separate normal user experience from debug experience. Normal screens should use product language. Debug screens may show prompts, JSON, model routes, logs, repairs, and configuration.

## Phase 2: Generate Reference Screenshots

Before asking a frontend model to write real files, generate a compact set of production-quality reference screenshots for the most important screens or sections. This replaces HTML or Markdown visual references. The references should show the desired UX feel, information architecture, visual density, material language, and interaction hierarchy.

If image generation is available, this step is almost mandatory. If it is not available, proceed with the written backend/design brief and let the frontend model create the visual direction directly.

Generate references from the same constraints used in the frontend prompt:

- The backend-only brief.
- tokens and design rationale (ui-looks & ux-feels).
- Local frontend rules such as in "Frontend principles"
- The product's UX feel, UI design system (with a clear design style), and product experience rules.
- The blacklist of generic solutions: generic card grids, safe SaaS dashboards, purple gradients, chat wrappers, centered template heroes, and "clean modern" defaults.
- Accessibility and implementation constraints: readable text, clear hierarchy, realistic responsive surfaces, focusable controls, and no impossible layouts.

Recommended reference set:

- One screenshot for each primary screen or mode.
- One screenshot for the densest workflow.
- One screenshot for a debug/admin surface if the product has one.
- One mobile or narrow-layout reference when responsive behavior is high-risk.

For a seven-screen app, create references like:

- `design/references/page1.png`
- `design/references/page2.png`
- `design/references/page3.png`
- `design/references/page4.png`
- `design/references/page5.png`
- `design/references/page6.png`
- `design/references/page7.png`

Reference screenshots should look like plausible app screenshots, not loose concept art. They should contain perfect text, the layout, visual language, and screen purpose must be clear enough for a frontend model to implement.

Use a prompt like this for each screen:

```md
Create a production-quality app screenshot reference for this screen.

This is a visual reference for a frontend implementation model, not production code and not a standalone mock. The screenshot should communicate layout, UX hierarchy, visual style, density, materiality, and interaction feel.

Product:
[PASTE PRODUCT SUMMARY]

Screen:
[SCREEN NAME AND PURPOSE]

Backend/state this screen must support:
[PASTE SCREEN-SPECIFIC STATE, ACTIONS, EMPTY/LOADING/ERROR STATES]

Design system:
[PASTE RELEVANT SUMMARY OR TOKENS]

Frontend principles:
- Avoid generic card grids, SaaS dashboards, chat layouts, purple gradients, glassmorphism, and "clean modern" defaults.
- Commit to one distinctive aesthetic stance that fits the product.
- Make the screen feel immediately recognizable and usable.
- Keep text readable and controls plausible for HTML/CSS implementation.
- Do not invent backend behavior that does not exist.

Output:
- One high-fidelity screenshot-style image.
- No browser chrome unless requested.
- No explanatory annotations.
```

After generating references, select the strongest images and include them directly in the frontend-model prompt as visual references. Do not ask the frontend model to recreate them pixel-perfectly. Ask it to implement the same product logic, hierarchy, and design quality in real files.

## Phase 3: Direct Frontend Generation Prompt

Always generate the real frontend files directly. Do not ask for static mocks, standalone demos, prototype HTML, or fake interaction sandboxes. The design model should receive a strong backend brief, design rules, and the generated reference screenshots, then output the actual files Codex will integrate.

Use a prompt like this:

```md
IMPORTANT: be diligent and comprehensive. Do not produce a generic frontend.

Design and implement the real frontend for the following backend description.

This is not a standalone mock. Modify or output the real frontend files listed below. The backend/state/API logic already works or is already specified. Your job is to build the frontend and UX around that backend.

Do not create:
- A static mock.
- A standalone demo.
- A separate prototype HTML.
- Fake replacement logic that bypasses the backend.
- A visual-only design that cannot be wired to the existing contracts.

Frontend files to produce or replace:
[LIST EXACT FILES, for example index.html, src/js/app.js, src/css/tokens.css, src/css/layout.css, src/css/components.css]

Preserve these contracts:
- Existing event contracts:
- Existing data attributes:
- Existing form/input identifiers:
- Existing route/view identifiers:
- Existing functions and exports:
- Existing storage keys:
- Existing API calls:
- Existing tests:

Follow these frontend principles:
- First identify and avoid high-probability generic solutions: default system fonts, Inter/Roboto/Open Sans as the whole identity, purple gradients, centered SaaS heroes, generic card grids, stock dashboard layouts, evenly safe palettes, and anything describable only as "clean and modern."
- Commit to a distinctive aesthetic stance that is defensible for this product.
- Make the interface memorable through typography, color, spatial composition, materiality, and purposeful motion.
- Keep accessibility non-negotiable: keyboard navigation, focus states, semantic HTML, contrast, responsive behavior, and reduced-motion support.
- Every visual decision should help the product feel clearer, more usable, or more emotionally correct.

Define the frontend from these design inputs:

## UX Feel
[Describe how the app should feel in use. Examples: physical tabletop, action cockpit, calm professional workbench, dense trading terminal, studio instrument, editorial archive, tactical game board.]

## UI Design System
[Describe materials, palette, typography, density, component geometry, motion, icon style, layout rhythm, and what generic patterns to avoid.]

## Product Experience Rules
[Describe what should be obvious, what should be hidden, what should happen automatically, what should require user choice, and what language should be removed from normal user surfaces.]

Use these generated reference screenshots as design direction, not as rigid pixel-perfect targets:
[ATTACH OR LINK GENERATED SCREEN REFERENCES, WITH ONE-LINE PURPOSE FOR EACH]

Now review this backend-only brief and create the frontend:

[PASTE ONLY-BACKEND]

Deliverable:
- Real frontend files, not a mock.
- Preserve the product logic and contracts while implementing the reference screenshot quality and screen hierarchy.
- If using Gemini or another model with tight output limits, split into turns:
  1. HTML and CSS files.
  2. JS/render layer.
  3. Focused repair pass if needed.
- If using Opus or another model with enough output budget, produce all files in one pass.
- Represent all major screens and core flows.
- Do not create a chat app unless the product is truly a chat app.
- Do not expose developer/debug controls in normal user screens.
- Keep debug/log/model details only in developer/admin screens.
```

Evaluate the generated frontend visually and functionally before accepting it. Look for:

- Does it feel specific to this product?
- Can the user understand the main loop without backend knowledge?
- Are primary actions obvious?
- Are debug/admin surfaces visually separated?
- Is the interface memorable after a short glance?
- Does it preserve the stated backend contracts?

If the frontend is generic, ornamental, or contract-breaking, ask for a targeted repair pass before doing manual cleanup.

## Phase 4: Codex Integration

A generated frontend file set is still not guaranteed production-ready. It may have fake assumptions, broken scroll behavior, missing dynamic states, or renamed selectors. Codex must integrate and verify it against the actual app.

Checklist:

- Apply changes with scoped patches.
- Preserve backend files unless a frontend contract requires a small adapter.
- Confirm imports, scripts, and asset paths still resolve.
- Run syntax checks.
- Run unit tests.
- Start the local server if the app needs one.
- Use a browser to smoke-test the real app, not only static screenshots.
- Navigate every major screen.
- Exercise at least one complete happy path.
- Exercise one empty state and one error/debug state.

For browser smoke tests, always verify:

- The page can scroll where content exceeds the viewport.
- Fixed headers, command bars, and panels do not trap content.
- Text does not overlap.
- Buttons retain stable size and clear focus states.
- Dynamic content rendered by the real app has matching CSS.
- Mobile and desktop layouts both remain usable.
- Console errors are absent or understood.

## Phase 5: Integration Seams To Repair

Expect seams. The generated files usually cover the intended screens, while the real app has dynamic content, edge states, and runtime constraints.

Common seams:

- `overflow: hidden` prevents scrolling after a full-screen design is mapped into a content-heavy app.
- Main components are styled, but real dynamic classes are not.
- Data attributes or handler selectors were renamed.
- Forms look correct but no longer update state.
- Buttons are visually present but not wired.
- Debug surfaces leak machine language into normal screens.
- Empty/loading/error states fall back to unstyled browser defaults.
- Responsive layouts collapse into a single unreadable column.
- Fixed bottom command bars cover content.
- Generated content is longer than the design assumptions and breaks panels.
- External links, import/export, save, or file maintenance screens were omitted.

Repair these in Codex, using the existing backend behavior as the source of truth.

## Two Standard Paths

### Path A: New Backend-First Project

1. Define or implement backend/state/API/contracts.
2. Keep frontend minimal.
3. Write `ONLY-BACKEND`.
4. Include a visual north star if the product needs a strong world, brand, or material feel.
5. Generate reference screenshots for the main screens when image generation is available.
6. Ask the design model for real frontend files using the direct generation prompt and references.
7. Use Gemini in multiple turns when output is large, or Opus in one shot when feasible.
8. Integrate with Codex.
9. Test and repair seams.
10. Preserve the resulting contracts for future work.

### Path B: Existing App Frontend Replacement

1. Inspect the app and identify what already works.
2. List contracts that must survive.
3. Extract `ONLY-BACKEND` from the current backend, not from the weak UI.
4. Do not show the current UI to the design model unless the user wants specific visual continuity.
5. Generate reference screenshots for the main screens when image generation is available.
6. Ask for real frontend files that preserve real contracts and follow the references.
7. Use Gemini in multiple turns when output is large, or Opus in one shot when feasible.
8. Integrate in Codex.
9. Run tests and browser smoke checks.
10. Patch seams without changing backend behavior.
11. Only then iterate on visual polish.

## Output Artifacts

Useful artifacts for this workflow:

- `design/ONLY-BACKEND.md`: product/backend brief for the design model.
- `design/DESIGN.MD`: canonical design tokens, rationale, and guardrails.
- `design/references/*.png`: generated production-quality screen references for the main app surfaces.
- Real frontend files or patches.
- `design/integration-notes.md`: contracts preserved, seams repaired, and remaining risks.

## Quality Gate

The workflow is successful when:

- The app's backend behavior still works.
- The frontend no longer feels like a generic dashboard, chat wrapper, or model playground unless that is the actual product.
- The main user loop is clear on the first screen where it matters.
- Normal users do not need to understand prompts, model routes, JSON, or internal state machinery.
- Developer/debug surfaces still expose enough information to diagnose failures.
- The design is distinctive, but the product remains usable.
- Tests and browser smoke checks pass.
