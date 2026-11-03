require "json"
require "yaml"
require "nokogiri"
require "uri"
require "pathname"
require "fileutils"
require_relative "markdown"
require_relative "post_path"

root = Pathname.new(ARGV.fetch(0)).expand_path
manifest = JSON.parse((root / "manifest.json").read)
abort "Use a finished archive." unless manifest["complete"]
captured_date = root.basename.to_s[/\A\d{4}-\d{2}-\d{2}/]
abort "The archive directory must start with its capture date (YYYY-MM-DD)." unless captured_date
excluded = YAML.safe_load(File.read("_data/excluded_archive_pages.yml"))

page_files = {
  "1342" => "instruktorer", "404" => "ordningsregler", "2137" => "graderingar",
  "2040" => "alingsaslagret", "283" => "alingsaslagret-2004",
  "285" => "alingsaslagret-2005", "287" => "alingsaslagret-2006",
  "289" => "alingsaslagret-2007", "295" => "alingsaslagret-2008",
  "297" => "alingsaslagret-2010", "415" => "alingsaslagret-2011",
  "987" => "alingsaslagret-2013", "990" => "alingsaslagret-2012",
  "1037" => "kai-out-west", "435" => "stadgar",
  "31" => "traningsavgifter", "1677" => "drakter", "3065" => "schema",
  "1648" => "kontakt", "18" => "kalendarium", "1674" => "ju-jutsu-kai",
  "274" => "barntraning", "272" => "graderingssystem", "2581" => "borja-trana"
}
page_files.transform_values! do |name|
  if name == "alingsaslagret"
    "alingsaslagret/index"
  elsif name.start_with?("alingsaslagret-")
    "alingsaslagret/#{name.delete_prefix('alingsaslagret-')}"
  else
    name
  end
end
routes = {}
page_files.each do |id, name|
  file = Pathname.new("_club_pages/#{name}.md")
  routes[id] = YAML.safe_load(file.read.split("---", 3)[1])["permalink"]
end
source_pages = manifest["pages"].select do |page|
  id = page["url"][/[?&](?:page_id|p)=(\d+)/, 1]
  id && !excluded.include?(id)
end
source_pages.each do |page|
  id = page["url"][/[?&](?:page_id|p)=(\d+)/, 1]
  routes[id] ||= "/arkiv/#{id}/"
