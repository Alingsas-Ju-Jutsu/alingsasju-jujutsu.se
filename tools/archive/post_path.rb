require "date"
require "pathname"

module ArchivePostPath
  module_function

  def for(metadata)
    date = Date.strptime(metadata.fetch("published_sort"), "%Y%m%d").iso8601
    slug = metadata.fetch("title").downcase.tr("åäö", "aao").gsub(/[^a-z0-9]+/, "-").sub(/^-/, "").sub(/-$/, "")
    folder = metadata.fetch("grading") ? "graderingar" : "nyheter"
    Pathname.new("_club_pages/#{folder}/#{date}-#{slug}.md")
  end
end
