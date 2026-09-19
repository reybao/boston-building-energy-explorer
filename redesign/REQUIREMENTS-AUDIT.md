# Requirements audit — 18 September 2026

Scope: local redesign at `/redesign/`, the shared analysis implementation in `dist/`, existing data processing and course materials. The public site still serves the previous version. “Implemented” below is not a claim that the redesigned public delivery is finished.

| Requirement | Status and location |
| --- | --- |
| Actual workbook; reproducible processing; preserved source; privacy-minimized exports | Implemented in the existing processing workflow and `dist/data`. This revision does not change analytical data or the original workbook. |
| Building/campus separation and fixed eligible benchmarks | Implemented: 5,487 building IDs; 5,034 non-campus buildings; 453 campus members; 91 campus summaries; 5,125 aggregate reporting entities. Fixed type/area groups require at least 20 eligible observations. |
| Overview, users, research question, supported findings and recommendations | Available through `analysis.html#overview` (Findings & recommendations). Campus-inclusive reported aggregates remain separate. |
| EUI distributions with median, range and sample size | Restored to the redesign through `analysis.html#explore`. Rows now share one linear scale. |
| Interactive size/EUI scatterplot | Restored in Full charts & table; positive-value logarithmic axes, omitted-record counts, details and keyboard controls. |
| Searchable/sortable table; type, area, ZIP, reporting-status filters; reset and CSV | Restored in Full charts & table. The map's analysis link carries its property type and ZIP selection. Benchmarks remain fixed. |
| Separate energy-investigation and data-quality lists | Restored through `analysis.html#priorities`. Transparent sorts; records with invalid energy inputs remain reviewable. |
| Individual comparison, sample size, median, quartiles and relative position | Compare a building presents two bars and plain-language differences. Expand Check the inputs & assumptions for quartiles and percentile. |
| Scenario 0–100%, default 50%, required formula and label | Implemented for one building or map selection, and in the investigation workspace. The displayed output retains “Benchmark scenario energy difference.” Moving halfway toward typical use is distinguished from the percentage change in total energy. No eligible observations displays No data available. |
| Data/methods, dictionary, sources, dates, cleaning and limitations | Available through `analysis.html#methods`; details are expandable. The energy-use year remains independently unconfirmed and is labeled as required. Download date remains unknown, distinct from processing date. |
| Real Massachusetts geography, Boston default | Implemented with MassGIS/HERE ZIP polygons, reported ZIP matching, explicit coverage and sparse-data states. ZIPs are not neighborhoods or building point locations. |
| Dataset, one-page methodology web/PDF, reflection | Existing completed materials linked in Data & course materials. |
| Original five-minute presentation pages and English outline | Existing materials available; the planned duration is five minutes. |
| Subsequently requested actual five-minute operation video | **Completed locally on September 19.** An actual five-minute browser-operation recording with embedded English captions, MP4 playback, chapter navigation, SRT and English outline is available at `/dist/walkthrough.html`. Updated with English neural narration (Ava), aligned to 20 caption segments. It demonstrates the current preview; public release remains pending. |
| GitHub repository containing source/workflow/README | **Not completed.** Repository created at https://github.com/reybao/boston-building-energy-explorer, but source upload remains blocked by browser file-access permission. Existing downloadable ZIP contains the published version, not the local redesign. |
| Updated public website | **Not completed.** Previous version is live at https://boston-building-energy-explorer.reybao.chatgpt.site. Redesign remains a local review, consistent with the user's request to confirm charts before replacement. |
| Shared course submission spreadsheet | Not edited; explicit user instruction would be required. |

## Plain-language changes

- `1.00 × peers` becomes **About the same**; `1.25 ×` becomes **25% higher**; `0.80 ×` becomes **20% lower**.
- The measured quantity is energy per square foot, compared with the median of similar-use, similar-size buildings. Differences are rounded to whole percentages; less than 0.5% is displayed as About the same.
- The ZIP headline summarizes the median of individual buildings' fixed-reference ratios; it is not a ratio of total ZIP energy or an area-weighted statistic.
- Main charts use “Similar buildings”; technical definitions remain in expandable explanations.
- Scenario zero reads **No change**; unavailable data is not displayed as zero.

## Verification for this revision

- JavaScript syntax checks passed for shared analysis and redesign modules.
- Existing actual-data analytical tests passed: fixed benchmarks, filters, sorting, distributions, CSV fields, scenario 0/50/100%, empty population and invalid fractions.
- Display-label checks passed for equal/higher/lower/unavailable values and rounding.
- Browser: default building 100083 shows 75% higher; quartiles 40.9–67.5 and relative percentile are visible in details.
- Browser: 50% movement toward typical use shows a 2.65 million kBtu difference and 21% reduction of reported energy; 0% displays No change.
- Browser: ZIP 02127 shows 7% higher, 138 comparable / 141 total Multifamily records. The full-analysis link preserves this selection and shows 141 records / 138 energy-eligible.
- Browser: full distributions/scatter/table load; ZIP filtering updates the table; separate Data-quality review cases tab works; dataset and deliverable links resolve to the existing `/dist/` assets.
- Browser: main comparison/scenario pages and full-analysis/methods pages checked at 390 px with no document overflow; desktop data-review layout inspected at 1440 px.
- The operation video was subsequently recorded and checked on September 19. GitHub source upload and deployment verification of the redesign remain outstanding.

## Final delivery update — September 19, 2026

The previous pending-delivery entries above are superseded: the reviewed interface and final neural-narrated video are published at the existing URL; GitHub contains the full source archive and README; course sheet M17:N17 is saved for Rey Bao. Source archive delivery preserves all project folders; the original workbook and credentials are excluded. README now documents building and serving the reviewed release from build/.
