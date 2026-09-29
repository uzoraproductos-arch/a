---
name: brand-book-generator
description: Generate comprehensive brand books and design guidelines from scratch through a guided interview flow. Produces three deliverables - a structured .md design guidelines document, an interactive .jsx brand book component, and a downloadable brand assets kit (ZIP with SVG logos, symbol, wordmark, and variants). Use this skill whenever the user wants to create brand guidelines, a brand book, design system documentation, visual identity guidelines, or any brand-related documentation for a new or existing project. Also trigger when the user mentions "brand book", "design guidelines", "brand guidelines", "visual identity", "design system", "style guide", or wants to document a brand's colors, typography, logo usage, voice and tone. Also trigger when the user wants to design a logo, create logo variants, improve an existing logo, generate brand assets, or create a downloadable brand kit. Works for any brand, not just specific ones.
---

# Brand Book Generator

> **En este repositorio (Auditavisión)** — estas reglas mandan sobre el resto
> del documento:
>
> 1. **Lee primero `docs/marca/BRIEF.md`.** Ahí está todo lo que ya se extrajo
>    del sitio (colores, fuentes, logo actual, voz) y las preguntas abiertas.
>    En la entrevista pregunta sólo lo que el brief marca como pendiente.
> 2. **El entregable principal es `DESIGN.md` en la raíz del repositorio**, no
>    `{brand}-design-guidelines.md`. Sigue `md-template.md`, pero los tokens
>    deben usar **los nombres de variables que ya existen** en
>    `assets/css/auditavision.css` (`--gold`, `--bg-card`, `--font-serif`…)
>    y cubrir los dos temas, oscuro y `[data-theme="light"]`. Omite la
>    configuración de Tailwind: el sitio no la usa.
> 3. Los SVG del logo van en `assets/brand/logos/{combined,symbol,wordmark}/`.
>    Las rutas `/home/claude` y `/mnt/user-data` de abajo no aplican aquí.
> 4. El brand book `.jsx` y el ZIP son opcionales: pregúntale a quien te lo
>    pidió antes de generarlos.
> 5. Documenta la marca; no reescribas el CSS ni el HTML en la misma pasada.
>    Aplicar `DESIGN.md` al sitio es un trabajo aparte.

Generate professional brand books, design guidelines, and brand asset kits through a guided discovery flow. Produces three outputs:

1. **Design Guidelines (.md)** - Comprehensive markdown reference document
2. **Brand Book (.jsx)** - Interactive React component (the brand book itself)
3. **Brand Assets Kit (.zip)** - Downloadable ZIP with all logo SVGs, variants, and brand assets

## Workflow Overview

```
Phase 1: Discovery Interview
Phase 2: Logo Design / Improvement
Phase 3: Generate Outputs (md + jsx + assets)
Phase 4: Delivery (present files + ZIP)
```

---

## Phase 1: Discovery Interview

Before generating anything, gather all brand information through a structured interview. Ask questions in batches (not all at once) to keep it conversational. Adapt based on what the user already provides.

**Batch 1: Brand Essence** (start here)

Ask about:
- Brand name (exact casing, any special characters)
- Tagline or slogan
- What the brand does (1-2 sentences)
- Positioning (what type of company/product)
- Target audience
- What the brand is NOT (anti-positioning)
- Tone descriptors (3-5 adjectives)

**Batch 2: Logo**

Ask about:
- Does the user have an existing logo? If yes, ask them to upload it (SVG, PNG, or any image)
- Do they want to improve/refine the existing logo or start fresh?
- Logo type preference: wordmark, symbol, combo mark, monogram?
- Visual style keywords (geometric, organic, minimal, bold, etc.)
- Any specific elements, shapes, or symbols to incorporate
- Special logo rules or restrictions

**Batch 3: Colors**

Ask about:
- Primary brand color(s) with hex values
- Do they have a full color scale (50-950) or just a few key colors?
- Secondary/accent colors
- Neutral palette (warm or cool?)
- Semantic colors (success, error, warning, info)
- Any color rules (what NOT to do)

If the user provides only a few key colors, offer to generate full scales using the provided colors as anchors.

**Batch 4: Typography**

Ask about:
- Primary font (display/headings) - name, weights, source (Google Fonts, custom, etc.)
- Secondary font (body/UI) - name, weights
- Mono font (if applicable) - for code, data, metadata
- Any type scale preferences
- Font pairing rules

