from typing import Any

from resume_md.components import (
    ATSInfoComponent,
    HeadingComponent,
    ListComponent,
    PageBreakComponent,
    ParagraphComponent,
    ResumeBanner,
    ResumeComponent,
    TableComponent,
)


def tokens_to_components(tokens: list[dict[str, Any]]) -> list[ResumeComponent]:
    """
    Convert tokens from the tokenizer to resume components

    Args:
        tokens: List of tokens from the tokenizer

    Returns:
        List of resume components
    """
    components: list[ResumeComponent] = []

    # Process the first heading specially for the header
    if tokens and tokens[0]["type"] == "heading" and tokens[0]["level"] == 1:
        name: str = tokens[0]["content"]

        # If there's a paragraph next, treat it as contact info
        if len(tokens) > 1 and tokens[1]["type"] == "paragraph":
            contact_info = tokens[1]["content"]
            components.append(ResumeBanner(name, contact_info))
            tokens = tokens[2:]  # Remove the first two tokens
        else:
            components.append(ResumeBanner(name))
            tokens = tokens[1:]  # Remove only the first token

    # Process the remaining tokens
    for token in tokens:
        if token["type"] == "heading":
            components.append(HeadingComponent(token["level"], token["content"]))
        elif token["type"] == "paragraph":
            components.append(ParagraphComponent(token["content"]))
        elif token["type"] == "list":
            components.append(ListComponent(token["list_type"], token["items"]))
        elif token["type"] == "table":
            components.append(
                TableComponent(token["headers"], token["alignments"], token["rows"])
            )
        elif token["type"] == "page-break":
            components.append(PageBreakComponent())
        elif token["type"] == "ats-info":
            components.append(ATSInfoComponent(token["contents"]))

    return components
