require "minitest/autorun"
require "tmpdir"
require "jekyll"
require "nokogiri"

class ArchiveNavigationTest < Minitest::Test
  def test_archive_preserves_pages_and_moves_old_sections_under_foreningen
    root = File.expand_path("..", __dir__)
    %w[nyheter graderingar alingsaslagret].each do |folder|
      refute Dir.exist?(File.join(root, "_club_pages", folder)), "Historical folders belong only in archive: #{folder}"
    end
    Dir.mktmpdir do |destination|
      site = Jekyll::Site.new(Jekyll.configuration(
        "source" => root, "destination" => destination,
        "config" => File.join(root, "_config.yml"), "quiet" => true
      ))
      Dir.chdir(root) { site.process }
      navigation = site.data.fetch("navigation")
      refute_includes navigation.map { |group| group["title"] }, "Läger"
      association = navigation.find { |group| group["title"] == "Föreningen" }
      archive = association.fetch("links").find { |link| link["title"] == "Arkiv" }
      assert_equal "/foreningen/arkiv/", archive.fetch("url")
      refute archive.key?("children"), "Archive sections are reached through the overview, not a submenu"
      refute association["links"].any? { |link| %w[Graderingar Nyheter].include?(link["title"]) }

      check_links = lambda do |links|
        links.each do |link|
          assert File.file?(File.join(destination, link.fetch("url"), "index.html")), link["url"]
          check_links.call(link["children"]) if link["children"]
        end
      end
      check_links.call([archive])

      archived = site.collections.fetch("club_pages").docs.select do |page|
        page.relative_path.start_with?("_club_pages/archive/")
      end
      assert_operator archived.length, :>, 20
      archived.each do |page|
        assert page.data["archived"], page.relative_path
        html = Nokogiri::HTML(File.read(page.destination(destination)))
        assert_equal 1, html.css(".archive-notice").length, page.url
        refute_nil html.at_css('.breadcrumbs a[href="/foreningen/arkiv/"]'), page.url
        assert page.url.start_with?("/foreningen/arkiv/"), page.url
        refute_includes page.url, "/foreningen/arkiv/foreningen/arkiv/"
        html.css('a[href^="/foreningen/arkiv/"], img[src^="/foreningen/arkiv/"]').each do |element|
          url = (element["href"] || element["src"]).split("#").first
          target = File.join(destination, url)
          target = File.join(target, "index.html") if url.end_with?("/")
          assert File.file?(target), "#{page.url} links to missing #{url}"
        end
      end
      %w[nyheter/index.html foreningen/graderingar/index.html lager/index.html].each do |path|
        refute File.exist?(File.join(destination, path)), "Old route must be available for new pages: #{path}"
      end
      %w[nyheter graderingar].each do |section|
        refute site.frontmatter_defaults.find("_club_pages/#{section}/new/new.md", :club_pages, "archived")
      end

      home = Nokogiri::HTML(File.read(File.join(destination, "index.html")))
      assert_equal ["Föreningen", "Träning & praktiskt", "Om Ju-Jutsu"],
                   home.css(".site-nav > details > summary").map(&:text)
      assert_equal 1, home.css('.site-nav a[href="/foreningen/arkiv/"]').length
      assert_empty home.css('.site-nav a[href="/foreningen/arkiv/"]').first.parent.css("details")
      overview = Nokogiri::HTML(File.read(File.join(destination, "foreningen/arkiv/index.html")))
      %w[graderingar nyheter lager].each do |section|
        refute_nil overview.at_css(%(a[href="/foreningen/arkiv/#{section}/"])), section
      end
      assert_empty home.css(".archive-notice")
      assert_empty Nokogiri::HTML(File.read(File.join(destination, "traning/schema/index.html"))).css(".archive-notice")
    end
  end
end
