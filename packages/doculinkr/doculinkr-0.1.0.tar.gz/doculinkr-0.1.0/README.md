# DocuLinkr

> **DocuLinkr**: A Python CLI tool to seamlessly link & manage Docusaurus documentation
> from multiple Git projects into one unified website.

![PyPI](https://img.shields.io/pypi/v/doculinkr)
![Python Versions](https://img.shields.io/pypi/pyversions/doculinkr)
![License](https://img.shields.io/pypi/l/doculinkr)

🔗 **Project home**: [https://github.com/FormuLearn/DocuLinkr](https://github.com/FormuLearn/DocuLinkr)

📖 **Live example**: [https://docs.formulearn.org](https://docs.formulearn.org)

**Note**: This project is still in very early development. If seeing this before approximately 5th June 2025 it's possible the live example will not yet be live. The system may also still be quite buggy. Any issues and pull requests to this Project's GitHub page are, of course, welcome!

---

## Overview

Many organizations maintain documentation in separate Git repositories. DocuLinkr automates the process of merging these scattered docs into a single Docusaurus site, while preserving each project’s individual history and structure.

Key capabilities:

* **Scaffold** a new Docusaurus site preconfigured for DocuLinkr (`init`).
* **Link** a subproject to a main DocuLinkr site via symlinks or copies (`link`).
* **Create** boilerplate docs for new subprojects (`startdocs`).
* **Merge** docs from either a main site or multiple subprojects (`merge`).
* **Serve** the documentation locally with live reloading (`serve`).

---

## Installation

Install the latest release from PyPI:

```bash
pip install doculinkr
```

Alternatively, install from source for development:

```bash
git clone https://github.com/FormuLearn/DocuLinkr.git
cd DocuLinkr
pip install -e .
```

DocuLinkr requires:

* Python 3.10 or newer
* Node.js & npm (for Docusaurus scaffolding and serving)

---

## Commands

All commands are available via the `doculinkr` entry point.

### `doculinkr init <site_name>`

Initialize a new Docusaurus site wired up for DocuLinkr:

```bash
doculinkr init my-docs-site [--template <template>] [--no-blog]
```

Options:

* `--template`: Docusaurus scaffold template (default: `classic`).
* `--no-blog`: Remove the default blog plugin and folder.

This command will:

1. Ensure you’re inside a Git repository.
2. Run `npx create-docusaurus <site_name> <template>`.
3. Optionally strip out the blog.
4. Render custom configuration (`docusaurus.config.js`), sidebars, homepage components, and `doculinkr.yaml`.
5. Seed an example project in `docs/ExampleProject/`.

### `doculinkr link --site <url_or_path>`

Link a subproject into an existing DocuLinkr main site for local preview:

```bash
doculinkr link --site https://github.com/org/main-docs.git [--copy]
```

Steps:

1. Verifies you’re in a Git repo root (not a main site).
2. Ensures `docs/` exists (prompts to create if missing).
3. Clones or pulls the upstream main site into `.doculinkr/main/`.
4. Renders and injects a `symlink-docs` plugin to map your `docs/` into the main site.
5. Symlinks (or copies, with `--copy`) your local `docs/` into the clone’s `docs/`.
6. Adds `.doculinkr/` to your `.gitignore`.

### `doculinkr startdocs -n <ProjectName>`

Scaffold a new subfolder under `docs/` for a project’s documentation:

```bash
doculinkr startdocs --proj-name MyProject
```

Result:

* Creates `docs/MyProject/` if missing.
* Adds `index.md` and `getting_started.md` from templates.

### `doculinkr merge [--site <url_or_path>]`

Merge mode varies by context:

* **Subproject mode** (`--site`):

  * Refreshes the local clone of the main site in `.doculinkr/main/`.
  * Re-injects the symlink-docs plugin (in case config changed).
  * Re-links `docs/` → `.doculinkr/main/docs/`.

* **Main-site mode** (no `--site`, invoked inside a main site):

  * Reads `doculinkr.yaml` to locate each project’s repo.
  * Clones each, grabs their `docs/`, and copies them into the main site.

### `doculinkr serve [--site-name <folder>] [--install]`

Launch a local Docusaurus development server:

```bash
# Serve a main site
doculinkr serve

# Serve a linked subproject (after `link`)
doculinkr serve --site-name MainSiteFolder [--install]
```

Options:

* `--install`: run `npm install` before starting.

Under the hood, it runs `npm run start` in the appropriate folder.

---

## Configuration (`doculinkr.yaml`)

When `init` or `link` generates `doculinkr.yaml`, it looks like:

```yaml
projects:
  - name: ExampleProject
    path: docs/ExampleProject
    git_path: https://github.com/YourOrg/ExampleProject.git
  - name: Another
    path: docs/Another
    git_path: ../AnotherRepo
```

In **main-site mode**, `merge` reads this to fetch each project’s docs.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

> *Built with ❤️ by Nicholas Roy, CTO at FormuLearn B.V.*
