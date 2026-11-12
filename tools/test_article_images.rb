require "fileutils"
require "minitest/autorun"
require "tmpdir"
require "jekyll"
require "nokogiri"
require_relative "../_plugins/article_images"

class ArticleImagesIntegrationTest < Minitest::Test
  def test_folder_articles_publish_resized_images_at_the_article_url
    Dir.mktmpdir do |source|
      root = File.expand_path("..", __dir__)
      FileUtils.mkdir_p(File.join(source, "tools"))
      FileUtils.cp(File.join(root, "tools/resize_article_images.py"), File.join(source, "tools"))
      FileUtils.mkdir_p(File.join(source, "_includes"))
      FileUtils.cp(File.join(root, "_includes/article-images.html"), File.join(source, "_includes"))
      FileUtils.mkdir_p(File.join(source, "_layouts"))
      File.write(File.join(source, "_layouts/test.html"),
                 "---\n---\n{{ content }}{% include article-images.html %}")
      %w[nyheter graderingar].each do |section|
        folder = File.join(source, "_club_pages", section, "2026-11-12-#{section}-test")
        FileUtils.mkdir_p(folder)
        File.write(File.join(folder, "2026-11-12-test.md"), <<~MARKDOWN)
          ---
          title: Test
          layout: test
          image_descriptions:
            photo.jpg: Gruppbild efter graderingen
          ---
          Artikeltext.
        MARKDOWN
        success = system("python3", "-c",
                         "from PIL import Image; import sys; Image.new('RGB', (3200,2400), 'red').save(sys.argv[1])",
                         File.join(folder, "photo.jpg"))
        assert success
      end
      text_folder = File.join(source, "_club_pages", "nyheter", "2026-11-12-text")
      FileUtils.mkdir_p(text_folder)
      File.write(File.join(text_folder, "2026-11-12-text.md"), "---\nlayout: test\npermalink: /nyheter/text/\n---\nText only.")
      destination = File.join(source, "_site")
      site = Jekyll::Site.new(Jekyll.configuration(
        "source" => source, "destination" => destination, "config" => [],
        "layouts_dir" => "_layouts", "includes_dir" => "_includes",
        "collections" => { "club_pages" => { "output" => true } },
        "baseurl" => "/test", "exclude" => ["tools"], "quiet" => true
      ))
      Dir.chdir(source) { site.process }
      assert_equal source, site.source
      assert site.layouts.key?("test"), site.layouts.keys.inspect
      assert_equal "test", site.collections["club_pages"].docs.first.data["layout"]
      refute_empty site.collections["club_pages"].docs.find { |d| d.data["title"] == "Test" }.data["article_images"]
      %w[nyheter graderingar].each do |section|
        output_folder = File.join(destination, "nyheter", "2026-11-12-#{section}-test")
        assert File.file?(File.join(output_folder, "photo.jpg"))
        html = Nokogiri::HTML(File.read(File.join(output_folder, "index.html")))
        refute_nil html.at_css("img"), html.to_html
        assert_equal "/test/nyheter/2026-11-12-#{section}-test/photo.jpg", html.at_css("img")["src"]
        assert_equal "Gruppbild efter graderingen", html.at_css("img")["alt"]
        assert_equal 1, html.css("img").length
        assert_operator html.to_html.index("Artikeltext."), :<, html.to_html.index("<img")
        success = system("python3", "-c", <<~PYTHON, File.join(output_folder, "photo.jpg"))
          from PIL import Image
          import sys
          with Image.open(sys.argv[1]) as image:
              assert image.size == (1600, 1200), image.size
        PYTHON
        assert success
        original = File.join(source, "_club_pages", section, "2026-11-12-#{section}-test", "photo.jpg")
        assert system("python3", "-c",
                      "from PIL import Image; import sys; assert Image.open(sys.argv[1]).size == (3200,2400)",
                      original)
      end
      assert File.file?(File.join(destination, "nyheter/text/index.html"))
      text_html = File.read(File.join(destination, "nyheter/text/index.html"))
      refute_includes text_html, "article-images"
      assert_equal 2, Dir.glob(File.join(destination, "**/*.jpg")).length
    end
  end
end
