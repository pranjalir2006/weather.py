import tkinter as tk
from tkinter import messagebox
import requests
import threading
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import requests
import threading
from datetime import datetime

# OpenWeather API Key
API_KEY = "YOUR_API_KEY_HERE"

BASE_URL = "https://api.openweathermap.org/data/2.5"

BASE_URL = "https://api.openweathermap.org/data/2.5"


def get_weather(city):
    try:
        # Convert city name into geographic coordinates
        geo_url = "https://api.openweathermap.org/geo/1.0/direct"

        geo_response = requests.get(
            geo_url,
            params={
                "q": city,
                "limit": 1,
                "appid": API_KEY
            },
            timeout=10
        )
        geo_response.raise_for_status()
        locations = geo_response.json()

        if not locations:
            raise ValueError("City not found. Check the city name.")

        location = locations[0]
        lat = location["lat"]
        lon = location["lon"]

        # Fetch current weather
        current_response = requests.get(
            f"{BASE_URL}/weather",
            params={
                "lat": lat,
                "lon": lon,
                "appid": API_KEY,
                "units": "metric"
            },
            timeout=10
        )
        current_response.raise_for_status()
        current = current_response.json()

        # Fetch five-day forecast
        forecast_response = requests.get(
            f"{BASE_URL}/forecast",
            params={
                "lat": lat,
                "lon": lon,
                "appid": API_KEY,
                "units": "metric"
            },
            timeout=10
        )
        forecast_response.raise_for_status()
        forecast = forecast_response.json()

        return current, forecast

    except requests.exceptions.Timeout:
        raise ValueError("Request timed out. Try again.")

    except requests.exceptions.HTTPError:
        raise ValueError(
            "Weather API error. Check your API key and account access."
        )

    except requests.exceptions.RequestException:
        raise ValueError("Network error. Check your internet connection.")


def display_weather():
    city = city_entry.get().strip()

    if not city:
        messagebox.showwarning("Input Error", "Please enter a city name.")
        return

    search_button.config(state="disabled", text="Loading...")
    result_label.config(text="Fetching weather data...")
    forecast_label.config(text="")

    def worker():
        try:
            current, forecast = get_weather(city)
            root.after(0, lambda: show_results(current, forecast))

        except ValueError as error:
            root.after(0, lambda: show_error(str(error)))

    threading.Thread(target=worker, daemon=True).start()


def show_results(current, forecast):
    search_button.config(state="normal", text="Get Weather")

    city = current["name"]
    country = current["sys"]["country"]
    temperature = current["main"]["temp"]
    humidity = current["main"]["humidity"]
    feels_like = current["main"]["feels_like"]
    wind = current["wind"]["speed"]
    description = current["weather"][0]["description"].title()

    result = (
        f"Weather in {city}, {country}\n\n"
        f"Temperature: {temperature:.1f} °C\n"
        f"Feels Like: {feels_like:.1f} °C\n"
        f"Humidity: {humidity}%\n"
        f"Wind Speed: {wind} m/s\n"
        f"Condition: {description}"
    )

    result_label.config(text=result)

    # Select one forecast entry for each day
    daily = {}

    for item in forecast["list"]:
        date = item["dt_txt"].split()[0]

        if date not in daily:
            daily[date] = item

    forecast_text = "\n5-DAY FORECAST\n"

    for date, item in list(daily.items())[:5]:
        day = datetime.strptime(date, "%Y-%m-%d").strftime("%a, %d %b")
        temp = item["main"]["temp"]
        condition = item["weather"][0]["description"].title()

        forecast_text += (
            f"\n{day}: {temp:.1f} °C - {condition}"
        )

    forecast_label.config(text=forecast_text)


def show_error(error):
    search_button.config(state="normal", text="Get Weather")
    result_label.config(text="")
    messagebox.showerror("Weather Error", error)


# Tkinter window
root = tk.Tk()
root.title("Live Weather Application")
root.geometry("480x620")
root.configure(bg="#eaf4ff")

title = tk.Label(
    root,
    text="WEATHER FORECAST APP",
    font=("Arial", 20, "bold"),
    bg="#eaf4ff",
    fg="#174a7e"
)
title.pack(pady=20)

city_entry = tk.Entry(
    root,
    font=("Arial", 14),
    width=25,
    justify="center"
)
city_entry.pack(pady=10)
city_entry.insert(0, "Bengaluru")

search_button = tk.Button(
    root,
    text="Get Weather",
    font=("Arial", 12, "bold"),
    bg="#2471c8",
    fg="white",
    command=display_weather
)
search_button.pack(pady=15)

result_label = tk.Label(
    root,
    text="Enter a city to see its weather",
    font=("Arial", 13),
    bg="#eaf4ff",
    justify="center"
)
result_label.pack(pady=20)

forecast_label = tk.Label(
    root,
    text="",
    font=("Arial", 11),
    bg="#eaf4ff",
    justify="left"
)
forecast_label.pack(pady=15)

root.mainloop()