end
assets = manifest["assets"].to_h { |asset| [(root / asset["file"]).to_s, asset] }
url_assets = manifest["assets"].to_h { |asset| [asset["url"].sub(%r{^https?://(?:www\.)?}, ""), asset] }
source_paths = manifest["pages"].filter_map do |page|
  id = page["url"][/[?&](?:page_id|p)=(\d+)/, 1]
  next if excluded.include?(id)
  [(root / page["file"]).to_s, id ? routes.fetch(id) : "/"]
end.to_h
copied = {}
issues = []
processed = {}
existing_posts = Dir.glob("_club_pages/**/*.md").to_h do |path|
  metadata = YAML.safe_load(File.read(path).split("---", 3)[1])
  [metadata["source_id"], Pathname.new(path)]
end
FileUtils.mkdir_p("assets/archive")

def local_path(value)
  "{{ '#{value}' | relative_url }}"
end

def resolve_reference(value, source, root, assets, url_assets, source_paths, routes)
  return [value, nil] if value.start_with?("#", "mailto:", "tel:", "data:")
  if value.match?(%r{\Ahttps?://})
    uri = URI.parse(value)
    if uri.host&.sub(/^www\./, "") == "alingsasju-jutsu.se"
      id = URI.decode_www_form(uri.query || "").to_h.values_at("page_id", "p").compact.first
      return [local_path(routes[id]), nil] if id && routes[id]
      return [local_path("/"), nil] if uri.path == "/" && !uri.query
    end
    asset = url_assets[value.split("#").first.sub(%r{^https?://(?:www\.)?}, "")]
    return [local_path("/assets/archive/#{File.basename(asset['file'])}"), asset] if asset
    return [nil, nil] if uri.host&.sub(/^www\./, "") == "alingsasju-jutsu.se"
    return [value, nil]
  end
  file = (root / source["file"]).dirname.join(value.split(/[?#]/).first).cleanpath.to_s
  return [local_path(source_paths[file]) + (value.include?("#") ? "##{value.split('#', 2).last}" : ""), nil] if source_paths[file]
  asset = assets[file]
  return [local_path("/assets/archive/#{File.basename(asset['file'])}"), asset] if asset
  [nil, nil]
end

source_pages.each do |source|
  id = source["url"][/[?&](?:page_id|p)=(\d+)/, 1]
  next if excluded.include?(id)
  next if processed[id]
  processed[id] = true
  doc = Nokogiri::HTML((root / source["file"]).read)
  body = doc.at_css(".colibri-post-content") || doc.at_css("#content")
  abort "No content container for #{source['url']}" unless body
  fragment = Nokogiri::HTML.fragment(body.inner_html)
  fragment.css("script, style, form, input, button, noscript, svg").remove
  fragment.xpath(".//comment()").remove
  title = source["title"].sub(/\s+[–-]\s+Alingsås Ju-Jutsuklubb$/, "")
  display_title = page_files[id] ? YAML.safe_load(File.read("_club_pages/#{page_files[id]}.md").split("---", 3)[1]).fetch("title") : title

  fragment.css("*").each do |node|
    node.attribute_nodes.each do |attribute|
      node.remove_attribute(attribute.name) unless %w[id href src alt width height colspan rowspan title].include?(attribute.name)
    end
    node.name = "h2" if node.name == "h1"
    if node.name == "a" && node.text.strip.match?(/\A[^\s]+@[^\s]+\.[^\s]+\z/)
      node["href"] = "mailto:#{node.text.strip}"
    end
    %w[href src].each do |attribute|
      value = node[attribute]
      next unless value
      if attribute == "href" && value.include?("attachment_id=") && node.at_css("img")
        value = node.at_css("img")["src"]
      end
      resolved, asset = resolve_reference(value, source, root, assets, url_assets, source_paths, routes)
      if asset
        FileUtils.cp(root / asset["file"], "assets/archive/#{File.basename(asset['file'])}")
        copied[asset["file"]] = asset
      end
      if resolved && !(node.name == "img" && !asset && !value.start_with?("data:"))
        node[attribute] = resolved
      else
        issues << { "page" => routes[id], "reference" => value, "kind" => node.name == "img" ? "missing_image" : "missing_link" }
        if node.name == "img"
          replacement = Nokogiri::XML::Node.new("p", fragment.document)
          replacement["class"] = "source-unavailable"
          replacement.content = "Bilden är inte tillgänglig. #{node['alt']}".strip
          node.replace(replacement)
        elsif node.name == "a"
          node.name = "span"
          node.remove_attribute("href")
          node["title"] = "Länken är inte längre tillgänglig."
          node.add_child(" (länkmål saknas)") unless node.at_css("img")
        else
          node.remove_attribute(attribute)
        end
      end
    end
    if node.name == "img" && node.parent
      node["alt"] = "Bild från #{title}" if node["alt"].to_s.strip.empty?
      node["loading"] = "lazy"
    elsif node.name == "iframe"
      node["title"] ||= "Kalendarium"
      node["loading"] = "lazy"
    end
  end

  # Strip the WordPress layout while keeping semantic content in its original order.
  fragment.css("div, span").reverse_each do |node|
    next if node["class"] == "source-unavailable" || node["title"]
    node.replace(node.children)
  end
  fragment.css("h2,h3,h4,h5,h6,p,a").each do |node|
    node.remove if node.text.strip.empty? && node.css("img,iframe").empty?
  end
  fragment.css("h2,h3,h4").each do |node|
    node.remove if node.text.strip.casecmp?(display_title.strip)
  end
  if id == "2040"
    fragment.add_child('<h2>Tidigare Alingsåsläger</h2>')
    year_links = page_files.select { |_, name| name.match?(%r{alingsaslagret/\d+}) }.map do |year_id, name|
      "<li><a href=\"#{local_path(routes.fetch(year_id))}\">Alingsåslägret #{name[/\d+$/]}</a></li>"
    end
    list = Nokogiri::XML::Node.new("ul", fragment.document)
    list.inner_html = year_links.join
    fragment.add_child(list)
  end
  if fragment.text.strip.empty? && fragment.css("img,iframe").empty?
    abort "Extracted empty content for #{id}"
  end
  # Liquid syntax is introduced only by our rewritten local URLs.
  html = fragment.to_html.gsub("&#39;", "'").gsub(/\{\{.*?\}\}/) { |link| link.gsub("%20", " ") }
  html = html.gsub(/^[ \t]+\n/, "").gsub(/\n{3,}/, "\n\n").strip
  if page_files[id]
    file = Pathname.new("_club_pages/#{page_files.fetch(id)}.md")
    metadata = YAML.safe_load(file.read.split("---", 3)[1])
    next if metadata["maintained_content"]
  else
    existing = existing_posts[id]
    next if existing && YAML.safe_load(existing.read.split("---", 3)[1])["maintained_content"]
    date_link = doc.css(".h-blog-meta a").find { |link| link["href"].to_s.match?(/[?&]m=\d{8}/) }
    date = date_link&.[]("href")&.slice(/[?&]m=(\d{8})/, 1)
    metadata = {
      "title" => title, "category" => "Nyheter", "permalink" => routes.fetch(id),
      "news" => true, "published_label" => date_link&.text&.strip,
      "grading" => doc.css(".colibri-post-category").any? { |node| node.text.strip == "Graderingar" },
      "source_author" => doc.css(".h-blog-meta a").find { |link| link["href"].to_s.include?("author=") }&.text&.strip,
      "published_sort" => date || "00000000"
    }
    file = existing || ArchivePostPath.for(metadata)
    FileUtils.mkdir_p(file.dirname)
  end
  metadata["source_date"] = captured_date
  metadata["source_id"] = id
  metadata["historical"] = true if !page_files[id] || %w[18 3065 2581 435].include?(id) || page_files[id].match?(%r{alingsaslagret/\d+})
  metadata["missing_media"] = true if issues.any? { |issue| issue["page"] == routes[id] && issue["kind"] == "missing_image" }
  file.write(metadata.to_yaml + "---\n\n" + ArchiveMarkdown.convert(html))
end
sponsor_source = source_pages.find { |page| page["url"].include?("?p=") }
if sponsor_source
  sponsor_doc = Nokogiri::HTML((root / sponsor_source["file"]).read)
  sponsors = sponsor_doc.css(".colibri-sidebar a").select { |link| link.at_css("img") }
  sponsor_data = sponsors.map do |link|
    image = link.at_css("img")
    src, asset = resolve_reference(image["src"], sponsor_source, root, assets, url_assets, source_paths, routes)
    abort "Missing sponsor image #{image['src']}" unless asset
    FileUtils.cp(root / asset["file"], "assets/archive/#{File.basename(asset['file'])}")
    copied[asset["file"]] = asset
    { "name" => image["alt"], "url" => link["href"], "image" => "/assets/archive/#{File.basename(asset['file'])}" }
  end
  Pathname.new("_data/archive_sponsors.yml").write(sponsor_data.to_yaml)
end
documents = copied.values.select { |asset| asset["file"].match?(/\.(pdf|docx?|xlsx?)$/) }.map do |asset|
  {
    "title" => URI::DEFAULT_PARSER.unescape(File.basename(URI.parse(asset["url"]).path)),
    "url" => "/assets/archive/#{File.basename(asset['file'])}"
  }
end
Pathname.new("_data/archive_documents.yml").write(documents.to_yaml)
Pathname.new("_data/import_report.json").write(JSON.pretty_generate({
  "pages" => processed.size, "assets" => copied.size, "issues" => issues
}) + "\n")
puts "Imported #{processed.size} unique pages, #{copied.size} assets; #{issues.size} unresolved source references explicitly marked."
