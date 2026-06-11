"""Digital Lifeline – Home Assistant custom integration.

Slaat personen op die via de Digital Lifeline app worden aangemaakt en stelt
hun gegevens (telefoonnummer, e-mail, medicijngebruik, type) beschikbaar als
sensor-entiteiten voor gebruik in automatiseringen en notificaties.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.storage import Store

from .const import (
    DOMAIN,
    STORAGE_KEY,
    STORAGE_VERSION,
    PERSON_TYPES,
    PERSON_TYPE_MONITORED,
    SERVICE_ADD_PERSON,
    SERVICE_UPDATE_PERSON,
    SERVICE_REMOVE_PERSON,
    EVENT_PERSON_ADDED,
    EVENT_PERSON_UPDATED,
    EVENT_PERSON_REMOVED,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

# ── Service schemas ──────────────────────────────────────────────────────────

ADD_PERSON_SCHEMA = vol.Schema({
    vol.Optional("id", default=""): cv.string,
    vol.Optional("nickname", default=""): cv.string,
    vol.Optional("display_name", default=""): cv.string,
    vol.Optional("first_name", default=""): cv.string,
    vol.Optional("last_name", default=""): cv.string,
    vol.Optional("gender", default=""): cv.string,
    vol.Optional("birthdate", default=""): cv.string,
    vol.Optional("street", default=""): cv.string,
    vol.Optional("housenumber", default=""): cv.string,
    vol.Optional("zipcode", default=""): cv.string,
    vol.Optional("city", default=""): cv.string,
    vol.Optional("phone", default=""): cv.string,
    vol.Optional("email", default=""): cv.string,
    vol.Optional("medication", default=""): cv.string,
    vol.Optional("notes", default=""): cv.string,
    vol.Optional("relation", default=""): cv.string,
    vol.Optional("organization", default=""): cv.string,
    vol.Optional("caregiver_function", default=""): cv.string,
    vol.Optional("notification_types", default=[]): vol.All(cv.ensure_list, [cv.string]),
    vol.Optional("notification_channels", default=[]): vol.All(cv.ensure_list, [cv.string]),
    vol.Optional("person_type", default=PERSON_TYPE_MONITORED): vol.In(PERSON_TYPES),
    vol.Optional("photo", default=""): cv.string,
})

UPDATE_PERSON_SCHEMA = vol.Schema({
    vol.Required("person_id"): cv.string,
    vol.Optional("nickname"): cv.string,
    vol.Optional("display_name"): cv.string,
    vol.Optional("first_name"): cv.string,
    vol.Optional("last_name"): cv.string,
    vol.Optional("gender"): cv.string,
    vol.Optional("birthdate"): cv.string,
    vol.Optional("street"): cv.string,
    vol.Optional("housenumber"): cv.string,
    vol.Optional("zipcode"): cv.string,
    vol.Optional("city"): cv.string,
    vol.Optional("phone"): cv.string,
    vol.Optional("email"): cv.string,
    vol.Optional("medication"): cv.string,
    vol.Optional("notes"): cv.string,
    vol.Optional("relation"): cv.string,
    vol.Optional("organization"): cv.string,
    vol.Optional("caregiver_function"): cv.string,
    vol.Optional("notification_types"): vol.All(cv.ensure_list, [cv.string]),
    vol.Optional("notification_channels"): vol.All(cv.ensure_list, [cv.string]),
    vol.Optional("person_type"): vol.In(PERSON_TYPES),
    vol.Optional("photo"): cv.string,
})

REMOVE_PERSON_SCHEMA = vol.Schema({
    vol.Required("person_id"): cv.string,
})


# ── Setup ────────────────────────────────────────────────────────────────────

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Digital Lifeline component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Digital Lifeline from a config entry."""
    store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    stored = await store.async_load() or {"persons": []}

    hass.data[DOMAIN] = {
        "store": store,
        "persons": stored.get("persons", []),
        "entry_id": entry.entry_id,
    }

    async def _save():
        await store.async_save({"persons": hass.data[DOMAIN]["persons"]})

    # ── Service: add_person ──────────────────────────────────────────────────
    async def handle_add_person(call: ServiceCall) -> None:
        person = {
            "id": call.data.get("id") or str(uuid.uuid4()),
            "nickname": call.data.get("nickname", ""),
            "display_name": call.data.get("display_name", ""),
            "first_name": call.data.get("first_name", ""),
            "last_name": call.data.get("last_name", ""),
            "gender": call.data.get("gender", ""),
            "birthdate": call.data.get("birthdate", ""),
            "street": call.data.get("street", ""),
            "housenumber": call.data.get("housenumber", ""),
            "zipcode": call.data.get("zipcode", ""),
            "city": call.data.get("city", ""),
            "phone": call.data.get("phone", ""),
            "email": call.data.get("email", ""),
            "medication": call.data.get("medication", ""),
            "notes": call.data.get("notes", ""),
            "relation": call.data.get("relation", ""),
            "organization": call.data.get("organization", ""),
            "caregiver_function": call.data.get("caregiver_function", ""),
            "notification_types": call.data.get("notification_types", []),
            "notification_channels": call.data.get("notification_channels", []),
            "person_type": call.data.get("person_type", PERSON_TYPE_MONITORED),
            "photo": call.data.get("photo", ""),
            "created_at": datetime.now().isoformat(),
            "updated_at": None,
        }
        hass.data[DOMAIN]["persons"].append(person)
        await _save()
        hass.bus.async_fire(EVENT_PERSON_ADDED, person)
        _LOGGER.info(
            "Digital Lifeline: persoon toegevoegd – %s (%s) [%s]",
            person["nickname"],
            person["person_type"],
            person["id"],
        )

    # ── Service: update_person ───────────────────────────────────────────────
    async def handle_update_person(call: ServiceCall) -> None:
        person_id = call.data["person_id"]
        updatable = [
            "nickname", "display_name", "first_name", "last_name", "gender",
            "birthdate", "street", "housenumber", "zipcode", "city", "phone", "email",
            "medication", "notes", "relation", "organization", "caregiver_function",
            "notification_types", "notification_channels", "person_type", "photo",
        ]
        for person in hass.data[DOMAIN]["persons"]:
            if person["id"] == person_id:
                for key in updatable:
                    if key in call.data:
                        person[key] = call.data[key]
                person["updated_at"] = datetime.now().isoformat()
                await _save()
                hass.bus.async_fire(EVENT_PERSON_UPDATED, person)
                _LOGGER.info("Digital Lifeline: persoon bijgewerkt – %s", person_id)
                return
        _LOGGER.warning("Digital Lifeline: persoon niet gevonden – %s", person_id)

    # ── Service: remove_person ───────────────────────────────────────────────
    async def handle_remove_person(call: ServiceCall) -> None:
        person_id = call.data["person_id"]
        before = len(hass.data[DOMAIN]["persons"])
        hass.data[DOMAIN]["persons"] = [
            p for p in hass.data[DOMAIN]["persons"] if p["id"] != person_id
        ]
        if len(hass.data[DOMAIN]["persons"]) < before:
            await _save()
            hass.bus.async_fire(EVENT_PERSON_REMOVED, {"id": person_id})
            _LOGGER.info("Digital Lifeline: persoon verwijderd – %s", person_id)
        else:
            _LOGGER.warning("Digital Lifeline: persoon niet gevonden – %s", person_id)

    hass.services.async_register(DOMAIN, SERVICE_ADD_PERSON, handle_add_person, schema=ADD_PERSON_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_UPDATE_PERSON, handle_update_person, schema=UPDATE_PERSON_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_REMOVE_PERSON, handle_remove_person, schema=REMOVE_PERSON_SCHEMA)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Digital Lifeline: integratie stoppen…")

    # Verwijder event listeners voordat platforms worden unloaded
    for unsub in hass.data.get(DOMAIN, {}).get("unsub_listeners", []):
        try:
            unsub()
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Digital Lifeline: fout bij afmelden listener: %s", err)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        for service in (SERVICE_ADD_PERSON, SERVICE_UPDATE_PERSON, SERVICE_REMOVE_PERSON):
            try:
                hass.services.async_remove(DOMAIN, service)
            except Exception as err:  # noqa: BLE001
                _LOGGER.warning("Digital Lifeline: fout bij verwijderen service %s: %s", service, err)
        hass.data.pop(DOMAIN, None)
        _LOGGER.debug("Digital Lifeline: integratie gestopt")
    else:
        _LOGGER.error("Digital Lifeline: stoppen mislukt – platforms konden niet worden unloaded")

    return unload_ok
