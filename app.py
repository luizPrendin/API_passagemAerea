# app.py
from flask import Flask, request, jsonify, render_template_string
import requests
from datetime import datetime

app = Flask(__name__)

# Dicionários de mapeamento
iata_mapping = {
    "São Paulo": "GRU",
    "Roma": "FCO",
    "Paris": "CDG",
    "Nova York": "JFK",
    "Tóquio": "NRT",
    "Londres": "LHR",
    "Berlim": "TXL",
    "Dubai": "DXB",
    "Sydney": "SYD",
    "Buenos Aires": "EZE",
    # Adicione mais mapeamentos conforme necessário
}

airline_mapping = {
    "AF": "AIR FRANCE",
    "LH": "LUFTHANSA",
    "BA": "BRITISH AIRWAYS",
    "AA": "AMERICAN AIRLINES",
    "DL": "DELTA AIR LINES",
    "EK": "EMIRATES",
    "QR": "QATAR AIRWAYS",
    "SQ": "SINGAPORE AIRLINES",
    "NH": "ALL NIPPON AIRWAYS",
    "QF": "QANTAS",
    "KL": "KLM"
    # Adicione mais mapeamentos conforme necessário
}

airport_mapping = {
    "GRU": "São Paulo (Guarulhos)",
    "FCO": "Roma (Fiumicino)",
    "CDG": "Paris (Charles de Gaulle)",
    "JFK": "Nova York (John F. Kennedy)",
    "NRT": "Tóquio (Narita)",
    "LHR": "Londres (Heathrow)",
    "TXL": "Berlim (Tegel)",
    "DXB": "Dubai (International)",
    "SYD": "Sydney (Kingsford Smith)",
    "EZE": "Buenos Aires (Ezeiza)",
    # Adicione mais mapeamentos conforme necessário
}

# Função para obter o token de acesso
def get_access_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": "EcGG2CCqQeWtbWPpBURxOa27xsCh64KN",
        "client_secret": "GPLXA8d3ccDr67FA"
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Error getting access token:", response.json())
        return None

@app.route('/')
def index():
    return render_template_string(open("index.html").read())

@app.route('/search-flights', methods=['POST'])
def search_flights():
    data = request.json
    origin_name = data['origin']
    destination_name = data['destination']
    departure_date = data['departure_date']
    return_date = data.get('return_date')
    adults = data['adults']

    origin = iata_mapping.get(origin_name, origin_name)
    destination = iata_mapping.get(destination_name, destination_name)

    # Verificação e formatação das datas
    try:
        departure_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
        if return_date:
            return_date = datetime.strptime(return_date, '%Y-%m-%d').date()
            if return_date <= departure_date:
                return jsonify({"error": "Data de retorno deve ser após a data de partida"}), 400
    except ValueError as e:
        return jsonify({"error": "Formato de data inválido. Use AAAA-MM-DD."}), 400

    access_token = get_access_token()
    if not access_token:
        return jsonify({"error": "Could not retrieve access token"}), 500

    api_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departure_date.strftime('%Y-%m-%d'),
        "adults": adults
    }
    if return_date:
        params["returnDate"] = return_date.strftime('%Y-%m-%d')

    response = requests.get(api_url, headers=headers, params=params)
    print("Request params:", params)
    print("Response status code:", response.status_code)
    print("Response data:", response.json())

    if response.status_code == 200:
        flight_offers = response.json().get('data', [])
        formatted_offers = []
        for offer in flight_offers:
            itineraries = offer.get('itineraries', [])
            price = offer.get('price', {}).get('total', 'N/A')
            airlines = offer.get('validatingAirlineCodes', [])
            for itinerary in itineraries:
                segments = itinerary.get('segments', [])
                for segment in segments:
                    origin_code = segment.get('departure', {}).get('iataCode', 'N/A')
                    destination_code = segment.get('arrival', {}).get('iataCode', 'N/A')
                    departure_time = segment.get('departure', {}).get('at', 'N/A')
                    arrival_time = segment.get('arrival', {}).get('at', 'N/A')
                    formatted_offers.append({
                        'airline': ', '.join([airline_mapping.get(code, code) for code in airlines]),
                        'price': price,
                        'origin': airport_mapping.get(origin_code, origin_code),
                        'destination': airport_mapping.get(destination_code, destination_code),
                        'departure_time': departure_time,
                        'arrival_time': arrival_time
                    })
        return jsonify(formatted_offers)
    else:
        error_detail = response.json().get('errors', [{}])[0].get('detail', 'Unknown error')
        print("Error detail:", error_detail)
        return jsonify({"error": f"Falha na busca de passagens: {error_detail}"}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