**Batch 5: Components & Patterns** (optional, only if relevant)

Ask about:
- Button styles (primary, secondary, ghost, danger)
- Spacing system (base-4, base-8)
- Border radius preferences
- Card/container patterns
- Any specific UI components to document

**Batch 6: Voice & Tone** (optional, only if relevant)

Ask about:
- Writing principles (how the brand speaks)
- Do's and don'ts for copy
- Glossary or specific terminology
- Language preferences (formal vs casual, specific language)

---

## Phase 2: Logo Design / Improvement

This phase creates all logo assets as SVGs. There are two paths:

### Path A: Design from scratch

1. Based on the interview, propose 2-3 logo concepts as SVG artifacts
2. Each concept should include a **combined mark** (symbol + wordmark together)
3. Explain the rationale behind each concept (symbolism, geometry, brand alignment)
4. Ask the user to pick one or give feedback
5. Iterate until the user approves
6. Once approved, proceed to **Logo Variant Generation**

### Path B: Improve existing logo

1. The user uploads their current logo (image or SVG)
2. Analyze the current logo: strengths, weaknesses, alignment with brand values
3. Propose 2-3 improvement directions:
   - Refinement (small tweaks: proportions, spacing, weight)
   - Evolution (moderate changes: simplified form, updated style)
   - Reimagination (significant redesign keeping core elements)
4. Present each as an SVG artifact
5. Ask the user to pick one or give feedback
6. Iterate until the user approves
7. Once approved, proceed to **Logo Variant Generation**

### Logo Variant Generation

Once the base logo is approved, generate the full set of SVG variants:

**Logo Types:**
1. **Combined Brand Mark** - Symbol + wordmark together (horizontal lockup)
2. **Symbol / Icon** - The icon/symbol alone
3. **Wordmark** - The text/name alone

**Color Variants for each type:**
1. **Primary** - Brand's primary color on transparent background
2. **Monochrome Dark** - Solid dark color (for light backgrounds)
3. **Monochrome Light** - Solid white/light color (for dark backgrounds)
4. **Accent variants** - If the brand has accent colors, create those variants too

**SVG Requirements:**
- Clean, optimized SVG code (no unnecessary groups, transforms, or metadata)
- Consistent viewBox across variants of the same type
- Use `fill` attributes with hex colors (no classes or external stylesheets)
- No text elements (convert all text to paths for the wordmark)
- Maintain consistent proportions and spacing across all variants

**Naming Convention:**
```
{brand}-combined-{color}-{bg}.svg
{brand}-symbol-{color}-{bg}.svg
{brand}-wordmark-{color}-{bg}.svg
```

Examples:
```
moffin-combined-blue-light.svg    (blue logo, for light backgrounds)
moffin-combined-white-dark.svg    (white logo, for dark backgrounds)
moffin-symbol-blue-light.svg
moffin-wordmark-blue-light.svg
```

### Logo Design Principles

When creating or improving logos as SVG:
- Use simple geometric shapes (paths, circles, rects) when possible
- Maintain optical balance (visual centering, not mathematical centering)
- Ensure the symbol works at small sizes (16x16 favicon test)
- Keep stroke counts minimal
- Test contrast: the logo must be clearly visible on both light and dark backgrounds
- The wordmark should use custom lettering as paths, not font references
- Maintain a consistent stroke weight or visual weight across all elements

---

## Phase 3: Generate Outputs

Once the interview is complete and the logo is approved, generate all three deliverables.

### 3A: Design Guidelines (.md)

Read the template structure from `md-template.md`. Follow that structure, filling in the brand's specific information. Key sections:

1. Brand Essence (positioning, tone, audience, personality)
2. Logo (usage rules, variants, clear space, sizing, file reference list)
3. Colors (full palette tables with hex values, usage guidelines, semantic mapping, color ratios, CSS custom properties, Tailwind config)
4. Typography (type system, type scale, font imports, usage rules)
5. Components (buttons, inputs, cards if applicable)
6. Voice & Tone (if applicable)
7. Do's & Don'ts
8. Quick Reference (CSS variables, Tailwind config, copy-paste ready)

**Addition for logo section:** Include a table listing all generated SVG files with their use case:

```markdown
### Logo Files

| File | Type | Color | Use |
|------|------|-------|-----|
| {brand}-combined-blue-light.svg | Combined | Primary | Light backgrounds |
| {brand}-combined-white-dark.svg | Combined | White | Dark backgrounds |
| {brand}-symbol-blue-light.svg | Symbol | Primary | Favicons, app icons |
| ... | ... | ... | ... |
```

