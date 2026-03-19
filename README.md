# Scootermania

Scootermania ist eine Flask-Webapplikation für den Verleih von E-Scootern in der Schweiz. Die Anwendung bildet die Normaufgabe mit Rollen für Anbieter und Fahrer, QR-gestütztem Fahrtstart, minutengenauer Abrechnung und REST-API ab.

## Funktionen

- Registrierung mit Vorname, Nachname, Benutzername, E-Mail und Passwort
- Login mit Benutzername oder E-Mail und Passwort
- Rollen für Fahrer und Anbieter
- Zahlungsmittel für Fahrerprofile
- Fahrzeuge erfassen, bearbeiten und entfernen
- QR-Code-gestütztes Starten und Beenden von Fahrten
- Erfassung von Startzeit, Endzeit, Distanz und GPS-Position
- Minutengenaue Preisberechnung mit Startpreis plus Preis pro Minute
- Zahlungsabbildung über verarbeitete Transaktionen
- REST-API mit Bearer-Token
- Pytest-Tests
- Deployment mit Gunicorn und Nginx

## Verwendete Technologien

- Python 3.11+
- Flask
- Flask-Login
- Flask-SQLAlchemy
- PostgreSQL im Betrieb
- SQLite im Testbetrieb
- Gunicorn
- Nginx

## Projektstruktur

```text
scootermania/
|-- app/
|-- deploy/
|-- requirements.txt
`-- wsgi.py
```

## Lokale Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Danach die Werte in `.env` anpassen.

## Datenbank initialisieren

```bash
source .venv/bin/activate
set -a
source .env
set +a
flask --app wsgi:app db upgrade
```

## Entwicklungsserver starten

```bash
source .venv/bin/activate
set -a
source .env
set +a
flask --app wsgi:app run --debug
```

## Bedienung

1. Als Anbieter registrieren und Fahrzeuge mit Code, Akku und GPS-Daten anlegen.
2. Als Fahrer registrieren und ein Zahlungsmittel hinterlegen.
3. In der Fahrzeugübersicht oder unter `/rides/scan` den QR-Code eingeben.
4. Fahrt starten und anschliessend auf der Fahrtenseite beenden.
5. Die Anwendung berechnet die Dauer minutengenau und erzeugt eine verarbeitete Zahlung.

## API verwenden

Token direkt per API beziehen:

```bash
curl -H "Content-Type: application/json" \
  -d '{"login":"rider_demo","password":"DemoPass123!"}' \
  https://lab45.ifalabs.org/api/auth/token
```

Fachliche Endpunkte aufrufen:

```bash
curl -H "Authorization: Bearer DEIN_TOKEN" https://lab45.ifalabs.org/api/scooters
curl -H "Authorization: Bearer DEIN_TOKEN" https://lab45.ifalabs.org/api/rides
```

## Tests ausführen

```bash
PYTHONPATH=. .venv/bin/pytest -v
```

## Deployment

Gunicorn startet die Anwendung intern auf `127.0.0.1:8000`. Nginx übernimmt den externen Zugriff als Reverse Proxy.
