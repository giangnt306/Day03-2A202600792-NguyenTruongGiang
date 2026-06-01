import re


def format_citation(title: str, authors: str, year: int, style: str = "APA") -> str:
    """
    Format paper metadata into standard academic citation styles.
    Args:
        title: Title of the paper.
        authors: Authors of the paper (comma-separated list).
        year: Publication year.
        style: Citation style — 'APA', 'IEEE', or 'BibTeX' (default: APA).
    """
    style = style.upper().strip()
    author_list = [a.strip() for a in authors.split(",") if a.strip()]
    if not author_list:
        author_list = ["Unknown"]

    if style == "APA":
        formatted_authors = []
        for author in author_list:
            parts = author.split(" ")
            if len(parts) > 1:
                lastname = parts[-1]
                initials = "".join([f"{p[0]}." for p in parts[:-1]])
                formatted_authors.append(f"{lastname}, {initials}")
            else:
                formatted_authors.append(author)

        if len(formatted_authors) > 1:
            authors_str = ", & ".join([", ".join(formatted_authors[:-1]), formatted_authors[-1]])
        else:
            authors_str = formatted_authors[0]

        return f"{authors_str} ({year}). {title}."

    elif style == "IEEE":
        formatted_authors = []
        for author in author_list:
            parts = author.split(" ")
            if len(parts) > 1:
                lastname = parts[-1]
                initials = " ".join([f"{p[0]}." for p in parts[:-1]])
                formatted_authors.append(f"{initials} {lastname}")
            else:
                formatted_authors.append(author)

        authors_str = ", ".join(formatted_authors)
        return f'{authors_str}, "{title}," {year}.'

    elif style in ["BIBTEX", "BIB"]:
        first_author_lastname = author_list[0].split(" ")[-1].lower()
        first_word_title = title.split(" ")[0].lower()
        cite_key = f"{first_author_lastname}{year}{first_word_title}"
        cite_key = re.sub(r"[^a-z0-9]", "", cite_key)

        return (
            f"@article{{{cite_key},\n"
            f"  author    = {{{' and '.join(author_list)}}},\n"
            f"  title     = {{{title}}},\n"
            f"  year      = {{{year}}}\n"
            f"}}"
        )

    return (
        f"Unsupported citation style '{style}'. "
        f"Please use APA, IEEE, or BibTeX. "
        f"Raw reference: {authors} ({year}). {title}."
    )
