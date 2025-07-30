import streamlit as st
from streamlit.components.v1 import html
import os
from dadosfera.utils import consts


VERSION = os.getenv("VERSION", "0.0.1")
SOFTWARE_LIFECYCLE = os.getenv("SOFTWARE_LIFECYCLE", "alpha")
DEPLOYMENT_ENVIRONMENT = os.getenv("ENV", "dev")
LANGUAGE = os.getenv("LANGUAGE_CODE", "en")

TEXT_ELEMENTS_MAPPER = {
    'en': {
        'software_lifecycle': 'Software Lifecycle',
        'deployment_environment': 'Deployment Environment',
        'cancel': 'Cancel Subscription',
        'financial': 'Financial',
        'support': 'Support',
    },
    'pt': {
        'software_lifecycle': 'Ciclo de Vida',
        'deployment_environment': 'Ambiente',
        'cancel': 'Cancelar',
        'financial': 'Financeiro',
        'support': 'Suporte',
    },
    'es': {
        'software_lifecycle': 'Ciclo de Vida',
        'deployment_environment': 'Entorno de Despliegue',
        'cancel': 'Cancelar',
        'financial': 'Financiero',
        'support': 'Soporte',
    }
}


def set_page_config(
    page_title="Inicio",
    page_layout="centered",
    initial_sidebar_state='auto'
):
    st.set_page_config(
        page_icon=consts.PAGE_LOGO,
        page_title=page_title,
        layout=page_layout,
        initial_sidebar_state=initial_sidebar_state
    )


def add_sidebar_image():
    st.sidebar.image(image=consts.LOGO, use_container_width=True)


def add_custom_elements(cancel_link="https://docs.dadosfera.ai/discuss", financial_department_link="mailto:financeiro@dadosfera.ai", support_link="mailto:suporte@dadosfera.ai"):
    decoration = """
    <script>
    const decoration = parent.document.querySelector('div[data-testid="stDecoration"]')
            if (decoration) {
              decoration.style.backgroundImage = "linear-gradient(90deg, rgb(0, 128, 255), rgb(0, 255, 255))";
            }
    </script>
    """
    software_lifecycle_text = TEXT_ELEMENTS_MAPPER[LANGUAGE]['software_lifecycle']
    deployment_environment_text = TEXT_ELEMENTS_MAPPER[LANGUAGE]['deployment_environment']
    cancel_text = TEXT_ELEMENTS_MAPPER[LANGUAGE]['cancel']
    financial_text = TEXT_ELEMENTS_MAPPER[LANGUAGE]['financial']
    support_text = TEXT_ELEMENTS_MAPPER[LANGUAGE]['support']
    if os.environ.get('APP_TIER', 'free') == 'free':
        footer_text = f"<div class='footer'><p><b>v{VERSION}</b></p><p>{software_lifecycle_text}: <b>{SOFTWARE_LIFECYCLE}</b></p><p>{deployment_environment_text}:  <b>{DEPLOYMENT_ENVIRONMENT}</b></p><br><a href={support_link}>{support_text}</a></div>"
    else:
        footer_text = f"<div class='footer'><p><b>v{VERSION}</b></p><p>{software_lifecycle_text}: <b>{SOFTWARE_LIFECYCLE}</b></p><p>{deployment_environment_text}:  <b>{DEPLOYMENT_ENVIRONMENT}</b></p><br><a href={cancel_link}>{cancel_text}</a><a href={financial_department_link}>{financial_text}</a><a href={support_link}>{support_text}</a></div>"

    override_footer = f"""
    <script>
        element = parent.document.getElementsByTagName("footer")[0]
        element.innerHTML = "{footer_text}";
    </script>
    """

    style = """
    <style>
    .footer {
        display: flex;
        justify-content: space-between;

    }
    .footer a {
      cursor: pointer;
      text-decoration: none;
    }
    #MainMenu {
      display: none;
    }
    .stDeployButton {
        display: none;
    }
    </style>
"""

    html(decoration,  height=0)
    html(override_footer,  height=0)
    st.write(style, unsafe_allow_html=True)
# Função principal que chama todas as outras


def brand(
    page_title="Inicio",
    page_layout="centered",
    initial_sidebar_state="auto"
):
    set_page_config(page_title, page_layout, initial_sidebar_state)
    add_sidebar_image()
