---
title: Grafik
category: Träning & praktiskt
permalink: "/grafik/"
description: Ladda ner affischer för Alingsås Ju-Jutsuklubb som PNG eller PDF i olika storlekar.
---

## Affischer

{% for poster in site.data.poster.posters %}
  {% assign poster_name = poster[0] %}
  {% assign poster_settings = poster[1] %}
  {% assign preview_path = poster_name | append: "-preview.png" | prepend: "assets/generated/" %}
  {% assign base_path = poster_name | append: "-poster.png" | prepend: "assets/generated/" %}
### {{ poster_settings.title | default: poster_name | capitalize | escape }}

<a href="{{ preview_path | relative_url }}" target="_blank" rel="noopener"><img src="{{ preview_path | relative_url }}" alt="Förhandsvisning av {{ poster_settings.title | default: poster_name | escape }}" loading="lazy"></a>

{% assign a4_path = base_path | replace: ".png", "-a4.pdf" %}
{% assign a3_path = base_path | replace: ".png", "-a3.pdf" %}
{% assign a4_cropped_path = base_path | replace: ".png", "-a4-cropped.pdf" %}
{% assign a3_cropped_path = base_path | replace: ".png", "-a3-cropped.pdf" %}
{% assign original_path = base_path | replace: ".png", "-original.png" %}

| Filformat | Storlek | Hela affischen | Beskuren |
| :--- | :--- | :--- | :--- |
| PDF | A4 | [Ladda ner]({{ a4_path | relative_url }}){:target="_blank" rel="noopener"} | [Ladda ner]({{ a4_cropped_path | relative_url }}){:target="_blank" rel="noopener"} |
| PDF | A3 | [Ladda ner]({{ a3_path | relative_url }}){:target="_blank" rel="noopener"} | [Ladda ner]({{ a3_cropped_path | relative_url }}){:target="_blank" rel="noopener"} |
| PNG | Originalstorlek | [Ladda ner]({{ original_path | relative_url }}){:target="_blank" rel="noopener"} | — |
{% for size in poster_settings.sizes %}{%- if forloop.first -%}
    {%- assign download_path = base_path -%}
  {%- else -%}
    {%- assign size_suffix = size | prepend: "-" | append: ".png" -%}
    {%- assign download_path = poster_name | append: "-poster" | append: size_suffix | prepend: "assets/generated/" -%}
  {%- endif -%}
| PNG | {{ size }} px | [Ladda ner]({{ download_path | relative_url }}){:target="_blank" rel="noopener"} | — |
{% endfor -%}
{: .poster-downloads }

{% endfor %}