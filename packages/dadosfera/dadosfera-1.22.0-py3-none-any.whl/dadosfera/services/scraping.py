import requests


def get_content_from_url(url: str) -> bytes:
    """
    Retrieves the content from a specified URL using a GET request with a Firefox user agent.

    Args:
        url (str): The URL to fetch content from.

    Returns:
        bytes or None: The raw content of the webpage if successful (status code 200),
                      None if the request fails.

    Example:
        content = get_content_from_url('https://example.com')
        if content:
            # Process the content
            pass

    Note:
        - Uses Firefox user agent to mimic browser behavior
        - Requires the 'requests' library
        - Does not handle exceptions, caller should implement error handling
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0"
    }

    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        return r.content


def parse_content_from_html(html_content):
    """
    Parses HTML content into a BeautifulSoup object for easy manipulation and searching.

    Args:
        html_content (str or bytes): Raw HTML content to be parsed.

    Returns:
        BeautifulSoup: A parsed BeautifulSoup object representing the HTML document.

    Example:
        soup = parse_content_from_html(html_content)
        title = soup.find('title')

    Note:
        - Requires the 'beautifulsoup4' library
        - Uses 'html.parser' as the parsing engine
    """
    from bs4 import BeautifulSoup

    return BeautifulSoup(html_content, "html.parser")


def extract_text_from_html(html_content) -> str:
    """
    Extracts visible text content from HTML while filtering out script, style, and comment content.

    Args:
        html_content (str or bytes): Raw HTML content to extract text from.

    Returns:
        str: A single string containing all visible text from the HTML document,
             with each text segment separated by spaces.

    Implementation Details:
        1. Uses an internal tag_visible() function to determine if text should be included
        2. Filters out content from: style, script, head, title, meta tags and comments
        3. Joins all visible text segments with spaces
        4. Strips whitespace from each text segment

    Example:
        html = '<html><body><p>Hello</p><script>var x = 1;</script><p>World!</p></body></html>'
        text = extract_text_from_html(html)
        # Returns: "Hello World!"

    Note:
        - Requires 'beautifulsoup4' library
        - Preserves the natural reading order of the document
        - Removes unnecessary whitespace while maintaining word separation
    """
    from bs4.element import Comment

    def tag_visible(element) -> bool:
        """
        Determines if a given HTML element's text should be visible in the final output.

        Args:
            element: BeautifulSoup element to check

        Returns:
            bool: True if the element's text should be visible, False otherwise
        """
        if element.parent.name in [
            "style",
            "script",
            "head",
            "title",
            "meta",
            "[document]",
        ]:
            return False
        if isinstance(element, Comment):
            return False
        return True

    soup = parse_content_from_html(html_content)
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return " ".join(t.strip() for t in visible_texts)
