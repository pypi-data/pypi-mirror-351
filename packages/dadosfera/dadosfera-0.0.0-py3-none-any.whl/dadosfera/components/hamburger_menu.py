import streamlit as st
from streamlit.components.v1 import html


def add_custom_elements():
    cancel_subscription = """
    <script>
// Utilitários para criação de elementos DOM e SVG
const DomUtils = (() => {
  function createSvgElement(name, attributes) {
    const element = document.createElementNS("http://www.w3.org/2000/svg", name);
    for (const [key, value] of Object.entries(attributes)) {
      element.setAttribute(key, value);
    }
    return element;
  }

  function createElementWithClasses(type, classes) {
    const element = document.createElement(type);
    element.classList.add(...classes);
    return element;
  }

  return {
    createSvgElement,
    createElementWithClasses,
  };
})();

// Manipulador de Dropdown
const DropdownHandler = (() => {
  function toggleDropdown(event) {
    const dropdownMenu = this.querySelector(".hamburgerDropdown");
    if (dropdownMenu) {
      dropdownMenu.style.display =
        dropdownMenu.style.display === "none" ? "block" : "none";
      event.stopPropagation();
    }
  }

  function closeDropdownIfClickedOutside(event) {
    const dropdownMenu = document.querySelector(".hamburgerDropdown");
    const menuContainer = document.querySelector(".hamburgerMenuContainer");
    if (menuContainer && !menuContainer.contains(event.target) && dropdownMenu) {
      dropdownMenu.style.display = "none";
    }
  }

  return {
    toggleDropdown,
    closeDropdownIfClickedOutside,
  };
})();

// Função para criar o menu dropdown
function createDropdownContent(menuContainer) {
  const dropdown = DomUtils.createElementWithClasses("div", ["hamburgerDropdown"]);
  const ul = DomUtils.createElementWithClasses("ul", []);

  ul.setAttribute("role", "option");
  ul.setAttribute("aria-selected", "false");
  ul.setAttribute("aria-disabled", "false");

  const aboutLi = DomUtils.createElementWithClasses("li", []);
  const aboutSpan = DomUtils.createElementWithClasses("span", []);
  aboutSpan.innerText = "Fórum";
  aboutLi.appendChild(aboutSpan);

  const cancelLi = DomUtils.createElementWithClasses("li", []);
  const cancelSpan = DomUtils.createElementWithClasses("span", []);
  cancelSpan.innerText = "Cancel Subscription";
  cancelLi.appendChild(cancelSpan);

  ul.appendChild(aboutLi);
  ul.appendChild(cancelLi);
  dropdown.appendChild(ul);
  menuContainer.appendChild(dropdown);
}

// Função principal para inicializar o menu
function initializeMenu() {
  const stToolbar = parent.document.querySelector('div[data-testid="stToolbar"]');
  if (!stToolbar) return;

  let menuContainer = DomUtils.createElementWithClasses("div", ["hamburgerMenuContainer"]);
  let existingMenuContainer = stToolbar.querySelector(".hamburgerMenuContainer");
  if (existingMenuContainer) return;

  let hamburgerMenu = stToolbar.querySelector(".hamburgerMenu");

  if (!hamburgerMenu) {
    hamburgerMenu = DomUtils.createSvgElement("svg", {
      viewBox: "0 0 24 24",
      "aria-hidden": "true",
      focusable: "false",
      fill: "currentColor",
      color: "inherit"
    });

    hamburgerMenu.classList.add("hamburger-icon");

    const path2 = DomUtils.createSvgElement("path", {
      d: "M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z",
    });

    hamburgerMenu.appendChild(path2);
    menuContainer.appendChild(hamburgerMenu);
    menuContainer.addEventListener("click", DropdownHandler.toggleDropdown);

    createDropdownContent(menuContainer);

    stToolbar.appendChild(menuContainer);
    document.addEventListener("click", DropdownHandler.closeDropdownIfClickedOutside);
  }
}
initializeMenu()
    </script>
    """

    remove_hamburguer_menu = """
    <style>
        #MainMenu { display: none; }

        .hamburger-icon {
            width: 1.25rem;
            height: 1.25rem;
        }

        .hamburgerMenuContainer {
            border: 1rem;
            cursor: pointer;
            padding: 1rem;
        }

        .hamburgerMenuContainer:hover {
            background-color: #ddd;
            border-radius: 0.4rem;
        }


        .hamburgerDropdown {
            display: none;
            position: absolute;
            background-color: #f9f9f9;
            width: 10rem;
            border: 1px solid #ccc;
            # top: 100%;       /* position dropdown just below the menu */
            top: 3rem; /* add 5px gap below the menu */
            right: 0.3rem;
            border-radius: 0.6rem;

        }

        .hamburgerDropdown ul {

            list-style-type: none;
            margin: 0;
            padding: 0;
            cursor: pointer;
            border-radius: 1rem;
        }

        .hamburgerDropdown li {
            padding: 8px;
            color: #1700a2;
            cursor: pointer;
            border-radius: 0.6rem;
        }

        .hamburgerDropdown li:hover {
            background-color: #ddd;
        }
    </style>
    """

    html(cancel_subscription)
    st.write(remove_hamburguer_menu, unsafe_allow_html=True)


# Função principal que chama todas as outras


def hamburger_menu():
    add_custom_elements()
