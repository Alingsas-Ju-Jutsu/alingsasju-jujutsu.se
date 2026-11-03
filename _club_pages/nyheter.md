---
title: Nyheter
category: Föreningen
permalink: /nyheter/
---

Tidigare nyheter från Alingsås Ju-Jutsuklubb. Innehållet är historiskt och
uppgifter om datum, tider och arrangemang kan vara inaktuella.

{% assign news = site.club_pages | where: "news", true | sort: "published_sort" | reverse %}
{% for article in news %}
- [{{ article.title }}]({{ article.url | relative_url }}){% if article.published_label %} — {{ article.published_label }}{% endif %}
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
