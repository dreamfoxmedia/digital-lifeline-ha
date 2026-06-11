## 1.1.1

- Fix: logging niveau debug → info zodat start/stop zichtbaar is in HA logboek
- Fix: add-on icoon op juiste locatie (root add-on map) voor Supervisor

## 1.1.0

- Fix: integratie stoppen veroorzaakte een fout door niet-afgemelde event listeners
- Event listeners (person_added/updated/removed) worden nu netjes afgemeld bij unload
- Betere foutmeldingen in de log bij problemen tijdens stoppen

## 1.0.9

- update_person schema uitgebreid met alle velden (first_name, last_name, notes, etc.)
- Bewaakt persoon nu volledig wijzigbaar vanuit de app

## 1.0.8

- Nieuw veld: `notes` (extra informatie over beperkingen/bijzonderheden)
- `notes` beschikbaar als sensor attribuut voor gebruik in automatiseringen

## 1.0.7

- Fix: persoon verwijderen in de app verwijdert nu ook de HA entiteit correct
- Nieuw: `add_person` service accepteert app-ID zodat app en HA dezelfde ID gebruiken
- Nieuw velden in service schema: `first_name`, `last_name`, `gender`, `relation`, `organization`, `caregiver_function`, `notification_types`, `notification_channels`
- Integratie versie 1.0.3

## 1.0.6

- Fix: add-on start werkt nu correct via `init: false` + expliciete ENTRYPOINT
- Omzeilt S6 overlay problemen in HA base images

## 1.0.5

- Verbeterde sensor attributen: adres, medicatie, meldingen
- Sensornaam op basis van voor- en achternaam

## 1.0.4

- Initiële add-on release
