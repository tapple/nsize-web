# nSize

SECURITY TODO:
- SSL
- Require Token Auth for the LSL Gateway Registration, so other server's can't impersonate mine
- Change the auth for Outfit server to be compatable with Django token auth (Authorization Header, not query param)
- Require Token Auth for the delivery api so that people can't use it to spam others with inventory offers, or overload the in-world servers

TESTING TODO:
- make migrations for sl_profile so it's unit tests can be run via manage.py
- write unit tests for sl_cap_gateway
- make some unit tests for the lsl services, using their api

INFRA TODO:
- Maybe make a db backend for sl_cap_gateway so I don't have to pay for a redis instance I'm not using

