require "json"
require "nokogiri"
require "pathname"
require "uri"

origin = ARGV.fetch(0, "https://alingsasju-jutsu.se")
base = ARGV.fetch(1, "")
root = Pathname.new("_site")
errors = []
files = Dir.glob("_site/**/*.html")
abort "Build the site first." if files.empty?

files.each do |file|
  document = Nokogiri::HTML(File.read(file))
  route = "/" + Pathname.new(file).relative_path_from(root).to_s.sub(/index\.html$/, "")
  expected_url = "#{origin}#{base}#{route}"
  errors << "#{file}: missing Swedish language" unless document.at_css("html")["lang"] == "sv-SE"
  errors << "#{file}: expected one h1" unless document.css("h1").size == 1
  errors << "#{file}: missing title" if document.at_css("title")&.text.to_s.strip.empty?
  errors << "#{file}: missing description" if document.at_css('meta[name="description"]')&.[]("content").to_s.strip.empty?
  errors << "#{file}: incorrect canonical" unless document.at_css('link[rel="canonical"]')&.[]("href") == expected_url
  sharing_image = document.at_css('meta[property="og:image"]')&.[]("content").to_s
  if sharing_image.start_with?("#{origin}#{base}/")
    image_path = URI::DEFAULT_PARSER.unescape(sharing_image.delete_prefix("#{origin}#{base}/"))
    errors << "#{file}: broken sharing image" unless root.join(image_path).file?
  else
    errors << "#{file}: missing or incorrect sharing image"
  end
  document.css("img").each do |image|
    errors << "#{file}: missing image alternative" unless image.key?("alt")
  end
  document.css("th").each do |header|
    errors << "#{file}: empty table header" if header.text.gsub(/[[:space:]]/, "").empty?
  end
  document.css('script[type="application/ld+json"]').each do |script|
    begin
      JSON.parse(script.text)
    rescue JSON::ParserError => error
      errors << "#{file}: invalid structured data: #{error.message}"
    end
  end
  document.css("[href], [src]").each do |node|
    %w[href src].each do |attribute|
      value = node[attribute]
      next unless value&.start_with?("/") && !value.start_with?("//")
      unless base.empty? || value.start_with?("#{base}/")
        errors << "#{file}: missing deployment prefix in #{value}"
        next
      end
      path = URI::DEFAULT_PARSER.unescape(value.delete_prefix(base).split(/[?#]/).first)
      local = root.join(path.delete_prefix("/"))
      errors << "#{file}: broken local reference #{value}" unless local.file? || (local / "index.html").file?
    end
  end
end

sitemap = Nokogiri::XML((root / "sitemap.xml").read) { |config| config.strict }
locations = sitemap.xpath("//*[local-name()='loc']").map(&:text)
errors << "Sitemap contains 404 page" if locations.any? { |location| location.end_with?("/404.html") }
errors << "Incorrect sitemap origin/base path" unless locations.all? { |location| location.start_with?("#{origin}#{base}/") }
errors << "Missing homepage in sitemap" unless locations.include?("#{origin}#{base}/")
errors << "Incorrect robots sitemap URL" unless (root / "robots.txt").read.include?("Sitemap: #{origin}#{base}/sitemap.xml")
abort errors.join("\n") unless errors.empty?
puts "Verified #{files.size} HTML pages: metadata, structured data, image alternatives, table headers, local references, sitemap and robots.txt."
