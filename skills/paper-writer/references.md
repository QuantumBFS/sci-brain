# Source reference material

Distilled rule lists from the two source guides that back `paper-writer/SKILL.md`. Use this when the main SKILL.md leaves a judgment call open, or when teaching a collaborator *why* a given rule exists.

---

## A. John Martinis — *Writing a Scientific Paper* (Oct. 2012)

UCSB experimental-physics group notes. Original PDF in `sources/NotesOnWritingPaper12.pdf`.

### General principles

- Break the paper into 7 sections (Title/Abstract, Intro, Theory, Methods, Results, Analysis, Conclusions). Short letters drop the explicit headers but the reader still parses these roles.
- Title + abstract is a short *advertisement* of the paper.
- A reader should get the basic idea from title + abstract + introduction + figures-and-captions + conclusions alone.
- Figures + captions must explain the work by themselves.
- Captions: concise, but define the data and summarize the graph.
- Introduce no more than one concept per sentence. If you break this rule, both concepts must be simple.
- Sequence figures, results, and explanations deliberately for clarity.
- Use references aggressively — they save you from re-deriving or re-justifying.

### §1 Title and Abstract

- Rewrite *last*, once you fully understand the experiment.
- One paragraph, 5–10 lines, roughly one sentence per body section.
- Title: descriptive.

### §2 Introduction — why should readers be interested?

- Start with the general principle being tested and why it matters to physics.
- Include history — what was done before, what you're testing newly.
- Include why it may matter for applications in science and technology.
- Start discussing the background physics of your system.
- This is the hardest section to write but the most important for acceptance.

### §3 Theory — background to understand the experiment

- State or review the minimum theory needed.
- It's fine to state assumptions and quote formulas without derivation, assuming an expert audience. Include intermediate steps only if non-trivial. Keep concise — this is an experiment, not a theory paper.
- The figure of the experiment usually goes here.
- Define terminology and variables logically (order matters: earlier symbols define later ones).
- Keep the physics basic; subtler details belong in the Analysis section.

### §4 Experimental Methods — so the experiment can be repeated

- Enough detail to reproduce, but not too much on trivial issues. (As a student, err toward "more"; the advisor will cut.)
- Be concise: state, don't explain.
- *Do* write fully about tricky, unusual, or surprising steps you needed.
- Order methods logically; build on what you've already discussed.
- Refer to the experimental sketch often; add figures/pictures if needed.
- Check every variable is defined.

### §5 Results — a sequence of graphs telling a story

- Plot *all* figures *before* writing — they are the backbone.
- Use a series of figures to tell a story, from simple data to complex analysis. Be logical in the order, building on concepts already explained.
- You don't have to show all raw data in the complex figures.
- Discuss check experiments. Use an appendix or a supplementary paper (Nature/Science/PRL space limits) if they fragment the flow.
- In the text, walk the reader through each plot: explain x-axis, then y-axis, then how data changes with x. Data is obvious to you, not them.
- After trends, discuss where errors come from and what error bars represent.
- Your data describes nature and is "correct" by itself. If it disagrees with theory, that's fine — but the more radical the result, the harder acceptance becomes.

### §6 Analysis — how the data makes theoretical sense

- Often intertwined with Results; combining them is fine, especially when a sequence of increasingly complex graphs carries the explanation.
- Convention: **data as points, theory as lines, plotted together** so the reader can immediately see agreement.
- Best when theory plots as a *straight* line — anyone can then check by eye. Curved-theory plots only with deliberate reason.
- Does theory pass through error bars?
  - Small deviations within bars: fine.
  - A few slightly outside: fine.
  - Many large deviations: discuss as possible systematic error.
  - Error bars much bigger than deviations: also discuss — you've likely underestimated errors.
- Introduce more complex theory or check theory *here*, not in §3.

### §7 Conclusions — what was learned

