require "date"
require "tzinfo"

module DatedContent
  class Generator < Jekyll::Generator
    safe true

    def generate(site)
      today = TZInfo::Timezone.get("Europe/Stockholm").utc_to_local(site.time.getutc).to_date
      schedule = site.data.fetch("groups", {})
      activities = site.collections["activities"]&.docs || []

      upcoming_activities = activities.select do |activity|
        %w[title description].each do |field|
          if activity.data[field].to_s.strip.empty?
            raise Jekyll::Errors::FatalException, "#{activity.relative_path}: #{field} must not be empty"
          end
        end
        date = parse_date(activity.data["event_date"], "#{activity.relative_path}: event_date")
        date >= today
      end
      visible_activities = upcoming_activities.select do |activity|
        parse_date(activity.data["event_date"], "#{activity.relative_path}: event_date") <= today + 42
      end

      grading_groups = schedule.fetch("groups", {}).values.select do |group|
        grading = group.fetch("grading", {})
        date = grading["date"].to_s.strip
        time = grading["time"].to_s.strip
        if date.empty?
          !time.empty?
        else
          parse_date(date, "_data/groups.yml: #{group['name']} grading.date") >= today
        end
      end

      exceptions = schedule.fetch("exceptions", []).select.with_index do |exception, index|
        parse_date(exception["date"], "_data/groups.yml: exceptions[#{index}].date") >= today
      end

      board_entries = visible_activities.map do |activity|
        { "date" => activity.data["event_date"].to_s, "activity" => activity }
      end
      upcoming_entries = upcoming_activities.map do |activity|
        { "date" => activity.data["event_date"].to_s, "activity" => activity }
      end
      grading_groups.each do |group|
        date = group.fetch("grading")["date"].to_s.strip
        next if date.empty?

        entry = { "date" => date, "grading_group" => group }
        upcoming_entries << entry
        board_entries << entry if parse_date(date, "#{group['name']} grading.date") <= today + 42
      end

      exceptions.each do |exception|
        date = exception["date"].to_s
        if parse_date(date, "exception.date") <= today + 28
          board_entries << { "date" => date, "exception" => exception }
        end
      end

      term_start_date = schedule.fetch("term_start", {})["date"].to_s.strip
      unless term_start_date.empty?
        date = parse_date(term_start_date, "_data/groups.yml: term_start.date")
        if (today - 21..today + 21).cover?(date)
          board_entries << { "date" => term_start_date, "term_start" => true }
        end
      end

      site.data["dated_content"] = {
        "board_entries" => board_entries.sort_by { |entry| entry["date"] },
        "upcoming_entries" => upcoming_entries.sort_by { |entry| entry["date"] },
        "activities" => visible_activities.sort_by { |activity| activity.data["event_date"].to_s },
        "grading_groups" => grading_groups,
        "exceptions" => exceptions.sort_by { |exception| exception["date"].to_s }
      }
    end

    private

    def parse_date(value, location)
      text = value.to_s
      return Date.iso8601(text) if text.match?(/\A\d{4}-\d{2}-\d{2}\z/)

      raise ArgumentError
    rescue ArgumentError
      raise Jekyll::Errors::FatalException, "#{location}: invalid date #{value.inspect}; expected YYYY-MM-DD"
    end
  end
end
