import requests
import json
import arrow
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

LAT = 56.338
LNG = -2.781
WIDTH = 800
HEIGHT = 480
API_KEY = ''

def api_request():
    start = arrow.now().floor('day')
    end = arrow.now().shift(days = 5).floor('day')

    tides = requests.get(
    'https://api.stormglass.io/v2/tide/extremes/point',
    params={
        'lat': LAT,
        'lng': LNG,
        'start': start,
        'end': end,
        'datum': 'MLLW'
    },
    headers={
        'Authorization': API_KEY
    }
    )

    weather = requests.get(
    'https://api.stormglass.io/v2/weather/point',
    params={
        'lat': LAT,
        'lng': LNG,
        'params': ','.join(['waterTemperature']),
    },
    headers={
        'Authorization': API_KEY
    }
    )

    return tides, weather

def draw_display(next, next2, weather_json, bitplot):
    big_font = ImageFont.truetype("Merriweather/Merriweather-Regular.ttf", size = 30)
    small_font = ImageFont.truetype("Merriweather/Merriweather-Regular.ttf", size = 20)
    italic_font = ImageFont.truetype("Merriweather/Merriweather-Italic.ttf", size = 30)

    out = Image.new("1", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(out)

    draw.text((WIDTH * 0.025, HEIGHT * 0.042),
        "East Sands, St. Andrews",
        font = italic_font)

    if next[2] == "high":
        draw.text((WIDTH * 0.025, HEIGHT * 0.146),
            "The tide is rising!",
            font = big_font)
    else:
        draw.text((WIDTH * 0.025, HEIGHT * 0.146),
            "The tide is falling!",
            font = big_font)

    draw.text((WIDTH * 0.025, HEIGHT * 0.250),
        "The next {} tide is at {},\nwhich is {}".format(next[2], next[1].format("HH:mm"),
        next[1].humanize()),
        font = big_font)

    draw.text((WIDTH * 0.025, HEIGHT * 0.416),
        "The next {} tide is at {},\nwhich is {}".format(next2[2], next2[1].format("HH:mm"),
        next2[1].humanize()),
        font = big_font)

    draw.text((WIDTH * 0.025, HEIGHT * 0.600),
        "Sea temperature is {}C".format(weather_json['hours'][0]['waterTemperature']['sg']),
        font = big_font)

    out.paste(bitplot, (int(WIDTH * 0.60), int(HEIGHT * 0.025)))

    out.show()

def plot_tides(tide_data):
    heights = []
    times = []
    plt.rcParams['font.size'] = 12

    for record in tide_data:
        heights.append(record[0])
        times.append(record[1].format("ddd HH:mm"))

    times.reverse()
    heights.reverse()

    plt.figure(figsize = (2, 5))
    plt.barh(times, heights)
    plt.title("Next five days")
    plt.xlabel("Height (m)")
    plt.savefig("plot.png", bbox_inches = 'tight')

def main():

    tides, weather = api_request()

    tide_json = tides.json() # Parse JSONs
    weather_json = weather.json()

    tide_data = []

    for record in tide_json['data'] :
        tide_data.append((record['height'], arrow.get(record['time']), record['type']))

    index = 0
    for record in tide_data: # get the next tide time
        if record[1] > arrow.utcnow():
            next = record
            break
        index += 1

    next2 = tide_data[index + 1] # get the one after it
    
    plot_tides(tide_data)

    bitplot = Image.open("plot.png").convert("1")

    draw_display(next, next2, weather_json, bitplot)

if __name__ == "__main__":
    main()