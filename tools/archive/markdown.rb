require "nokogiri"

module ArchiveMarkdown
  module_function

  def escape(text)
    text.gsub(/[\\`*_\[\]]/) { |character| "\\#{character}" }
  end

  def children(node)
    node.children.map { |child| render(child) }.join
  end

  def inline(node)
    children(node).gsub(/[ \t\r\n]+/, " ").strip
  end

  def render(node)
    return escape(node.text.gsub(/[[:space:]]+/, " ")) if node.text?
    return "" if node.comment?
    case node.name
    when "div", "span", "tbody", "thead", "dl", "dt", "wbr"
      children(node)
    when "p", "figure", "figcaption"
      text = children(node).strip
      text = text.gsub(/^(\d+)\. /, '\1\\. ') if node.name == "p"
      "\n\n#{text}\n\n"
    when /^h[1-6]$/
      "\n\n#{'#' * node.name[1].to_i} #{inline(node)}\n\n"
    when "strong", "b"
      content = children(node)
      text = inline(node)
      text.empty? ? "" : "#{' ' if content.match?(/\A\s/)}**#{text}**#{' ' if content.match?(/\s\z/)}"
    when "em", "i"
      content = children(node)
      text = inline(node)
      text.empty? ? "" : "#{' ' if content.match?(/\A\s/)}*#{text}*#{' ' if content.match?(/\s\z/)}"
    when "a"
      return children(node) unless node["href"]
      link = "[#{inline(node)}](<#{node['href'].gsub('%20', ' ')}>)"
      node.at_css("img") ? "\n\n#{link}\n\n" : link
    when "img"
      "\n\n![#{escape(node['alt'].to_s)}](<#{node['src'].gsub('%20', ' ')}>)\n\n"
    when "br"
      "  \n"
    when "colgroup", "col"
      ""
    when "ul", "ol"
      items = node.element_children.select { |child| child.name == "li" }
      "\n\n" + items.each_with_index.map do |item, index|
        marker = node.name == "ol" ? "#{index + 1}." : "-"
        text = children(item).strip
        "#{marker} #{text.gsub("\n", "\n  ")}"
      end.join("\n") + "\n\n"
    when "blockquote"
      "\n\n#{children(node).strip.gsub(/^/, '> ')}\n\n"
    when "table"
      rows = node.css("tr").map do |row|
        row.element_children.select { |cell| %w[td th].include?(cell.name) }.map do |cell|
          # Escape table separators in text, never inside a Liquid URL.
          inline(cell).split(/(\{\{.*?\}\})/).map { |part| part.start_with?("{{") ? part : part.gsub("|", "\\|") }.join
        end
      end
      width = rows.map(&:size).max
      rows.each { |row| row.fill("", row.size...width) }
      # Headerless source tables keep their first data row; use an empty header.
      header = node.at_css("th") ? rows.shift : Array.new(width, "")
      "\n\n" + [header, Array.new(width, "---"), *rows].map { |row| "| #{row.join(' | ')} |" }.join("\n") + "\n\n"
    when "iframe"
      "\n\n[Öppna kalendern](<#{node['src']}>)\n\n"
    else
      raise "Unsupported content element: #{node.name}"
    end
  end

  def convert(html)
    fragment = Nokogiri::HTML.fragment(html)
    fragment.children.map { |node| render(node) }.join.gsub(/ *\n[ \t]+/, "\n").gsub(/\n{3,}/, "\n\n").strip + "\n"
  end
end
