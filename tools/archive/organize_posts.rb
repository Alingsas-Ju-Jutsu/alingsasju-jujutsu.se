require "json"
require "yaml"
require "nokogiri"
require "fileutils"
require_relative "post_path"

root = Pathname.new(ARGV.fetch(0))
manifest = JSON.parse((root / "manifest.json").read)
sources = manifest["pages"].select { |page| page["url"].match?(/[?&]p=\d+/) }.to_h do |page|
  [page["url"][/[?&]p=(\d+)/, 1], page]
end
posts = Dir.glob("_club_pages/**/*.md").filter_map do |file|
  _, frontmatter, body = File.read(file).split("---", 3)
  metadata = YAML.safe_load(frontmatter)
  next unless metadata["news"]
  source = sources.fetch(metadata.fetch("source_id"))
  document = Nokogiri::HTML((root / source.fetch("file")).read)
  metadata["grading"] = document.css(".colibri-post-category").any? { |node| node.text.strip == "Graderingar" }
  [Pathname.new(file), ArchivePostPath.for(metadata), metadata.to_yaml + "---" + body]
end
abort "Duplicate dated filenames" unless posts.map { |_, target, _| target }.uniq.size == posts.size
posts.each do |source, target, content|
  abort "Destination already exists: #{target}" if source != target && target.exist?
end
posts.each do |source, target, content|
  FileUtils.mkdir_p(target.dirname)
  source.write(content)
  FileUtils.mv(source, target) unless source == target
end
puts "Organized #{posts.size} posts into dated news and grading folders."
