class TextBodyRenderer:
    """
    BodyRenderer class to render email body content.

    Parameters:
        title (str): Email title.
        message (str): Email message.
    """

    def __init__(self, template, title, message):
        self.title = title
        self.message = message
        self.template = template

    def render(self):
        """
        Renders the email body content.

        Returns:
            str: Email body content.
        """
        return self.template.format(title=self.title, message=self.message)


class DictBodyRenderer:
    """
    BodyRenderer class to render email body content.

    Parameters:
        title (str): Email title.
        message (str): Email message.
    """

    def __init__(self, template, **kwargs):
        self.template = template
        self.kwargs = kwargs

    def render(self):
        """
        Renders the email body content.

        Returns:
            str: Email body content.
        """
        return self.template.format(**self.kwargs)
