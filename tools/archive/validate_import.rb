require "json"
require "nokogiri"
require "pathname"
require "yaml"
require "digest"

root = Pathname.new(ARGV.fetch(0))
manifest = JSON.parse((root / "manifest.json").read)
errors = []
excluded = YAML.safe_load(File.read("_data/excluded_archive_pages.yml"))
pages = {}
Dir.glob("_club_pages/**/*.{md,html}").each do |file|
  errors << "Page is not Markdown: #{file}" unless File.extname(file) == ".md"
  errors << "Raw HTML content in #{file}" if File.read(file).match?(/<\/?[a-z][a-z0-9]*(?:\s[^>]*|\/?)>/i)
  metadata = YAML.safe_load(File.read(file).split("---", 3)[1])
  pages[metadata["source_id"]] = metadata if metadata["source_id"]
end
errors << "Homepage contains raw HTML" if File.read("index.md").match?(/<\/?[a-z][a-z0-9]*(?:\s[^>]*|\/?)>/i)

def normalize(text)
  text.downcase.gsub(/[[:space:]]/, "")
end

seen = {}
manifest["pages"].each do |page|
  id = page["url"][/[?&](?:page_id|p)=(\d+)/, 1]
  next if excluded.include?(id)
  next unless id && !seen[id]
  seen[id] = true
  metadata = pages[id]
  unless metadata
    errors << "Missing migrated page #{id}"
    next
  end
  output = Pathname.new("_site#{metadata.fetch('permalink')}index.html")
  unless output.file?
    errors << "Missing generated page #{output}"
    next
  end
  target = Nokogiri::HTML(output.read).at_css(".page-content__body")
  unless target
    errors << "Missing page body #{output}"
    next
  end
  next if metadata["maintained_content"]
  source = Nokogiri::HTML((root / page["file"]).read)
  body = source.at_css(".colibri-post-content") || source.at_css("#content")
  body.css("script,style,form,svg").remove
  errors << "HTML rendered as a code block on #{id}" if target.css("pre").size > body.css("pre").size
  normalized = normalize(target.text)
  title = normalize(metadata.fetch("title"))
  body.xpath(".//text()").each do |node|
    text = normalize(node.text.strip)
    next if text.size < 3 || text == title
    errors << "Missing text on #{id}: #{node.text.strip[0,120]}" unless normalized.include?(text)
  end
  expected = body.css("img").size
  actual = target.css("img").size + target.text.scan("Bilden är inte tillgänglig.").size
  errors << "Image count on #{id}: #{expected} != #{actual}" unless expected == actual
  errors << "Table count on #{id} changed" unless body.css("table").size == target.css("table").size
end

html_files = Dir.glob("_site/**/*.html")
html_files.each do |file|
  document = Nokogiri::HTML(File.read(file))
  document.css("[href],[src]").each do |node|
    %w[href src].each do |attribute|
      value = node[attribute]
      next unless value
      errors << "Unexpanded Liquid in #{file}: #{value}" if value.include?("{{")
      if value.match?(%r{\Ahttps?://(?:www\.)?alingsasju-jutsu\.se/.*[?&](?:page_id|p|attachment_id)=})
        errors << "Legacy WordPress link in #{file}: #{value}"
      end
      next if value.start_with?("http:", "https:", "mailto:", "tel:", "data:", "#")
      path = value.split(/[?#]/).first
      local = path.start_with?("/") ? Pathname.new("_site").join(path.delete_prefix("/")) : Pathname.new(file).dirname.join(path)
      errors << "Broken link in #{file}: #{value}" unless local.file? || (local / "index.html").file?
    end
  end
end
expected_schedule = YAML.safe_load(File.read("_data/training_schedule.yml")).fetch("groups")
%w[_site/index.html _site/traning/schema/index.html _site/borja-trana/index.html].each do |file|
  document = Nokogiri::HTML(File.read(file))
  groups = document.css(".training-schedule__group")
  errors << "Incorrect group count in #{file}" unless groups.size == expected_schedule.size
  expected_schedule.zip(groups).each do |expected, group|
    next unless group
    errors << "Incorrect group heading in #{file}" unless normalize(group.at_css("h3").text) == normalize("#{expected['name']} #{expected['ages']}")
    expected_days = expected["sessions"].map { |session| session.fetch("day") }
    expected_times = expected["sessions"].map { |session| "#{session.fetch('start')} – #{session.fetch('end')}" }
    errors << "Incorrect schedule in #{file}" unless group.css("dt").map(&:text) == expected_days && group.css("dd").map { |node| node.text.strip } == expected_times
  end
end
beginner = Nokogiri::HTML(File.read("_site/borja-trana/index.html")).at_css(".page-content__body")
errors << "Beginner archive section still present" if beginner.at_css("details")
errors << "Beginner page missing fee link" unless beginner.at_css('a[href="/traning/traningsavgifter/"]')
errors << "Wave background still present" if File.read("_site/assets/css/main.css").include?("waves-inverted")
manifest["assets"].each do |asset|
  local = Pathname.new("assets/archive/#{File.basename(asset['file'])}")
  next unless local.file?
  errors << "Asset changed: #{local}" unless Digest::SHA256.file(local).hexdigest == Digest::SHA256.file(root / asset["file"]).hexdigest
end
report = JSON.parse(File.read("_data/import_report.json"))
excluded.each do |id|
  errors << "Excluded page #{id} still exists" if pages.key?(id) || File.exist?("_site/arkiv/#{id}/index.html")
end
errors << "Login page still exists" if File.exist?("_site/foreningen/instruktorer/logga-in/index.html")
errors << "Incorrect imported page total" unless seen.size == report["pages"]
abort errors.uniq.join("\n") unless errors.empty?
puts "Verified #{seen.size} migrated source pages, #{html_files.size} generated routes, text, images, tables and local links."
