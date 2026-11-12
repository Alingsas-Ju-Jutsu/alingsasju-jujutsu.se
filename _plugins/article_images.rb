require "json"
require "open3"
require "pathname"

module ArticleImages
  class ImageFile < Jekyll::StaticFile
    def initialize(site, cache, relative_path, public_path)
      super(site, cache, File.dirname(relative_path), File.basename(relative_path))
      @public_path = public_path
    end

    def destination(dest)
      File.join(dest, @public_path)
    end
  end

  class Generator < Jekyll::Generator
    safe true
    priority :highest

    def generate(site)
      collection = site.collections["club_pages"]
      return unless collection

      cache = File.join(site.source, ".jekyll-cache", "article-images")
      manifest = []
      images = []
      folders = {}
      destinations = {}
      collection.docs.each do |article|
        relative = Pathname.new(article.path).relative_path_from(Pathname.new(site.source)).to_s
        next unless relative.match?(%r{\A_club_pages/(nyheter|graderingar)/[^/]+/[^/]+\.md\z})

        folder = File.dirname(article.path)
        article.data["permalink"] ||= "/nyheter/#{File.basename(folder)}/"
        if folders.key?(folder)
          raise Jekyll::Errors::FatalException, "Only one Markdown article is allowed in #{folder}"
        end
        folders[folder] = true
        article.data["article_images"] = []
        unless article.url.end_with?("/")
          raise Jekyll::Errors::FatalException, "Article with local images needs a trailing-slash permalink: #{relative}"
        end
        Dir.children(folder).sort.each do |name|
          source = File.join(folder, name)
          next unless File.file?(source)
          next unless name.match?(/\.(jpe?g|png|webp)\z/i)

          public_path = File.join(article.url.delete_prefix("/"), name)
          if Pathname.new(public_path).each_filename.include?("..") || destinations.key?(public_path)
            raise Jekyll::Errors::FatalException, "Conflicting article image path: #{public_path}"
          end
          destinations[public_path] = true
          cached_path = File.join(File.dirname(relative), name)
          manifest << { source: source, destination: File.join(cache, cached_path) }
          images << ImageFile.new(site, cache, cached_path, public_path)
          descriptions = article.data["image_descriptions"] || {}
          article.data["article_images"] << {
            "url" => "/#{public_path}",
            "alt" => descriptions[name] || "Bild till #{article.data['title']}"
          }
          # Collection assets must not also publish the unoptimized source image.
          site.static_files.reject! { |file| file.path == source }
          collection.files.reject! { |file| file.path == source }
        end
      end
      return if manifest.empty?

      _, error, status = Open3.capture3(
        "python3", File.join(site.source, "tools", "resize_article_images.py"),
        stdin_data: JSON.generate(manifest)
      )
      unless status.success?
        raise Jekyll::Errors::FatalException, "Article image resizing failed:\n#{error}"
      end
      site.static_files.concat(images)
      Jekyll.logger.info "Article images:", "optimized #{images.length} images (max 1600 px)"
    end
  end
end
