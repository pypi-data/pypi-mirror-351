from bs4 import BeautifulSoup, Tag


def find_attr_value(
    soup: BeautifulSoup, tag_name: str, attr_name: str, **kwargs
) -> str | None:
    """Find the single string value of an attribute in a tag, if any."""
    result_set = soup.find_all(name=tag_name, **kwargs)
    if len(result_set) != 1:
        return None
    tag = result_set[0]
    if not isinstance(tag, Tag):
        return None
    attr_value = tag.get(attr_name)
    if not isinstance(attr_value, str):
        return None
    return attr_value
