from notion import Client, Components, Properties
from .html import NotionBlockMapping
from .styles import Style, DefaultStyle

import os

class NotionExporter:
    def __init__(self, client: Client) -> None:
        self.__notion_client = client

    def __get_pages(self, filter: str) -> list[str]:
        pages = self.__notion_client.search_pages(query=filter)
        return [page["id"] for page in pages["results"]]

    def __get_page(self, page_id: str) -> dict:
        return self.__notion_client.get_page_by_id(page_id)

    def __get_blocks(self, page: dict) -> list[dict]:
        blocks = self.__notion_client.get_block_children(page["id"])
        return [block for block in blocks["results"]]

    def export_page(self, filter: str = "", style: Style = DefaultStyle()) -> None:
        print(f"🔍 Searching for pages...")
        pages = self.__get_pages(filter)
        print(f"🔍 Found {len(pages)} pages to export!")
        for page in pages:
            page = self.__get_page(page)
            page_title = page["properties"]["Name"]["title"][0]["plain_text"]
            print(f"📄 Exporting {page_title}...")
            html = "<html>"
            html += style.get_style()
            html += "<body>"
            html += f"<div class='notion-properties'>"
            html += f"<span class='notion-properties-icon'>{page['icon']['emoji']}</span>"
            html += f"<h2>{page_title}</h2>"
            html += f"</div>"
            blocks = self.__get_blocks(page)
            for block in blocks:
                mapping = NotionBlockMapping(block)
                if mapping.mapping_result():
                    html += "".join(mapping.get_html())
            html += "</body></html>"
            html = html.replace("  ", "")
            html = html.replace("\n", "")
            self.save_html(html, page_title)
            print(f"✅ Exported {page_title}!")

    def save_html(self, html: str, page_title: str) -> None:
        print(f"💾 Saving {page_title}...")
        os.makedirs("output", exist_ok=True)
        with open(f"output/{page_title}.html", "w") as f:
            f.write(html)
        print(f"✅ Saved {page_title}!")
