# Digital Lifeline – Home Assistant Integratie

Sla personen op die via de **Digital Lifeline app** worden aangemaakt en gebruik hun gegevens in Home Assistant automatiseringen voor notificaties.

---

## Installatie via Home Assistant Add-on Store

> Geen HACS nodig – werkt direct via Home Assistant.

1. Ga in Home Assistant naar **Instellingen → Add-ons → Add-on Store**
2. Klik op de **⋮ (drie puntjes)** rechtsboven → **Repositories**
3. Plak de volgende URL en klik **Toevoegen**:
   ```
   https://github.com/dreamfoxmedia/digital-lifeline-ha
   ```
4. Zoek het **Digital Lifeline** add-on en klik op **Installeren**
5. Klik op **Starten** en wacht tot je ziet: *Installatie geslaagd!*
6. **Herstart Home Assistant**
7. Ga naar **Instellingen → Apparaten & Diensten → Integratie toevoegen**
8. Zoek op **Digital Lifeline** en volg de stappen

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

- **Entity ID:** `sensor.digitallifeline_<naam>`
- **State:** persoon-type als leesbaar label
- **Icoon:** `mdi:account-heart` / `mdi:account-group` / `mdi:medical-bag`

### Beschikbare attributen

| Attribuut | Omschrijving |
|---|---|
| `id` | Uniek persoon-ID |
| `person_type` | `monitored` / `family` / `caregiver` |
| `nickname` | Familienaam |
| `display_name` | Naam voor meldingen |
| `birthdate` | Geboortedatum (dd-mm-yyyy) |
| `address` | Volledig adres |
| `phone` | Telefoonnummer |
| `email` | E-mailadres |
| `medication` | Medicijngebruik en medische info |

---

## Acties (services)

### `digital_lifeline.add_person`

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
  medication: "Metformine 500mg"
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

## Voorbeeld: notificatie bij alarm

```yaml
automation:
  alias: "Digital Lifeline – Alarm bewaakt persoon"
  trigger:
    - platform: state
      entity_id: binary_sensor.bewegingssensor
      to: "on"
  action:
    - variables:
        persoon: "{{ states.sensor | selectattr('attributes.person_type','eq','monitored') | first }}"
    - action: notify.mobile_app
      data:
        title: "Melding voor {{ persoon.attributes.display_name }}"
        message: >
          Beweging gedetecteerd.
          Adres: {{ persoon.attributes.address }}.
          Medicijngebruik: {{ persoon.attributes.medication }}
```

---

## Gegevensopslag

Alle gegevens worden **lokaal** opgeslagen in Home Assistant. Er worden geen gegevens naar externe servers verstuurd.

---

## Ondersteuning

Bezoek [help.digitallifeline.nl](https://help.digitallifeline.nl) voor vragen en ondersteuning.
