# The Human Element

A design-research study of **10,042 public security incidents**, asking a question the
breach reports mostly skip: where did the interface set the person up to fail?

Security post-mortems tend to stop at "human error" — a person clicked the wrong thing,
sent to the wrong address, left the bucket open. That is a description, not an
explanation. This study re-reads the [VERIS Community Database](https://github.com/vz-risk/VCDB)
(the open dataset behind Verizon's DBIR) as a corpus of **design failures**, classifies
them, and asks what the interfaces had in common.

Everything here is reproducible from public data with the standard library.

**→ [Read the report](https://the-human-element.netlify.app)** — the findings, with six
figures drawn from the derived data.

---

## What it found

**Organisations do not catch their own mistakes.** Of the error-caused incidents where
the discovery route is known, **78% were discovered from outside the organisation** — and
the single most common discoverer is *the customer whose data was exposed*. Compare
hacking incidents at 85% external discovery, where an adversary is actively hiding. With
self-inflicted error nobody is hiding anything, and organisations still don't see it.

**Blast radius scales with the abstraction of the interface.** Median records exposed,
by failure class:

| Failure class | Median records | n |
|---|---:|---:|
| Wrong recipient (misdelivery) | **2** | 802 |
| Unprotected portability | 808 | 335 |
| Visibility-state illegibility | 1,581 | 256 |
| Phishing / trust-cue failure | 3,020 | 116 |
| Unsafe defaults / misconfiguration | **700,000** | 236 |

A person can mis-address one letter at a time. A console checkbox exposes seven hundred
thousand people. The duty of care in a design should scale with its blast radius, and
mostly it doesn't.

**The "hacker" mental model is about half the story.** Within this corpus, 26.4% of
incidents are *purely* self-inflicted — error with no hacking and no social engineering
involved. For every four attacker-caused breaches there are roughly three that nobody
attacked.

**Failure modes migrate with the medium.** Misdelivery, loss and disposal failures peak
in 2010–2014 and collapse; misconfiguration peaks in 2015–2019 and persists. The corpus
watches breach causation move out of mailrooms and dumpsters and into cloud consoles.

**Misdelivery is more postal than digital.** Within misdelivery narratives, letters,
envelopes, mailings and faxes together outnumber email roughly two to one. Mail-merge
and envelope-stuffing are recurring mechanisms, as is name confusability.

Full working through in [`FINDINGS.md`](FINDINGS.md), with the caveat attached to each.

---

## What it can't tell you

The caveats are part of the finding, not a disclaimer at the bottom:

- **Source bias.** A large US Veterans Affairs import inflates the error class and
  public-administration share. Read class counts as "within this corpus", not as a
  population estimate.
- **Coverage decline.** VCDB coverage peaks 2010–2019 and thins after 2020. Post-2020
  trends are reported as *relative share*, never as absolute counts.
- **Record counts are sparse.** Exposure counts are known for only ~30% of incidents, so
  the blast-radius ladder uses medians — means are dominated by outliers.
- **Discovery is visible only when reported.** Externally-discovered breaches are
  plausibly more likely to become public at all, which biases the 78% upward by an
  unknown amount.
- **53% of error incidents have no recorded discovery route** and sit outside that
  finding entirely.

---

## The taxonomy

The core of the method is a nine-class taxonomy of design failure, mapping VERIS action
varieties onto the interface property that permitted them — for example misdelivery onto
*wrong-recipient affordances*, publishing error onto *visibility-state illegibility*,
misconfiguration onto *unsafe defaults*, phishing onto *trust-cue failure*. Classes,
exemplars and the machine rules used to apply them are in [`TAXONOMY.md`](TAXONOMY.md).

Classification is rule-based and inspectable rather than model-based, so any number in
the report can be traced back to the rule and the rows that produced it.

---

## Reproducing it

No dependencies — Python standard library only.

```
python3 pipeline/fetch.py      # pull VCDB
python3 pipeline/build.py      # → data/derived/{incidents,narratives}.csv
python3 pipeline/taxonomy.py   # apply the nine-class taxonomy
python3 pipeline/profile.py    # → stats.json, PROFILE.md
```

Ground-truth counts reconcile exactly: 10,042 incidents, 9,523 with narratives, 2,681
error, 644 social. Raw and derived data are gitignored — regenerate rather than trusting
a checked-in copy. See [`pipeline/README.md`](pipeline/README.md).

The report itself is `site/index.html`, fully self-contained: six inline SVG figures with
tooltips and data-table fallbacks, light and dark, no build step and no network calls.
Open it straight from disk.

---

## Repo map

| Path | |
|---|---|
| `SPEC.md` | the working contract — scope, method, known biases |
| `TAXONOMY.md` | the nine design-failure classes, exemplars, machine rules |
| `FINDINGS.md` | findings F1–F6 with their caveats |
| `SITE-SPEC.md` | report copy and chart specifications |
| `pipeline/` | fetch → build → taxonomy → profile |
| `site/index.html` | the interactive report |

## See also

[`to-scale`](https://uxhimanshuk.github.io/to-scale/) — the breach timelines in this
dataset, drawn as architectural sections. `pipeline/timelines.py` derives the figures it
uses: median 30.4 days to discovery, 2 days to containment on the 93 incidents recording
both. It also turned up a finding that belongs to this study rather than that one —
**a mistake takes longer to find than an attacker.** Error-caused breaches are discovered
after a median of **91.3 days** (n=297); hacking after **60.9** (n=309). Nobody conceals a
misconfiguration, and it still takes half again as long to notice as an adversary who is
actively hiding, which is the strongest version yet of this study's central claim.

[`clicked-through`](https://github.com/uxhimanshuk/clicked-through) — the
qualitative counterpart. This study establishes from incident records that
warnings and defaults fail at scale, but cannot say *why* anyone proceeded,
because VCDB stores outcomes rather than reasoning. That one asks technical
practitioners, and finds them describing the mechanisms unprompted: a warning with
no compliant answer available, an organisation that forbids the compliant answer,
and a fix whose real objective is the silence of the indicator.

Neither establishes a frequency. Together they do something harder to dismiss — a
pattern found in incident records, described independently by the people who work
inside it.

---

Built by [Himanshu Kalra](https://himanshukalra.com). Data: the VERIS Community Database,
used under its own licence. Code here is MIT.
