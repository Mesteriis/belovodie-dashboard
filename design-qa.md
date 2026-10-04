# Belovodie Command visual verification

## New 100% baseline (owner-selected previous 80%)

The owner selected the live panel at its previous 80% as the new 100% target.
This supersedes an independent typography/layout reduction. Only the owned
canvas scale and its preference conversion changed; layout, tokens and bindings
remain the same.

- Source: `.local/baseline-target-old-80.png`, production Home, previous 80%.
- Implementation: `.local/baseline-preview-new-100.png`, preview Home, new 100%.
  Both are native 1600×900 pixel captures at a 1600×900 CSS viewport, with the
  same browser density, Today selected, details closed and HA chrome hidden.
  No image rescaling was required. The live weather and clock changed between
  captures; these are expected provider/time differences.
- Full comparison: `.local/baseline-comparison-full.png` (3200×900). Focused
  typography/spacing comparison: `.local/baseline-comparison-font-spacing.png`.
  Both were opened together. All nine primary region coordinates match within
  0.03 CSS pixels and computed title fonts match. No actionable P0/P1/P2
  differences remain: typography, spacing, palette, assets and copy retain the
  selected appearance. Supplied weather artwork and library icons are unchanged.
- Real settings clicks verified 95% → zoom 0.76, the 50% bound → 0.4, the 150%
  bound → 1.2, and reset 100% → 0.8. The old URL at 80% showed 100% in settings.
  Navigation and reload retained the new 100% preference.
- Preview geometry passed 90 valid combinations: all 20 routes at 100%, plus
  five core routes at 50/150%, each at 2200×1440, 1280×800 and 800×1280. Three
  traversals were repeated after the browser viewport changed during navigation;
  the corrected harness sets dimensions after loading each route. No layout
  fix or rejected measurements were counted as passing evidence.
- Twenty-three local regressions passed, including old/new storage and URL
  migration, exact new 100%=old 80%, repeated navigation, bounds, blocked
  storage, scoped live updates and retained child actions/context. The private
  binding comparison retained 2,734 data/action contracts; only panel-scale
  JavaScript actions changed. No device services were executed.

final result: passed

## Scale and compact-control follow-up

- The owner's new density request supersedes the earlier enlarged native-tile
  typography. Titles are now 18px, values 20px and icons 36px. Tiles use horizontal
  content-sized rows with 8px/10px padding instead of filling large grid tracks.
  Actions inside preset dialogs use 18px labels and 56px controls. Source actions,
  entity bindings and native features remain unchanged.
- More → Panel Settings offers 50–150% in five-point steps and reset to 100%.
  Real clicks verified both bounds, live percentage updates, an open settings
  dialog throughout, reset, and 95% after navigation and reload. Preferences are
  scoped to the browser/dashboard; blocked storage uses the explicit URL.
- The existing Button Card runtime provides the canvas. Its nested-card
  `do_not_eval` option preserves child template/entity context. Native HA chrome
  and portalled dialogs stay at their normal scale. No additional card runtime.
- Preview rendered geometry passed all 20 routes × three scales (50/100/150%) ×
  three viewports (2200×1440, 1280×800, 800×1280): 180 checks. No configuration
  errors, document/full-view scrolling or primary regions outside the viewport.
  Temporary viewport overrides were reset.
- Twenty-one local regressions passed, including scope/defaults, invalid values,
  five-point rounding, bounds, live owned-DOM updates, reset, preserved URL values,
  blocked storage, child context/action retention and idempotent compact rows.
- Visual follow-up compares the previous native 1600×900 Home capture with the
  current 100% Home capture in the same browser. The intended compact entity
  change is verified separately on System. Evidence and combined comparisons
  are private under `.local`; no device data or screenshots are distributed.
- Earlier prototype findings were fixed before the 180-check run: an intrinsic
  Button Card host width left unused space; explicit full-width host styles fixed
  it. CSS zoom already compensates percentage dimensions, so removing a second
  inverse-width calculation restored the physical viewport size. The inner grid
  subtracts its padding once, keeping the footer fully visible. A native tile
  pseudo-element reset retains flat petrol surfaces.

final result: passed

## Interface toggle and stale-resource follow-up

- The user's already open Main tab retained Universal Card 1.0.8 and omitted
  newly installed frontend modules. It showed a configuration-error card in
  place of the forecast, default tab styles and native Home Assistant chrome.
  The server resource inventory and installed bundle were already 1.0.10.
  Reloading that same tab loaded the current resources and restored the forecast,
  styling and Kiosk Mode; a new Universal Card release was unnecessary.
- The More menu now starts with a reversible show/hide control. The choice is
  scoped to the current browser and dashboard, with an explicit URL fallback
  when browser storage is blocked. A click reloads the page and resource list.
- View height subtracts Kiosk Mode's zero header height when hidden, or the
  native Home Assistant header height when shown. Preview browser checks at
  2200 × 1440, 1280 × 800 and 800 × 1280 confirmed that showing the interface
  does not introduce page scrolling. Native mobile sidebar behavior is retained.
- Sixteen local and GitHub Actions tests passed, including default/scoped choices, navigation,
  reload, temporary editor override, blocked storage, URL preservation, control
  labels and absence of device-service calls.
