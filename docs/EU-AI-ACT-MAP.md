# Mapa EU AI Act (wsparcie zgodności)

| Obszar | Kontrola techniczna | Dowód |
|---|---|---|
| Art. 12 — rejestrowanie | chronologiczny, integralny łańcuch wejść, wyjść, werdyktów i czasu | eksport JSONL, offline verifier, retencja WORM |
| Art. 14 — nadzór człowieka | podpis TRANSACT, WAIT/SILENCE, STOP i jawne wznowienie | `human_accountable`, log decyzji, procedura operatora |
| Art. 50 — transparentność | identyfikacja trybu/modelu i odpowiedzi AI w API/dashboardzie | metadane rekordu, UI, dokumentacja integratora |

To mapowanie jest punktem wyjścia, nie opinią prawną ani automatycznym wykazaniem zgodności. Wdrożenie wymaga klasyfikacji systemu, oceny ryzyka, polityk retencji, informacji dla osób, zarządzania incydentami i przeglądu prawnego właściwego dla zastosowania.
