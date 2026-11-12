---
title: Träningsavgifter
category: Träning & praktiskt
permalink: "/traning/traningsavgifter/"
source_date: '2026-11-03'
source_id: '31'
maintained_content: true
description: 'Träningsavgifter hos Alingsås Ju-Jutsuklubb: terminsavgifter, familjerabatt,
  graderingsavgifter och information om betalning.'
---

{% assign knattar = site.data.groups.groups.toddlers %}
{% assign barn = site.data.groups.groups.children %}
{% assign vuxna = site.data.groups.groups.adults %}
{% assign fees = site.data.groups.fees %}

**Terminsavgift:**

| Grupp | Pris |
| --- | --- |
| {{ knattar.name }} {{ knattar.ages }} | {{ fees.term.toddlers }} kr |
| {{ barn.name }} {{ barn.ages }} | {{ fees.term.children }} kr |
{% for rate in fees.term.adults -%}
| {{ vuxna.name }} {{ rate.ages }} | {{ rate.fee }} kr |
{% endfor %}

På träningsavgiften lämnas **familjerabatt** om {{ fees.family_discount.fee }} kr / termin vid minst {{ fees.family_discount.minimum_people }} personer.

**Bankgiro {{ site.data.club.bankgiro }}**

**Swish {{ site.data.club.swish }}**

Ange **namn** och **träningsgrupp** som meddelande på inbetalningen.

Fyll i blanketten ”uppgifter till medlemsregistret” som ni får av er instruktör och lämna in den så snart som möjligt. Om ni har bytt adress eller telefonnummer så be om en ny blankett.

Vi är anslutna till ”Fritidskortet”. Har du barn i åldern 8-16 år kan du läsa mer om detta bidrag [HÄR](<https://fritidskortet.se/>)

Betalning av medlems- och träningsavgiften skall ha skett **senast**:

**För nybörjare:** vårterminen 10 februari och höstterminen 10 september. (Senast två veckor efter påbörjad provperiod vid löpande intag)

**För övriga medlemmar:** vårterminen 1 februari och höstterminen 1 september.

Vid **försenad** betalning är du välkommen att delta i träningen **efter** betald avgift.

I medlemsavgiften ingår medlemsavgift till Svenska Ju-Jutsu Kai, Svenska Budo och Kampsportsförbundet, som är anslutet till Riksidrottsförbundet. Detta innebär att du som medlem är försäkrad genom idrottens gemensamma försäkring.

**Stödmedlemskap:**

*Möjlighet att vara stödmedlem för {{ fees.supporting_membership }} kr / år*

**Graderingsavgift:**

| Grupp | Pris |
| --- | --- |
| {{ knattar.name }} {{ knattar.ages }} | {{ fees.grading.toddlers }} kr |
| {{ barn.name }} {{ barn.ages }} | {{ fees.grading.children }} kr |
| {{ vuxna.name }} {{ vuxna.ages }} | {{ fees.grading.adults }} kr |

Mon och knattepass medföljer i kostnaden vid ens första graderingstillfälle (1 sträck / mon gult). Vid nyinköp av ytterligare mon eller knattepass (senare grader / vid borttappat pass) tillkommer en kostnad på {{ fees.replacement_grading_pass }} kr.
