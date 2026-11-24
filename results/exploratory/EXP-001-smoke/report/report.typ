#let horizontalrule = line(start: (25%,0%), end: (75%,0%))

#show terms: it => {
  it.children
    .map(child => [
      #strong[#child.term]
      #block(inset: (left: 1.5em, top: -0.4em))[#child.description]
      ])
    .join()
}

#set table(
  inset: 6pt,
  stroke: none
)

#show figure.where(
  kind: table
): set figure.caption(position: top)

#show figure.where(
  kind: image
): set figure.caption(position: bottom)

#let content-to-string(content) = {
  if content.has("text") {
    content.text
  } else if content.has("children") {
    content.children.map(content-to-string).join("")
  } else if content.has("body") {
    content-to-string(content.body)
  } else if content == [ ] {
    " "
  }
}
#let conf(
  title: none,
  subtitle: none,
  authors: (),
  keywords: (),
  date: none,
  abstract: none,
  cols: 1,
  margin: (x: 1.25in, y: 1.25in),
  paper: "us-letter",
  lang: "en",
  region: "US",
  font: (),
  fontsize: 11pt,
  sectionnumbering: none,
  pagenumbering: "1",
  doc,
) = {
  set document(
    title: title,
    author: authors.map(author => content-to-string(author.name)),
    keywords: keywords,
  )
  set page(
    paper: paper,
    margin: margin,
    numbering: pagenumbering,
    columns: cols,
    )
  set par(justify: true)
  set text(lang: lang,
           region: region,
           font: font,
           size: fontsize)
  set heading(numbering: sectionnumbering)

  place(top, float: true, scope: "parent", clearance: 4mm)[
  #if title != none {
    align(center)[#block(inset: 2em)[
      #text(weight: "bold", size: 1.5em)[#title]
      #(if subtitle != none {
        parbreak()
        text(weight: "bold", size: 1.25em)[#subtitle]
      })
    ]]
  }

  #if authors != none and authors != [] {
    let count = authors.len()
    let ncols = calc.min(count, 3)
    grid(
      columns: (1fr,) * ncols,
      row-gutter: 1.5em,
      ..authors.map(author =>
          align(center)[
            #author.name \
            #author.affiliation \
            #author.email
          ]
      )
    )
  }

  #if date != none {
    align(center)[#block(inset: 1em)[
      #date
    ]]
  }

  #if abstract != none {
    block(inset: 2em)[
    #text(weight: "semibold")[Abstract] #h(1em) #abstract
    ]
  }
  ]

  doc
}
#show: doc => conf(
  font: ("Libertinus Serif",),
  pagenumbering: "1",
  cols: 1,
  doc,
)


= EXP-001 smoke matrix (exploratory)
<exp-001-smoke-matrix-exploratory>
#strong[EXPLORATORY.] These are exploratory simulated runs made before
the protocol freeze. They are not findings and are never pooled with
confirmatory results.

- Generated: 2026-11-24T16:09:14.091762Z by `swarm.report` (code
  revision of the generator: 99cc0c444fdfbab6749970b92cad5ebb5c8c2841).
- Experiment: EXP-001; labels: exploratory.
- Runs: 15 recorded, 15 ok, 0 failed.
- Code revision(s) of the runs: 99cc0c444fdfbab6749970b92cad5ebb5c8c2841
  (working tree dirty: False).
- Source files: `runs/*.json` (schema 1.0.0), `metrics.csv`,
  `run_manifest.json`.

== Per-arm summary (mean, SD across seeds)
<per-arm-summary-mean-sd-across-seeds>
#figure(
  align(center)[#table(
    columns: (10%, 10%, 10%, 10%, 10%, 10%, 10%, 10%, 10%, 10%),
    align: (auto,auto,auto,auto,auto,auto,auto,auto,auto,auto,),
    table.header([cell], [arm], [runs], [phi\_pre], [phi\_post], [cohesion], [collisions
      \/agent/100 steps], [tau median
      (censored)], [evals/step], [runtime s],),
    table.hline(),
    [rho=1, eta=0.3, r=1], [A0], [5], [0.493 (0.187)], [0.544
    (0.058)], [0.750 (0.024)], [5.259 (1.298)], [1 (0)], [2156.710
    (292.320)], [1.39],
    [rho=1, eta=0.3, r=1], [A1], [5], [0.063 (0.008)], [0.064
    (0.002)], [0.149 (0.020)], [0.000 (0.000)], [108.5 (1)], [1513.600
    (78.554)], [1.79],
    [rho=1, eta=0.3, r=1], [A2], [5], [0.860 (0.001)], [0.858
    (0.000)], [0.308 (0.077)], [1.442 (0.305)], [1 (0)], [920.655
    (26.678)], [0.63],
  )]
  , kind: table
  )

== Paired differences in phi\_post (planning quantity)
<paired-differences-in-phi_post-planning-quantity>
Within-cell differences between arms for the same seed. The SD feeds the
sample-size check of `research/protocol.md` section 6. Not a test of H0.

#figure(
  align(center)[#table(
    columns: (12.5%, 12.5%, 12.5%, 12.5%, 12.5%, 12.5%, 12.5%, 12.5%),
    align: (auto,auto,auto,auto,auto,auto,auto,auto,),
    table.header([contrast], [cell], [pairs], [mean], [SD], [min], [max], [projected
      95% CI half-width, 18 cells x 10 seeds],),
    table.hline(),
    [A1-A0], [rho=1, eta=0.3,
    r=1], [5], [-0.480], [0.059], [-0.571], [-0.407], [0.009],
    [A2-A0], [rho=1, eta=0.3,
    r=1], [5], [0.315], [0.058], [0.225], [0.385], [0.008],
  )]
  , kind: table
  )

== Runtime
<runtime>
- Mean runtime per run: 1.269 s (median 1.267 s, max 2.192 s), measured
  inside the worker, single thread.
- Projection for 540 runs at this mean: 11.4 min serial, about 1.4 min
  with 8 workers (assumes linear scaling and the same per-run cost in
  every cell; a planning estimate, not a measurement).

== Figures
<figures>
#figure(image("fig01_phi_timeseries.png"),
  caption: [
    FIG-01. Polarization phi(t) (dimensionless, 0 to 1) for every seed
    (one line per seed) and arm; dotted line marks the disturbance step
    t\_d.~Exploratory simulated data.
  ]
)

#figure(image("fig02_paired_differences.png"),
  caption: [
    FIG-02. Per-seed paired differences in phi\_post (dimensionless)
    between arms within a cell, one dot per seed. Exploratory; not a
    test of H0.
  ]
)
