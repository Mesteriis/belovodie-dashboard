# Existing-card decision, 2026-10-04

Checked HACS's current default dashboard catalog (772 repositories), current
repository documentation, the installed resources and the target Home Assistant
configuration before implementation.

Button Card already supports the reference's measurements, icons, actions and
navigation. Layout Card accepts CSS grid rows and a bounded viewport height.
Universal Card supplies tabs, lazy dialogs and Escape/backdrop closing. Its own
repository was updated separately: 1.0.9 fixes grid spacing, valid scrolling CSS
and dialog context; 1.0.10 opens initially expanded inline modes correctly.
Charts use established packages.
Therefore this project is one cohesive theme/layout preset, not another card.
Unrelated future frontend cards must have their own repositories.

For weather, compared [Weather Chart Card HA](https://github.com/w4mhi/weather-chart-card-ha),
[Clock Weather Card](https://github.com/pkissling/clock-weather-card),
[Nimbus](https://github.com/maxfok/nimbus-weather-card), and
[Platinum Weather Card Plus Charts](https://github.com/rudizl/platinum-weather-card-plus-charts).
Weather Chart Card HA v1.7.4 supports forecast-only mode, six hourly forecasts,
condition icons, precipitation bars and configurable colours. Its fixed layout
did not reproduce the selected reference as closely as the existing ApexCharts
and Button Card composition, so it is optional rather than a preset dependency.
The weather icon assets use the existing Basmilius icon library. The original
[Weather Chart Card](https://github.com/mlamberts78/weather-chart-card) explicitly
states that it is no longer maintained; use the maintained fork.

Navbar Card and Bubble Card were also considered. The selected composition can
use Button Card plus Universal Card for its existing menu/dialog interactions,
so adding another navigation/dialog runtime is unnecessary.

Installation follows [HACS theme requirements](https://hacs.xyz/docs/publish/theme/):
one theme file in `themes`. This project does not bundle or fork the dependencies.

For the requested 50–150% scale in five-point steps, inspected the installed
[Browser Control Card](https://github.com/mathoudebine/homeassistant-browser-control-card)
and Button Card 7.0.1 source. Browser Control Card's zoom actions use ten-point
steps on the entire document, without the requested bounded browser preference.
Button Card already supports nested cards with `do_not_eval` and JavaScript
actions. Its existing runtime therefore composes the scoped canvas and settings
controls without creating another card repository. Native detail cards use
compact Card Mod styles; existing actions and features are retained.

## Animated weather measurement (2026-10-04)

Reviewed existing weather cards before changing the preset. Atmo Weather Card
v7.5.0 (`whyisthisbroken/atmo-weather-card`, tag commit
`809c54aecfc5148a7e7d47cd7ca43699a376f211`, MIT) provides a canvas renderer for
Home Assistant weather states, real sun-based day/night, wind, clouds and
precipitation. Its HACS package includes the five required JavaScript modules.
Installed file hashes matched the tag exactly. This preset uses Atmo behind the
existing Button Card rather than publishing another renderer or borrowing its
source. The left-side scrim keeps the original measurement readable.

Alternatives: JonesChi/animated-weather-card emphasizes forecast rows and does
not preserve our current humidity/wind/feels-like composition directly;
maxfok/nimbus-weather-card and teuchezh/dynamic-weather-card provide whole weather
layouts. Atmo can serve strictly as the sky layer while the original measurement
keeps its fields, dimensions and actions. Its renderer pauses offscreen; this
preset adds a CSS reduced-motion fallback and hides the sky for unavailable data.

Primary references:
- https://github.com/whyisthisbroken/atmo-weather-card/tree/v7.5.0
- https://github.com/JonesChi/animated-weather-card
- https://github.com/maxfok/nimbus-weather-card
- https://github.com/teuchezh/dynamic-weather-card

## Atmospheric hourly workspace (2026-10-04)

Rechecked Atmo's forecast slider and
[Hourly Weather](https://github.com/decompil3d/lovelace-hourly-weather) before
implementing the selected scene/strip/plots concept. Their built-in forecast
layouts do not reproduce this composition or the existing separate Open-Meteo
feels-like/rain providers. No new card package is created: Button Card owns the
photographic hero and hourly values, ApexCharts owns both plots, and Universal
Card owns the horizon switch and details dialog. Atmo remains the installed
renderer for the smaller current-weather measurement.

Weather-code classification follows the
[Open-Meteo WMO table](https://open-meteo.com/en/docs), including freezing drizzle,
freezing rain, snow grains and snow showers. Missing codes are not treated as
cloudy. Six/24-hour horizons, real sun timing and timestamp joins are tested
independently of the UI. The generated photographic assets match the selected
mockup's mountain/lake palette; they contain no weather data or location details.
