# Simplified visual redesign — awaiting user chart approval

This local preview lives at /redesign/ when the project root is served. It does not replace the published Site yet.

## Three explicit tasks

1. Explore map: select a reported ZIP area, change property-use focus, pan/zoom, and open one investigation candidate.
2. Compare a building: a shared-zero horizontal bar comparison of calculated Site EUI and its fixed type/size peer median. Invalid energy inputs and insufficient peer samples produce an unavailable state.
3. Try a scenario: adjust 0–100% of the above-peer gap for one building or the map selection. A shared-zero bar comparison shows reported vs scenario site energy. The metric uses the existing analytics module.

## Geography

MassGIS ZIP Codes (5-Digit) from HERE supplies real postal polygons. These are not neighborhoods. Buildings are joined by their reported ZIP string; no point locations or geocoded building positions are invented. The source describes 2018 Q2 HERE geometry with Boston updates in March 2024; the currently retrieved service snapshot and query are documented in data/map-provenance.json. Source service is https://services1.arcgis.com/hGdibHYSPO59RG1h/ArcGIS/rest/services/ZIP_Codes_5_Digit_from_HERE/FeatureServer/0.

Color is the median of building-level EUI/peer-median ratios within a ZIP. Each eligible building has a fixed peer group of at least 20. ZIP color additionally requires at least 20 comparison-eligible buildings in the chosen use category. Below 0.90×, 0.90–1.10× and above 1.10× are explicit project display bands. Sparse and absent populations do not receive an energy-performance color. Campus members and summaries are excluded.

552 polygon features cover 528 unique source postal codes (some ZIPs have multiple pieces). Energy populations are aggregated by unique building ID, never by number of polygon features.

## Checks on the preview

- Multifamily: 1,947/1,947 reported records match a boundary ZIP. Office: 423/423. All uses: 5,032/5,034, with source ZIPs 02201 and 02137 unmatched; counts remain visible.
- ZIP 02127 Multifamily has 138 comparison-eligible buildings / 141 reported. Independent Python median ratio = 1.073649406259661; UI reports “7% higher”.
- BERDO 100083 calculated EUI = 93.56942515841494, fixed peer median = 53.401003688700065, n=159, 75% above after rounding. Independently recomputed full gap = 5,299,500.181342423 kBtu.
- Actual browser 0%, 50%, 100% scenarios returned 0.00, 2.65, 5.30 million kBtu respectively.
- Negative-energy record 102879 displays Review the data first; its scenario displays No data available.
- Actual map area selection updates the sidebar; choosing an area by keyboard/select is supported. Pan/zoom and state context controls are present.
- All three pages have document width = scroll width = 390 at the tested mobile breakpoint. Desktop layout inspected at 1440×1000.

## Video follow-up after charts are approved

Replace the text-only presentation as the primary demo with a real five-minute website-operation recording (MP4), accompanied by English captions. Record the approved interface, not a slideshow of screenshots. Proposed sequence totals 300 seconds:

- 0:00–0:25: decision question and map legend.
- 0:25–1:35: switch property type, choose ZIP, inspect coverage and an example.
- 1:35–2:45: compare the selected building, explain the two bars and fixed peers.
- 2:45–4:00: show 0%, 50%, 100%, then the map-selection scenario.
- 4:00–4:35: export the result and locate the short methodology note.
- 4:35–5:00: what the benchmark can and cannot tell us.

The preview was subsequently recorded on September 19 after the user asked to generate the demonstration. It has not replaced the public site; final chart confirmation remains pending.

## Plain-language and completeness revision

Comparison multipliers are now shown as “About the same”, “25% higher”, or “20% lower”; all compare calculated energy per square foot with a fixed use/size-group median. Secondary analysis pages restore distributions, scatterplots, filtered tables, separate review lists, findings, recommendations and course materials. See REQUIREMENTS-AUDIT.md for coverage and unfinished delivery items.

## Professional data-product visual revision — September 19

- Deep-navy workspace navigation, cool-white surfaces, electric-blue actions and charts; amber remains reserved for above-reference map values.
- Map property-type and ZIP controls now share a visible top toolbar. Comparison search and scenario controls remain adjacent to results. Scenario presets offer 0%, 50%, and 100% alongside the continuous slider.
- Three locally stored, openly licensed Boston photographs add city context. They are labeled as context, never as a photograph of the selected building. Sources and license notices appear in image-credits.html.
- Mobile navigation exposes the additional analyses through More; all original analytical functionality remains accessible.
- Five-minute real browser capture is completed with embedded English captions and a downloadable speaking outline. The recording workflow is a local-only development utility, not a public upload service.

### Recording verification

The final MP4 is 300.00 seconds, 1920×1080, H.264, 24 fps, with embedded English captions and no audio track. Six frames across the five chapters were visually inspected. Browser playback reported a 300-second duration with no media error; the Compare chapter button successfully sought to 90 seconds. The preview server now supports video byte-range requests (`python3 scripts/serve_preview.py`) so chapter jumps work locally. The temporary recording receiver has been stopped. Final playback page: `/dist/walkthrough.html`.

### English narration update

A separate narrated MP4 now contains English synthetic speech (installed Samantha voice), aligned to the 20 caption intervals. It preserves the 300-second, 1920×1080 video, with AAC audio and normalized loudness. All 20 segments contain non-silent audio and fit their intervals without overlap. Browser playback and chapter seeking passed; Watch demo opens an in-page player from both primary and analysis pages, and closing the dialog pauses playback. The original silent MP4 is retained. The playback page and current website links use the narrated edition.

### Natural voice and resource placement

With explicit user authorization, the complete narration was regenerated using Microsoft Edge online speech, en-US-AvaMultilingualNeural. The conversational script and timing are in walkthrough-narration.md and narration-neural-timing.json. The MP4 remains 300 seconds, 1080p; all 20 segments contain audio and fit without overlap (maximum timing adjustment 3.6%). Video walkthrough now sits alongside the other Analysis & Resources entries and opens the player in place. Mobile More has the same entry. Browser playback, close/pause, mobile opening and 390px layout passed. Asset versioning prevents stale preview styles/scripts.
