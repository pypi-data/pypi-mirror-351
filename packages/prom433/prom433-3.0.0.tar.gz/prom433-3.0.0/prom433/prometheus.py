# rtl_433
# Copyright (C) 2021 Andrew Wilkinson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime, timezone
import dateutil.parser
import dateutil.tz
import dateutil.utils
import json
import logging

METRICS = {
    "prom433_last_message": {}
}

HELP_FORMAT = "#HELP %s %s"
TYPE_FORMAT = "#TYPE %s %s "
METRIC_FORMAT = "%s{%s} %f"

TEMP_HELP = \
    "The temperature in degrees celcius."
TEMP_TYPE = "gauge"

HUMIDITY_HELP = "The humidity in %."
HUMIDITY_TYPE = "gauge"

WIND_AVG_HELP = "The average windspeed in km/h."
WIND_AVG_HELP_M = "The average windspeed in m/s."
WIND_AVG_TYPE = "gauge"
WIND_MAX_HELP = "The maximum windspeed in km/h."
WIND_MAX_HELP_M = "The maximum windspeed in m/s."
WIND_MAX_TYPE = "gauge"
WIND_DIR_HELP = "The wind direction in degrees."
WIND_DIR_TYPE = "gauge"

UV_HELP = "UV intensity raw value."
UV_TYPE = "gauge"
UVI_HELP = "UV Index."
UVI_TYPE = "gauge"
LUX_HELP = "Light LUX in W/m^2."
LUX_TYPE = "gauge"

RAIN_HELP = "The total rainfall in mm."
RAIN_TYPE = "counter"

BATTERY_HELP = "The battery status."
BATTERY_TYPE = "gauge"

BATTERY_V_HELP = "The battery voltage."
BATTERY_V_TYPE = "gauge"

SUPERCAP_V_HELP = "The supercapacitor voltage."
SUPERCAP_V_TYPE = "gauge"

LAST_MESSAGE_HELP = "The time the last message was received."
LAST_MESSAGE_TYPE = "counter"

FREQ_HELP = "The frequency the last message was received on."
FREQ_TYPE = "guage"

RSSI_HELP = "The RSSI of the last message."
RSSI_TYPE = "guage"

SNR_HELP = "The Signal to noise ratio of the last message."
SNR_TYPE = "guage"

NOISE_HELP = "The noise level of the last message."
NOISE_TYPE = "guage"

RADIO_CLOCK_HELP = "The radio clock value of the last message, in unix time."
RADIO_CLOCK_TYPE = "counter"

FIRMWARE_HELP = "The firmware version."
FIRMWARE_TYPE = "gauge"

METRICS_PREFIXES = {
    "prom433_battery_ok": [BATTERY_HELP, BATTERY_TYPE],
    "prom433_battery_V": [BATTERY_V_HELP, BATTERY_V_TYPE],
    "prom433_supercap_V": [SUPERCAP_V_HELP, SUPERCAP_V_TYPE],
    "prom433_temperature": [TEMP_HELP, TEMP_TYPE],
    "prom433_humidity": [HUMIDITY_HELP, HUMIDITY_TYPE],
    "prom433_wind_dir_deg": [WIND_DIR_HELP, WIND_DIR_TYPE],
    "prom433_wind_avg": [WIND_AVG_HELP, WIND_AVG_TYPE],
    "prom433_wind_max": [WIND_MAX_HELP, WIND_MAX_TYPE],
    "prom433_wind_avg_m": [WIND_AVG_HELP_M, WIND_AVG_TYPE],
    "prom433_wind_max_m": [WIND_MAX_HELP_M, WIND_MAX_TYPE],
    "prom433_rain": [RAIN_HELP, RAIN_TYPE],
    "prom433_uv": [UV_HELP, UV_TYPE],
    "prom433_uvi": [UVI_HELP, UVI_TYPE],
    "prom433_light_lux": [LUX_HELP, LUX_TYPE],
    "prom433_last_message": [LAST_MESSAGE_HELP, LAST_MESSAGE_TYPE],
    "prom433_freq": [FREQ_HELP, FREQ_TYPE],
    "prom433_freq1": [FREQ_HELP, FREQ_TYPE],
    "prom433_freq2": [FREQ_HELP, FREQ_TYPE],
    "prom433_rssi": [RSSI_HELP, RSSI_TYPE],
    "prom433_snr": [SNR_HELP, SNR_TYPE],
    "prom433_noise": [NOISE_HELP, NOISE_TYPE],
    "prom433_radio_clock": [RADIO_CLOCK_HELP, RADIO_CLOCK_TYPE],
    "prom433_firmware": [FIRMWARE_HELP, FIRMWARE_TYPE]
}

METRICS_CONVERT = {
    "prom433_radio_clock":
        lambda x: dateutil.utils.default_tzinfo(dateutil.parser.parse(x),
                                                dateutil.tz.tzoffset("UTC", 0))
        .timestamp(),
    # TODO: need to only do if the original metric is in mV
    "prom433_battery_V": lambda v: v / 1000.0,
    "prom433_firmware":
        lambda v: v if isinstance(v, int) or v.isnumeric() else None
}

