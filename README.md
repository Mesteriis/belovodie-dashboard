# Belovodie Command

A dark petrol and cyan Home Assistant theme and Lovelace composition preset.
The desktop layout has four primary measurements, a tabbed workspace, a detail
dock and quick actions. Its default calibration is 2200 × 1440 CSS pixels;
the actual browser viewport controls the responsive layout. Details open in Universal
Card dialogs; long content scrolls inside the workspace or dialog.

This repository does not implement a new card. It composes existing projects:

| Function | Existing package |
| --- | --- |
| Measurements, actions, navigation and panel scale | [Button Card](https://github.com/custom-cards/button-card) 7.0.1+ |
| Animated weather measurement background | [Atmo Weather Card](https://github.com/whyisthisbroken/atmo-weather-card) v7.5.0 |
| Viewport grid | [Layout Card](https://github.com/thomasloven/lovelace-layout-card) |
| Tabs and dialogs | [Universal Card](https://github.com/Mesteriis/universal-card) 1.0.10+ |
| Forecast, precipitation and historical charts | [ApexCharts](https://github.com/RomRider/apexcharts-card) |
| Nested card styles | [Card Mod](https://github.com/thomasloven/lovelace-card-mod) |
| Historical charts | [ApexCharts](https://github.com/RomRider/apexcharts-card), [Mini Graph Card](https://github.com/kalkih/mini-graph-card) |
| Dashboard chrome | [Kiosk Mode](https://github.com/NemesisRE/kiosk-mode) |

## Installation

Add `Mesteriis/belovodie-dashboard` to HACS custom repositories with type **Theme**,
then download **Belovodie Command**. Enable your normal `frontend: themes:` include
if you have not already enabled themes. Reload themes and select **Belovodie
Command** on the intended dashboard views. Install the cards above through HACS.
No Home Assistant core restart is needed for this preset when themes are already
configured.

For the animated `bc_weather` measurement, add
`whyisthisbroken/atmo-weather-card` as a HACS custom repository of type **Dashboard**
and install v7.5.0. Reload the browser after installing its resource. The composer
uses the existing weather entity and `sun.sun` (override with
`variables.sun_entity`) for live conditions and day/night. Temperature, feels-like,
humidity, wind and actions remain in the original Button Card. Atmo draws the sky
behind them, at 20 FPS and DPR 1, and pauses when offscreen. Unknown/unavailable
weather hides the animation. Reduced-motion preferences use the original static
art. Weather data is not sent to Atmo's authors; its upstream card requests the
Figtree stylesheet from Google Fonts. Atmo is MIT licensed and installed intact;
this repository does not copy its renderer or assets.

The theme changes colours and typography. The optional offline composer produces
the bounded layout; downloading a theme does not rewrite an existing dashboard.
Provide an existing Lovelace JSON configuration and a local JSON list of page
bindings (`path`, `title`, four `metrics`, workspace `tabs`, `dock`, `footer`, `last`).
Keep both files private. The renderer has no network access or credentials:

```sh
python3 tools/render.py original.json pages.json output.json \
  --url-path dashboard-example --clock-entity sensor.time --screen 2200x1440
```

`--screen WIDTHxHEIGHT` is a configurable typography/spacing calibration, not a
fixed page size. The Python API accepts `compose(..., screen=Screen(width, height))`
from `src/screen.py`. Use CSS viewport pixels rather than a panel's physical pixel
count. The same rendered dashboard can be used on different devices: its height
tracks `100dvh`, and its measurements and spacing scale with viewport width and
height. At 1650px and below the header shows fewer tabs; at 1056px and below primary
measurements use two columns and the detail dock moves below the workspace. Every
route remains reachable from **Ещё**. On short screens long working content scrolls
inside the card; compact density caps prevent a small calibration from enlarging
text beyond its slots. The page stays bounded. No device detection service or
screen-specific dashboard copies are required.

For storage dashboards, apply the rendered configuration through Home Assistant's
dashboard editor/API after backing up the original. For YAML dashboards, back up
and replace the configured Lovelace YAML file, validate that the parsed content
matches the renderer's output, then reload the dashboard. JSON output is valid
YAML; it may also be serialized as ordinary YAML without changing its contents.
The storage-save API cannot write a YAML dashboard. Keep the existing dashboard
mode and avoid editing Home Assistant's internal storage files. No core restart
is needed for this dashboard-file change.

Each original view must appear in the bindings;
the renderer rejects a missing view. Original button templates are retained.
Entity IDs, device actions and routes are supplied by the owner, never guessed.

Measurement templates display `—` and **Нет данных** for unavailable/unknown
entities. An optional `guard_entity` prevents a stale derived meter from being
presented as a live measurement. Use `guard_entities` when an aggregate depends
on several measurements; every dependency must be available. Explicitly label partial-meter data. The preset
does not change any control service or local/cloud routing.

`hourly_generator(field)` reads an existing entity's `attributes.hourly.time`
and the selected hourly field for ApexCharts. Unix seconds are converted to
milliseconds; the chart horizon selects points. Missing values remain null and
explicit zero remains zero. Label apparent temperature as apparent temperature.
No forecast or departure data are fabricated when a provider is unavailable.

### Atmospheric hourly forecast

`forecast.atmospheric_forecast(...)` composes the selected photographic hero,
hourly strip, two compact ApexCharts plots and a Universal Card details dialog.
Its 6/24-hour switch is local to the card and resets to six hours on reload; it
creates no helper entity and calls no device service. The 24-hour strip scrolls
horizontally inside the card. The enclosing workspace keeps its viewport bound. Short screens retain scrolling
inside the workspace; the document itself does not grow. Both plots use the
allocated container height, including the inner `#graph`, with a zero parent
height offset. This avoids ApexCharts 2.2.3's responsive-config clone failure
when crossing a breakpoint.

Pass existing `weather_entity`, `sun_entity`, `clock_entity`, `rain_entity`,
`feels_entity`, `details_cards` and a unique `card_id`. The rain provider must
expose Unix-second `attributes.hourly.time`, WMO `weather_code` and
`precipitation` in millimeters. The feels-like provider supplies its own Unix-second
`hourly.time` and `apparent_temperature` in Celsius. Temperatures are joined by
timestamp, never by array position. The composer includes the required Button
Card templates automatically. Preserve the caller's actual entity bindings and
details actions when replacing an existing forecast.

The hero photograph follows the **current** Home Assistant weather condition;
the hourly icons follow each forecast point. Clear, cloudy and rainy conditions
have separate day/night photographs, selected by the existing sun entity.
Fog, snow and thunderstorms have their own photographs; wind uses the cloudy
landscape. Nighttime hourly icons use the sun entity's next rising/setting
timestamps. All nine generated landscape assets live in `assets/forecast/` and
are embedded in the theme as WebP; HACS installs them with the theme, without
separate local file uploads. Rebuild/check them with:

```sh
python3 tools/build_theme_assets.py
python3 tools/build_theme_assets.py --check
```

If the sun is unavailable, day/night is unknown (a reported `clear-night` weather
state still selects the night image); other conditions retain a neutral daytime
photograph. An unavailable rain provider or an expired forecast horizon clears
the hero artwork and forecast. Missing temperature or rain remains `—`, and
zero rain remains `0 мм`. Missing hours retain their clock slot instead of
shifting later forecasts left. Current-condition artwork does not imply that the same
condition holds for every forecast hour. Unknown WMO codes get no guessed icon.

`styled(card, css, selector=...)` uses Card Mod's documented shadow-root styles
for nested cards. It also removes inherited card pseudo-element overlays that
would otherwise change the intended surfaces. Workspace scrolling stays inside
the card; details are closed dialogs and do not extend the document.
`visual_tile(card)` keeps the native tile's actions and features with horizontal
controls, 18px titles, 20px values, 36px icons and smaller padding. Groups of these
tiles use content-sized rows instead of stretching controls across the workspace.
Preset actions inside dialogs also use compact 18px text and 56px controls;
primary measurements keep their display typography.

**Ещё → Настройки панели** contains a live scale control. **100%** now uses the
previous **80%** appearance: panel fonts, icons, padding and vertical tracks are
20% smaller than the original baseline. Decrease or increase it in **5 percentage point** steps between **50%**
and **150%**, or reset to 100%. The preference is stored per browser and dashboard
and applies to every route after navigation and reload. Different tablets keep
their own values. New URL overrides use `bc_scale=100&bc_scale_base=80` and provide
a fallback when browser storage is unavailable. Legacy saved values and URLs
without `bc_scale_base` are converted to the new baseline; old 80% becomes new
100%. Conversion rounds to five-point steps and respects the new 50–150% bounds.
Versioned browser storage prevents converting a new preference again; the legacy
value remains intact. Native HA controls and dialogs keep their existing scale.

Scale uses the installed Button Card as a transparent canvas around the existing
Layout Card. `do_not_eval` preserves each child's entity/template context and
original actions. Only that canvas is zoomed; it still fills the available view.
The document, native Home Assistant interface and dialogs retain their normal
scale. Compact dialogs stay readable while the panel is zoomed. No additional
card runtime, device helper or Home Assistant service call is required.

Navigation's **Ещё** menu starts with **Показать интерфейс HA** / **Скрыть интерфейс
HA**. The control shows or hides Home Assistant's header and sidebar together.
The default is hidden. The choice is stored per browser and dashboard, survives
navigation and reload, and does not change other devices or dashboards. Kiosk
Mode's documented JavaScript templates read the preference; Button Card's
JavaScript action saves it and reloads the page. If browser storage is blocked,
the URL override still switches the current view. The layout subtracts the native
header height when it is visible, so the page remains bounded in either mode.

The same menu includes Settings, HACS and an editor link with `disable_km`,
which temporarily shows administration without changing the saved choice.
After HACS installs or updates a card, reload the entire browser tab to load its
current resource list. An already open tab can retain older Universal Card code
and omit newly installed Card Mod or Kiosk Mode until that reload, producing a
configuration error or default styling despite a correct server configuration.

## Development

```sh
python3 -m unittest discover -s tests -v
```

The formatter regression uses Node.js; the composer itself needs only Python's
standard library. Source templates are in `src`, the single HACS theme is in
`themes`. The generated weather artwork is embedded in the theme, so HACS manages
the asset with the theme. No device registry, credentials or private snapshots
belong in this repository.

See [package research](docs/package-research.md) for the reuse decision.
