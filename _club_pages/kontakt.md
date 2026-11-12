---
title: Kontakt
category: Träning & praktiskt
permalink: "/kontakt/"
source_date: '2026-11-03'
source_id: '1648'
maintained_content: true
description: Kontakta Alingsås Ju-Jutsuklubb. Här hittar du klubbens kontaktpersoner,
  adress på Tennisvägen 8 i Alingsås och information om träning.
---

**Kontaktuppgifter**

{% for person in site.data.contacts.contact_persons %}
**{{ person.role }}:**
<div style="padding-left: 1.5rem; margin-bottom: 1rem;" markdown="1">
{{ person.name }}<br>
{%- if person.email %}
{%- assign email_label = person.email_label | default: "Email" %}
**{{ email_label }}:** [{{ person.email }}](mailto:{{ person.email }})<br>
{%- endif %}
{%- if person.phone %}
**Tel:** {{ person.phone }}<br>
{%- endif %}
</div>
{% endfor %}
**Alingsås Ju-Jutsu Klubb**

| Uppgift | Information |
| --- | --- |
| Föreningsnummer | {{ site.data.club.organization_number | default: site.data.contacts.club_info.organization_number }} |
| Adress | {{ site.data.club.address | default: site.data.contacts.club_info.address }} |
| Postadress | {{ site.data.club.postal_address | default: site.data.contacts.club_info.postal_address }} |
| Öppettider | [{{ site.data.club.opening_hours | default: site.data.contacts.club_info.opening_hours }}]({{ site.data.club.opening_hours_url | default: site.data.contacts.club_info.opening_hours_url | relative_url }}) |
| Bankgiro | {{ site.data.club.bankgiro | default: site.data.contacts.club_info.bankgiro }} |
| Swish | {{ site.data.club.swish | default: site.data.contacts.club_info.swish }} |