TAG_KEYS = {"id", "channel", "model"}

IGNORE_TAGS = {
    "*": {"mic", "mod"},
    "Fineoffset-WHx080": {"subtype"},
    "LaCrosse-TX35DTHIT": {"newbattery"},
    "LaCrosse-TX29IT": {"newbattery"},
    "Fineoffset-WS90": {"flags", "data"}
}

METRIC_NAME = {
    "battery_ok": "prom433_battery_ok",
    "battery_mV": "prom433_battery_V",
    "supercap_V": "prom433_supercap_V",
    "temperature_C": "prom433_temperature",
    "humidity": "prom433_humidity",
    "wind_dir_deg": "prom433_wind_dir_deg",
    "wind_avg_km_h": "prom433_wind_avg",
    "wind_max_km_h": "prom433_wind_max",
    "wind_avg_m_s": "prom433_wind_avg_m",
    "wind_max_m_s": "prom433_wind_max_m",
    "rain_mm": "prom433_rain",
    "uv": "prom433_uv",
    "uvi": "prom433_uvi",
    "light_lux": "prom433_light_lux",
    "last_message": "prom433_last_message",
    "freq": "prom433_freq",
    "freq1": "prom433_freq1",
    "freq2": "prom433_freq2",
    "rssi": "prom433_rssi",
    "snr": "prom433_snr",
    "noise": "prom433_noise",
    "radio_clock": "prom433_radio_clock",
    "light_lux": "prom433_light_lux",
    "firmware": "prom433_firmware",
}

# {"time" : "2021-05-08 15:27:58", "model" : "Fineoffset-WHx080",
# "subtype" : 0, "id" : 202, "battery_ok" : 0, "temperature_C" : 6.900,
# "humidity" : 63, "wind_dir_deg" : 158, "wind_avg_km_h" : 4.896,
# "wind_max_km_h" : 8.568, "rain_mm" : 2.400, "mic" : "CRC"}
# {"time" : "2021-05-08 15:28:02", "model" : "Nexus-TH", "id" : 177,
# "channel" : 3, "battery_ok" : 0, "temperature_C" : 21.300, "humidity" : 39}
# {"time":"2022-11-08 14:54:14","model":"Eurochron-EFTH800",
# "id":3672,"channel":6,"battery_ok":1,"temperature_C":20.5,"humidity":60,"mic":"CRC",
# "mod":"ASK","freq":433.91904,"rssi":-0.117409,"snr":20.23702,"noise":-20.3544}


def prometheus(message, drop_after):
    payload = json.loads(message)

    tags, data, unknown = {}, {}, {}

    for key, value in payload.items():
        if key == "time":
            if ':' in payload[key]:
                time_value = dateutil.parser.parse(payload[key]).timestamp()
            else:
                time_value = datetime.fromtimestamp(float(payload[key])) \
                             .timestamp()
        elif key in TAG_KEYS:
            tags[key] = value
        elif key in METRIC_NAME:
            data[key] = value
        else:
            unknown[key] = value

    tag_value = ", ".join(["%s=\"%s\"" % (k, payload[k])
                           for k in sorted(tags)])

    METRICS["prom433_last_message"][tag_value] = time_value
    for key in data:
        metric = METRIC_NAME[key]
        if metric is None:
            continue
        if metric not in METRICS:
            METRICS[metric] = {}
        METRICS[metric][tag_value] = \
            METRICS_CONVERT.get(metric, lambda x: x)(payload[key])

    unknown = {key: value for (key, value) in unknown.items() if key not in
               (IGNORE_TAGS["*"] | IGNORE_TAGS.get(tags["model"], set()))}

    if len(unknown) > 0:
        logging.warn(f"Message has unknown tags ({unknown}): {message}")

    if drop_after > 0:
        tags_to_drop = set()

        for tag_value in METRICS["prom433_last_message"].keys():
            limit = time_value - drop_after
            if METRICS["prom433_last_message"][tag_value] < limit:
                tags_to_drop.add(tag_value)

        if len(tags_to_drop) == 0:
            return

        logging.info(f"Dropping {len(tags_to_drop)} as not seen"
                     + " for {drop_after} seconds")
        for tag_value in tags_to_drop:
            logging.info(f"Dropping {tag_value}")
            for metric in METRICS.keys():
                if tag_value in METRICS[metric]:
                    del METRICS[metric][tag_value]


def get_metrics():
    lines = []
    for metric_name in sorted(METRICS.keys()):
        lines.append(HELP_FORMAT
                     % (metric_name, METRICS_PREFIXES[metric_name][0]))
        lines.append(TYPE_FORMAT
                     % (metric_name, METRICS_PREFIXES[metric_name][1]))
        for (tags, values) in METRICS[metric_name].items():
            if values is not None:
                lines.append(METRIC_FORMAT % (metric_name, tags, values))

    return "\n".join(lines)
