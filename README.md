# Alingsås Ju-Jutsu

Jekyll-webbplats för GitHub Pages, konfigurerad för `https://alingsasju-jutsu.se`.

## Uppdatera träningstider

Alla aktuella träningstider finns i **en enda fil**:
[`_data/training_schedule.yml`](_data/training_schedule.yml).
Ändringar där visas automatiskt på **startsidan, Schema och Börja träna**.
Du behöver inte installera något eller ändra dessa sidor var för sig.

### Så redigerar du direkt på GitHub

1. Öppna [schemafilen](_data/training_schedule.yml) och kontrollera att
   grenen **main** är vald.
2. Klicka på pennan **Edit this file** ovanför filens innehåll. Du behöver
   vara inloggad och ha skrivbehörighet. Du kan också använda
   [direktlänken till redigering](https://github.com/Alingsas-Ju-Jutsu/alingsasju-jujutsu.se/edit/main/_data/training_schedule.yml).
3. Ändra önskade tider, terminsstart eller avvikelser enligt exemplen nedan.
   Behåll indrag, bindestreck och citattecken. Ändra bara de uppgifter som
   ska uppdateras.
4. Klicka på **Commit changes…** och skriv en kort beskrivning, till exempel
   ”Uppdatera vuxnas söndagsträning”.
5. Om GitHub tillåter det kan du välja att spara direkt till **main**.
   Då startar publiceringen direkt. Om en ny gren eller ett ändringsförslag
   krävs skapar du det i stället; en ansvarig person behöver sedan granska
   och slå ihop det till **main**.
6. Följ publiceringen under **Actions → Deploy Jekyll site to Pages**.
   När den är klar kontrollerar du tiderna på webbplatsen. Om körningen
   misslyckas öppnar du den för att se felet; ändringen är då inte publicerad.

### Ändra en grupps träningstider

Leta upp gruppen under `groups`. `name` är gruppnamnet, `ages` är åldrarna
och varje post under `sessions` är ett träningstillfälle. `day` är veckodagen,
`start` starttiden och `end` sluttiden.

Exempel på en vuxengrupp med två träningstillfällen:

```yaml
  - name: Vuxna
    ages: "14+ år"
    sessions:
      - day: Torsdagar
        start: "19.45"
        end: "21.00"
      - day: Söndagar
        start: "19.45"
        end: "21.00"
```

För att ändra söndagstiden redigerar du bara `start` och `end` under
`Söndagar` i rätt grupp. Tiderna ovan är ett exempel på formatet; ersätt inte
hela filen med exemplet eftersom andra grupper och inställningar då försvinner.

### Ändra terminsstart

Ändra `date` under `term_start` överst i filen:

```yaml
term_start:
  title: Terminsstart
  date: "2027-01-10"
```

Datumet visas som det är skrivet. Du kan också skriva exempelvis
`"10 januari 2027"`. Behåll citattecknen. Med `date: ""` visas
”Datum meddelas snart.”.

### Lägg till lov eller andra avvikelser

Under `exceptions` kan du ange datum och en kort beskrivning i `reason`.
Använd datumformatet `YYYY-MM-DD` inom citattecken:

```yaml
exceptions:
  - date: "2026-10-22"
    reason: Höstlov
  - date: "2026-12-24"
    reason: Ingen träning på julafton
```

Lägg till en ny post med samma indrag för varje datum. Beskriv vilka grupper
som berörs om avvikelsen inte gäller alla. Listan visas i datumordning under
”Avvikelser i träningsschemat”. Avvikelser är information till besökarna;
de ändrar inte de återkommande träningstiderna automatiskt.

Ta bort en passerad avvikelses båda rader när den inte längre ska visas.
För att dölja hela avvikelsesektionen ersätter du listan med:

```yaml
exceptions: []
```

**Viktigt:** YAML använder indrag för att koppla ihop uppgifter. Använd
mellanslag, inte tabbar, och behåll samma indrag som i den befintliga filen.
Sätt datum och tider inom citattecken. En framtida terminsstart eller avvikelse
innebär inte tidsinställd publicering: allt du sparar till `main` publiceras
vid nästa lyckade byggning.

## Uppdatera instruktörer

Instruktörssidan byggs av HTML-kort med vanliga porträttbilder.
Ändra namn, bild och eventuell presentation i
[`_data/instructors.yml`](_data/instructors.yml). Du behöver inte skapa
nya affischbilder när texten ändras.

Varje post har `name` (namn), `image` (sökväg till porträttbild),
`color` (kortets bakgrundsfärg), `level` (grad, till exempel `2 dan`)
och `description` (valfri presentation). Graden visas under porträttet,
med samma ju-jutsu-emblem som vid namnet. Med `level: ""` döljs gradfältet.
Välj `black`, `brown`, `blue`, `orange` eller `green` för `color`, till
exempel `color: brown`. Färgerna är anpassade för läsbar vit text.
Utan `color` används svart.
Med `description: ""` visas ingen
presentationstext. Ordningen i filen styr ordningen på sidan. Kopiera en
hel post för att lägga till en instruktör eller ta bort posten för att
ta bort någon från sidan. Ladda upp nya porträtt i
`assets/images/instructors/` och ange motsvarande sökväg i `image`.
Använd en vanlig porträttbild utan inbakad text.

## Träningsaffischen på Schema

GitHub bygger automatiskt en aktuell PNG-affisch från
[`_data/training_schedule.yml`](_data/training_schedule.yml) vid varje publicering.
Affischen innehåller terminsstart, grupper, åldrar och ordinarie träningstider.
Lov och andra avvikelser visas bara i webbplatsens textschema, inte på affischen.
Ändra YAML-filen som vanligt; ingen bild behöver redigeras manuellt.
På sidan Schema visas affischen med en nedladdningslänk.

Generatorn finns i `tools/build_poster.py` och återanvänder överdelen av
originalaffischen med foto, logotyp och rubrik. Originalets gamla tider och
datum beskärs bort och ersätts med en mörk schemaruta: grupperna visas i
tre kolumner med terminsstart nedanför. När en bakgrund utan text finns kan
den ersätta den beskurna originalbilden.
Genererade bilder i `assets/generated/` ska inte checkas in.
`make build` och `make serve` genererar också affischen via Docker.
Starta om förhandsvisningen efter schemaändringar för att uppdatera PNG-filen;
textschemat uppdateras fortfarande med Jekylls vanliga omladdning.

## Redigera sidor

GitHub Copilot-agenter följer
[`.github/copilot-instructions.md`](.github/copilot-instructions.md) för
gemensamma redigeringsregler i kodförrådet. Lägg bestående riktlinjer där.
Exakta formuleringar, datum, berörda sidor och kriterier för att uppgiften är
klar hör hemma i GitHub-ärendet som tilldelas agenten. Uppdatera instruktionerna
när webbplatsens innehållsstruktur eller redigeringsflöde ändras.
Vid vanliga innehållsuppdateringar redigerar agenter Markdown och gemensam
YAML-data samt sparar och skickar ändringarna till uppgiftens gren och
ändringsförslag, utan att köra Docker, installera beroenden eller bygga
webbplatsen lokalt. GitHubs Copilot coding agent kan inte skicka direkt till
`main` eller godkänna och slå ihop sitt eget ändringsförslag. Instruktioner
i kodförrådet kan inte ge dessa behörigheter. En ansvarig person granskar och
slår ihop ändringen, varefter GitHub Actions bygger och publicerar automatiskt.
Utvecklingsändringar i mallar eller verktyg behöver fortfarande relevanta
bygg- och testkontroller.

Redigera rätt fil i `_club_pages/`: text, rubriker, länkar, bilder och tabeller
skrivs i Markdown, inte i separata HTML-innehållsfiler. Behåll YAML-metadata
(frontmatter) överst; `title` styr rubriken och `permalink` styr sidans URL.
Nyhetsartiklar finns i `_club_pages/nyheter/` och graderingsinlägg i
`_club_pages/graderingar/`. Båda använder filnamn som `YYYY-MM-DD-title.md`,
baserade på publiceringsdatumet. Deras `permalink`-värden behåller befintliga
offentliga URL:er oförändrade. Nyhets- och dokumentöversikten är `nyheter.md`
och nås på `/nyheter/`. Alingsåslägrets sidor samlas i
`_club_pages/alingsaslagret/`, med `index.md` för översikten och årsfiler
som `2004.md`.

Startsidan är `index.md`: dess YAML-metadata innehåller texter för
huvudsektionen, navigering och kontakt, medan Markdown-innehållet innehåller
schemasektionen. Gemensam HTML finns i `_layouts/` och `_includes/` för att
bevara den responsiva designen. Navigering, scheman, dokumentlistor och
sponsoruppgifter finns i `_data/`. Kalenderlänken öppnar Google Kalender
i stället för att bädda in en HTML-iframe.

När du redigerar en importerad sida lägger du till `maintained_content: true`
i dess metadata så att framtida importer inte skriver över ändringarna.
`_data/excluded_archive_pages.yml` listar borttagna källsidors ID:n som inte
får återställas av framtida importer.

Så här upprepar du innehållsöverföringen från ett färdigt arkiv:

```sh
make import
# Eller välj ett annat färdigt arkiv:
make import ARCHIVE=_old_site/<timestamp-directory>
make build
make import-test
```

Importverktyget behåller klubbens befintliga sidadresser och omvandlar
WordPress-länkar till lokala sidor och resurser. En ny import ersätter
genererat sidinnehåll och metadata om inte `maintained_content: true` är satt.
Den återställer inte WordPress-tillägg, inloggning eller det gamla temats skript.
Importkontrollen jämför originaltext samt antal bilder och tabeller på
oredigerade sidor, verifierar mediekopior och kontrollerar alla genererade
lokala länkar och gemensamma schemavisningar. Redigerade sidor som markerats
med `maintained_content: true` undantas från jämförelser med källinnehållet.

## Lokal utveckling med Docker

Installera Docker med Compose-tillägget och GNU Make. Starta sedan
utvecklingsservern med automatisk omladdning:

```sh
make serve
```

Öppna [http://localhost:4000](http://localhost:4000). Projektmappen är monterad
i containern, så ändringar slår igenom automatiskt. Stoppa servern med
`Ctrl+C` eller `make stop`.

Bygg den statiska webbplatsen till `_site/` eller ta bort genererade filer med:

```sh
make build
make clean
```

Webbplatsen byggs och publiceras av GitHub Actions-arbetsflödet i
`.github/workflows/pages.yml`. Välj **GitHub Actions** som källa för byggning
och publicering under Pages i kodförrådets inställningar.

Publiceringsflödet läser webbplatsens domän och bassökväg från GitHub Pages
och åsidosätter motsvarande värden i `_config.yml` för den byggningen.
Testwebbplatsen på
`https://alingsas-ju-jutsu.github.io/alingsasju-jujutsu.se/` använder därför
kodförrådets sökväg för resurser och länkar. Vid lansering anger du
`alingsasju-jutsu.se` som egen domän under **Settings → Pages**, uppdaterar DNS
och kör publiceringsflödet igen. Då används domänen utan kodförrådets sökväg;
ingen kodändring behövs. Lokal förhandsvisning med Docker påverkas inte.

## Lansering på alingsasju-jutsu.se

1. Låt domänens befintliga DNS-inställningar vara oförändrade medan
   testwebbplatsen granskas. Se till att det uppdaterade publiceringsflödet
   har skickats till `main`.
2. När det är dags att byta öppnar du **Settings → Pages**, behåller
   **GitHub Actions** som källa och anger `alingsasju-jutsu.se` under
   **Custom domain**. Kodförrådets `CNAME`-fil innehåller redan domänen,
   men med denna Actions-baserade publicering måste den även anges i
   Pages-inställningarna.
3. Hos DNS-leverantören ersätter du motstridiga A/AAAA-poster för
   rotdomänens webbplats (`@`) med GitHub Pages A-poster:

   | Typ | Namn | Värde |
   | --- | --- | --- |
   | A | @ | 185.199.108.153 |
   | A | @ | 185.199.109.153 |
   | A | @ | 185.199.110.153 |
   | A | @ | 185.199.111.153 |
   | CNAME | www | alingsas-ju-jutsu.github.io |

   Använd DNS-leverantörens motsvarighet till `@` för rotdomänen.
   CNAME-värdet för `www` ska endast vara ett värdnamn, utan kodförrådets
   sökväg. Behåll e-postens MX-poster och andra orelaterade TXT-poster.
   Om IPv6/AAAA-poster finns ska de uppdateras till GitHubs dokumenterade
   värden, eller gamla AAAA-poster för webbplatsen tas bort, så att
   IPv6-besökare inte fortsätter hamna på den gamla servern. Kontrollera
   aktuella värden i GitHubs [dokumentation för egna domäner](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
   innan DNS ändras.
4. Öppna **Actions → Deploy Jekyll site to Pages → Run workflow** och välj
   `main` efter att domänen sparats. Byggningen använder automatiskt domänen
   och en tom bassökväg i stället för `/alingsasju-jujutsu.se`.
5. Vänta på Pages DNS-kontroll och att certifikatet utfärdas. Aktivera sedan
   **Enforce HTTPS** under **Settings → Pages** när valet blir tillgängligt.
6. Kontrollera `https://alingsasju-jutsu.se/` och
   `https://www.alingsasju-jutsu.se/`, inklusive bilder, menyer, träningsschema
   och en nyhetsartikel. Kontrollera att länkar och kanoniska URL:er använder
   den riktiga domänen utan kodförrådets prefix. GitHubs projektadress kan
   därefter omdirigeras till den egna domänen.

Du behöver inte ändra `_config.yml`, Markdown-länkar eller CSS-sökvägar vid
bytet: arbetsflödet hämtar publiceringsadressen från GitHub Pages-inställningarna.
DNS-ändringar och utfärdande av certifikat kan ta tid. Behåll åtkomsten till
det gamla webbhotellet tills den nya webbplatsen har bekräftats fungera.

Startsidan och undersidorna använder den arkiverade webbplatsens logotyp,
stora huvudbilder för dator och mobil, klubbadress, kontaktuppgifter,
sociala länkar och navigering. Alla länkar i klubbens menyer går till sidor på
denna webbplats. Det offentliga arkivet har överförts till 24 klubbundersidor
och 60 daterade nyhetssidor som nås via `/nyheter/`. Avgifter, kontaktuppgifter,
regler, instruktörspresentationer, scheman, stadgar, lägerrapporter,
graderingsgallerier och länkade dokument ingår. Alingsåslägrets årssidor
ligger kvar under Läger → Alingsåslägret.

Källinformationen hämtades 2026-11-03 och har inte verifierats som aktuell.
Kalendern från 2013, det äldre schemat och nyheterna är historiska.
Material enbart för instruktörer var lösenordsskyddat och finns inte på denna
statiska webbplats. Graderingsinlägg utan tillgängliga foton har tagits bort.
En otillgänglig extern lägerbild har markerats i stället för att länkas in
från den externa servern. Trasiga källänkar är också markerade.
`_data/import_report.json` innehåller referenser som inte kunde lösas.
Originalarkivet `_old_site` behålls lokalt som källreferens och ingår varken
i Git eller i den genererade webbplatsen. Sidinnehållet lagras direkt i
`_club_pages/*.md`, med mediefiler i `assets/archive/`, så publiceringen är
inte beroende av det lokala källarkivet.

## Publicera en nyhet utan att redigera filer

Välj **Issues → New issue → Publicera en nyhet**. Skriv eller klistra in
texten, eller ge agenten stödord med de fakta som ska vara med. Dra in bilder
om du vill. Det enda obligatoriska fältet är vad du vill berätta.

En ansvarig person tilldelar ärendet till **Copilot**, som föreslår rubrik,
formaterar texten och skapar ett ändringsförslag. Nyheten kommer automatiskt
med på sidan Nyheter. Kontrollera text och bilder, godkänn och slå ihop
förslaget till **main** för att publicera. Samma krav på Copilot-behörighet och
granskning som för schemaändringar gäller här.

Lämna publiceringsdatum tomt för publicering så snart förslaget är granskat.
För ett framtida datum behöver en ansvarig person vänta med sammanslagningen;
webbplatsen har ingen automatisk tidsinställd publicering.

## Ändra schemat utan att redigera filer

1. Öppna fliken **Issues** på GitHub, välj **New issue** och sedan
   **Ändra träningsschema**.
2. Beskriv ändringen med vanliga ord: vilken grupp, vilka tider eller vilket
   datum och när ändringen ska gälla. Du behöver inte kunna YAML eller kod.
3. En person med rätt behörighet tilldelar ärendet till **Copilot**.
   Detta kräver att Copilot coding agent är tillgänglig och aktiverad för
   kontot/organisationen; formuläret startar inte agenten automatiskt.
4. Copilot förbereder ett ändringsförslag (pull request) med en sammanfattning.
   Kontrollera att grupper, tider och datum är rätt. Besvara eventuella frågor
   i ärendet eller ändringsförslaget.
5. En ansvarig person godkänner och slår ihop förslaget till **main**.
   GitHub Actions bygger och publicerar sedan webbplatsen.

Samma schemauppgifter används på startsidan, Schema och Börja träna. Ändringar
behöver därför bara beskrivas en gång. Publiceringen sker vid sammanslagning,
inte automatiskt på ett framtida startdatum. Om ändringen ska publiceras senare
behöver sammanslagningen planeras av en ansvarig person.

## Sökmotorer och tillgänglighet

Webbplatsen genererar sidtitlar, kanoniska URL:er, delningsmetadata,
`sitemap.xml` och `robots.txt`. Sidornas `description` i YAML-metadata används
som beskrivning för sökresultat. Nya nyheter ska även ha `date: "YYYY-MM-DD"`
och `seo: { type: BlogPosting }`. Adresserna anpassas automatiskt till testdomänen eller den egna
domänen vid publicering.

Klubbens logotyp används som standardbild för delning (`og:image`).
Inställningen finns under `defaults` i `_config.yml`. En enskild sida kan
ange en egen delningsbild med `image: /assets/images/bild.jpg` i sin metadata.

Behåll en tydlig rubrikordning: sidmallen skapar huvudrubriken, så börja
innehållets rubriker med `##`. Skriv beskrivande länktexter och bildalternativ,
och använd riktiga kolumnrubriker i tabeller. Viktig text i affischer behöver
också finnas som vanlig text. Startsidan har en knapp för att pausa bildspelet;
besökarens inställning för minskad rörelse respekteras. Menyerna fungerar med
tangentbord och kan stängas med Escape.

Förbättringarna riktar sig mot WCAG 2.2 AA men är inte en certifiering eller
juridisk bedömning. Manuell granskning med skärmläsare, zoom och tangentbord
behövs även efter automatiska kontroller. Äldre PDF-/Excel-dokument och
bildgallerier behöver separat bedömas; en automatiserad HTML-kontroll
bekräftar inte deras tillgänglighet.

Vid utveckling kan du efter `make build` kontrollera metadata, strukturerad
data, bildalternativ, tabellrubriker, lokala länkar och sökmotorfiler med:

```sh
docker compose run --rm site ruby tools/validate_site.rb
```

För en byggning med annan domän och bassökväg kan dessa anges som argument
till kontrollskriptet. Detta är inte ett krav vid vanliga innehållsuppdateringar.

Webbplatsens egna mallar laddar inga analysverktyg, externa typsnitt eller
inbäddade sociala flöden. Kartor, kalender och sociala medier öppnas via länkar.
Detta ersätter inte klubbens ansvar att granska publicering av personuppgifter,
foton (särskilt på barn), värdtjänstens behandling av besöksdata eller behovet
av integritetsinformation. Lägg inte till en samtyckesbanner som en kosmetisk
åtgärd; bedöm faktisk behandling och samtyckesbehov innan nya spårningstjänster
eller inbäddningar införs.

## Arkivera den offentliga källwebbplatsen

```sh
make scrape
```

Detta bygger en separat Playwright-container och besöker offentliga länkar
på samma webbplats med vanlig Chromium. Verktyget öppnar inte administrationssidor,
loggar inte in, använder inga tillägg för att dölja automatisering, löser inte
CAPTCHA och gör inte nya försök vid en pågående åtkomstblockering.
Anropen sker i följd med två sekunders paus mellan sidorna.

Varje körning skapar en tidsstämplad mapp i `_old_site/` utan att ändra
tidigare arkiv. Den sparar renderad HTML, inlästa bilder, bakgrunder,
typsnitt och CSS, länkade dokument på samma webbplats (inklusive PDF-,
Word- och Excel-filer) samt `manifest.json`. Sid- och resurslänkar skrivs
om till lokala filer; externa länkar behålls. Skript tas bort från sparad
HTML, så detta är ett innehållsarkiv för överföring, inte en fungerande
WordPress-kopia. Endast sidor som nås via offentliga länkar upptäcks.
Olänkade sidor och privat instruktörsmaterial kräver en behörig export.

Kommandot avslutas med fel vid blockerade sidor, misslyckad hämtning av
resurser eller en ofullständig genomsökning. Trasiga källänkar (404/410)
loggas i `brokenLinks` och stoppar inte genomsökningen. Se manifestfilen
och `last-page.html` / `last-page.png` för feldetaljer. Om vanlig
webbläsarinläsning fortfarande misslyckas kan du begära en export eller
be webbhotellet tillåta arkiveringsverktyget.

Så här ändrar du källadress eller gränser för genomsökningen:

```sh
SOURCE_URL=https://alingsasju-jutsu.se/ MAX_PAGES=500 DELAY_MS=2000 make scrape
make scrape-test
```

Ett ofullständigt arkiv med sparad kö kan återupptas i samma mapp:

```sh
RESUME_ARCHIVE=/archive/<timestamp-directory> make scrape
```
