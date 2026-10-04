# Existing-card decision, 2026-10-04

Checked HACS's current default dashboard catalog (772 repositories), current
repository documentation, the installed resources and the target Home Assistant
configuration before implementation.

Button Card already supports the reference's measurements, icons, actions and
navigation. Layout Card accepts CSS grid rows and a bounded viewport height.
Universal Card 1.0.8 already supplies tabs, lazy dialogs, Escape/backdrop closing
and Home Assistant context for nested cards. Charts use established packages.
Therefore this project is one cohesive theme/layout preset, not another card.
Unrelated future frontend cards must have their own repositories.

For weather, compared [Weather Chart Card HA](https://github.com/w4mhi/weather-chart-card-ha),
[Clock Weather Card](https://github.com/pkissling/clock-weather-card),
[Nimbus](https://github.com/maxfok/nimbus-weather-card), and
[Platinum Weather Card Plus Charts](https://github.com/rudizl/platinum-weather-card-plus-charts).
Weather Chart Card HA v1.7.4 supports forecast-only mode, six hourly forecasts,
condition icons, precipitation bars and configurable colours. The original
[Weather Chart Card](https://github.com/mlamberts78/weather-chart-card) explicitly
states that it is no longer maintained; use the maintained fork.

Navbar Card and Bubble Card were also considered. The selected composition can
use Button Card plus Universal Card for its existing menu/dialog interactions,
so adding another navigation/dialog runtime is unnecessary.

Installation follows [HACS theme requirements](https://hacs.xyz/docs/publish/theme/):
one theme file in `themes`. This project does not bundle or fork the dependencies.
