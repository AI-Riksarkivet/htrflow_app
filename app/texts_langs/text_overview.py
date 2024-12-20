def read_markdown(file_path: str) -> str:
    with open(file_path, "r") as file:
        content = file.read()

    return f"""{content}"""


class TextOverview:
    # HTRFLOW
    htrflow_col1 = read_markdown("app/texts_langs/overview/htrflow/htrflow_col1.md")
    htrflow_col2 = read_markdown("app/texts_langs/overview/htrflow/htrflow_col2.md")
    htrflow_row1 = read_markdown("app/texts_langs/overview/htrflow/htrflow_row1.md")
    htrflow_tab1 = read_markdown("app/texts_langs/overview/htrflow/htrflow_tab1.md")
    htrflow_tab2 = read_markdown("app/texts_langs/overview/htrflow/htrflow_tab2.md")
    htrflow_tab3 = read_markdown("app/texts_langs/overview/htrflow/htrflow_tab3.md")
    htrflow_tab4 = read_markdown("app/texts_langs/overview/htrflow/htrflow_tab4.md")

    # faq & discussion
    text_faq = read_markdown("app/texts_langs/overview/faq_discussion/faq.md")
    text_discussion = read_markdown("app/texts_langs/overview/faq_discussion/discussion.md")

    # Contributions
    contributions = read_markdown("app/texts_langs/overview/contributions/contributions.md")
    huminfra_image = read_markdown("app/texts_langs/overview/contributions/huminfra_image.md")

    # Changelog & Roadmap
    changelog = read_markdown("app/texts_langs/overview/changelog_roadmap/changelog.md")
    old_changelog = read_markdown("app/texts_langs/overview/changelog_roadmap/old_changelog.md")

    roadmap = read_markdown("app/texts_langs/overview/changelog_roadmap/roadmap.md")

    # duplicate & api
    duplicate = read_markdown("app/texts_langs/overview/duplicate_api/duplicate.md")
    api1 = read_markdown("app/texts_langs/overview/duplicate_api/api1.md")
    api_code1 = read_markdown("app/texts_langs/overview/duplicate_api/api_code1.md")
    api2 = read_markdown("app/texts_langs/overview/duplicate_api/api2.md")
    api_code2 = read_markdown("app/texts_langs/overview/duplicate_api/api_code2.md")
