const gradingSections = document.querySelectorAll(".training-schedule__gradings");

if (gradingSections.length > 0) {
  const swedishDate = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Europe/Stockholm",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
  const invalidDates = new Set();

  const updateGradingTimes = () => {
    const parts = Object.fromEntries(
      swedishDate.formatToParts(new Date()).map(({ type, value }) => [type, value])
    );
    const today = `${parts.year}-${parts.month}-${parts.day}`;

    gradingSections.forEach((section) => {
      const entries = section.querySelectorAll(".training-schedule__grading");
      entries.forEach((entry) => {
        const date = entry.dataset.gradingDate;
        if (!date) {
          entry.hidden = false;
          return;
        }

        const parsed = new Date(`${date}T00:00:00Z`);
        const valid = /^\d{4}-\d{2}-\d{2}$/.test(date) &&
          !Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === date;
        if (!valid && !invalidDates.has(date)) {
          console.warn(`Invalid grading date "${date}": expected YYYY-MM-DD.`);
          invalidDates.add(date);
        }
        entry.hidden = valid && date < today;
      });
      section.hidden = !Array.from(entries).some((entry) => !entry.hidden);
    });
  };

  updateGradingTimes();
  window.setInterval(updateGradingTimes, 60 * 1000);
  document.addEventListener("visibilitychange", updateGradingTimes);
}
