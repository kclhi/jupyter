FROM osixia/openldap:1.2.4

ADD certs /container/service/slapd/assets/certs

COPY load-ppolicy.ldif /container/service/slapd/assets/config/bootstrap/ldif/custom/
COPY overlay-ppolicy.ldif /container/service/slapd/assets/config/bootstrap/ldif/custom/
