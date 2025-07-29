from __future__ import annotations

import re
import os
import uuid

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class SubSection:
    title: str
    content: str
    page_number: list[int]

    @classmethod
    def get_sections(cls, raw_subsection: str, page_number: int) -> Section:
        raw_subsection = raw_subsection.strip()
        section_fields = raw_subsection.split("\n", maxsplit=1)
        return SubSection(
            section_fields[0],
            section_fields[1] if len(section_fields) > 1 else "",
            [page_number],
        )


@dataclass
class Section:
    title: str
    content: str
    pages_number: list[int]
    subsections: list[SubSection] = Field(default=[])

    @classmethod
    def get_sections(cls, raw_section: str, page_number: int) -> Section:
        raw_section = raw_section.strip()
        section_fields = raw_section.split("\n", maxsplit=1)
        return Section(
            section_fields[0],
            section_fields[1] if len(section_fields) > 1 else "",
            [page_number],
        )

    def get_subsections_starting_in_page(self) -> list[SubSection]:
        section_regexp = r"((?:\n|^)#{2}\s.*?(?=\n#{1,6}\s|\Z))"
        raw_sections = re.findall(section_regexp, self.content, re.DOTALL)
        subsections = [
            SubSection.get_sections(raw_section, self.page_number)
            for raw_section in raw_sections
        ]
        return subsections


@dataclass
class Page:
    content: str
    page_number: int
    _id: str = Field(default=str(uuid.uuid4()))
    sections: list[Section] = Field(default=[])
    subsections: list[SubSection] = Field(default=[])

    @classmethod
    def get_page(cls, raw_pages: str, page_number) -> Page:
        page_title = f"# Page {page_number}"
        page_content = raw_pages[len(page_title) :].strip()
        return Page(page_content, page_number)

    def get_sections_starting_in_page(self) -> list[Section]:
        # Commence à un niveau 1 ou 2, s'arrête au prochain niveau 1, 2 ou 3
        section_regexp = r"((?:\n|^)(?:#{1,2})\s.*?(?=\n#{1,3}|\Z))"
        raw_sections = re.findall(section_regexp, self.content, re.DOTALL)
        sections = [
            Section.get_sections(raw_section, self.page_number)
            for raw_section in raw_sections
        ]
        return sections


@dataclass
class Manual:
    pages: list[Page]
    sections: list[Section]
    subsections: list[Section]
    name: str

    @classmethod
    def get_manual(cls, manual: str, file_name: str) -> Manual:
        pages = cls.get_pages(manual)
        sections = cls.get_sections(pages)
        return cls(pages, sections, file_name)

    @classmethod
    def get_pages(slf, text: str) -> list[Page]:
        pages_regexp = r"(# Page.*?(?=\n# Page|\Z))"
        pages_raw = re.findall(pages_regexp, text, re.DOTALL)
        if len(pages_raw) == 0:
            pages_raw = [text]
        pages = [
            Page.get_page(raw_page, id_page + 1)
            for id_page, raw_page in enumerate(pages_raw)
        ]
        return pages

    @classmethod
    def get_sections(cls, pages: list[Page]) -> list[Section]:
        sections_dict = {}
        for id_page, page in enumerate(pages):
            if not page.content.startswith("## ") and id_page > 0:
                # Unfinished section or sub-sections
                unfinished_section = pages[id_page - 1].sections[-1]
                unfinished_content = page.content.split("\n##\\s")[0]
                unfinished_section.content += unfinished_content
                unfinished_section.pages_number.append(page.page_number)
                page.sections.append(unfinished_section)
            sections = page.get_sections_starting_in_page()
            page.sections += sections
            sections_dict.update({section.title: section for section in sections})
        return list(sections_dict.values())

    @classmethod
    def get_subsections(cls, sections: list[Section]) -> list[SubSection]:
        # TODO correct subsection parsing
        subsections_dict = {}
        for id_page, section in enumerate(sections):
            subsections = section.get_subsections_starting_in_page()
            section.subsections += subsections
            subsections_dict.update(
                {subsection.title: subsection for subsection in subsections}
            )
        return list(subsections_dict.values())

    @classmethod
    def get_manual_structure(cls, raw_manual: str, file_name: str) -> Manual:
        pages = Manual.get_pages(raw_manual)
        sections = Manual.get_sections(pages)
        subsections = Manual.get_subsections(sections)
        return Manual(pages, sections, subsections, file_name)

    @classmethod
    def from_file(cls, folder_path: str, file_name: str) -> Manual:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path) as f:
            text = f.read()
        return cls.get_manual_structure(text, file_name)
