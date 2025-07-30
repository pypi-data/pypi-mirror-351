from typing import Literal
from streamlit.components.v1 import html
import streamlit as st


def add_print_button(layout: Literal["h", "v"] = "v"):
    """
    Adds a print button with specified output layout.

    Parameters:
        layout ("h", "v"): The layout of the output pdf.
            - "h" for horizontal layout
            - "v" for vertical layout

    This function adds a print button to the page, allowing users to print the content of the app.

    Example usage:
    add_print_button("h")  # Adds a print button with horizontal layout.
    """

    width = "320mm"
    height = "210mm"

    if layout == "v":
        width = "210mm"
        height = "320mm"

    st.markdown(
        f"""
        <style>
            @media print {{
                [data-testid="stSidebar"] {{
                    display: none !important;
                }}
                body {{
                    width: {width};
                }}
                @page {{
                    size: {width} {height};
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    html(
        """
            <style>
                body {
                    margin: 0px;
                }
                button {
                    align-items: center;
                    background-color: rgb(249, 249, 251);
                    border-bottom-color: rgba(49, 51, 63, 0.2);
                    border-bottom-left-radius: 4px;
                    border-bottom-right-radius: 4px;
                    border-bottom-style: solid;
                    border-bottom-width: 1px;
                    border-left-color: rgba(49, 51, 63, 0.2);
                    border-left-style: solid;
                    border-left-width: 1px;
                    border-right-color: rgba(49, 51, 63, 0.2);
                    border-right-style: solid;
                    border-right-width: 1px;
                    border-top-color: rgba(49, 51, 63, 0.2);
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    border-top-style: solid;
                    border-top-width: 1px;
                    box-sizing: border-box;
                    color: rgb(49, 51, 63);
                    cursor: pointer;
                    display: inline-flex;
                    font-family: "Source Sans Pro", sans-serif;
                    font-size: 16px;
                    height: 36px;
                    justify-content: center;
                    line-height: 25.6px;
                    margin-bottom: 0px;
                    margin-left: 0px;
                    margin-right: 0px;
                    margin-top: 0px;
                    overflow-x: visible;
                    overflow-y: visible;
                    padding-bottom: 4px;
                    padding-left: 12px;
                    padding-right: 12px;
                    padding-top: 4px;
                    text-align: center;
                    text-indent: 0px;
                    text-size-adjust: 100%;
                    width: 100px;
                }
                button p{
                    box-sizing: border-box;
                    color: rgb(49, 51, 63);
                    display: block;
                    font-family: "Source Sans Pro", sans-serif;
                    font-size: 15px;
                    line-height: 25.6px;
                    padding-bottom: 0px;
                    padding-left: 0px;
                    padding-right: 0px;
                    padding-top: 0px;
                    word-break: break-word;
                    -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
                }
            </style>
            <button id="print-button">
                <p>Gerar PDF</p>
            </button>

            <script>
                try {
                    document.addEventListener("DOMContentLoaded", () => {
                        const printButton = document.getElementById('print-button')
                        printButton.addEventListener("click", event => {
                            event.preventDefault();
                            parent.window.print();
                        }, false);
                    })
                } catch(e) {
                    console.error(e)
                }
            </script>
        """,
        None,
        40,
    )
