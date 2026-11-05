---
title: Barnträning
category: Träning & praktiskt
permalink: "/ju-jutsu/barntraning/"
source_date: '2026-11-03'
source_id: '274'
maintained_content: true
description: Praktisk information för vårdnadshavare om barnträningen i Alingsås
  Ju-Jutsuklubb, grupper, engagemang och läger.
---

## För vårdnadshavare

### Trygghet
Vi vill att alla barn ska känna sig trygga och ha roligt på träningen. De första gångerna är du som vårdnadshavare välkommen att vara med inne i dojon, så att ditt barn får en trygg start. Därefter har vi inte möjlighet att ha föräldrar eller andra vårdnadshavare närvarande i dojon under passen. Det ger instruktörerna arbetsro att leda träningen, ta hand om barnen och hjälpa gruppen att hitta fokus och gemenskap.

### Engagemang
Vi uppskattar engagemang och välkomnar dig som vill bidra till klubben, men för att vara med och hjälpa till under träningarna behöver man, som våra instruktörer, ha gått ledarskapsutbildning och ha kunskaper i ju-jutsu något vi **inte** förutsätter att vårdnadshavare har möjlighet att skaffa sig. Om du är intresserad av att engagera dig, kontakta oss så berättar vi mer om det finns sätt att bidra till klubben.

### Grupper
 Vi rekommenderar att barn börjar träna i den grupp som passar deras ålder, men det är också möjligt att byta grupp och träna med en annan grupp om det passar bättre pga t.ex. erfarenhet, kompisar eller andra skäl. Detta kan du diskutera med instruktörerna på plats eller kontakta klubben om du vill ha hjälp att hitta rätt grupp.

{% for group in site.data.groups.schedule %}
{% assign age_group = site.data.groups.groups[group.group] %}
{% if age_group.type == "barn" %}
**{{ group.name | default: age_group.name }}** – {{ age_group.ages }}{% if group.label %} · {{ group.label }}{% endif %}
{% for session in group.sessions %}
  - {{ session.day }} kl. {{ session.start }}–{{ session.end }}
{% endfor %}
{% endif %}
{% endfor %}

[Se träningsschemat]({{ '/traning/schema/' | relative_url }}){: .button}

### Tävlingar och läger
Alingsås Ju-Jutsuklubb arrangerar inte tävlingar eller läger för barn, men vi uppmuntrar äldre barn att delta i läger och andra aktiviteter som arrangeras av Svenska Ju-jutsuförbundet. Det är ett roligt sätt att träffa andra barn som tränar ju-jutsu, lära sig nya tekniker och utveckla sin träning.

## Bälten och gradering

Läs om bältesfärger, sho- och monsystemet samt kraven för gradering på sidan
[Graderingssystem för barn]({{ '/ju-jutsu/graderingssystem-barn/' | relative_url }}).
