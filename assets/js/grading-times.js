const datedSections = [
  {
    sections: document.querySelectorAll(".training-schedule__gradings"),
    entrySelector: ".training-schedule__grading",
    dateField: "gradingDate",
  },
  {
    sections: document.querySelectorAll(".training-schedule__exceptions"),
    entrySelector: "[data-exception-date]",
    dateField: "exceptionDate",
  },
];

if (datedSections.some(({ sections }) => sections.length > 0)) {
  const swedishDate = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Europe/Stockholm",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
  const invalidDates = new Set();

  const updateDatedSections = () => {
    const parts = Object.fromEntries(
      swedishDate.formatToParts(new Date()).map(({ type, value }) => [type, value])
    );
    const today = `${parts.year}-${parts.month}-${parts.day}`;

    datedSections.forEach(({ sections, entrySelector, dateField }) => {
      sections.forEach((section) => {
        const entries = section.querySelectorAll(entrySelector);
        entries.forEach((entry) => {
          const date = entry.dataset[dateField];
          if (!date) {
            entry.hidden = false;
            return;
          }

          const parsed = new Date(`${date}T00:00:00Z`);
          const valid = /^\d{4}-\d{2}-\d{2}$/.test(date) &&
            !Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === date;
          if (!valid && !invalidDates.has(date)) {
            console.warn(`Invalid ${dateField} "${date}": expected YYYY-MM-DD.`);
            invalidDates.add(date);
          }
          entry.hidden = valid && date < today;
        });
        section.hidden = !Array.from(entries).some((entry) => !entry.hidden);
      });
    });
  };

  updateDatedSections();
  window.setInterval(updateDatedSections, 60 * 1000);
  document.addEventListener("visibilitychange", updateDatedSections);
}
