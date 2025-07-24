from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
BASE_URL = "https://meteo.cbpio.pl"

@app.route("/gui/weather")
def simple_weather():
    city = request.args.get("city", "Warszawa")

    if "application/json" in request.headers.get("Accept", "") or "curl" in request.headers.get("User-Agent", ""):
        try:
            response = requests.get(f"https://meteo.cbpio.pl/weather", params={"city": city})
            return jsonify(response.json())
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return render_template("weather.html")

@app.route("/gui/weather/geo")
def geo_weather_page():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        msg = {"error": "Podaj współrzędne, np. ?lat=52.4&lon=16.9"}
        if "application/json" in request.headers.get("Accept", "") or "curl" in request.headers.get("User-Agent", ""):
            return jsonify(msg), 400
        return msg["error"], 400

    try:
        response = requests.get("https://meteo.cbpio.pl/weather/geo", params={"latitude": lat, "longitude": lon})
        data = response.json()
    except Exception as e:
        error_msg = {"error": str(e)}
        if "application/json" in request.headers.get("Accept", "") or "curl" in request.headers.get("User-Agent", ""):
            return jsonify(error_msg), 500
        return f"Błąd: {e}", 500

    if "application/json" in request.headers.get("Accept", "") or "curl" in request.headers.get("User-Agent", ""):
        return jsonify(data)

    return render_template("geo_weather.html", weather=data)

@app.route("/gui/forecast")
def forecast():
    city = request.args.get("city", "").strip()
    if not city:
        return render_template("forecast.html", city="", error="Nie podano miasta")

    try:
        forecast_data = requests.get(f"{BASE_URL}/forecast", params={"city": city}).json()
    except Exception as e:
        return render_template("forecast.html", city=city, error="Błąd pobierania danych")

    accept = request.headers.get("Accept", "")
    if "application/json" in accept:
        return jsonify(forecast_data)

    return render_template("forecast.html", city=forecast_data["city"], forecast=forecast_data["forecast"])

@app.route("/gui/forecast/hourly")
def hourly_forecast():
    city = request.args.get("city", "").lower()
    hours = request.args.get("hours", 24, type=int)

    if not city:
        return "Brak parametru 'city'", 400

    try:
        resp = requests.get("https://meteo.cbpio.pl/forecast/hourly", params={"city": city, "hours": hours})
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        error_msg = f"Błąd pobierania danych: {str(e)}"
        if "text/html" in request.headers.get("Accept", ""):
            return render_template("hourly_forecast.html", city=city.capitalize(), hourly_forecast=None, error=error_msg)
        return jsonify({"error": error_msg}), 500

    hourly = data.get("hourly_forecast", {})

    if "text/html" in request.headers.get("Accept", ""):
        return render_template("hourly_forecast.html", city=city.capitalize(), hourly_forecast=hourly, error=None)
    else:
        return jsonify(data)

@app.route("/gui/history/range")
def history_range():
    city = request.args.get("city", "").lower()
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    accept = request.headers.get("Accept", "")

    if not city or not start_date or not end_date:
        error_msg = "Brak wymaganych parametrów"
        if "text/html" in accept:
            return render_template("history_range.html", city=city.capitalize(),
                                   start_date=start_date, end_date=end_date,
                                   history=None, error=error_msg)
        else:
            return jsonify({"error": error_msg}), 400

    url = f"https://meteo.cbpio.pl/history-range?city={city}&start_date={start_date}&end_date={end_date}"

    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        if "text/html" in accept:
            return render_template("history_range.html", city=city.capitalize(),
                                   start_date=start_date, end_date=end_date,
                                   history=None, error=str(e))
        else:
            return jsonify({"error": str(e)}), 500

    history = data.get("history")

    if "text/html" in accept:
        return render_template("history_range.html", city=city.capitalize(),
                               start_date=start_date, end_date=end_date,
                               history=history, error=None)
    else:
        return jsonify({
            "city": city.capitalize(),
            "start_date": start_date,
            "end_date": end_date,
            "history": history
        })

@app.route("/app/")
def index():
    return render_template("index.html")

@app.route("/app/get_weather", methods=["POST"])
def get_weather():
    data = request.get_json()
    lat = data.get("lat")
    lon = data.get("lon")

    if lat is None or lon is None:
        return jsonify({"error": "Missing coordinates"}), 400

    try:
        current = requests.get(f"{BASE_URL}/weather/geo", params={"latitude": lat, "longitude": lon}).json()
        forecast = requests.get(f"{BASE_URL}/forecast/geo", params={
            "latitude": lat,
            "longitude": lon,
            "days": 7
        }).json()
        hourly = requests.get(f"{BASE_URL}/forecast/hourly/geo", params={
            "latitude": lat,
            "longitude": lon,
            "hours": 24
        }).json()

        return jsonify({
            "current": current,
            "daily": forecast,
            "hourly": hourly
        })
    except Exception as e:
        print("Error fetching data:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
