# Syqlorix: Build Hyper-Minimal Web Pages in Pure Python

![Syqlorix Logo Placeholder](https://via.placeholder.com/150x50?text=Syqlorix)

## Overview

**Syqlorix** is a futuristic Python package inspired by Flask and Dominate, designed to build full HTML documents—including **CSS** and **JavaScript**—from a **single Python script**. It offers a pure Python DSL (Domain-Specific Language) for authoring web interfaces, making it a single-file web page builder that is zero-dependency, readable, and easily embeddable for dynamic web content creation.

## Goals & Design Philosophy

🔹 **Simpler than Dominate**
🔹 **More readable than raw HTML**
🔹 **No need for separate `.html`, `.css`, or `.js` files**

### Core Design Principles

*   **All-in-One**: Write entire pages in one `.py` file.
*   **Minimal API**: Small surface area, quick to learn.
*   **Super Readable**: Feels like Markdown, acts like HTML.
*   **Framework-Ready**: Works seamlessly with Flask, Starlette, etc.
*   **Tech-Aesthetic**: Feels modern, futuristic, efficient.

## Example Usage

```python
from syqlorix import Page

page = Page(title="Welcome to Syqlorix")

with page.body:
    page.h1("Build Pages in Python")
    page.p("No need for HTML files. This is all Python.")

    with page.div(id="features", style="border: 1px solid #ddd; padding: 15px; border-radius: 8px;"):
        page.h2("Key Features")
        page.ul(
            page.li("HTML via functions"),
            page.li("Inline CSS/JS blocks"),
            page.li("Flask integration"),
            page.li("Zero dependencies!"),
        )
    page.button("Click Me", id="btn", _class="my-button")

page.style("""
    body { font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 40px; line-height: 1.6; color: #333; }
    h1 { color: #0d6efd; }
    h2 { color: #0d6efd; border-bottom: 1px solid #eee; padding-bottom: 5px; }
    .my-button { background: #0d6efd; color: white; border: none; padding: 12px 20px; border-radius: 5px; cursor: pointer; font-size: 1em; transition: background 0.3s ease; }
    .my-button:hover { background: #0a58ca; }
    #features { background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 30px; }
    ul { list-style-type: none; padding: 0; }
    li { margin-bottom: 8px; background: #e9ecef; padding: 8px 12px; border-radius: 4px; display: flex; align-items: center; }
    li::before { content: '✨'; margin-right: 8px; }
""")

page.script("""
    document.getElementById('btn').onclick = function() {
        alert('Clicked with Syqlorix! This is a single Python file.');
    };
""")

html_output = page.render()

print(html_output)
```

## Key API Features

*   `Page(...)` → Main class to construct a page.
*   `page.h1()`, `page.div()`, `page.ul()` → HTML tag functions.
*   `with page.body:` → Context-managed content creation for nesting.
*   `page.style(css_str)` → Add CSS inline within a `<style>` tag in the `<head>`.
*   `page.script(js_str)` → Add JS inline within a `<script>` tag before `</body>`.
*   `page.render()` → Outputs the full HTML page string including `<!DOCTYPE html>`.
*   `syqlorix.serve_page_dev(page_obj, port=8000)` → New utility to serve a `Page` object with a simple development server.

## Target Use Cases

*   **Fast Prototyping**: Quickly mock up HTML content without juggling multiple files, using `serve_page_dev`.
*   **Dynamic HTML Generation**: For developers who need to generate HTML on the fly without a full-blown templating engine.
*   **Educational Tools**: A clear, Python-only way to demonstrate HTML structure.
*   **Static Site Generation**: Build simple static sites purely with Python scripts.
*   **Small Web Services**: Embed HTML generation directly into Flask/Starlette applications.

## Name Rationale: “Syqlorix”

*   💡 *Invented word*: completely unique and claimable.
*   🧠 *Tech-aesthetic*: futuristic, protocol-sounding.
*   💎 *Rare*: zero collisions on Google, PyPI, or GitHub.
*   ⚡ *Brand-ready*: distinctive and pronounceable.

## Future Directions

*   `syqlorix.css()` → Mini dict-based CSS DSL for programmatic CSS.
*   `syqlorix.include("nav.py")` → Component loading for larger projects.
*   `syqlorix.emit()` → Export to static HTML file directly.
*   CLI support: `syqlorix build site.py > index.html`

## Get Started (Local Installation)

1.  **Clone this repository**
2.  **Navigate to the project root** in your terminal.
3.  **Install in editable mode** or as a regular package:

    ```bash
    pip install .
    ```

    Once published to PyPI, you can install directly:
    ```bash
    pip install syqlorix
    ```

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.