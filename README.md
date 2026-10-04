# Belovodie Command

A dark petrol and cyan Home Assistant theme and Lovelace composition preset.
The desktop layout has four primary measurements, a tabbed workspace, a detail
dock and quick actions. It targets a 2200 × 1440 display. Details open in Universal
Card dialogs; long content scrolls inside the workspace or dialog.

This repository does not implement a new card. It composes existing projects:

| Function | Existing package |
| --- | --- |
| Measurements, actions and navigation | [Button Card](https://github.com/custom-cards/button-card) |
| Viewport grid | [Layout Card](https://github.com/thomasloven/lovelace-layout-card) |
| Tabs and dialogs | [Universal Card](https://github.com/Mesteriis/universal-card) |
| Forecast and precipitation | [Weather Chart Card HA](https://github.com/w4mhi/weather-chart-card-ha) |
| Historical charts | [ApexCharts](https://github.com/RomRider/apexcharts-card), [Mini Graph Card](https://github.com/kalkih/mini-graph-card) |
| Dashboard chrome | [Kiosk Mode](https://github.com/NemesisRE/kiosk-mode) |

## Installation

Add `Mesteriis/belovodie-dashboard` to HACS custom repositories with type **Theme**,
then download **Belovodie Command**. Enable your normal `frontend: themes:` include
if you have not already enabled themes. Reload themes and select **Belovodie
Command** on the intended dashboard views. Install the cards above through HACS.
No Home Assistant core restart is needed for this preset when themes are already
configured.

The theme changes colours and typography. The optional offline composer produces
the bounded layout; downloading a theme does not rewrite an existing dashboard.
Provide an existing Lovelace JSON configuration and a local JSON list of page
bindings (`path`, `title`, four `metrics`, workspace `tabs`, `dock`, `footer`, `last`).
Keep both files private. The renderer has no network access or credentials:

```sh
python3 tools/render.py original.json pages.json output.json \
  --url-path dashboard-example --clock-entity sensor.time
```

Apply the rendered configuration through Home Assistant's dashboard editor/API
after backing up the original. Each original view must appear in the bindings;
the renderer rejects a missing view. Original button templates are retained.
Entity IDs, device actions and routes are supplied by the owner, never guessed.

Measurement templates display `—` and **Нет данных** for unavailable/unknown
entities. An optional `guard_entity` prevents a stale derived meter from being
presented as a live measurement. Explicitly label partial-meter data. The preset
does not change any control service or local/cloud routing.

Navigation's **Ещё** menu includes Settings, HACS and an editor link with
`disable_km` so hiding dashboard chrome does not remove access to administration.
Kiosk Mode applies only to the rendered dashboard.

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
