# Aggiornamento automatico – Milano My Events

Questo file descrive come aggiornare la pagina https://sydro82.github.io/MilanoMyEvents/ .
La pagina è generata da `build.py` a partire da `template.html`, `data/meta.json` e un file JSON per fonte in `data/sources/`.

## Procedura

1. `git pull` prima di tutto (la pagina può essere stata modificata da altre conversazioni).
2. Per ogni **fonte automatica** qui sotto: leggi la fonte, costruisci la lista degli eventi da oggi in poi
   e **sostituisci** il file della fonte. Se una fonte non si legge (errore, sito bloccato, struttura cambiata,
   browser non raggiungibile) **non toccare il suo file** e segnalalo nel riepilogo.
   Controllo di buon senso: se una fonte che prima aveva molti eventi ora ne restituisce 0 o pochissimi, non sostituire il file e segnalalo.
3. Le **fonti manuali** (`osteria-del-jazz`, `parteciprato-newsletter`, `teatro-carcano`, `manuali-vari`, `proposte`) non si rileggono: si lasciano come sono.
4. Proposte dal modulo (sezione sotto).
5. Aggiorna in `data/meta.json` lo `status` delle fonti automatiche (`"OK · N"` con N eventi, oppure `"Errore · <motivo breve>"` con `cls: "ko"`).
6. `python3 build.py --check`, poi `python3 build.py`.
7. Commit (autore `sydro82 <sydro82@users.noreply.github.com>`) e push su `main`. Messaggio tipo `Aggiornamento automatico GG/MM`.
8. Dopo 1–2 minuti verifica che la pagina online si carichi e mostri il numero di eventi atteso.
9. Riepilogo per Marco: per ogni fonte eventi nuovi / rimossi / errori, proposte pubblicate, proposte in attesa di approvazione.

## Formato di un evento

```json
{"title": "…", "start": "2026-12-05", "end": "2026-12-05", "time": "21:00", "end_time": "23:30",
 "venue": "Nome locale, indirizzo", "price": "7€", "url": "https://…", "note": "", "cat": "Concerto"}
```

- `start`/`end` in formato AAAA-MM-GG; `end` = `start` per eventi di un giorno. Eventi su più giorni (mostre, repliche): `start` = primo giorno, `end` = ultimo.
- `time`/`end_time` in HH:MM, vuoti se non indicati.
- `cat` (tipo): Concerto, Musica, Ballo, Cinema, Incontro, Corso, Teatro, Stand-up, Mostra, Mercatino, Festival, Serata, Laboratorio, Natale, Ritrovo, Socialità, Benessere, Planetario.
- `group`, `kids`, `free` **non vanno messi**: li calcola `build.py` (Cinema→Cinema, Corso→Corsi, Teatro/Stand-up→Teatro, Better Together→Better; bambini e gratis con parole chiave).
  Mettili solo per forzare un valore diverso dalla regola.
- Titoli: in italiano come sulla fonte, accorciati a ~70 caratteri se troppo lunghi (tieni il soggetto, togli frasi promozionali).
- Non inventare nulla: prezzi, orari e luoghi solo se la fonte li riporta.

## Fonti automatiche

| File | Fonte | Come leggerla |
|---|---|---|
| `corte-dei-miracoli` | https://www.latigredicarta.it/corte_dei_miracoli/calendario/ | WebFetch. venue `Corte dei Miracoli, via Mortara 4`. cat: Concerto per jam/concerti, Cinema per proiezioni/cineforum, Incontro per letture/incontri. |
| `biko` | https://www.bikoclub.net/ | WebFetch. venue `Biko`. Prezzi "prevendita" come `12€ prev.`; link DICE come url. note `Tessera Arci obbligatoria`. Corsi di tango: cat Corso; milonghe: Ballo. |
| `nidaba` | https://nidaba.it/concerti/concerti/ | WebFetch. venue `Nidaba Theatre`, cat Concerto. Prezzo solo se indicato. |
| `better-together-sito` | https://www.bettertogetherspace.it/ (sezione ritrovi) | WebFetch. Un evento per ritrovo: title `Ritrovo Better Together`, time `09:00`, end_time = chiusura, venue con indirizzo e metro, cat Ritrovo, price `5€ primo mese / 12€ singolo / 40€ mese`, url `https://www.bettertogetherspace.it/#ritrovi`, note `Coworking 9–19, circoli di dialogo 11 e 16, pasti conviviali.` (+ ` Tessera dello spazio richiesta.` dove indicato). |
| `better-together-instagram` | https://www.instagram.com/better.together.space/ | **Browser integrato** (serve il Mac acceso). Apri il profilo, apri il post più recente che elenca "le seguenti attività spontanee" della settimana e leggi la didascalia. Un evento per attività: title `BT · <attività>`, cat Socialità/Benessere/Cinema/Incontro, price `Incluso nella quota`, url del post, note `Attività della settimana dal post Instagram del GG/MM`. Tieni anche le attività delle settimane precedenti se non ancora passate. Se il browser non risponde, salta la fonte. |
| `milano-da-scrocco` | https://www.milanodascrocco.com/eventi.php | **Browser integrato**: apri la pagina e nella pagina esegui `await fetch('/dmxConnect/api/frontend/lista_eventi_by_date.php?vardate=<OGGI>T00%3A00%3A00&startdate=<G>-<MonthName>-<AAAA>&enddate=<OGGI+2 mesi>%2000%3A00%3A00.000').then(r=>r.json())`; prendi gli eventi unici di `repeatDatew[].query[]` (evento_name, start_date, end_date, ora_inizio/minuti_inizio, ora_fine/minuti_fine; ore 0 = non indicato). url `https://www.milanodascrocco.com/evento.php?nome=<evento_slug>`, venue `Milano`, price `Gratis / low cost`. cat: Mostra / Mercatino / Festival / Serata / Teatro / Laboratorio / Natale / Incontro. |
| `teatri-possibili` | https://www.teatripossibili.it/eventi/elenco/ | WebFetch. Spettacoli → Teatro, seminari/open day → Corso, club del cinema → Cinema, club del libro → Incontro. |
| `planetario` | https://booking.lofficina.eu/Sito/Default.aspx?partner=PLAN | WebFetch. title `Planetario · <titolo>`, venue `Civico Planetario Ulrico Hoepli, corso Venezia 57`, cat Planetario, url = link Acquisto.aspx dell'evento, note `Prenotazione online su LOfficina`. |

MilanoToday (https://www.milanotoday.it/eventi/…) blocca le letture automatiche (403): non riprovare.

## Proposte dal modulo

Foglio: https://docs.google.com/spreadsheets/d/1Gw3QjCE6FR8nz6wYtKMdDQSMe1hSIp24vqcM71I_NL0 (scheda "Risposte del modulo 1").
Colonne: A data, B link, C prezzo/gratis, D info aggiuntive, E nome, F **Approvato** (sì/no, la compila Marco), G **Pubblicato** (la compila Claude).

- Righe con F = `sì` e G vuota: apri il link, ricava l'evento (usa C e D per completare), aggiungilo a `data/sources/proposte.json`, poi scrivi in G la data `GG/MM/AAAA`.
  Se il link è una **fonte** (sito/profilo con tanti eventi) e non un singolo evento, non aggiungerla: scrivi in G `fonte – da valutare` e segnalala a Marco.
- Righe con F vuota: non pubblicarle, elencale nel riepilogo come "in attesa di approvazione".
- Righe con F = `no`: ignorale.
