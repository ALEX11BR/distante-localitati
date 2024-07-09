# Distanțe orașe

## Folosire calcul-distante.py
Comanda:
```shell
DISTANTE_JUDET=BR DISTANTE_ORASE=da DISTANTE_TIP=time DISTANTE_OUTPUT=timpi_importanti_br.csv ./calcul_distante.py
```

Variabilele de mediu au semnificația:
- `DISTANTE_JUDET`: codul județului (nesetat => toată țara)
- `DISTANTE_ORASE`: dacă e setat, nu se calculează între 2 sate
- `DISTANTE_TIP`: ce se calculează; `time` => timpi (min), `distance` => distanțe (km)
- `DISTANTE_OUTPUT`: fișierul CSV unde se scriu distanțele

Pentru alte filtre mai avansate se poate folosi ceva de genul:
```shell
python3 -c 'from calcul_distante import compute_distances; compute_distances((lambda city: city["properties"]["countyMn"] == "BR"), (lambda city: city["properties"]["rank"] in ["0", "I", "II", "III"]]))'
```

## Folosire graphhopper.sh
`./graphhopper.sh`: deschide un server cu datele din `graphhopper_data`. Dacă nu e cache făcut, se rulează mai întâi `./graphhopper.sh init`.

`./graphhopper.sh init`: descarcă fișierele cu localități și drumuri OpenStreetMap dacă nu sunt prezente și inițializează cacheul de date de drumuri

`./graphhopper.sh reset`: șterge fișierele cu localități și drumuri OpenStreetMap preexistente înainte de rularea `./graphhopper.sh init`.
