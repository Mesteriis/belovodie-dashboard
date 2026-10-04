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
        "name": text("return 'Ближайшие '+f.hours+' часов';"),
        "custom_fields": {
            "date": text("return f.date;"), "range": text("return f.range;"),
            "caption": "Ощущается",
            "condition": text("return f.condition;"),
            "weather": text("return f.icon?'<img alt=\"\" src=\"" + ICON_BASE + "'+f.icon+'.svg\">':'';")},
        "styles": {
            "card": [{"height":"100%"},{"box-sizing":"border-box"},{"border":"none"},
                     {"border-radius":"0"},{"padding":"22px 24px"},{"box-shadow":"none"},
                     {"background-color":"#0b2632"},
                     {"background-image":text("return f.asset?'var(--bc-forecast-'+f.asset+')':'none';")},
                     {"background-size":"cover"},{"background-position":"center"}],
            "grid":[{"grid-template-areas":'"n date" "range range" "caption caption" "weather condition"'},
                    {"grid-template-columns":"48px minmax(0,1fr)"},
                    {"grid-template-rows":"34px minmax(0,1fr) 28px 44px"},{"row-gap":"4px"}],
            "name":[{"grid-column":"1 / 3"},{"justify-self":"start"},{"align-self":"start"},
                    {"font-size":"clamp(20px,2.1vw,34px)"},{"font-weight":"500"}],
            "custom_fields":{
                "date":[{"position":"absolute"},{"right":"24px"},{"top":"24px"},{"font-size":"16px"},{"color":"#9fc5d6"}],
                "range":[{"align-self":"end"},{"justify-self":"start"},{"font-size":"clamp(46px,6vw,96px)"},{"line-height":"1.1"},{"font-weight":"500"}],
                "caption":[{"justify-self":"start"},{"font-size":"20px"}],
                "condition":[{"justify-self":"start"},{"font-size":"24px"},{"text-align":"left"}],
                "weather":[{"height":"44px"},{"width":"44px"}]},
        },
        "extra_styles":"#container{color:#dceef5;text-shadow:0 1px 8px #001820}#weather img{width:100%;height:100%}"
                       "@media(max-width:1056px){#date{font-size:13px!important;top:10px!important;right:12px!important}"
                       "#name{font-size:20px!important;max-width:66%;white-space:normal}#caption{font-size:16px!important}"
                       "#condition{font-size:18px!important}}",
    }
    hour = {
        "show_name":False,"show_icon":False,"show_label":False,"tap_action":{"action":"none"},
        "custom_fields":{
            "time":text("const p=f.points[variables.slot];return p?f.timeLabel(p.time):'—';"),
            "weather":text("const p=f.points[variables.slot];return p?.icon?'<img alt=\"\" src=\""+ICON_BASE+"'+p.icon+'.svg\">':'';"),
            "temperature":text("const p=f.points[variables.slot];return p?.temperature===null||!p?'—':Math.round(p.temperature)+'°';"),
            "rain":text("const p=f.points[variables.slot];return '<ha-icon icon=\"mdi:water\"></ha-icon> '+f.formatRain(p?.precipitation??null);"),
        },
        "styles":{
            "card":[{"height":"100%"},{"box-sizing":"border-box"},{"background":"transparent"},
                    {"border":"none"},{"border-radius":"0"},{"padding":"8px 0"},{"box-shadow":"none"}],
            "grid":[{"grid-template-areas":'"time" "weather" "temperature" "rain"'},
                    {"grid-template-columns":"1fr"},{"grid-template-rows":"24px minmax(28px,1fr) 40px 24px"}],
            "custom_fields":{
                "time":[{"font-size":"18px"},{"color":"#9fc5d6"}],
                "weather":[{"height":"46px"},{"width":"46px"},{"justify-self":"center"}],
                "temperature":[{"font-size":"34px"},{"font-weight":"500"},{"color":"#dceef5"}],
                "rain":[{"font-size":"16px"},{"color":"#9fc5d6"}]},
        },
        "extra_styles":"#weather img{width:100%;height:100%}#rain ha-icon{--mdc-icon-size:18px;color:#45c7e8;vertical-align:middle}"
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
            "chart":{"height":"100%","toolbar":{"show":False},"animations":{"enabled":False},
                     "fontFamily":"Inter, Segoe UI, sans-serif","foreColor":"#9fc5d6"},
            "grid":{"borderColor":"#244452","padding":{"top":0,"bottom":-6,"left":4,"right":12}},
            "stroke":{"width":0 if rain else 2,"curve":"smooth"},
            "markers":{"size":0 if rain else 3},"legend":{"show":False},
            "tooltip":{"theme":"dark"},"dataLabels":{"enabled":False},
            "xaxis":{"type":"datetime","labels":{"show":False},"axisTicks":{"show":False},"axisBorder":{"show":False}},
            "yaxis":{"min":0 if rain else "EVAL:function(v){return Math.floor(v-2);}",
                     "tickAmount":2,"decimalsInFloat":1 if rain else 0,
                     "labels":{"style":{"fontSize":"14px","colors":"#9fc5d6"}},
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
        return styled(card,':host{height:100%;display:block}ha-card{background:none!important;border:0!important;padding:0!important;box-shadow:none!important;height:100%!important}.wrapper,#graph-wrapper{height:100%;margin:0!important}#spinner-wrapper{position:absolute;right:6px;top:6px;height:auto;min-height:0}', 'apexcharts-card')

    horizons=[]
    for hours in (6,24):
        values={**bindings,'hours':hours}
        hero=button('',template='bc_forecast_hero',entity=rain_entity,
                    triggers_update=triggers,variables=values)
        slots=[button('',template='bc_forecast_hour',entity=rain_entity,
                      triggers_update=triggers,variables={**values,'slot':i}) for i in range(hours)]
        strip=styled(grid(slots,f'repeat({hours},minmax(72px,1fr))',height='100%',gap='0px'),
                     ':host{height:100%;display:block;overflow-x:auto;overscroll-behavior:contain;scrollbar-width:thin}#root{height:100%;min-height:0}.card{border-right:1px solid #244452}.card:last-child{border-right:0}', 'layout-card')
        details=modal('Подробнее','mdi:chevron-right',details_cards,f'{card_id}-details-{hours}')
        details['custom_css']['css']+='\n.universal-card{background:none!important;border:0!important}.header{height:100%;justify-content:flex-end;padding:0 20px!important}.header-left,.expand-icon{display:none!important}.header-title{font-size:16px!important;font-weight:400!important}.header-right{margin-left:0!important}'
        panel=grid([hero,strip,graph(hours),graph(hours,True),details],
                   rows='43% 24% 15% 11% 7%',height='100%',gap='0px')
        horizons.append({'label':f'{hours} ч','cards':[panel]})
    result=tabs(horizons,card_id)
    result['tabs_config'].update(show_icons=False,content_padding='0px',tab_min_width='60px')
    result['custom_css']['css']=(ROOT/'src/forecast-tabs.css').read_text()
    return result
