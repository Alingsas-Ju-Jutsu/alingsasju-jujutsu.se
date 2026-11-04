---
title: Grafik
category: Träning & praktiskt
permalink: "/grafik/"
description: Ladda ner affischer för Alingsås Ju-Jutsuklubb i olika storlekar.
---

## Affischer

{% for poster in site.data.poster.posters %}
  {% assign poster_name = poster[0] %}
  {% assign poster_settings = poster[1] %}
  {% assign preview_path = poster_name | prepend: "-preview.png" | prepend: "assets/generated/" %}
  {% assign base_path = poster_name | append: "-poster.png" | prepend: "assets/generated/" %}
### {{ poster_settings.title | default: poster_name | capitalize | escape }}

<a href="{{ preview_path | relative_url }}"><img src="{{ preview_path | relative_url }}" alt="Förhandsvisning av {{ poster_settings.title | default: poster_name | escape }}" loading="lazy"></a>

{% for size in poster_settings.sizes %}
  {% if forloop.first %}
    {% assign download_path = base_path %}
  {% else %}
    {% assign size_suffix = size | prepend: "-" | append: ".png" %}
    {% assign download_path = poster_name | append: "-poster" | append: size_suffix | prepend: "assets/generated/" %}
  {% endif %}
- [{{ size }} px PNG]({{ download_path | relative_url }})
{% endfor %}
{% endfor %}