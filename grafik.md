---
title: Grafik
category: Träning & praktiskt
permalink: "/grafik/"
description: Ladda ner affischer och logotyp för Alingsås Ju-Jutsuklubb i olika format och storlekar.
---

## Affischer och logotyp

{% for graphic in site.data.graphics.graphics %}
  {% assign graphic_name = graphic[0] %}
  {% assign graphic_settings = graphic[1] %}
  {% assign preview_path = graphic_name | append: "-preview.png" | prepend: "assets/generated/" %}
  {% assign base_path = graphic_name | append: "-graphic.png" | prepend: "assets/generated/" %}
### {{ graphic_settings.title | default: graphic_name | capitalize | escape }}

![Förhandsvisning av {{ graphic_settings.title | default: graphic_name | escape }}]({{ preview_path | relative_url }})

{% assign a4_path = base_path | replace: ".png", "-a4.pdf" %}
{% assign a3_path = base_path | replace: ".png", "-a3.pdf" %}
{% assign a4_cropped_path = base_path | replace: ".png", "-a4-cropped.pdf" %}
{% assign a3_cropped_path = base_path | replace: ".png", "-a3-cropped.pdf" %}
{% assign original_path = base_path | replace: ".png", "-original.png" %}
{% assign source_extension = graphic_settings.background | split: "." | last | downcase %}

| Filformat | Storlek | {% if graphic_settings.background_colors %}Bakgrund{% else %}Version{% endif %} | Nedladdning |
| :--- | :--- | :--- | :--- |
{% if source_extension == "svg" -%}
| SVG | Skalbar | Original | [Ladda ner]({{ graphic_settings.background | relative_url }}){: .button target="_blank" rel="noopener"} |
{% endif -%}
{% unless graphic_settings.include_schedule == false -%}
{% if graphic_settings.sizes.size > 0 -%}
| PDF | A4 | Hela affischen | [Ladda ner]({{ a4_path | relative_url }}){: .button target="_blank" rel="noopener"} |
| PDF | A4 | Beskuren | [Ladda ner]({{ a4_cropped_path | relative_url }}){: .button target="_blank" rel="noopener"} |
| PDF | A3 | Hela affischen | [Ladda ner]({{ a3_path | relative_url }}){: .button target="_blank" rel="noopener"} |
| PDF | A3 | Beskuren | [Ladda ner]({{ a3_cropped_path | relative_url }}){: .button target="_blank" rel="noopener"} |
{% endif -%}
{% endunless -%}
{% unless source_extension == "svg" -%}
| PNG | Originalstorlek | Hela bilden | [Ladda ner]({{ original_path | relative_url }}){: .button target="_blank" rel="noopener"} |
{% endunless -%}
{% for size in graphic_settings.sizes %}{%- if forloop.first -%}
    {%- assign download_path = base_path -%}
  {%- else -%}
    {%- assign size_suffix = size | prepend: "-" | append: ".png" -%}
    {%- assign download_path = graphic_name | append: "-graphic" | append: size_suffix | prepend: "assets/generated/" -%}
  {%- endif -%}
{% if graphic_settings.background_colors -%}
{% for background in graphic_settings.background_colors -%}
  {% assign variant_suffix = background[0] | prepend: "-" | append: ".png" -%}
  {% assign variant_path = download_path | replace: ".png", variant_suffix -%}
  {% assign background_label = background[0] -%}
  {% if background_label == "transparent" %}{% assign background_label = "Transparent" %}{% endif -%}
  {% if background_label == "white" %}{% assign background_label = "Vit" %}{% endif -%}
| PNG | {{ size }} px | {{ background_label | escape }} | [Ladda ner]({{ variant_path | relative_url }}){: .button target="_blank" rel="noopener"} |
{% endfor -%}
{% else -%}
| PNG | {{ size }} px | Hela bilden | [Ladda ner]({{ download_path | relative_url }}){: .button target="_blank" rel="noopener"} |
{% endif -%}
{% endfor -%}
{: .graphics-downloads }

{% endfor %}