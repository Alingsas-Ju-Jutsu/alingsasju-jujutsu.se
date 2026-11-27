---
title: Äldre nyheter
category: Arkiv
archived: true
maintained_content: true
permalink: "/foreningen/arkiv/nyheter/"
description: 'Arkiv med äldre nyheter, graderingar, läger och dokument från
  Alingsås Ju-Jutsuklubb.'
---

Tidigare nyheter från Alingsås Ju-Jutsuklubb. Innehållet är historiskt och
uppgifter om datum, tider och arrangemang kan vara inaktuella.

{% assign news = site.club_pages | where_exp: "article", "article.path contains '_club_pages/foreningen/arkiv/nyheter/'" %}
{% assign gradings = site.club_pages | where_exp: "article", "article.path contains '_club_pages/archive/graderingar/'" %}
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
