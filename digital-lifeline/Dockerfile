ARG BUILD_FROM
FROM $BUILD_FROM

# Kopieer de integratie-bestanden naar de image
COPY custom_components /integration/custom_components

# Kopieer het run-script
COPY rootfs /

RUN chmod a+x /usr/bin/digital-lifeline
