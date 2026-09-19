# Boston Building Energy Explorer

Compare similar buildings and identify priorities for further investigation.

[Live website](https://boston-building-energy-explorer.reybao.chatgpt.site) · [GitHub repository](https://github.com/reybao/boston-building-energy-explorer)

A lightweight static website for Boston energy planners, building managers and community sustainability organizations. No backend, authentication or JavaScript dependencies are required. The website, analysis, methodology and presentation are in English.

## Obtain the project

The repository contains the complete project as browsable folders: `redesign/`, `dist/`, `scripts/`, and `tests/`, plus requirements and documentation. Use GitHub’s **Code → Download ZIP** and extract it, or clone the repository. Run the commands below from the extracted repository root. The root `project-source.zip` is an additional packaged copy. The original workbook is deliberately excluded; obtain it from the official source only if you want to reproduce data processing. The generated public data is already included for running the website.

Two large CSV downloads (`buildings.csv` and `aggregate-entities.csv`) are stored losslessly as `.csv.gz` files in GitHub to fit browser-upload limits. The packaging and build scripts automatically restore the original CSV files. The public website provides ordinary CSV downloads.

## Run locally

From this project directory, run:

```sh
python3 scripts/package_source.py
python3 scripts/build_site.py
python3 -m http.server 8765 --bind 127.0.0.1 --directory build
```

Open http://127.0.0.1:8765. Serve the directory over HTTP; opening index.html directly will block data requests in some browsers.

The current interface is authored in `redesign/`; shared analysis code, generated data and course materials are in `dist/`. `scripts/build_site.py` combines them into `build/`, resolves production paths, and includes only the final narrated video. Validate JavaScript syntax with `node --check dist/app.js`. Fonts use Google Fonts with local system fallbacks.

## Reproduce the analysis and materials

1. Obtain the original `2025-reported-energy-and-water-metrics.xlsx` from the [official Analyze Boston resource](https://data.boston.gov/dataset/building-emissions-reduction-and-disclosure-ordinance/resource/911db0b1-437f-43ba-86bb-860cc1cd9319) and put it beside this README. The supplied original is retained unchanged locally and intentionally excluded from the public source repository to avoid republishing owner names.
2. Create a Python virtual environment and install `requirements.txt`.
3. Run `python3 scripts/process_data.py`.
4. Run `python3 scripts/create_deliverables.py`.
5. Run `python3 scripts/verify_data.py` and `node tests/analytics.test.mjs`.
6. Run `python3 scripts/package_source.py` to refresh the downloadable source package, including the current interface and final narrated video.
7. Run `python3 scripts/build_site.py` to assemble the public site.

The original file SHA-256 is `640b6a3ecb48084bfb169dcc8a6df8978ec5439f44c5f794f010cadbbf84bbb6`. A later official download might differ. The processor records the actual input hash and processing time. Original download date is unknown. The publisher's resource update date is not treated as proof of the local workbook revision.

## Source and period

This is the **2025 disclosure release; energy-use year not independently confirmed**. [Boston's BERDO page](https://www.boston.gov/departments/environment/berdo) describes annual reporting of the previous calendar year, suggesting 2024. Neither the resource page nor supplied workbook explicitly confirms the consumption year for this particular release. The application keeps that distinction visible.

Official resource page observed: created October 2, 2025; updated March 3, 2026. The source page identifies the release as 2025 Reported Energy and Water Metrics.

## Record grain and deduplication

- `dist/data/buildings.csv`: one row per unique building ID, including campus members. Use `grain=non_campus` for independent building analysis.
- `dist/data/campus-summaries.csv`: one row per campus. Do not add these records to their members.
- `dist/data/aggregate-entities.csv`: non-campus buildings + one summary per campus, excluding members. This is the only provided fact table designed for campus-inclusive sums.
- `dist/data/campus-relationships.csv`: one row per campus/member reference, including missing building IDs. This is not an energy fact table.
- `dist/data/source-records.json.gz`: all source appearances, safe original values, normalized identifier values, number formats, sheet and Excel row. Repeated appearances must not be summed.
- `dist/data/peer-benchmarks.csv`: one row per primary-type/area-band reference group.
- `dist/data/duplicate-conflicts.csv`: field-level disagreements after numeric normalization. An empty body means none found.
- `dist/data/metadata.json`: coverage, count reconciliation, exclusions, distributions, provenance hash and aggregate inclusion counts.

The processor locates headers dynamically and identifies numeric building IDs and C-prefixed campus summaries. Appended main-sheet campus summaries reuse its building layout with the first two fields repurposed. The campus sheet has different summary/member layouts and a repeated header. The campus worksheet wins duplicate members and summaries. Field differences remain documented; energy-relevant conflicts exclude energy comparisons.

The workbook Summary says campuses were removed from the main sheet, but actual rows contradict this. Two summary references (104716 and 107224) have no building records. No synthetic buildings are created to fill that gap.

## Analytical decisions

Calculated Site EUI is total site energy / reported gross floor area excluding parking. Reported EUI is separate. Required inputs, nonnegative energy, positive area, a known primary use, a reported-EUI reconciliation within 0.11 kBtu/ft² and relevant component checks determine energy eligibility. A component cannot exceed the total by more than max(1 kBtu, 0.01% of total); electricity is converted to kBtu only for this lower-bound check. Onsite renewable electricity is already included in electricity use according to the dictionary.

Missing, explicit not-applicable, unparseable, negative and zero states remain distinct. No missing components are imputed as zero. Numeric text converts while originals remain in the CSV and source JSON. ZIP and parcel zeros use the workbook's verified number format. ENERGY STAR score missingness is not treated as reporting noncompliance.

Emissions and water checks are separate. The observed emissions-component sum is compared with reported total at max(0.01 kgCO₂e, 0.0001% of total) tolerance. Incomplete coverage remains flagged, including when the observed sum agrees. Negative emissions or mismatches do not automatically invalidate energy inputs. The water review threshold is >1,000 gallons/ft²/year and does not automatically exclude energy comparison. These thresholds are project rules, not official standards.

Area bands are `<25k`, `25k–<50k`, `50k–<100k`, `100k–<250k`, `>=250k` ft², selected after inspecting the source's area distribution. Peers require identical primary use and band. Reference groups are fixed to the full eligible release and include the candidate itself. Quartiles use linear interpolation. Minimum n=20 is a display rule, not a significance claim. Investigation candidates exceed their peer group's 75th percentile. There is no composite score.

Scenario energy difference = `max(0, calculated_eui - peer_median) * area * fraction`. Fraction is 0–1, default 0.5. Only eligible non-campus buildings with enough peers enter. Empty eligible populations produce null / “No data available”, not zero. The calculation is centralized in `dist/analytics.js`; stored building gaps are generated by the processor. Filters never regenerate benchmarks.

“In compliance” means reporting and verification. The source category `state` remains unexplained. Estimated emissions are not final emissions-compliance determinations. ZIP codes are not neighborhoods. The map uses actual MassGIS/HERE ZIP polygons, defaults to Boston, and reports matching coverage. It does not imply exact building coordinates or statewide energy coverage.

## Course materials

- `dist/methodology.html` and `dist/deliverables/methodology.pdf`: same methodology content; PDF fits one letter-size page.
- `dist/presentation.html`: six navigable presentation pages; timed to five minutes, including a live demo.
- `dist/deliverables/speaking-outline.md`: English speaking outline.
- `dist/reflection.html` and `dist/deliverables/reflection.md`: limitations and interpretation.
- `dist/walkthrough.html` and `dist/deliverables/boston-energy-walkthrough-natural.mp4`: actual five-minute operation recording with English neural narration and captions; available from Video walkthrough in the main navigation.
- `dist/deliverables/walkthrough-narration.md`: full spoken transcript.
- `redesign/image-credits.html`: Boston photo licenses and attribution.
- `VERIFICATION.md`: actual checks performed and any remaining limits.

## Deploy

Run `python3 scripts/package_source.py` and `python3 scripts/build_site.py`, then publish `build/` on any static host. Every data file and course deliverable must be served. Hash navigation supports static hosting without rewrite rules. `.openai/hosting.json` retains the registered Sites identity and static directory. Do not create a second Site for this checkout.

The public website and repository URLs are recorded in `dist/data/delivery.json`. The course submission spreadsheet was updated with explicit user authorization on September 19, 2026: Rey Bao, row 17, PS1 Site URL (M17) and PS1 Repo (N17).

## Limits

One release cannot establish trends, policy effects or causal impacts. Peer matching does not fully control operating conditions. Missingness and sample selection matter. Costs, prices, occupancy, hours, age and equipment performance are insufficient. Benchmark scenarios are not engineering savings estimates, emissions-reduction promises or payback calculations.
