// Button Card templates: bindings remain in the caller's private configuration.
function forecastModel(states, variables, hass, now = Date.now()) {
  const invalid = e => !e || ['unknown', 'unavailable'].includes(e.state);
  const number = value => value === null || value === undefined || value === '' ||
    typeof value === 'boolean' || !Number.isFinite(Number(value)) ? null : Number(value);
  const rain = states[variables.rain_entity];
  const feels = states[variables.feels_entity];
  const weather = states[variables.weather_entity];
  const sun = states[variables.sun_entity];
  const hours = variables.hours === 24 ? 24 : 6;
  const base = Math.floor(now / 3600000) * 3600;
  const rh = invalid(rain) ? null : rain.attributes?.hourly;
  const fh = invalid(feels) ? null : feels.attributes?.hourly;
  const temperatures = new Map();
  if (Array.isArray(fh?.time)) fh.time.forEach((time, i) => {
    const t = number(time);
    if (t !== null) temperatures.set(t, number(fh.apparent_temperature?.[i]));
  });
  const rising = Date.parse(sun?.attributes?.next_rising);
  const setting = Date.parse(sun?.attributes?.next_setting);
  function nightAt(time) {
    if (invalid(sun)) return null;
    if (!Number.isFinite(rising) || !Number.isFinite(setting))
      return sun.state === 'below_horizon' ? true : sun.state === 'above_horizon' ? false : null;
    return sun.state === 'above_horizon'
      ? time * 1000 >= setting && time * 1000 < rising
      : sun.state === 'below_horizon' ? time * 1000 < rising || time * 1000 >= setting : null;
  }
  function condition(code) {
    if ([0, 1].includes(code)) return 'clear';
    if ([2, 3].includes(code)) return 'cloudy';
    if ([45, 48].includes(code)) return 'fog';
    if ([51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82].includes(code)) return 'rain';
    if ([71, 73, 75, 77, 85, 86].includes(code)) return 'snow';
    if ([95, 96, 99].includes(code)) return 'storm';
    return null;
  }
  function icon(kind, night) {
    const phase = night === true ? 'night' : 'day';
    return ({clear: 'clear-' + phase, cloudy: night === true ? 'overcast-night' : 'cloudy',
      rain: 'overcast-' + phase + '-rain', snow: 'snow', fog: 'fog',
      storm: 'thunderstorms-' + phase + '-rain'})[kind] || null;
  }
  const points = [];
  if (Array.isArray(rh?.time)) rh.time.forEach((raw, i) => {
    const time = number(raw);
    if (time === null || time < base || time >= base + hours * 3600) return;
    const code = number(rh.weather_code?.[i]);
    const kind = condition(code);
    const night = nightAt(time);
    points.push({time, temperature: temperatures.get(time) ?? null,
      precipitation: number(rh.precipitation?.[i]), kind, night, icon: icon(kind, night)});
  });
  points.sort((a, b) => a.time - b.time);
  const temps = points.map(p => p.temperature).filter(v => v !== null);
  const kinds = {sunny:'clear', 'clear-night':'clear', partlycloudy:'cloudy', cloudy:'cloudy',
    rainy:'rain', pouring:'rain', lightning:'storm', 'lightning-rainy':'storm',
    fog:'fog', snowy:'snow', 'snowy-rainy':'snow', windy:'cloudy', 'windy-variant':'cloudy'};
  const kind = invalid(weather) ? null : kinds[weather.state] || null;
  const night = invalid(sun) ? weather?.state === 'clear-night' ? true : null : sun.state === 'below_horizon';
  const asset = points.length && kind ? kind + (['clear','cloudy','rain'].includes(kind)
    ? '-' + (night === true ? 'night' : 'day') : '') : null;
  const labels = {clear:'Ясно', cloudy:'Пасмурно', rain:'Дождь', fog:'Туман', snow:'Снег', storm:'Гроза'};
  const min = temps.length ? Math.round(Math.min(...temps)) : null;
  const max = temps.length ? Math.round(Math.max(...temps)) : null;
  const locale = hass?.locale?.language || 'ru';
  const timezone = hass?.config?.time_zone || 'UTC';
  const timeLabel = time => new Date(time * 1000).toLocaleTimeString(locale,
    {timeZone:timezone, hour:'2-digit', minute:'2-digit'});
  return {hours, points, asset, kind, night, icon:icon(kind, night),
    range: min === null ? '—' : min === max ? min + '°' : min + '–' + max + '°',
    condition: !points.length ? 'Нет прогноза' : labels[kind] || 'Нет текущих данных',
    date: new Date(now).toLocaleDateString(locale,{timeZone:timezone,day:'numeric',month:'long'}),
    timeLabel, formatRain: value => value === null ? '—' : value.toLocaleString(locale,{maximumFractionDigits:1}) + ' мм'};
}