- Short paragraph summarizing the results.
- Optional second paragraph on applications, future directions, implications.
- Acknowledge significant help, then funding sources, in a final separate paragraph. (Funding acknowledgments are important — don't omit them.)

---

## B. Jan von Delft — *Style Guide* for scientific writing

LMU theoretical-physics group guide. Online: <https://homepages.physik.uni-muenchen.de/~vondelft/JansStyleGuide.html>

### Guiding principle

*"Only polished products sell well."* Readers expect optimized final work, not your development history. Poor presentation = audience disengages within minutes.

### Notation and equations

- **Consistency:** never reuse the same symbol for different meanings in nearby sections.
- If notation must change, *signal it explicitly* — never silent.
- Invest time early in choosing the most convenient notation. If a better choice appears mid-project, **adopt it henceforth and rewrite earlier work** rather than tolerating inconsistency.
- Reader annoyance with bad notation is a leading cause of paper abandonment.
- Compact formulas: use when explaining strategy, summarizing manipulations, when reader needs only conceptual structure, and when experts can fill in.
- Explicit (long) formulas: use for non-obvious steps, hard-won tricks, simplifications of prior expert work, key intermediates downstream work depends on, flagship results, and equations matched to plotted figures (reference the figure in the caption).
- Avoid explicit formulas that any competent reader could derive from compact ones — they waste reader attention.

### Figures — the most-remembered element

- "Figures are what most readers remember best about your paper, talk, or poster. Therefore, it pays to optimize them."
- **Design for multiple uses:** key figures must work unchanged in a talk. Build in beamer-compatibility at paper time, not later. Test on an actual projector. Test greyscale printing before submission.

#### Beamer compatibility

- **Line weight ≥ 2** for all curves (or at minimum for main results).
- **Color choice:** avoid faint colors (light yellow / green / grey). Prefer black, blue, red, dark orange, magenta, violet, dark brown.
- Distinguish curves with line *style* (solid, dashed, dash-dot) in addition to color so the figure survives greyscale.

#### Greyscale safety

- Include "(Color online)" in the caption when publishing in color.
- Refer to line *style*, not color, in captions: "the dashed line shows" not "the red line shows."
- Test actual greyscale output.

#### Legend / labeling

- Legend text and axis numbers should not be much smaller than surrounding paper body text. Maximum reduction factor 2/3.
- Place small parameter boxes (e.g., `T = 0`, `V = 0`) directly in the figure to save caption space and increase talk-suitability.

#### Dimensionless quantities (theory papers)

- Use dimensionless plots (`G/G₀`, `T/Γ`, `V_g/Γ`, ...) whenever possible:
  - generalizes the result beyond a single parameter set,
  - clarifies the relevant scale of the problem,
  - choose the dimensionless combination that *maximizes clarity of the main message*.
- If a better combination is found after plotting, redo the plot — the time is worth it.
- Exception: comparison with dimensional experimental data.

#### Critical rule

> **"NEVER, EVER, plot anything in arbitrary units!!!"** (Referenced negatively to Jan Hendrik Schön's problematic practice.)

#### Figure explanation

- Discuss and explain every important, novel, or striking feature in the text. The reader expects an explanation for unexpected peaks/dips — ideally a back-of-envelope argument.
- If you don't understand a featured element: either exclude it, or comment explicitly that it merits future investigation.

### Ten tips for *starting* paper writing

A sequence of tasks that defeats perfectionism-induced writer's block.

1. Start with **figures** — identify which figures best convey the main message. Plot them.
2. Make an **outline** — telegram-style organization plus key equations. Show to advisor; require feedback.
3. **Draft the introduction roughly.** Explain field interest, big questions, and (in accessible language) main results. For long papers, indicate where the key results / figures appear. Polish later; rough draft now to prevent paralysis.
4. **Write Section 2 carefully** — complete sentences (cannot postpone indefinitely). Writer's block usually dissolves here. Show this section to an advisor or collaborator early for style/notation/clarity feedback.
5. **Abstract and introduction refinement.** Only after the body nears final form. Polish them together.
6. **Conclusions** often restate the introduction in newly technical language — the reader now has the background.
7. **Clarify main results.** Walk the whole paper; ensure each main result has a sentence like *"This figure / equation / conclusion is our (first, second, third...) main result."*
8. **Iterate the main body extensively.** Many revision passes.
9. **Final polish on abstract / intro / conclusion.** Once more, after the body is done. "95% of all readers will read only these."
10. **External feedback.** Friends and officemates; experts in the area (most oblige if interesting; mention the submission timeline); competitors as goodwill. Take all comments seriously — unclear passages to a friend will confuse a referee.

### Theses (vs. papers — different audience)

- Papers target time-limited experts; theses target fellow grad students and professors outside your sub-field, learning from your work.
- Include more detail than papers, with pedagogical presentation: precisely what you did and how.
- Don't reproduce long textbook passages.
- Citations: precise — equation and page numbers, not "just citing a 700-page book by name."
- Summarize the key ideas behind standard methods even when not deriving them in full.
- When integrating already-published papers (which were optimized for expert readers): add introductory sections sketching background, plus technical appendices explaining details experts take for granted. Write to yourself ten years from now.

### Posters

- Function: blackboard-level prompts that *you* explain face-to-face. Not for solo reading.
- Without the speaker, viewers read only: title, sometimes abstract, "very important!" visual figures.
- Design principle: **BIG, SIMPLE, ONLY KEY WORDS, NO LONG PARAGRAPHS.**
- Include references; pin A4 copies of the poster nearby; offer preprints.

### Talks

- *Every talk is a potential job talk.* A single talk may decide a hire. Maximize quality every time.
- First-slide ideal contents (≈ 5 minutes of intro material — not the bare title-and-name slide that audiences see for 10 seconds):
  1. Title, speaker name (underlined), co-authors, collaborators.
  2. One or two beautiful motivating figures + one or two summarizing main-result figures.
  3. One-line statement of the main question.
  4. Outline of *at most* 4–5 points.
  5. One-line statement of the main result.
- Sequence: introduction first, *then* outline (so the outline lands when the audience is engaged).
- Per-slide rules:
  - One key idea per slide. The slide title names that idea.
  - One-line takeaway at the bottom, highlighted (red on yellow works).
  - Pace at 2–3 minutes minimum per slide (preferably 3–5). Rushing causes the audience to disengage.
- Figures and equations on slides:
  - Almost every slide has a figure. If you have no results figure, draw an explanatory cartoon.
  - Maximum three equations per slide.
  - Resist live derivation — "99% of the audience is lost within 10 seconds." Talks convey intuition and results, not derivations.
- References: included inconspicuously, complete (`First-author et al., PRL, 10, 193 (2000)`), and visible. People notice when they're miscited.
- Summary slide: mini-versions of main-result figures + open questions + future prospects.
- Avoid cute animations (swirling, blinking) — distracting.
- Consistent color scheme: color 1 for titles, 2 for references, 3 for formulas, 4 for main results, etc. Same fonts.
- Inexperienced speakers: type out a word-for-word script for the first few minutes (and for any delicate moments — competitor errors, inconclusive experiments). Memorize.
- Practice talks: at least one a week before. For job/invited talks, two or three.

### Structural principles (information flow)

- **Logical-linear flow.** Introduction → body → conclusions. First sections build context; later sections assume earlier material.
- **Topic-stress positioning.** Begin sections with motivation; end with main results.
- **Given-new.** Introduce notation and concepts before using them. Don't assume reader familiarity with your conventions.
- **Signposting.** Explicitly signal notation changes. State main results with "This is our main result." Use outline slides/sections.

### Sentence-level rules

- **Active over passive** where it sharpens the agent of the action.
- **Parallelism** — outline points, takeaways, lists should be grammatically parallel.
- **Avoid nominalization** — verbs over noun-phrase-of-verb. ("Adopt notation" beats "perform notation adoption.")
- **Concrete vivid verbs:** optimize, alert, adopt, iterate.

### Common mistakes (cross-reference)

- Notation: symbol reuse; tolerating bad notation; silent changes.
- Figures: thin lines; faint colors; tiny text; arbitrary units; unexplained features.
- Writing: perfectionism before drafting; polishing intro/abstract before body is drafted; no early-feedback loop; no explicit main-result statements.
- Talks: title-only first slide; outline before introduction; rushing; too many equations; inconsistent formatting; under-practice.
- Theses: copying expert paper text without pedagogical context; vague citations; failing to explain standard methods.

### Summary — core principles

1. Excellence requires sustained effort: *"only polished products sell well."*
2. Audience matters: papers serve time-limited experts; theses serve learning students; talks convey intuition and results.
3. Notation and presentation enable understanding: consistency and clarity precede correctness.
4. Visuals dominate memory: figures first, integrated everywhere.
5. Pacing permits comprehension: enough time per slide, section, equation.
6. State main results explicitly: at least one sentence per major result, clearly labeled.
7. External feedback is essential.
8. Practice and iterate: early feedback and many revision passes prevent late catastrophes.

---

## C. Model paper — Ho, Choi, Pichler & Lukin, PRL 122, 040603 (2019)

*Periodic orbits, entanglement and quantum many-body scars in constrained models: matrix product state approach.* Rendered to markdown from arXiv:1807.01815 (v2, matching the accepted manuscript) at `sources/1807.01815_Ho2019_quantum-scars.md`, supplementary material included. This letter executes the rules in sections A and B. Read it before drafting a letter, and imitate it when a style judgment call is open.

What to imitate, with locations:

- **Abstract: one move per sentence.** Four sentences: the system ("We analyze quantum dynamics of strongly interacting, kinetically constrained many-body systems"), the experimentally motivated method ("Motivated by recent experiments demonstrating surprising long-lived, periodic revivals…, we introduce a manifold of locally entangled spin states… and derive equations of motions for them"), the finding ("We find that they feature isolated, unstable periodic orbits, which capture the recurrences"), the implication ("Our results provide a theoretical framework…").
- **The four introduction beats, in order.** (a) A one-sentence field hook: "Understanding non-equilibrium dynamics in closed quantum many-body systems is of fundamental importance." (b) Prior work compressed to its role — ETH, integrable systems, many-body localization — each cited, none re-derived. (c) The gap in one explicit sentence: "However, to date, a firm connection to the theory of single-particle quantum scars [36] has not been established." (d) A contribution paragraph opening "In this Letter, we develop…" that names the method, the finding, and points at Fig. 1(a,b).
- **Run-in headers that name each section's job.** "Kinetically constrained spin models. — We consider a family of interacting, constrained spin models and demonstrate that they show atypical thermalization behavior…". The first sentence after every header says what the section will do.
- **Define at first use, then interpret in plain words.** The Hamiltonian, Eq. (1), is followed immediately by "Here, a basis on each site i is spanned by…", defining every symbol, and then by a physical reading: "The Hamiltonian (1) has a simple interpretation: each spin rotates freely about the x-axis if both its neighbors are in the state |0⟩, while its dynamics is frozen otherwise."
- **Figures carry the story from page one.** Fig. 1 contrasts the two behaviors the whole letter explains — periodic orbit vs. relaxation to a saddle point. Its caption defines the plotted quantities, names the trend, and states the extracted period.
- **Signpost words at every turn.** "Specifically," "Conversely," "Most surprisingly," "Furthermore," "therefore" — the reader always knows whether a sentence narrows, contrasts, or escalates the argument.
