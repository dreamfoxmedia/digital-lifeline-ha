ARG BUILD_FROM
FROM $BUILD_FROM

COPY custom_components /integration/custom_components
COPY rootfs /

RUN chmod a+x /etc/services.d/digital_lifeline/run
