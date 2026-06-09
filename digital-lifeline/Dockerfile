ARG BUILD_FROM
FROM $BUILD_FROM

COPY custom_components /integration/custom_components
COPY rootfs /

RUN chmod a+x /usr/bin/digital-lifeline

ENTRYPOINT ["/bin/bash", "/usr/bin/digital-lifeline"]
