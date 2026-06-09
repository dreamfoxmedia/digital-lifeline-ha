# Digital Lifeline – Home Assistant Integratie

Sla personen op die via de **Digital Lifeline app** worden aangemaakt en gebruik hun gegevens in Home Assistant automatiseringen voor notificaties.

---

## Installatie via HACS

1. Ga in Home Assistant naar **HACS → Integraties → ⋮ → Aangepaste repositories**
2. Voeg de URL van deze GitHub-repository toe en kies categorie **Integratie**
3. Zoek naar **Digital Lifeline** en klik op **Downloaden**
4. Herstart Home Assistant
5. Ga naar **Instellingen → Apparaten & Diensten → Integratie toevoegen**
6. Zoek op **Digital Lifeline** en volg de stappen

## Handmatige installatie

1. Kopieer de map `custom_components/digital_lifeline` naar je Home Assistant configuratiemap onder `custom_components/`
2. Herstart Home Assistant
3. Voeg de integratie toe via **Instellingen → Apparaten & Diensten**

---

## Persoon-types

Elke persoon krijgt één van de volgende labels:

| Type | Waarde | Omschrijving |
|---|---|---|
| Bewaakt persoon | `monitored` | De persoon die in de gaten wordt gehouden |
| Familielid | `family` | Familie die notificaties ontvangt |
| Hulpverlener | `caregiver` | Professionele zorgverlener of mantelzorger |

---

## Sensor-entiteiten

Voor elke persoon wordt een sensor-entiteit aangemaakt:

- **Entity ID:** `sensor.dl_<naam>`
- **State:** persoon-type als leesbaar label (`Bewaakt persoon`, `Familielid`, `Hulpverlener`)
- **Icoon:** `mdi:account-heart` / `mdi:account-group` / `mdi:medical-bag`

### Beschikbare attributen

| Attribuut | Omschrijving |
|---|---|
| `id` | Uniek persoon-ID |
| `person_type` | `monitored` / `family` / `caregiver` |
| `nickname` | Familienaam |
| `display_name` | Naam voor meldingen |
| `birthdate` | Geboortedatum (dd-mm-yyyy) |
| `address` | Volledig adres (opgemaakte tekst) |
| `phone` | Telefoonnummer |
| `email` | E-mailadres |
| `medication` | Medicijngebruik en medische info |
| `created_at` | Tijdstip van aanmaken |
| `updated_at` | Tijdstip van laatste wijziging |

---

## Acties (services)

### `digital_lifeline.add_person`

Wordt automatisch aangeroepen door de Digital Lifeline app. Kan ook handmatig worden gebruikt.

```yaml
action: digital_lifeline.add_person
data:
  nickname: "Opa"
  display_name: "Johannes de Vries"
  birthdate: "01-01-1945"
  street: "Dorpsstraat"
  housenumber: "12 B"
  zipcode: "1234 AB"
  city: "Amsterdam"
  phone: "+31612345678"
  email: "opa@example.com"
  medication: "Metformine 500mg, bloedverdunners"
  person_type: "monitored"
```

### `digital_lifeline.update_person`

```yaml
action: digital_lifeline.update_person
data:
  person_id: "<id uit sensor-attribuut>"
  phone: "+31687654321"
```

### `digital_lifeline.remove_person`

```yaml
action: digital_lifeline.remove_person
data:
  person_id: "<id uit sensor-attribuut>"
```

---

## Voorbeeld: notificatie sturen bij alarm

```yaml
automation:
  alias: "Digital Lifeline – Alarm bewaakt persoon"
  trigger:
    - platform: state
      entity_id: binary_sensor.bewegingssensor_slaapkamer
      to: "on"
  action:
    - variables:
        persoon: "{{ states.sensor | selectattr('attributes.person_type','eq','monitored') | first }}"
        familie: "{{ states.sensor | selectattr('attributes.person_type','eq','family') | list }}"
    - action: notify.mobile_app
      data:
        title: "Melding voor {{ persoon.attributes.display_name }}"
        message: >
          Beweging gedetecteerd bij {{ persoon.attributes.display_name }}.
          Adres: {{ persoon.attributes.address }}.
          {% if persoon.attributes.medication %}
          Medicijngebruik: {{ persoon.attributes.medication }}
          {% endif %}
    - repeat:
        for_each: "{{ familie }}"
        sequence:
          - action: notify.sms
            data:
              target: "{{ repeat.item.attributes.phone }}"
              message: "Alarm: beweging bij {{ persoon.attributes.display_name }}"
```

---

## Events

De integratie vuurt de volgende Home Assistant events:

| Event | Wanneer |
|---|---|
| `digital_lifeline_person_added` | Persoon aangemaakt |
| `digital_lifeline_person_updated` | Persoon bijgewerkt |
| `digital_lifeline_person_removed` | Persoon verwijderd |

---

## Gegevensopslag

Alle persoonsgegevens worden **lokaal** opgeslagen in Home Assistant (`.storage/digital_lifeline_persons`). Er worden geen gegevens naar externe servers verstuurd.
