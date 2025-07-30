import streamlit as st


def format_page(page_title, layout="wide", initial_sidebar_state="expanded"):
    """Format the streamlit page to the pattern of a dadosfera data app page

    Args:
        page_title (str): the title of the page
            Example: "My Streamlit App"
        layout (str): How the page content should be laid out. Defaults to "centered", which constrains the elements into a centered column of fixed width; "wide" uses the entire screen. Defaults to 'wide'.
        initial_sidebar_state (str): How the sidebar should start out. Defaults to "auto", which hides the sidebar on small devices and shows it otherwise.
          "expanded" shows the sidebar initially; "collapsed" hides it.
          In most cases, you should just use "auto", otherwise the app will look bad when embedded and viewed on mobile.

    Returns:
        None
    See Also:
        - https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config

    """
    st.set_page_config(
        page_title=page_title,
        page_icon="https://s3.amazonaws.com/gupy5/production/companies/1286/career/2122/images/2022-01-05_13-07_logo.png",
        layout=layout,
        initial_sidebar_state=initial_sidebar_state,
    )

    st.sidebar.image(
        "https://cdn-images-1.medium.com/max/1200/1*OPrCFbKQFOeL0QKCuDeR1g.png",
        width=300,
    )
