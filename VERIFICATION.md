# Verification record

Processing and validation date: September 18, 2026 (UTC).

## Data and calculation checks completed

- Original workbook SHA-256 unchanged: `640b6a3ecb48084bfb169dcc8a6df8978ec5439f44c5f794f010cadbbf84bbb6`.
- Reconciled 5,487 unique building IDs, 5,034 non-campus buildings, 453 present campus members, 91 campus summaries and 5,125 aggregate reporting entities.
- Campus/member relationship lists have 455 references. Two IDs (104716 and 107224) are absent from the building records. No synthetic rows or campus allocations were created.
- 544 duplicate record appearances removed. No conflicting shared safe field values after numeric normalization. Owner names and free-text notes are omitted from public exports.
- Independently read source records and recomputed all non-campus calculated EUIs using Decimal arithmetic. Independently confirmed 3,285 numeric reported EUIs and pre-screen median 64.5 with Python statistics.
- Checked fixed peer medians and quartiles independently with statistics.median and inclusive quantiles, allowing floating-point tolerance.
- Verified campus-member exclusion, metric-specific flags, actual negative records 102879/105219, genuine zero retention, water flags that do not exclude energy, minimum peer n=20 and upper-quartile candidate selection.
- Verified CSV/JSON record counts and calculated values, and independently summed aggregate CSV values with Decimal. Public raw values contain no owner-name column.
- Real-data JavaScript checks passed for combined filters, immutable peer benchmarks, 0%, 50%, 100%, invalid fractions and empty-population scenario behavior, export columns, sorting and distributions.
- The methodology PDF contains exactly one page; rendered and visually reviewed. A missing subscript glyph was corrected before delivery.

## Browser checks

- Desktop 1440×1000: explorer loaded actual data, showing 2,370 default-focus buildings and 2,291 energy-eligible records. The scatterplot discloses exclusions and has a table alternative.
- Combined Multifamily Housing + 25,000–50,000 ft² yielded 553 records / 533 eligible; adding ZIP 02127 and reporting status in compliance yielded 61 / 60. Sorting and reset operated.
- BERDO 100933 detail view showed fixed peer n=841 and median 73.7 after filtering to one record. Keyboard-accessible dialog closes with a labeled button or Escape.
- Scenario UI at 0% returned a genuine zero, at 100% returned the full benchmark gap, and with no eligible records returned “No data available”. The quality-review list retained negative record 102879.
- WebMCP filter_buildings registered with the intended schema; valid input updated the visible filter state; invalid property type failed without changing it.

- Six presentation pages were opened and visually checked. Navigation and total five-minute timing passed.
- 390px responsive checks used a same-origin frame because the browser viewport override did not apply reliably. Explorer, priorities and methods all had document width = scroll width = 390 after fixing grid minimum-width overflow; Office filtering worked (423 records / 408 eligible). This verifies layout, not physical-device touch behavior.
- Public-site Chrome export filtered to BERDO 100933, produced one selected record, and completed a 1,013-byte CSV download, visible in Chrome Recent Download History. The in-app browser did not expose its download completion. CSV contents and selection agreement also passed automated checks.
- Prepared export links are cleared after filters or scenario fraction change, avoiding stale exports.

## Publication checks

- Sites deployment succeeded publicly at https://boston-building-energy-explorer.reybao.chatgpt.site.
- Public Chrome loaded the actual data; the single-building selection retained the fixed peer median and n=841.
- All 23 non-HTML static resources (excluding delivery metadata) returned byte-identical content. Four HTML routes redirect to extensionless URLs and include the hosting provider's standard injected script.
- GitHub repository created; source upload is blocked by Chrome extension file access permission. A complete downloadable source ZIP is available on the published website.

## Interpretation limits

Energy-use year remains unconfirmed. The source publication page labels the release 2025 and the general Boston guidance suggests prior-year data. Missingness and selection remain. Components have incomplete emissions coverage, even when the observed sum agrees. Passing these checks is not an energy audit, causal study, engineering savings estimate or BERDO emissions-compliance finding.

## Reviewed release — September 19, 2026

- Re-ran actual-data analytical tests and independent workbook verification: passed.
- Added a reproducible build combining redesign/ with shared dist/ analysis and final course materials; all generated local HTML resource links resolve.
- Published reviewed map interface, comparison, scenario, secondary analytics and final 300-second neural-narrated video.
- Public browser verified the new map loaded actual data.
- GitHub accepted README and complete project-source.zip; source archive preserves the project directory structure.
- Saved public site and repository URLs in course submission Sheet1!M17:N17 for Rey Bao; read back both values and observed Saved to Drive.
