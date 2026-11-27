require "fileutils"
require "minitest/autorun"
require "tmpdir"
require "jekyll"
require "nokogiri"
require_relative "../_plugins/dated_content"

class DatedContentTest < Minitest::Test
  Activity = Struct.new(:data, :relative_path)

  def activity(date, title = "Activity")
    Activity.new(
      { "event_date" => date, "title" => title, "description" => "Information om handelsen." },
      "_activities/test.md"
    )
  end

  def generate(activities: [], groups: {}, exceptions: [], instant: "2026-11-27T12:00:00Z")
    data = {
      "groups" => { "groups" => groups, "exceptions" => exceptions }
    }
    collections = { "activities" => Struct.new(:docs).new(activities) }
    site = Struct.new(:data, :time, :collections).new(data, Time.iso8601(instant), collections)
    DatedContent::Generator.new.generate(site)
    data.fetch("dated_content")
  end

  def test_board_includes_today_and_day_42_but_not_yesterday_or_day_43
    activities = %w[2027-01-09 2027-01-08 2026-11-26 2026-12-01 2026-11-27].map { |date| activity(date) }
    original = Marshal.dump(activities)
    result = generate(activities: activities)
    assert_equal %w[2026-11-27 2026-12-01 2027-01-08], result["activities"].map { |item| item.data["event_date"] }
    assert_equal %w[2026-11-27 2026-12-01 2027-01-08 2027-01-09], result["upcoming_entries"].map { |entry| entry["date"] }
    assert_equal original, Marshal.dump(activities), "Filtering must not delete or change source entries"
  end

  def test_gradings_and_exceptions_expire_without_a_six_week_limit
    groups = {
      "past" => { "name" => "Past", "grading" => { "date" => "2026-11-26" } },
      "today" => { "name" => "Today", "grading" => { "date" => "2026-11-27" } },
      "future" => { "name" => "Future", "grading" => { "date" => "2027-06-01" } },
      "time_only" => { "name" => "Time only", "grading" => { "date" => "", "time" => "14:00" } },
      "empty" => { "name" => "Empty", "grading" => { "date" => "", "time" => "" } },
      "missing" => { "name" => "Missing" }
    }
    exceptions = %w[2027-06-01 2026-11-26 2026-11-27].map { |date| { "date" => date, "reason" => "Test" } }
    result = generate(groups: groups, exceptions: exceptions)
    assert_equal ["Today", "Future", "Time only"], result["grading_groups"].map { |group| group["name"] }
    assert_equal %w[2026-11-27 2027-06-01], result["exceptions"].map { |item| item["date"] }
  end

  def test_expiry_uses_swedish_midnight_in_winter_and_summer
    [
      ["2026-11-27", "2026-11-27T22:59:59Z", "2026-11-27T23:00:00Z"],
      ["2026-06-27", "2026-06-27T21:59:59Z", "2026-06-27T22:00:00Z"]
    ].each do |date, before_midnight, midnight|
      groups = { "test" => { "grading" => { "date" => date } } }
      exceptions = [{ "date" => date }]
      [before_midnight, midnight].each_with_index do |instant, index|
        result = generate(activities: [activity(date)], groups: groups, exceptions: exceptions, instant: instant)
        %w[activities grading_groups exceptions].each do |key|
          assert_equal 1 - index, result[key].length, "#{key} at #{instant}"
        end
      end
    end
  end

  def test_six_week_window_spans_daylight_saving_changes_as_calendar_days
    result = generate(
      activities: [activity("2026-04-12"), activity("2026-04-13")],
      instant: "2026-03-01T12:00:00Z"
    )
    assert_equal ["2026-04-12"], result["activities"].map { |item| item.data["event_date"] }
  end

  def test_valid_yaml_date_objects_are_supported
    result = generate(activities: [activity(Date.new(2026, 11, 27))])
    assert_equal 1, result["activities"].length
  end

  def test_invalid_or_missing_dates_fail_with_the_source_location
    ["2026-02-30", "2026-13-01", "27 november", "20261127", "", nil].each do |date|
      error = assert_raises(Jekyll::Errors::FatalException) { generate(activities: [activity(date)]) }
      assert_includes error.message, "_activities/test.md: event_date"
      error = assert_raises(Jekyll::Errors::FatalException) { generate(exceptions: [{ "date" => date }]) }
      assert_includes error.message, "_data/groups.yml: exceptions[0].date"
    end
    error = assert_raises(Jekyll::Errors::FatalException) do
      generate(groups: { "test" => { "name" => "Test", "grading" => { "date" => "2026-02-30" } } })
    end
    assert_includes error.message, "Test grading.date"
  end

  def test_activity_title_and_description_are_required
    %w[title description].each do |field|
      entry = activity("2026-11-27")
      entry.data[field] = " "
      error = assert_raises(Jekyll::Errors::FatalException) { generate(activities: [entry]) }
      assert_includes error.message, "_activities/test.md: #{field}"
    end
  end

  def test_absent_data_produces_empty_sections
    site = Struct.new(:data, :time, :collections).new({}, Time.iso8601("2026-11-27T12:00:00Z"), {})
    DatedContent::Generator.new.generate(site)
    assert_equal({ "board_entries" => [], "upcoming_entries" => [], "activities" => [], "grading_groups" => [], "exceptions" => [] }, site.data["dated_content"])
  end

  def test_board_includes_gradings_without_activities_and_uses_the_same_date_window
    groups = {}
    %w[2026-11-26 2026-11-27 2027-01-08 2027-01-09].each do |date|
      groups[date] = { "name" => date, "grading" => { "date" => date, "time" => "14:00" } }
    end
    groups["undated"] = { "grading" => { "time" => "15:00" } }
    result = generate(groups: groups)
    assert_empty result["activities"]
    assert_equal %w[2026-11-27 2027-01-08], result["board_entries"].map { |entry| entry["date"] }
    assert result["board_entries"].all? { |entry| entry["grading_group"] }
    result = generate(groups: groups, activities: [activity("2026-12-01")])
    assert_equal %w[2026-11-27 2026-12-01 2027-01-08], result["board_entries"].map { |entry| entry["date"] }
  end

  def test_cms_activity_fields_have_help_and_match_the_collection
    root = File.expand_path("..", __dir__)
    cms = YAML.load_file(File.join(root, ".pages.yml"), aliases: true)
    activities = cms.fetch("content").find { |entry| entry["name"] == "activities" }
    assert_equal "_activities", activities["path"]
    assert_equal "{primary}-{fields.event_date}.md", activities["filename"]
    assert_equal %w[title event_date description body images], activities["fields"].map { |field| field["name"] }
    activities["fields"].reject { |field| field["name"] == "images" }.each do |field|
      assert field["required"], field["name"]
      refute_empty field["description"], field["name"]
    end
  end

  def test_real_templates_render_filtered_content_and_hide_empty_schedule_sections
    Dir.mktmpdir do |source|
      root = File.expand_path("..", __dir__)
      %w[_includes _layouts _data _activities].each { |dir| FileUtils.mkdir_p(File.join(source, dir)) }
      %w[training-schedule grading-time notice-board upcoming-events navigation-links article-images swedish-date].each do |name|
        FileUtils.cp(File.join(root, "_includes/#{name}.html"), File.join(source, "_includes"))
      end
      %w[home activity page].each do |name|
        FileUtils.cp(File.join(root, "_layouts/#{name}.html"), File.join(source, "_layouts"))
      end
      File.write(File.join(source, "_layouts/default.html"), "---\n---\n{{ content }}")
      FileUtils.cp(File.join(root, "_club_pages/index.md"), File.join(source, "index.md"))
      FileUtils.cp(File.join(root, "_club_pages/handelser.md"), File.join(source, "handelser.md"))
      File.write(File.join(source, "schema.html"), "---\n---\n{% include training-schedule.html show_grading=true %}")
      File.write(File.join(source, "borja.html"), "---\n---\n{% include training-schedule.html %}")
      entries = [
        activity("2026-11-26", "Old notice"),
        activity("2026-11-27", "Today"),
        activity("2027-01-08", "Day 42"),
        activity("2027-01-09", "Too far")
      ]
      entries.each_with_index do |entry, index|
        entry.data["description"] = "<script>unsafe</script>"
        entry.data["images"] = [{ "image" => "/assets/images/example.jpg", "alt" => "Träning på mattan" }]
        File.write(File.join(source, "_activities/activity-#{index}-#{entry.data['event_date']}.md"),
                   "#{entry.data.to_yaml}---\n## Details\n\nFull activity information.")
      end
      File.write(File.join(source, "_data/groups.yml"), {
        "term_start" => { "title" => "Terminsstart", "date" => "1 januari" },
        "groups" => {
          "old" => { "name" => "Old group", "grading" => { "date" => "2026-11-26" } },
          "current" => {
            "name" => "Current group", "sessions" => [{ "day" => "Sunday", "start" => "18.00", "end" => "19.00" }],
            "grading" => { "date" => "2026-11-27", "time" => "14:00", "is_preliminary" => true }
          }
        },
        "exceptions" => [
          { "date" => "2026-11-26", "reason" => "Old exception" },
          { "date" => "2026-11-27", "reason" => "Current exception" }
        ]
      }.to_yaml)
      config = YAML.load_file(File.join(root, "_config.yml"))
      ["2026-11-27T12:00:00Z", "2027-06-01T12:00:00Z", "2026-11-27T12:00:00Z"].each_with_index do |instant, index|
        if index == 2
          Dir.glob(File.join(source, "_activities/*.md")).each { |path| File.delete(path) }
        end
        visible = index != 1
        site = Jekyll::Site.new(Jekyll.configuration(
          "source" => source, "destination" => File.join(source, "_site"),
          "config" => [], "plugins" => [], "plugins_dir" => [], "quiet" => true,
          "time" => Time.iso8601(instant), "baseurl" => "/test",
          "collections" => config.fetch("collections"), "defaults" => config.fetch("defaults")
        ))
        Dir.chdir(source) { site.process }
        home = Nokogiri::HTML(File.read(File.join(source, "_site/index.html")))
        schema = Nokogiri::HTML(File.read(File.join(source, "_site/schema.html")))
        beginner = Nokogiri::HTML(File.read(File.join(source, "_site/borja.html")))
        events = Nokogiri::HTML(File.read(File.join(source, "_site/aktiviteter/index.html")))
        if index.zero?
          assert_equal ["Today", "Current group – preliminär gradering", "Day 42", "Too far"], events.css(".event-summary h2").map(&:text)
          assert_equal "/test/aktiviteter/activity-3-2027-01-09/", events.css(".event-summary h2 a").last["href"]
        elsif index == 1
          assert_empty events.css(".event-summary")
          assert_includes events.text, "Det finns inga kommande händelser"
        else
          assert_equal 1, events.css(".event-summary").length
        end
        assert_equal visible ? 1 : 0, home.css("#anslagstavla").length
        assert_empty home.css(".notice-board script")
        assert_empty home.css("[data-grading-date], [data-exception-date]")
        assert_empty beginner.css(".training-schedule__gradings")
        [home, schema, beginner].each do |html|
          assert_includes html.text, "Sunday"
          refute_includes html.text, "Old exception"
          assert_equal visible ? 1 : 0, html.css(".training-schedule__exceptions").length
        end
        assert_empty home.css(".training-schedule__gradings")
        assert_equal visible ? 1 : 0, schema.css(".training-schedule__gradings").length
        assert_equal visible ? 1 : 0, schema.css(".training-schedule__grading").length
        refute_includes schema.css(".training-schedule__gradings").text, "Old group"
        if index.zero?
          assert_operator home.to_html.index('id="anslagstavla"'), :<, home.to_html.index('class="training-schedule"')
          assert_equal ["Today", "Current group – preliminär graderingstid", "Day 42"], home.css(".notice-board h3").map(&:text)
          assert_equal ["/test/aktiviteter/activity-1-2026-11-27/", "/test/aktiviteter/activity-2-2027-01-08/"],
                       home.css(".notice-board h3 a").map { |link| link["href"] }
          assert_equal "/test/ju-jutsu/barntraning/#barngraderingar", home.at_css('.notice-board a[href*="barngraderingar"]')["href"]
          assert_includes home.css(".notice-board").text, "14:00"
        elsif index == 1
          assert_empty home.css(".notice-board__post")
          assert_empty home.css(".notice-board")
          refute_includes home.text, "Anslagstavla"
          refute_includes home.text, "Graderingstider"
          refute_includes home.text, "Avvikelser i träningsschemat"
        else
          assert_equal ["Current group – preliminär graderingstid"], home.css(".notice-board h3").map(&:text)
          assert_equal 1, home.css(".notice-board__post").length
        end
        next if index == 2

        4.times do |activity_index|
          date = entries[activity_index].data["event_date"]
          detail = Nokogiri::HTML(File.read(File.join(source, "_site/aktiviteter/activity-#{activity_index}-#{date}/index.html")))
          assert_includes detail.text, "Full activity information."
          assert_equal 1, detail.css("h1").length
          if index.zero?
            assert_equal "/test/#anslagstavla", detail.at_css('a[href$="#anslagstavla"]')["href"]
          else
            assert_empty detail.css('a[href$="#anslagstavla"]')
            refute_nil detail.at_css('a[href="/test/"]')
          end
          assert_equal 1, detail.css(".activity-date time").length
          assert_equal "/test/assets/images/example.jpg", detail.at_css(".article-images img")["src"]
          assert_equal "Träning på mattan", detail.at_css(".article-images img")["alt"]
          refute_nil detail.at_css('a[href="/test/aktiviteter/"]')
        end
      end
    end
  end
end