- Belovodie 0.1.3 was published, downloaded through HACS and verified against
  the release artifact. Universal Card remains at the verified 1.0.10 release.
  The YAML dashboard was backed up and replaced atomically, then force-reloaded
  through the Lovelace API. Readback exactly matched the proposed configuration;
  comparison retained every unrelated binding and action. No core restart.
- Production geometry checks passed for all 20 routes in both interface modes
  at 2200 × 1440, 1280 × 800 and 800 × 1280: 120 checks, no configuration-card
  errors, document overflow or full-height scrolling containers. The desktop
  header/sidebar and native mobile sidebar behavior matched the selected mode.
  Real clicks and reloads verified the saved choice and its reversal.
- Visual proof uses the ordinary 1600 × 900 browser window:
  `.local/interface-home-native-final.png`, `.local/interface-menu-native-final.png`
  and `.local/interface-shown-native-final.png`. The larger emulated screenshots
  had compositor tiling and were excluded from visual evidence; the three target
  sizes above have rendered DOM geometry evidence. Temporary viewport overrides
  were removed and the final interface choice was restored to hidden.

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
- [x] Run twelve preset regressions and Universal Card's 154-test coverage gates.

## Screen calibration and tablet follow-up

The offline renderer now exposes `--screen WIDTHxHEIGHT` and the Python API accepts
`Screen(width, height)`. This calibrates density; the live page continues to track
the browser's CSS viewport. Compact navigation retains every route in More; the
portrait grid has two metric columns and a horizontal closed detail dock.

Geometry checks covered all 20 preview routes at 1280×800 and 800×1280, followed
by all 20 at 2200×1440. No page overflow, default dialogs, unloaded images or
configuration-card errors appeared. A post-fix portrait recapture verifies room
and native-control grids in two columns. Wheel input moved the room card's own
scroll position while document scroll remained zero. The More dialog fit within
the portrait viewport, and the Allergen tab opened its real measurements.

The explicit 1280×800 calibration was saved and checked independently in the
browser. Compact density caps preserve readable values. Shared Button Card
styles keep the configuration below the transport message limit instead of
repeating calibration CSS for each button. Layout Card media-query feature keys
are normalized to match its browser MediaQueryList lookup. Twelve regressions
cover composition, parsing, preservation, query normalization and data semantics.
Private evidence: `.local/adaptive-layout-audit.json`,
`.local/adaptive-fixed-800-route-rooms.png`,
`.local/adaptive-fixed-800-route-system.png`, `.local/parameter-1280-real.png`.
The theme's zero masonry margin follows Layout Card's native CSS variable and
prevents inherited card margins from consuming compact grid tracks.

## Installed dashboard verification

The theme was updated through HACS and its SHA-256 matched the downloaded GitHub
release. The existing dashboard used YAML mode. Its raw source was backed up,
checked against the earlier API snapshot, and replaced atomically after a YAML
round-trip validation. Forced Home Assistant dashboard loading returned the exact
rendered configuration. Dashboard mode and Home Assistant core stayed unchanged.

All 20 installed routes were then checked at each of 2200×1440, 1280×800 and
800×1280 CSS pixels: 60 checks, no page overflow, open default dialogs,
configuration-card errors or unloaded images. Each route's actual browser zoom
was accounted for when emulating its CSS viewport; preferences were not changed.

The installed room modal fit the portrait viewport, inherited the original
button templates and loaded all photos. More stayed within the screen. Allergen
selection was verified after lazy loading completed, then Today was restored.
The complete installed Home view was compared with the selected reference;
room, system and finance views were reviewed as a contact sheet. Earlier accepted
native icon/marker and real-data differences remain the only visual constraints.
Private evidence: `.local/production-layout-audit.json`,
`.local/production-reference-comparison.png`, `.local/production-visual-review.png`,
`.local/production-home-final.png` and `.local/production-rooms-modal.png`.

## Animated weather measurement

The existing compact weather measurement now uses Atmo Weather Card v7.5.0 as
its non-interactive background. It follows the existing weather and sun entities;
the original Button Card retains temperature, feels-like, humidity, wind and
all bindings/actions. No weather renderer or icon asset was copied into this
repository. The dark scrim protects foreground readability and the original
100% calibration (previously 80%) stays unchanged.

All 20 preview routes passed at 2200×1440, 1280×800 and 800×1280 CSS pixels
(60 checks). Seven existing weather slots loaded the renderer. No visible
configuration errors or page overflow occurred. Live overcast/day classes matched
the current backend states. Two native viewport captures confirmed changing sky
pixels with unchanged data labels. The reduced-motion emulation hid the sky and
restored its display after clearing emulation. The first oversized whole-card
pixel-difference threshold was unsuitable for slow cloud drift; the final
measurement excludes labels and records 2193 changed sky pixels at >=3/255.
Upstream's 26 tests passed, including precipitation and simulated day/night;
the preset's 26 tests passed, including binding preservation and unavailable
weather. These simulated conditions are distinguished from the live overcast
condition; no Home Assistant entity states or physical devices were modified.

Private evidence: `.local/weather-preview-layout-audit.json`,
`.local/weather-motion-comparison.png`, `.local/weather-installed-package-hashes.json`.

final result: passed
