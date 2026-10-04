# Belovodie Command visual verification

final result: passed

Target: the third selected reference, `.local/selected-reference.png` (1487 × 1058).
Implementation: `.local/preview-home-release-retina.png` (4576 × 2996), browser
CSS viewport 2200 × 1440, DPR 2, browser zoom 1.04. Both images are normalized to
2200 × 1440 in `.local/comparison-release-preview.png` (4400 × 1440). Private
captures and Home Assistant bindings are intentionally not distributed.

State: Home, desktop, dark theme, Today selected, details closed. Actual provider
measurements replace the reference's demonstration values. The comparison was
opened together, followed by focused forecast, navigation and metric comparisons:
`.local/forecast-comparison-release-preview.png`,
`.local/navigation-comparison-release-preview.png`, and
`.local/metrics-comparison-release-preview.png`.

## Findings and comparison history

No actionable P0/P1/P2 differences remain in the verified state.

- P0, empty first workspace, comparison 09: initially expanded tabs/carousels
  stayed collapsed. Universal Card 1.0.10 now opens their initial mode through
  the normal lazy loader. Comparison 10 and the release comparison show mounted
  charts and routes. Three package regressions cover child mounting, repeat-load
  deduplication and keeping navigation subviews closed.
- P1, weather composition, comparison 04: the fixed weather-card layout did not
  reproduce the separate forecast and precipitation regions. Existing ApexCharts
  and Button Card now compose both regions with aligned hourly timestamps and
  explicit units. The release comparison shows both complete plots.
- P2, inherited overlays, comparison 07: nested card-mod pseudo-elements changed
  surfaces. Explicit nested styles reset them. Forecast, financial charts and
  primary native tiles now use the intended flat petrol surfaces.
- P2, chart clipping/scale, comparison 07: narrow axes and margins hid part of the
  precipitation region. Axis bounds, chart heights, margins and tab wrapper
  sizing were corrected. Both plots are visible in the focused release comparison.
- P2, truncated More label, comparison 04: header spacing now exposes the complete
  menu label. Navigation and the opened menu were verified in the browser.
- P2, small native controls/long states, route contact sheet: native tiles now use
  30px titles, 36px states and enlarged icons while retaining native actions and
  features. Long metric states use a smaller wrapping value style. Post-fix
  evidence: `.local/system-control-styled-ready.png`.
- P2, mixed tab/chart typography: tabs inherited the browser button default.
  They now inherit the dashboard font; chart labels use the same family at 24px.
  Computed browser styles confirm the Inter/Segoe UI/sans-serif stack and 30px tabs.

## Required fidelity surfaces

- Fonts: consistent Inter/Segoe UI/sans-serif stack and system fallback. Semibold
  primary numbers, regular secondary text, 30px tabs/titles, 24px chart labels.
  Long status strings wrap rather than being cut off.
- Spacing: four metrics, tabbed workspace, six-item detail dock, quick scenes and
  final meter follow the reference's hierarchy. All 20 default routes fit the
  2200 × 1440 viewport without document or full-height view scrolling. Card/dialog
  scrolling remains available. Waiting for the HA launch screen to disappear is
  required before capturing route evidence.
- Colors: petrol surfaces, cyan active controls, restrained scene colors and
  semantic warnings. Inherited gradients are removed from primary nested cards.
- Images: generated night-cloud artwork is installed; room photos and seven
  visible weather-library assets load. Native MDI/Basmilius library vectors supply
  icons; no handcrafted decorative SVG or CSS drawings were introduced.
- Copy: live values, correct units, apparent-temperature labels, partial-meter
  scope and missing-data states replace mock measurements. Allergen summaries
  use visual measurements. Secondary controls stay in closed dialogs.

## Functional evidence

Browser-tested initial loading; Today/Routes/Allergens switching; the More menu;
room dialogs with inherited dashboard templates; Escape/close behavior; named
shutter-room dialogs; transport switching between existing car and TMB sources,
with public transport restored. Google Maps links were checked for the matching
travel mode without opening precise-location URLs during tests.

All original view actions and button templates were compared and retained.
Physical light/scene/shutter actions were not executed during verification.
The 20-route geometry audit records no configuration-card errors, unloaded images,
open default dialogs or page overflow. Browser console checks found no errors
from this preset or Universal Card. An existing Custom Sidebar configuration error
is unrelated to the hidden dashboard chrome and is recorded as a separate runtime
limitation; no global sidebar configuration was changed.

## Accepted constraints and follow-up polish

- P3: native chart marker shapes and library icon silhouettes differ slightly
  from the raster reference. The retained HACS implementations provide real
  interactive graphs and controls.
- Expected: forecast shape, warnings, prices and departure availability vary
  with live data. Missing feeds remain missing rather than copying demo values.
- The reference has no screens for the other routes; they reuse the same
  verified layout, typography and actual native controls.

## Implementation checklist

- [x] Resolve package failures and recapture the initial workspace.
- [x] Compare full view and focused typography/chart regions.
- [x] Verify all 20 routes and primary non-device interactions.
- [x] Preserve action contracts and back up the original dashboard.
- [x] Run eight preset regressions and Universal Card's 154-test coverage gates.
