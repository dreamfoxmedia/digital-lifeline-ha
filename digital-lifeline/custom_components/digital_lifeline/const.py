"""Constants for the Digital Lifeline integration."""

DOMAIN = "digital_lifeline"
STORAGE_KEY = "digital_lifeline_persons"
STORAGE_VERSION = 1

PERSON_TYPE_MONITORED = "monitored"
PERSON_TYPE_FAMILY = "family"
PERSON_TYPE_CAREGIVER = "caregiver"

PERSON_TYPES = [PERSON_TYPE_MONITORED, PERSON_TYPE_FAMILY, PERSON_TYPE_CAREGIVER]

PERSON_TYPE_LABELS = {
    PERSON_TYPE_MONITORED: "Bewaakt persoon",
    PERSON_TYPE_FAMILY: "Familielid",
    PERSON_TYPE_CAREGIVER: "Hulpverlener",
}

SERVICE_ADD_PERSON = "add_person"
SERVICE_UPDATE_PERSON = "update_person"
SERVICE_REMOVE_PERSON = "remove_person"

EVENT_PERSON_ADDED = f"{DOMAIN}_person_added"
EVENT_PERSON_UPDATED = f"{DOMAIN}_person_updated"
EVENT_PERSON_REMOVED = f"{DOMAIN}_person_removed"
