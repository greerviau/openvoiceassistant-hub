import typing

class WhatToWear:
    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova

        self.weather_integration = self.ova.integration_manager.get_integration_module('open_weather_map')

    def _check_temp(self, temp):
        if temp < -7:   # ~20F
            return "very cold, so you should bundle up"
        elif temp < 5:  # ~40 F
            return "cold, so you might want to bundle up"
        elif temp < 10: # 50F
            return "fairly cold, so maybe wear a coat"
        elif temp >= 10 and temp <= 24: # 50F - ~75F
            return "quite comfortable, maybe just wear a sweater"
        elif temp > 24 and temp <= 32:  # ~75F - ~90F
            return "pretty warm, so you should be fine wearing something lightweight"
        else:
            return "very hot, so I would recommend shorts and a tshirt"

    def suggest_clothes(self, context: typing.Dict):
        morning, afternoon, evening = self.weather_integration.get_full_day_forecast()
        command = context['cleaned_command']

        if any(x in command.split() for x in ['morning']):
            afternoon, evening = None, None
        elif any(x in command.split() for x in ['afternoon']):
            morning, evening = None, None
        elif any(x in command.split() for x in ['tonight', 'evening']):
            morning, afternoon = None, None
        elif any(x in command.split() for x in ['later']):
            if morning:
                morning = None
            elif afternoon:
                afternoon = None

        morning_temp, morning_rain, morning_snow = 0, None, None
        afternoon_temp, afternoon_rain, afternoon_snow, afternoon_cooloff, afternoon_warmup = 0, None, None, False, False
        evening_temp, evening_rain, evening_snow = 0, None, None

        response = ""
        if morning:
            morning_temp = int(morning.temperature("celsius")["temp"])
            morning_rain = morning.rain != {}
            morning_snow = morning.snow != {}
            check_response = self._check_temp(morning_temp)
            response = f"This morning it will be {check_response}."
        if afternoon:
            afternoon_temp = int(afternoon.temperature("celsius")["temp"])
            afternoon_rain = afternoon.rain != {}
            afternoon_snow = afternoon.snow != {}
            check_response = self._check_temp(afternoon_temp)
            if not morning:
                response = f"This afternoon it will be {check_response}."
            elif morning_temp - afternoon_temp > 8: # ~15F cooloff
                afternoon_cooloff = True
                if morning_temp >= 10 and morning_temp <= 24:   # 50F - ~75F
                    response += f" This afternoon it's going to cool off, so maybe bring a coat aswell."
                elif morning_temp > 24:
                    response += f" It's going to get a little chilly this afternoon, so maybe grab a sweater."
                else:
                    response += f" It's going to get even colder this afternoon."
            elif afternoon_temp - morning_temp > 8: # ~15F warmup
                afternoon_warmup = True
                if morning_temp >= 10 and morning_temp <= 24:   # 50F - ~75F
                    response += f" This afternoon it's going to get warmer."
                elif morning_temp > 24:
                    response += f" This afternoon it's going to get even warmer."
                elif morning_temp < 10 and morning_temp > 5:
                    response += f" But this afternoon its going to warm up."
        if evening:
            evening_temp = int(evening.temperature("celsius")["temp"])
            evening_rain = evening.rain != {}
            evening_snow = evening.snow != {}
            check_response = self._check_temp(evening_temp)
            if not afternoon:
                response = f"Tonight it will be {check_response}."
            elif afternoon_temp - evening_temp > 8: # ~15F cooloff
                if not afternoon_cooloff:
                    if afternoon_temp >= 10 and afternoon_temp <= 24:   # 50F - ~75F
                        response += f" Tonight it's going to cool off, so maybe bring a coat aswell."
                    elif afternoon_temp > 24:
                        response += f" Tonight it's going to get a little chilly, so maybe grab a sweater."
                    else:
                        response += f" It's going to get even colder tonight."
            elif evening_temp - afternoon_temp > 8: # ~15F warmup
                if not afternoon_warmup:
                    if afternoon_temp >= 10 and afternoon_temp <= 24:   # 50F - ~75F
                        response += f" This evening it's going to get warmer."
                    elif afternoon_temp > 24:
                        response += f" This evening it's going to get even warmer."
                    elif afternoon_temp < 10 and afternoon_temp > 5:
                        response += f" But this evening its going to warm up."
        
        if morning_snow or afternoon_snow or evening_snow:
            response += f" It also may snow today, so be prepared."
        elif morning_rain or afternoon_rain or evening_rain:
            response += f" It also may rain today, so maybe bring a raincoat or an umbrella."
                    
        context["response"] = response