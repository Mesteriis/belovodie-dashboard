// ApexCharts data_generator: provider timestamps are Unix seconds.
const hourly = entity?.attributes?.hourly;
const field = __FIELD__;
if (!entity || ['unknown', 'unavailable'].includes(entity.state) ||
    !Array.isArray(hourly?.time) || !Array.isArray(hourly[field])) return [];
return hourly.time.map((time, i) => {
  const raw = hourly[field][i];
  return [Number(time) * 1000, raw === null || raw === undefined || raw === '' ? null : Number(raw)];
}).filter(([time, value]) => Number.isFinite(time) && time >= start.getTime() &&
  time < end.getTime() && (value === null || Number.isFinite(value)));
