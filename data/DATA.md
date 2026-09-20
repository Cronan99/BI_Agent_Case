# Dataset: försäljningsdata

Detta dataset följer med utvecklarcaset. Det består av sex CSV-filer med rådata. Filerna beskriver vilken data som finns, inte hur den ska modelleras eller lagras. Det avgör du.

## Filer

### brands.csv
Varumärkena och vilken leverantör (tillverkare) som äger dem.

| Kolumn | Beskrivning |
|---|---|
| brand_id | Unikt id för varumärket |
| brand_name | Varumärkets namn |
| supplier | Leverantören som äger varumärket |

### products.csv
Produktkatalogen. Varje produkt tillhör ett varumärke.

| Kolumn | Beskrivning |
|---|---|
| product_id | Unikt id för produkten |
| product_name | Produktnamn |
| brand_id | Varumärket produkten tillhör |
| category | Produktkategori |
| unit_price_sek | Listpris per enhet i SEK |

### stores.csv
Detaljhandelsföretagets butiker, dit försäljningen sker.

| Kolumn | Beskrivning |
|---|---|
| store_id | Unikt id för butiken |
| store_name | Butikens namn |
| city | Stad |
| region | Region (Götaland, Svealand, Norrland) |

### orders.csv
Försäljningstransaktioner på orderradsnivå, januari 2025 till juni 2026. En order kan bestå av flera rader.

| Kolumn | Beskrivning |
|---|---|
| order_line_id | Unikt id för orderraden |
| order_id | Ordern raden tillhör |
| order_date | Orderdatum (YYYY-MM-DD) |
| store_id | Butiken som lade ordern |
| product_id | Beställd produkt |
| quantity | Antal enheter |
| unit_price_sek | Pris per enhet vid ordertillfället i SEK |
| line_total_sek | Radens totalbelopp i SEK |

### users.csv
Personerna hos leverantörerna som ska kunna logga in i applikationen.

| Kolumn | Beskrivning |
|---|---|
| user_id | Unikt id för användaren |
| full_name | Namn |
| email | E-postadress |
| company | Leverantören personen arbetar hos |
| role | Personens roll |

### user_brand_access.csv
Vilka varumärken varje användare har tillgång till. En användare kan ha tillgång till ett eller flera varumärken.

| Kolumn | Beskrivning |
|---|---|
| user_id | Användare |
| brand_id | Varumärke användaren har tillgång till |

## Noteringar

- Datan är syntetisk men representativ. Belopp är i SEK.
- Filerna innehåller inga lösenord eller inloggningsuppgifter. Hur autentisering sätts upp för användarna är en del av uppgiften.
- Du får transformera, normalisera och komplettera datan som du vill när du läser in den i din databas.
