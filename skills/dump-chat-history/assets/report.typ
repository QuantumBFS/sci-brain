// Copy beside history.json; compile with: typst compile report.typ report.pdf
#let report = json("history.json")
#let sans = ("Avenir Next", "Libertinus Serif")
#let serif = ("Charter", "Libertinus Serif")
#let mono = "DejaVu Sans Mono"
#let ink = rgb("24282b")
#let muted = rgb("63707b")
#let rust = rgb("ae501b")
#let teal = rgb("22616a")
#set document(title: report.title, description: "Conversation history field note")
#set page(paper: "a4", margin: (x: 23mm, y: 20mm), footer: context {
  set text(font: sans, size: 8pt, fill: muted)
  [#report.title #h(1fr) #counter(page).display()]
})
#set text(font: serif, size: 10pt, fill: ink)
#set par(leading: 0.45em, spacing: 0.7em)
#show heading: set text(font: sans, weight: "semibold")
#show heading.where(level: 1): set text(size: 14pt)
#show raw: set text(font: mono, size: 8.7pt, hyphenate: false, ligatures: false)
#show raw.where(block: true): set block(width: 100%, fill: rgb("f2f3f4"), inset: 7pt, radius: 2pt, breakable: true)

#text(font: sans, size: 8pt, tracking: 1pt, fill: rust)[CONVERSATION FIELD NOTE]
#v(7pt)
// The topic is the title. Counts belong in metadata, never the headline.
#text(font: sans, size: 27pt, weight: "bold", report.title)
#v(7pt)
#text(size: 12pt, report.at("subtitle", default: ""))
#v(8pt)
#text(font: sans, size: 9pt, fill: muted)[
  #report.window.start – #report.window.end · #report.window.timezone
]
#v(5pt)
#report.scope
#v(5pt)
#report.coverage

= Transcript
#let visible = report.entries.filter(e => e.at("include_in_report", default: e.role == "user"))
#for entry in visible {
  let phase = entry.at("phase", default: none)
  if phase != none {
    block(width: 100%, fill: rgb("f6f3ef"), radius: 3pt, inset: 10pt, breakable: false)[
      #text(font: sans, weight: "semibold", phase)
    ]
  }
  // Long prompts and answers may flow across pages; never shrink or truncate them.
  block(width: 100%, inset: (left: 9pt), stroke: (left: 2pt + teal), breakable: true, above: 8pt, below: 9pt)[
    #block(sticky: true)[#text(font: sans, size: 8pt, fill: muted)[
      #entry.id · #entry.source · #entry.session_id · #entry.role · #entry.kind
      #if entry.at("branch_id", default: none) != none [ · branch #entry.branch_id]
      #if entry.at("outside_window", default: false) [ · context outside selected dates]
      #linebreak()
      #if entry.timestamp == none { [Time unavailable] } else { entry.timestamp }
    ]]
    #if "question" in entry {
      block(stroke: (paint: rgb("cdd4d9"), dash: "dashed", thickness: 0.5pt), inset: 7pt)[
        #text(font: sans, size: 8pt, fill: muted, entry.question)
      ]
    }
    // Treat strings as literal text. Do not eval markup, replace quotes, or hyphenate.
    #raw(entry.text, block: true)
    #if "attachment_note" in entry { text(font: sans, size: 9pt, fill: muted, entry.attachment_note) }
    #if "annotation" in entry {
      text(size: 9.5pt)[#text(fill: rust)[▸] #entry.annotation]
    }
    #text(font: sans, size: 7pt, fill: muted)[Source: #entry.provenance]
  ]
}

#if report.at("analysis", default: "") != "" [
  = Observations
  #report.analysis
]

= Sources and limits
#for source in report.sources [
  #block(breakable: true, above: 5pt)[
    #text(font: sans, size: 9pt, weight: "semibold", source.id)
    #linebreak()
    #raw(source.location, block: true)
    #source.at("note", default: "")
  ]
]
#report.at("method", default: "Original message strings are stored in history.json. The PDF wraps text for reading; annotations are separate from the transcript.")