### 3B: Brand Book (.jsx)

Read the template structure from `jsx-template.md`. The JSX brand book should be:

- A single-file React component with `export default`
- Uses `useState` for tab navigation
- Imports fonts from Google Fonts via `<link>` tag in the component
- Uses Tailwind utility classes for layout
- Inline styles for brand-specific values
- Tabbed interface with sections: Overview, Logo, Colors, Typography, Voice & Tone, Applications
- Interactive elements: color swatches with hex codes, typography previews, button previews, do/don't examples

**Logo tab enhancement:** The logo tab should embed the actual SVG code inline so the logos render directly in the brand book. Show each variant on appropriate backgrounds (light/dark).

Key patterns for the .jsx:
- Define all colors as a JS object at the top
- Create reusable sub-components: `ColorSwatch`, `Section`, and brand-specific components
- Use the brand's own fonts and colors throughout
- Sticky header with navigation tabs
- All text uses the brand's own typography
- Keep under 1000 lines

### 3C: Brand Assets Kit (.zip)

Generate a ZIP file containing all brand assets organized as follows:

```
{brand}-brand-kit/
├── logos/
│   ├── combined/
│   │   ├── {brand}-combined-primary-light.svg
│   │   ├── {brand}-combined-white-dark.svg
│   │   ├── {brand}-combined-dark-light.svg
│   │   └── {brand}-combined-{accent}-light.svg  (if applicable)
│   ├── symbol/
│   │   ├── {brand}-symbol-primary-light.svg
│   │   ├── {brand}-symbol-white-dark.svg
│   │   └── {brand}-symbol-dark-light.svg
│   └── wordmark/
│       ├── {brand}-wordmark-primary-light.svg
│       ├── {brand}-wordmark-white-dark.svg
│       └── {brand}-wordmark-dark-light.svg
├── guidelines/
│   └── {brand}-design-guidelines.md
└── README.md
```

**README.md contents:**
- Brief explanation of what's in the kit
- File listing with descriptions
- Color quick reference (hex values)
- Font names and where to get them
- Basic usage rules (do's and don'ts)

**How to create the ZIP:**

```bash
# Create directory structure
mkdir -p /home/claude/{brand}-brand-kit/logos/{combined,symbol,wordmark}
mkdir -p /home/claude/{brand}-brand-kit/guidelines

# Save each SVG variant to the appropriate directory
# (generate each SVG and write to file)

# Copy the guidelines .md
cp /home/claude/{brand}-design-guidelines.md /home/claude/{brand}-brand-kit/guidelines/

# Create the README
# (generate and write README.md)

# Create ZIP
cd /home/claude && zip -r /mnt/user-data/outputs/{brand}-brand-kit.zip {brand}-brand-kit/
```

---

## Phase 4: Delivery

Present all outputs to the user:

1. **Brand Book (.jsx)** - Present first (this is the hero deliverable)
2. **Design Guidelines (.md)** - Present second
3. **Brand Assets Kit (.zip)** - Present last with download link

```
Files delivered:
1. {brand}-brand-guidelines.jsx  (interactive brand book)
2. {brand}-design-guidelines.md  (reference document)
3. {brand}-brand-kit.zip         (all logo SVGs + guidelines)
```

Offer to iterate on any specific section, logo variant, or color.

---

## Important Rules

1. Never invent brand information. If something is missing, ask.
2. Always use the brand's exact color hex values. Don't approximate.
3. If the user provides reference files (existing brand materials), extract info from those first and only ask about gaps.
4. The .jsx must be a complete, self-contained React component that renders in Claude's artifact viewer.
5. The .md should be comprehensive enough to serve as a standalone reference.
6. Both document outputs should be consistent with each other.
7. Adapt the level of detail to what the user provides.
8. All SVGs must be clean, optimized, and use only `fill` with hex values.
9. The ZIP must contain ALL generated SVG variants, organized by type.
10. Logo proposals should always be presented as rendered SVG artifacts so the user can see them immediately.
11. During logo iteration, always ask for explicit approval before moving to variant generation.
12. If the user's existing logo is already strong, say so. Don't force changes.

## Reference Files

- `md-template.md` - Structure and section guide for the markdown output
- `jsx-template.md` - Architecture and patterns for the React brand book
