## Step 1 — Survey (parallel exploration)

Map the landscape before any discussion. Launch N subagents in parallel. The AI selects exploration strategies dynamically based on what is known vs. unknown. First iteration is broad; later iterations focus on gaps identified in previous iterations.

**Strategy menu (AI picks from these based on iteration context):**

Each subagent uses only its **primary sources** — not all sources. This keeps each subagent fast (2-4 tool calls, not 10+).

| # | Strategy | When to use | Primary sources |
|---|----------|-------------|-----------------|
| 1 | **Landscape mapping** | First iteration default — broad field overview | Semantic Scholar (citation graph) + arxiv |
| 2 | **Adjacent subfield** | Deep-dive into a neighboring cluster identified in prior iteration | arxiv + Semantic Scholar |
| 3 | **Cross-vocabulary** | Abstract away jargon, search other fields for the same structural problem | WebSearch + paper-search-mcp |
| 4 | **Cross-method** | Same problem, different computational or experimental approaches | paper-search-mcp + arxiv |
| 5 | **Historical lineage** | Who tried before, what failed, what changed since | Semantic Scholar (citation chains) |
| 6 | **Negative results** | Search for papers showing what does not work | arxiv + WebSearch |
| 7 | **Benchmarks and datasets** | What evaluation infrastructure exists | WebSearch + arxiv |

**Available sources** (subagents pick from these — not all of them):

- **User's Zotero library** (local-first) — search the user's own paper collection. See [Zotero lookup](SKILL.md#zotero-lookup). Only available if the user granted access in Step 0 (options a/c). If the user chose (d) skip or (b) Scholar only, do not use Zotero in any survey subagent.
- **arxiv MCP** — search topic, read abstracts
- **paper-search-mcp** — PubMed, bioRxiv, CrossRef for non-CS hits
- **Semantic Scholar MCP** — citation graphs, clusters, seminal works
- **WebSearch** — blog posts, talks, open problem lists

**Abstracts first, PDFs later.** At survey stage, subagents record paper identifiers (DOI, arxiv ID) so they can be fetched later during critique (Step 3) when specific claims need verification.

Each subagent produces a **summary report** saved to `articles/iteration-N/survey/strategy-<name>.md`. The report contains:

- **Field landscape** — what was found, key papers clustered by sub-theme with publication years, active research groups, citation graph shape, temporal trends (when did activity peak? is this area heating up or cooling down?)
- **Key open problems** — what are the important unsolved questions in this area?
- **Key bottlenecks** — what specific obstacles prevent progress on those problems?
- **References** — paper identifiers (DOI, arxiv ID, title, authors, year) and BibTeX entries. No full PDFs at this stage — just enough metadata to fetch them later if needed during critique.

**Main agent reads the summaries** — not individual search results. The summaries are the interface between subagents and the main agent. If a claim seems questionable, the main agent can re-search or fetch an abstract, but this is the exception, not the default.

**Ask:** "Which directions interest you? Pick one or more." List all major findings as numbered options. The user can select multiple.

**Fetch key PDFs:** After the user picks, download full PDFs for the key references related to the selected directions (typically 3-8 papers). Use the paper identifiers (DOI, arxiv ID) collected during survey. Save to `articles/iteration-N/survey/<first-author>-<year>-<short-title>.pdf`. Read them to extract methods, results, and details that abstracts miss — this deeper understanding feeds into brainstorming.

**Survey synthesis:** Based on the user's picks and the full-paper reads, the main agent writes a single focused **survey report** in markdown — consolidating the relevant findings into one coherent narrative with inline citations. Save to `articles/iteration-N/SURVEY-REPORT.md`.
