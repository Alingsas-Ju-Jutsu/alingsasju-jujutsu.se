---
title: Nyheter
category: Föreningen
permalink: "/nyheter/"
description: 'Nyheter från Alingsås Ju-Jutsuklubb: träning, graderingar, läger och
  aktiviteter. Läs daterade artiklar och hitta dokument från tidigare arrangemang.'
---

Tidigare nyheter från Alingsås Ju-Jutsuklubb. Innehållet är historiskt och
uppgifter om datum, tider och arrangemang kan vara inaktuella.

{% assign news = site.club_pages | where_exp: "article", "article.path contains '_club_pages/nyheter/'" %}
{% assign gradings = site.club_pages | where_exp: "article", "article.path contains '_club_pages/graderingar/'" %}
{% assign news = news | concat: gradings | sort: "date" | reverse %}
{% for article in news %}
- [{{ article.title }}]({{ article.url | relative_url }}){% if article.date %} — {% include swedish-date.html date=article.date %}{% endif %}
{% endfor %}

## Dokumentarkiv

Inbjudningar och blanketter från tidigare arrangemang. De är historiska
underlag, inte aktuella anmälningsblanketter.

{% for document in site.data.archive_documents %}
- [{{ document.title }}]({{ document.url | relative_url }})
{% endfor %}

## Tidigare sponsorer

{% for sponsor in site.data.archive_sponsors %}
[![{{ sponsor.name }}]({{ sponsor.image | relative_url }})]({{ sponsor.url }})

{% endfor %}
