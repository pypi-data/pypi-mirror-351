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
    page_number: list[int] # Stores the page number(s) where the subsection is found

    @classmethod
    def get_sections(cls, raw_subsection: str, page_number: int) -> SubSection: # Changed return type to SubSection
        raw_subsection = raw_subsection.strip() # Example: "### Title\nContent"
        subsection_fields = raw_subsection.split("\n", maxsplit=1)
        
        title_line = subsection_fields[0]
        # Remove "### " prefix, which is 4 characters long
        cleaned_title = title_line[4:].strip() if title_line.startswith("### ") else title_line.strip()
        
        content = subsection_fields[1] if len(subsection_fields) > 1 else ""
        
        return SubSection(
            cleaned_title,
            content,
            [page_number], # page_number is an int, SubSection expects list[int]
        )


@dataclass
class Section:
    title: str
    content: str
    pages_number: list[int]
    subsections: list[SubSection] = Field(default=[])

    @classmethod
    def get_sections(cls, raw_section: str, page_number: int) -> Section:
        raw_section = raw_section.strip() # Example: "## Title\nContent"
        section_fields = raw_section.split("\n", maxsplit=1)
        
        title_line = section_fields[0]
        # Remove "## " prefix, which is 3 characters long
        cleaned_title = title_line[3:].strip() if title_line.startswith("## ") else title_line.strip()

        content = section_fields[1] if len(section_fields) > 1 else ""
        
        return Section(
            cleaned_title,
            content,
            [page_number],
        )

    def get_subsections_starting_in_page(self) -> list[SubSection]:
        # Subsections are defined by H3 headings (###) within a section.
        # A subsection stops if an H1 (#), H2 (##), or another H3 (###) is encountered, or at the end of section content.
        # The regex captures the entire subsection block, starting with "### "
        subsection_regexp = r"((?:(?:\n|^)###\s).*?(?=\n(?:#\s|##\s|###\s)|\Z))"
        raw_subsections = re.findall(subsection_regexp, self.content, re.DOTALL)
        
        subsections = []
        if self.pages_number: # Ensure pages_number is not empty
            # Pass the primary page number of the section
            primary_page_number = self.pages_number[0] 
            for raw_subsection in raw_subsections:
                subsections.append(SubSection.get_sections(raw_subsection, primary_page_number))
        return subsections


@dataclass
class Page:
    content: str
    page_number: int
    _id: str = Field(default=str(uuid.uuid4()))
    sections: list[Section] = Field(default=[])
    subsections: list[SubSection] = Field(default=[])

    @classmethod
    def get_page(cls, page_content: str, page_number: int) -> Page:
        # Content is already processed by Manual.get_pages to remove delimiter
        return Page(page_content.strip(), page_number)

    def get_sections_starting_in_page(self) -> list[Section]:
        # Sections are defined by H2 headings (##)
        # A section stops if an H1 (#) or another H2 (##) is encountered, or at the end of page content.
        # The regex captures the entire section block, starting with "## "
        section_regexp = r"((?:(?:\n|^)##\s).*?(?=\n(?:#\s|##\s)|\Z))"
        raw_sections = re.findall(section_regexp, self.content, re.DOTALL)
        sections = [
            Section.get_sections(raw_section, self.page_number) # self.page_number is an int
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
    def get_pages(cls, text: str) -> list[Page]:
        # Delimiter pattern: a line starting with "# Page" (optional number) or "# " (H1)
        # Uses re.MULTILINE via (?m) flag inside the regex string.
        delimiter_pattern = r"(?:(?m)^# Page\s*\d*|(?m)^#\s[^\n]*)"

        delimiters = []
        for match in re.finditer(delimiter_pattern, text):
            # Store (full_match_text, start_index, end_index_plus_newline_if_present)
            # We search for \n after match.end() to ensure we split after the newline of the delimiter.
            newline_after_delimiter = text.find('\n', match.end())
            content_actual_start = newline_after_delimiter + 1 if newline_after_delimiter != -1 else match.end()
            
            delimiters.append({
                "text": match.group(0),
                "match_start": match.start(), # Start of the delimiter line
                "content_start": content_actual_start # Start of content (after delimiter line and its newline)
            })

        if not delimiters:
            if text.strip():
                # No delimiters, treat the whole text as a single page
                # Use the modified Page.get_page which now accepts content directly
                return [Page.get_page(text, 1)]
            return []

        pages_content_list = []
        for i in range(len(delimiters)):
            current_delimiter = delimiters[i]
            
            # Content for this page starts after the current delimiter line
            content_block_start = current_delimiter["content_start"]
            
            # Content for this page ends at the start of the next delimiter line, or EOF
            if i + 1 < len(delimiters):
                next_delimiter = delimiters[i+1]
                content_block_end = next_delimiter["match_start"]
            else:
                content_block_end = len(text)
            
            page_c = text[content_block_start:content_block_end]
            pages_content_list.append(page_c)
        
        pages = []
        for i, content_item in enumerate(pages_content_list):
            pages.append(Page.get_page(content_item, i + 1)) # page_number is 1-indexed
        
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
        # Subsection parsing is now corrected via changes in Section.get_subsections_starting_in_page and SubSection.get_sections
        subsections_dict = {}
        for section in sections: # Iterating directly over sections, id_page not needed here
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
