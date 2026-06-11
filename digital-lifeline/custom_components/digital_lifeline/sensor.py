from __future__ import annotations
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import (
    DOMAIN, PERSON_TYPE_MONITORED, PERSON_TYPE_LABELS,
    EVENT_PERSON_ADDED, EVENT_PERSON_UPDATED, EVENT_PERSON_REMOVED,
)

_LOGGER = logging.getLogger(__name__)

_ICONS = {
    "monitored": "mdi:account-heart",
    "family":    "mdi:account-group",
    "caregiver": "mdi:medical-bag",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    persons = hass.data[DOMAIN].get("persons", [])
    entities: dict[str, DigitalLifelinePersonSensor] = {}

    initial = [DigitalLifelinePersonSensor(p) for p in persons]
    for e in initial:
        entities[e.person_id] = e
    async_add_entities(initial)

    @callback
    def on_person_added(event):
        person = event.data
        if person["id"] not in entities:
            entity = DigitalLifelinePersonSensor(person)
            entities[entity.person_id] = entity
            async_add_entities([entity])

    @callback
    def on_person_updated(event):
        person = event.data
        entity = entities.get(person["id"])
        if entity:
            entity.update_person(person)

    @callback
    def on_person_removed(event):
        person_id = event.data.get("id")
        entity = entities.pop(person_id, None)
        if entity:
            hass.async_create_task(entity.async_remove())

    unsub = [
        hass.bus.async_listen(EVENT_PERSON_ADDED,   on_person_added),
        hass.bus.async_listen(EVENT_PERSON_UPDATED, on_person_updated),
        hass.bus.async_listen(EVENT_PERSON_REMOVED, on_person_removed),
    ]
    hass.data[DOMAIN]["unsub_listeners"] = unsub


class DigitalLifelinePersonSensor(SensorEntity):
    _attr_should_poll = False

    def __init__(self, person: dict) -> None:
        self._person = dict(person)
        self._attr_unique_id = f"{DOMAIN}_{person['id']}"
        self._update_meta()

    @property
    def person_id(self) -> str:
        return self._person["id"]

    def update_person(self, person: dict) -> None:
        self._person = dict(person)
        self._update_meta()
        self.async_write_ha_state()

    def _update_meta(self) -> None:
        p = self._person
        first = p.get("first_name") or ""
        last  = p.get("last_name")  or ""
        name  = " ".join(filter(None, [first, last])) \
                or p.get("display_name") or p.get("nickname") or "Onbekend"
        self._attr_name = f"DL {name}"
        self._attr_icon = _ICONS.get(p.get("person_type", "monitored"), "mdi:account")

    @property
    def state(self) -> str:
        return PERSON_TYPE_LABELS.get(
            self._person.get("person_type", PERSON_TYPE_MONITORED),
            self._person.get("person_type", PERSON_TYPE_MONITORED),
        )

    @property
    def extra_state_attributes(self) -> dict:
        p = self._person
        line1 = " ".join(filter(None, [p.get("street"), p.get("housenumber")]))
        line2 = " ".join(filter(None, [p.get("zipcode"), p.get("city")]))
        address = "\n".join(filter(None, [line1, line2]))
        return {
            "id":                   p.get("id"),
            "person_type":          p.get("person_type"),
            "first_name":           p.get("first_name"),
            "last_name":            p.get("last_name"),
            "nickname":             p.get("nickname"),
            "display_name":         p.get("display_name"),
            "birthdate":            p.get("birthdate"),
            "street":               p.get("street"),
            "housenumber":          p.get("housenumber"),
            "zipcode":              p.get("zipcode"),
            "city":                 p.get("city"),
            "address":              address,
            "phone":                p.get("phone"),
            "email":                p.get("email"),
            "medication":           p.get("medication"),
            "notes":                p.get("notes"),
            "gender":               p.get("gender"),
            "relation":             p.get("relation"),
            "organization":         p.get("organization"),
            "caregiver_function":   p.get("caregiver_function"),
            "notification_types":   p.get("notification_types", []),
            "notification_channels": p.get("notification_channels", []),
            "created_at":           p.get("created_at"),
            "updated_at":           p.get("updated_at"),
        }
