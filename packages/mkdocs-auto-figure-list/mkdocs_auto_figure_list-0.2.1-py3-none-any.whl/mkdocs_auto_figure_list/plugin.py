import re
import os
from mkdocs.plugins import BasePlugin

config_scheme = (
        ('heading', str),
        ('figure_label', str),
    )


class FigureListCreation(BasePlugin):
    def __init__(self):
        self.figures = []  # safes all images
        self.figure_counter = 1
        self.heading = "List of Figure"
        self.figure_label = "figure"
    
    def on_config(self, config):
        self.heading = self.config.get('heading', self.heading)
        self.figure_label = self.config.get('figure_label', self.figure_label)
        return config
    
    def on_page_markdown(self, markdown, page, config, files):
        list_items = []

        def figure_replacer(match):
            full_html = match.group(0)
            caption = match.group(2)
            fig_id = f"fig-{self.figure_counter}"
            labeled_caption = f"{self.figure_label} {self.figure_counter}: {caption}"

            new_html = re.sub(
                r'(<figcaption>)(.*?)(</figcaption>)',
                rf'\1{labeled_caption}\3',
                full_html,
                flags=re.DOTALL
            )

            if 'id="' not in full_html:
                new_html = re.sub(r'<figure', f'<figure id="{fig_id}"', new_html)

            dir = os.path.splitext(page.file.src_path)[0].replace("\\", "/")
            if dir != "index":
                path = '../' + dir + "/"
                figure_link = f"{path}#{fig_id}"
            else:
                figure_link = f"../#{fig_id}"

            list_items.append(
                f'<li><a href="{figure_link}">{labeled_caption}</a></li>'
            )

            self.figure_counter += 1
            return new_html

        # replace all figure tags
        markdown = re.sub(
            r'(<figure.*?>.*?<figcaption>(.*?)</figcaption>.*?</figure>)',
            figure_replacer,
            markdown,
            flags=re.DOTALL
        )

        if list_items:
            figure_list_html = '<ul class="list-of-figures">\n' + '\n'.join(list_items) + '\n</ul>'
            self.figures.append(figure_list_html)

        return markdown


    def on_post_build(self, config):
        if not self.figures:
            return

        output_dir = config['docs_dir']
        figure_file_path = os.path.join(output_dir, 'figure_list.md')

        auto_content = '\n'.join(self.figures)
        start_marker = '<!-- BEGIN AUTO-FIGURES -->'
        end_marker = '<!-- END AUTO-FIGURES -->'
        auto_block = f"{start_marker}\n{auto_content}\n{end_marker}"

        heading_line = f"# {self.heading}" 

        if os.path.exists(figure_file_path):
            with open(figure_file_path, 'r', encoding='utf-8') as f:
                existing = f.read()

            lines = existing.strip().splitlines()
            if lines and lines[0].startswith("#"):
                lines[0] = heading_line 
            else:
                lines.insert(0, heading_line)  
            existing = '\n'.join(lines)  

            # search for old block
            pattern = re.compile(
                rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}",
                re.DOTALL
            )
            match = pattern.search(existing)

            if match:
                old_auto_block = match.group(0)
                if old_auto_block.strip() == auto_block.strip():
                    print("Figure list has no changes.")
                    return  # to avoid loop 

                # replace the old block 
                new_file_content = pattern.sub(auto_block, existing)
            else:
                # add new block
                new_file_content = existing.strip() + "\n\n" + auto_block
        else:
            new_file_content = f"{heading_line}\n\n{auto_block}"

        # Write only, when something changed
        if os.path.exists(figure_file_path):
            with open(figure_file_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
        else:
            current_content = ""

        if current_content.strip() != new_file_content.strip():
            with open(figure_file_path, 'w', encoding='utf-8') as f:
                f.write(new_file_content)
            print(f"Figure list updated: {figure_file_path}")
        else:
            print("Figure list has no changes (content identical).")

