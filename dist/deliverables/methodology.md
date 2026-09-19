# Data & methodology

## Source and period

The supplied 2025-reported-energy-and-water-metrics.xlsx is the sole analytical input. Analyze Boston labels it a 2025 disclosure release. Energy-use year is not independently confirmed. Boston's general reporting guidance suggests prior-calendar-year data, but the resource does not explicitly confirm this file's period. The resource page was created 2025-10-02 and updated 2026-03-03. Original download date: unknown. Processing: 2026-09-18 UTC.

## Scope and deduplication

The workbook contains 5,487 unique building IDs: 5,034 non-campus buildings and 453 campus members. There are 91 campus summaries. Headers and identifier patterns locate sections; 544 duplicate appearances are removed. The campus worksheet wins duplicate summaries/members; shared fields agree after numeric normalization. The Summary's claim that campuses were removed from the main sheet is contradicted by its contents. Campus lists reference two absent building IDs (104716, 107224).

## Cleaning and quality

Original values, source sheet/row, normalized fields and value states remain in public analysis exports, excluding owner names and free-text notes. Missing, #N/A, zero, negative and unparseable values stay distinct. Verified Excel formats restore identifier zeros. Parcel addresses are labeled fallbacks. Unresolved energy-input problems exclude records from energy comparisons; water/emissions issues are separate. Water intensity above 1,000 gallons/ft²/year triggers review. Missing ENERGY STAR scores do not automatically imply reporting failure.

## Metrics and checks

Calculated Site EUI = total site energy (kBtu) / reported gross floor area (ft², excluding parking). Numerator must be nonnegative; denominator positive. Reported EUI stays separate. Absolute difference >0.11 kBtu/ft² excludes unresolved cases. Negative/unparseable energy components or a component exceeding total by max(1 kBtu, 0.01%) also trigger energy review. Electricity converts at 3.412141633 kBtu/kWh only for that check. Onsite renewables are already included in electricity and are not added again. Emissions use kgCO₂e; divide by 1,000 for tons. Emissions intensity uses area including enclosed parking. Observed component sums are checked at max(0.01 kg, 0.0001% of total) tolerance; missing components remain unknown.

## Peers, rankings and scenario

Fixed peers match primary use and area bands: <25k, 25–<50k, 50–<100k, 100–<250k and ≥250k ft². The positive-area median is 35,200 ft². 3,257 records pass energy checks; 2,647 have groups of at least 20, a display rule rather than statistical assurance. Quartiles use linear interpolation. Candidates exceed their peer 75th percentile; filters never change benchmarks. Scenario difference = max(0, calculated EUI − peer median) × area × closure fraction (0–1; default 0.5). Only comparison-eligible non-campus records qualify. This illustrates a benchmark gap, not engineering savings.

## Coverage, aggregation and limits

3,285/5,034 non-campus records have numeric reported EUI (pre-screen median 64.5 kBtu/ft²). Aggregates use 5,125 entities: non-campus buildings + one summary per campus; never members as well. Reported sums are disclosure values, not citywide totals. Missingness and selection affect results. One release cannot show trends or policy effects. Use/size matching does not control operations; correlations are not causal. Estimated emissions do not establish final compliance. Costs, prices, occupancy, hours, age and equipment performance are unavailable or insufficient.