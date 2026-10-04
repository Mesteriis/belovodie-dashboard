"""The selected atmospheric forecast, composed from existing HACS cards."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ICON_BASE = "https://cdn.jsdelivr.net/gh/w4mhi/weather-chart-card-ha@v1.7.4/dist/icons/"


def expression(body):
    return "[[[ " + (ROOT / "src/forecast-model.js").read_text() + "\nconst f=forecastModel(states,variables,hass);" + body + " ]]]"


def forecast_templates():
    def text(body):
        return expression(body)
    hero = {
        "show_name": True, "show_icon": False, "show_label": False,
        "tap_action": {"action": "none"},
        "name": text("return 'Ближайшие '+f.hours+(f.hours===24?' часа':' часов');"),
        "custom_fields": {
            "date": text("return f.date;"), "range": text("return f.range;"),
            "caption": "Ощущается",
            "condition": text("return f.condition;"),
            "weather": text("return f.icon?'<img alt=\"\" src=\"" + ICON_BASE + "'+f.icon+'.svg\">':'';")},
        "styles": {
            "card": [{"height":"100%"},{"box-sizing":"border-box"},{"border":"none"},
                     {"border-radius":"0"},{"padding":"22px 24px"},{"box-shadow":"none"},
                     {"background-color":text("return f.asset?'#7b9bae':'#0b2632';")},
                     {"background-blend-mode":"multiply"},
                     {"background-image":text("return f.asset?'var(--bc-forecast-'+f.asset+')':'none';")},
                     {"background-size":"cover"},{"background-position":"center"}],
            "grid":[{"grid-template-areas":'"n date" "range range" "caption caption" "weather condition"'},
                    {"grid-template-columns":"48px minmax(0,1fr)"},
                    {"grid-template-rows":"34px minmax(0,1fr) 28px 44px"},{"row-gap":"4px"}],
            "name":[{"grid-column":"1 / 3"},{"justify-self":"start"},{"align-self":"start"},
                    {"font-size":"clamp(20px,2.1vw,44px)"},{"font-weight":"500"}],
            "custom_fields":{
                "date":[{"position":"absolute"},{"right":"24px"},{"top":"24px"},{"font-size":"16px"},{"color":"#9fc5d6"}],
                "range":[{"align-self":"end"},{"justify-self":"start"},{"font-size":"clamp(46px,6vw,112px)"},{"line-height":"1.1"},{"font-weight":"500"}],
                "caption":[{"justify-self":"start"},{"font-size":"20px"}],
                "condition":[{"justify-self":"start"},{"font-size":"24px"},{"text-align":"left"}],
                "weather":[{"height":"44px"},{"width":"44px"}]},
        },
        "extra_styles":"ha-card::before,ha-card::after{display:none!important;content:none!important}"
                       "#container{color:#dceef5;text-shadow:0 1px 8px #001820}#weather img{width:100%;height:100%;filter:brightness(0) saturate(100%) invert(72%) sepia(39%) saturate(1490%) hue-rotate(160deg) brightness(99%) contrast(89%)}"
                       "@media(max-width:1056px){#date{font-size:13px!important;top:10px!important;right:12px!important}"
                       "#name{font-size:20px!important;max-width:66%;white-space:normal}#caption{font-size:16px!important}"
                       "#condition{font-size:18px!important}}",
    }
    hour = {
        "show_name":False,"show_icon":False,"show_label":False,"tap_action":{"action":"none"},
        "custom_fields":{
            "time":text("const p=f.slots[variables.slot];return p?f.timeLabel(p.time):'—';"),
            "weather":text("const p=f.slots[variables.slot];return p?.icon?'<img alt=\"\" src=\""+ICON_BASE+"'+p.icon+'.svg\">':'';"),
            "temperature":text("const p=f.slots[variables.slot];return p?.temperature===null||!p?'—':Math.round(p.temperature)+'°';"),
            "rain":text("const p=f.slots[variables.slot];return '<ha-icon icon=\"mdi:water\"></ha-icon> '+f.formatRain(p?.precipitation??null);"),
        },
        "styles":{
            "card":[{"height":"100%"},{"box-sizing":"border-box"},{"background":"transparent"},
                    {"border":"none"},{"border-radius":"0"},{"padding":"8px 0"},{"box-shadow":"none"}],
            "grid":[{"grid-template-areas":'"time" "weather" "temperature" "rain"'},
                    {"grid-template-columns":"1fr"},{"grid-template-rows":"minmax(0,1fr) minmax(0,3fr) minmax(0,2fr) minmax(0,1fr)"}],
            "custom_fields":{
                "time":[{"font-size":"22px"},{"color":"#9fc5d6"}],
                "weather":[{"height":"100%"},{"max-height":"74px"},{"width":"74px"},{"justify-self":"center"}],
                "temperature":[{"font-size":"42px"},{"font-weight":"500"},{"color":"#dceef5"}],
                "rain":[{"font-size":"18px"},{"color":"#9fc5d6"}]},
        },
        "extra_styles":"ha-card::before,ha-card::after{display:none!important;content:none!important}"
                       "ha-card{container-type:size}#container{height:100%;min-height:0}"
                       "#container>*{min-height:0;line-height:1.1}#time{font-size:clamp(12px,14cqh,22px)!important}"
                       "#temperature{font-size:clamp(20px,26cqh,42px)!important}#rain{font-size:clamp(11px,12cqh,18px)!important}"
                       "#weather{width:100%!important;max-width:74px;min-height:0}"
                       "#weather img{width:100%;height:100%;object-fit:contain;filter:brightness(0) saturate(100%) invert(72%) sepia(39%) saturate(1490%) hue-rotate(160deg) brightness(99%) contrast(89%)}#rain ha-icon{--mdc-icon-size:1em;color:#45c7e8;vertical-align:middle}"
                       "@media(max-width:1056px){#time{font-size:14px!important}#temperature{font-size:26px!important}"
                       "#rain{font-size:13px!important}#weather{width:34px!important;height:34px!important}}",
    }
    return {"bc_forecast_hero":hero,"bc_forecast_hour":hour}


def atmospheric_forecast(*, weather_entity, rain_entity, feels_entity, sun_entity,
                         clock_entity, details_cards, card_id):
    """All providers/actions are supplied by the owner; this preset creates none."""
    from compose import button, grid, hourly_generator, modal, styled, tabs
    if not all(isinstance(e,str) and '.' in e for e in
               [weather_entity,rain_entity,feels_entity,sun_entity,clock_entity]):
        raise ValueError("Forecast requires existing weather, rain, feels-like, sun and clock entities")
    bindings = dict(weather_entity=weather_entity,rain_entity=rain_entity,
                    feels_entity=feels_entity,sun_entity=sun_entity)
    triggers = [weather_entity,rain_entity,feels_entity,sun_entity,clock_entity]

    def graph(hours, rain=False):
        opts = {
            "chart":{"height":"100%","parentHeightOffset":0,"toolbar":{"show":False},"animations":{"enabled":False},
                     "fontFamily":"Inter, Segoe UI, sans-serif","foreColor":"#9fc5d6"},
            "grid":{"borderColor":"#244452","padding":{"top":0,"bottom":-6,"left":46,"right":12}},
            "stroke":{"width":0 if rain else 3,"curve":"smooth"},
            "markers":{"size":0 if rain else 5},"legend":{"show":False},
            "tooltip":{"theme":"dark"},"dataLabels":{"enabled":False},
            "xaxis":{"type":"datetime","labels":{"show":False},"axisTicks":{"show":False},"axisBorder":{"show":False}},
            "yaxis":{"min":0 if rain else "EVAL:function(v){return Math.floor(v-2);}",
                     "tickAmount":2,"decimalsInFloat":1 if rain else 0,
                     "labels":{"minWidth":24,"maxWidth":24,"style":{"fontSize":"16px","colors":"#9fc5d6"}},
                     "title":{"text":"Осадки, мм" if rain else "Ощущается °C",
                              "style":{"fontSize":"12px","fontWeight":400,"color":"#9fc5d6"}}},
            "plotOptions":{"bar":{"columnWidth":"48%","borderRadius":2}},
        }
        if not rain:
            opts['yaxis']['max']="EVAL:function(v){return Math.ceil(v+2);}"
        card={"type":"custom:apexcharts-card","graph_span":f"{hours}h","span":{"start":"hour"},
              "header":{"show":False},"update_interval":"1min","apex_config":opts,
              "series":[{"entity":rain_entity if rain else feels_entity,"name":"Осадки" if rain else "Ощущается",
                         "type":"column" if rain else "line","color":"#2eb7e8" if rain else "#48c7ef",
                         "float_precision":1,"data_generator":hourly_generator("precipitation" if rain else "apparent_temperature"),
                         "show":{"in_header":False,"legend_value":False}}]}
        return styled(card,':host{height:100%;display:block}ha-card{background:none!important;border:0!important;padding:0!important;box-shadow:none!important;height:100%!important}.wrapper{display:block!important;padding:0!important}.wrapper,#graph-wrapper,#graph{height:100%;min-height:0;margin:0!important}#spinner-wrapper{position:absolute;right:6px;top:6px;height:auto;min-height:0}', 'apexcharts-card')

    horizons=[]
    for hours in (6,24):
        values={**bindings,'hours':hours}
        hero=button('',template='bc_forecast_hero',entity=rain_entity,
                    triggers_update=triggers,variables=values)
        # Let the template provide its horizon-aware title instead of HA's entity name.
        hero.pop('name')
        slots=[button('',template='bc_forecast_hour',entity=rain_entity,
                      triggers_update=triggers,variables={**values,'slot':i}) for i in range(0,hours,3 if hours==24 else 1)]
        strip=styled(grid(slots,f'repeat({len(slots)},minmax(0,1fr))',height='100%',gap='0px'),
                     ':host{height:100%;min-height:0;display:block}', 'layout-card')
        strip['card_mod']['style']['layout-card$'] = {
            '.': ':host{height:100%;min-height:0;display:block}',
            'grid-layout$': ':host{height:100%;min-height:0}div{height:100%;min-height:0;box-sizing:border-box;grid-template-rows:minmax(0,1fr)!important;overflow:hidden!important}button-card{min-height:0;height:100%}'
        }
        details=modal('Подробнее','mdi:chevron-right',details_cards,f'{card_id}-details-{hours}')
        details['custom_css']['css']+='\n.universal-card{background:none!important;border:0!important}.header{height:calc(100% - 8px);box-sizing:border-box;width:max-content;margin:4px 16px 4px auto;border:1px solid #24505d;border-radius:28px;justify-content:flex-end;padding:0 16px!important}.header-left{display:none!important}.header-title{font-size:16px!important;font-weight:400!important;text-align:right!important}.header-content{align-items:flex-end!important}.header-right{margin-left:0!important}.expand-icon{transform:rotate(-90deg)!important;width:18px!important;height:18px!important}'
        panel=grid([hero,strip,graph(hours),graph(hours,True),details],
                   rows='43% 22% 17% 12% 6%',height='100%',gap='0px')
        horizons.append({'label':f'{hours} ч','cards':[panel]})
    result=tabs(horizons,card_id)
    result['tabs_config'].update(show_icons=False,content_padding='0px',tab_min_width='60px')
    result['custom_css']['css']=(ROOT/'src/forecast-tabs.css').read_text()
    return result
