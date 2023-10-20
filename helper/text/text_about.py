from helper.text.markdown_reader import read_markdown


class TextAbout:
    # HTRFLOW
    htrflow_col1 = read_markdown("helper/text/about/htrflow/htrflow_col1.md")

    htrflow_col2 = read_markdown("helper/text/about/htrflow/htrflow_col2.md")

    htrflow_row1 = read_markdown("helper/text/about/htrflow/htrflow_row1.md")

    htrflow_tab1 = read_markdown("helper/text/about/htrflow/htrflow_tab1.md")

    htrflow_tab2 = read_markdown("helper/text/about/htrflow/htrflow_tab2.md")

    htrflow_tab3 = read_markdown("helper/text/about/htrflow/htrflow_tab3.md")

    htrflow_tab4 = read_markdown("helper/text/about/htrflow/htrflow_tab4.md")

    # Contributions
    contributions = read_markdown("helper/text/about/contributions/contributions.md")

    # Changelog & Roadmap
    current_changelog = read_markdown("helper/text/about/changelog_roadmap/current_changelog.md")

    old_changelog = read_markdown("helper/text/about/changelog_roadmap/old_changelog.md")

    roadmap = read_markdown("helper/text/about/changelog_roadmap/roadmap.md")


if __name__ == "__main__":
    pass
