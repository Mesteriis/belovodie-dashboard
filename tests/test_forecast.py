import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from forecast import atmospheric_forecast, forecast_templates


class ForecastTests(unittest.TestCase):
    def model(self, *, code=3, weather='cloudy', sun='above_horizon', hours=6,
              rain_state='1', feels_state='1', times=None, temperature=None, precipitation=None):
        values = dict(weather_entity='weather.test', rain_entity='sensor.rain',
                      feels_entity='sensor.feels', sun_entity='sun.test', hours=hours)
        times = [0, 3600, 7200, 10800, 14400, 86400] if times is None else times
        states = {
            'sensor.rain':dict(state=rain_state, attributes={'hourly':{'time':times,
                'weather_code':[code]*len(times), 'precipitation':precipitation or [0, None, .4, .5, .6, .7]}}),
            'sensor.feels':dict(state=feels_state, attributes={'hourly':{'time':times,
                'apparent_temperature':temperature or [10, None, 12, 13, 14, 15]}}),
            'sun.test':dict(state=sun, attributes={'next_setting':'1970-01-01T03:00:00Z',
                'next_rising':'1970-01-01T08:00:00Z'}),
            'weather.test':dict(state=weather, attributes={}),
        }
        script = (ROOT / 'src/forecast-model.js').read_text()
        script += '\nconst f=forecastModel('+json.dumps(states)+','+json.dumps(values)+', {locale:{language:"ru"},config:{time_zone:"UTC"}},3600000);'
        script += 'console.log(JSON.stringify({...f,firstTime:f.points.length?f.timeLabel(f.points[0].time):null}));'
        return json.loads(subprocess.check_output(['node','-e',script], text=True))

    def test_zero_missing_and_horizon_boundaries(self):
        f = self.model()
        self.assertEqual([p['time'] for p in f['points']], [3600,7200,10800,14400])
        self.assertIsNone(f['points'][0]['temperature'])
        self.assertIsNone(f['points'][0]['precipitation'])
        self.assertEqual(f['range'], '12–14°')
        self.assertEqual(f['firstTime'], '01:00')
        self.assertEqual(self.model(hours=24)['points'][-1]['time'], 86400)
        f = self.model(precipitation=[8,0,None,.5,.6,.7])
        self.assertEqual(f['points'][0]['precipitation'], 0)
        self.assertIsNone(f['points'][1]['precipitation'])

    def test_unavailable_providers_never_reuse_stale_attributes(self):
        f = self.model(rain_state='unavailable')
        self.assertEqual(f['points'], [])
        self.assertIsNone(f['asset'])
        self.assertEqual(f['condition'],'Нет прогноза')
        f = self.model(feels_state='unknown')
        self.assertEqual(f['range'],'—')
        self.assertTrue(all(p['temperature'] is None for p in f['points']))

    def test_weather_backgrounds_and_real_sunset(self):
        cases = {'sunny':'clear-day','clear-night':'clear-night','cloudy':'cloudy-day',
                 'partlycloudy':'cloudy-day','rainy':'rain-day','pouring':'rain-day',
                 'fog':'fog','snowy':'snow','snowy-rainy':'snow','lightning':'storm',
                 'lightning-rainy':'storm','windy':'cloudy-day','unknown':None}
        for state, asset in cases.items():
            sun = 'below_horizon' if state=='clear-night' else 'above_horizon'
            self.assertEqual(self.model(weather=state,sun=sun)['asset'], asset)
        self.assertEqual(self.model(weather='rainy',sun='below_horizon')['asset'],'rain-night')
        points=self.model(code=0)['points']
        self.assertEqual(points[1]['icon'],'clear-day')
        self.assertEqual(points[2]['icon'],'clear-night')

    def test_wmo_edge_cases_and_unknown_codes(self):
        cases={0:'clear',3:'cloudy',45:'fog',57:'rain',67:'rain',77:'snow',
               82:'rain',85:'snow',95:'storm',99:'storm',None:None,999:None}
        for code, kind in cases.items():
            self.assertEqual(self.model(code=code)['points'][0]['kind'],kind)

    def test_missing_hours_do_not_shift_the_hourly_strip(self):
        f=self.model(times=[3600,10800],temperature=[12,14],precipitation=[0,.1])
        self.assertEqual(len(f['slots']),6)
        self.assertEqual(f['slots'][0]['temperature'],12)
        self.assertEqual(f['slots'][1]['time'],7200)
        self.assertIsNone(f['slots'][1]['temperature'])
        self.assertEqual(f['slots'][2]['temperature'],14)

    def test_composition_preserves_private_details_and_local_horizon_control(self):
        source={'type':'tile','entity':'sensor.test','tap_action':{'action':'more-info'}}
        config=atmospheric_forecast(weather_entity='weather.test',rain_entity='sensor.rain',
            feels_entity='sensor.feels',sun_entity='sun.test',clock_entity='sensor.clock',
            details_cards=[source],card_id='bc-test-forecast')
        self.assertEqual([t['label'] for t in config['tabs']],['6 ч','24 ч'])
        self.assertFalse(config['remember_mode_state'])
        self.assertNotIn('call-service',json.dumps(config))
        for tab,hours in zip(config['tabs'],[6,24]):
            panel=tab['cards'][0]
            self.assertEqual(panel['cards'][0]['variables']['hours'],hours)
            self.assertEqual([c['variables']['slot'] for c in panel['cards'][1]['card']['cards']],
                             list(range(0,hours,3 if hours==24 else 1)))
            self.assertEqual(panel['cards'][4]['body']['cards'][0]['entity'],source['entity'])
        for tab in config['tabs']:
            for index in (2,3):
                chart=tab['cards'][0]['cards'][index]['card']['apex_config']
                self.assertNotIn('responsive',chart)
                self.assertEqual(chart['chart']['height'],'100%')
                self.assertEqual(chart['chart']['parentHeightOffset'],0)
        self.assertEqual(source['tap_action'],{'action':'more-info'})
        self.assertEqual(set(forecast_templates()),{'bc_forecast_hero','bc_forecast_hour'})
        self.assertNotIn('name',config['tabs'][0]['cards'][0]['cards'][0])

    def test_hour_strip_uses_bounded_grid_and_height_relative_typography(self):
        config=atmospheric_forecast(weather_entity='weather.test',rain_entity='sensor.rain',
            feels_entity='sensor.feels',sun_entity='sun.test',clock_entity='sensor.clock',
            details_cards=[],card_id='bc-test-forecast')
        for tab in config['tabs']:
            strip=tab['cards'][0]['cards'][1]
            self.assertIn('minmax(0,1fr)',strip['card']['layout']['grid-template-columns'])
            css=strip['card_mod']['style']['layout-card$']['grid-layout$']
            self.assertIn('grid-template-rows:minmax(0,1fr)',css)
            self.assertIn('overflow:hidden',css)
        hour=forecast_templates()['bc_forecast_hour']
        self.assertIn('container-type:size',hour['extra_styles'])
        self.assertIn('26cqh',hour['extra_styles'])

    def test_all_icons_exist_in_the_pinned_library(self):
        supported={'clear-day','clear-night','cloudy','overcast-day-rain','overcast-night-rain',
                   'snow','fog-day','fog-night','thunderstorms-day-rain','thunderstorms-night-rain'}
        for code in [0,1,2,3,45,48,51,53,55,56,57,61,63,65,66,67,71,73,75,77,80,81,82,85,86,95,96,99]:
            for night in ['above_horizon','below_horizon']:
                self.assertTrue(all(p['icon'] in supported for p in self.model(code=code,sun=night)['points']))
