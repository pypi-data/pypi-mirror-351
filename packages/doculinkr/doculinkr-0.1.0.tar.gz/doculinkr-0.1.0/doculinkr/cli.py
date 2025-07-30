import subprocess
import shutil
from pathlib import Path
import os
import tempfile
import yaml

import click
from git import Repo, InvalidGitRepositoryError
from rich.console import Console

from doculinkr.utils import render_template, inject_plugin_linewise, _clone_project, _clone_or_pull

console = Console()

@click.group()
@click.version_option()
def cli():
    """
    DocuLinkr: A CLI to seamlessly link & manage Docusaurus documentation.
    """
    pass

@cli.command()
@click.argument("site_name")
@click.option(
    "--template", default="classic",
    help="Docusaurus template to use (default: classic)"
)
@click.option(
    "--no-blog", is_flag=True,
    help="Disable the default blog plugin and remove blog from config"
)
def init(site_name: str, template: str, no_blog: bool):
    """
    Initialize a new Docusaurus site wired up to DocuLinkr.
    """
    # 1. Ensure we're in a git repository
    try:
        Repo(Path.cwd())
    except InvalidGitRepositoryError:
        console.print("[red]Error:[/red] must run inside a git repository root")
        raise click.Abort()

    # 2. Ensure npm is installed
    if shutil.which("npm") is None:
        console.print(
            "[red]Error:[/red] npm not found—please install Node.js and npm first."
        )
        raise click.Abort()

    # 3. Scaffold Docusaurus using npx
    console.print(
        f"📦 Scaffolding Docusaurus site: [bold]{site_name}[/bold] "
        f"with template '{template}'..."
    )
    try:
        subprocess.run(
            ["npx", "create-docusaurus", site_name, template],
            check=True
        )
    except subprocess.CalledProcessError:
        console.print(
            "[red]Error:[/red] failed to run npx create-docusaurus"
        )
        raise click.Abort()

    project_dir = Path.cwd() / site_name

    # 4. Optionally remove blog folder
    if no_blog:
        blog_dir = project_dir / "blog"
        if blog_dir.exists():
            console.print("🗑️  Removing default blog folder...")
            shutil.rmtree(blog_dir)

    # 5. Clean default docs subfolders
    docs_dir = project_dir / "docs"
    for sub in ["tutorial-basics", "tutorial-extras"]:
        subdir = docs_dir / sub
        if subdir.exists():
            console.print(f"🗑️  Removing default docs folder: {sub}/")
            shutil.rmtree(subdir)

    # 6. Render docusaurus.config.js template
    config_tpl = (
        "no_blog_docusaurus_config.js.j2"
        if no_blog else "blog_docusaurus_config.js.j2"
    )
    out_config = project_dir / "docusaurus.config.js"
    console.print(
        f"🔧 Rendering {'no-blog' if no_blog else 'blog'} config → docusaurus.config.js"
    )
    render_template(
        config_tpl,
        {"site_name": site_name},
        out_config,
    )

    # 7. Render other default templates
    context = {"site_name": site_name}
    templates = [
        ("sidebars.js.j2", project_dir / "sidebars.js"),
        (
            "homepageFeatures.js.j2",
            project_dir / "src" / "components" / "HomepageFeatures" / "index.js",
        ),
        (
            "default_index.js.j2",
            project_dir / "src" / "pages" / "index.js",
        ),
        ("doculinkr.yaml.j2", project_dir / "doculinkr.yaml"),
    ]
    for tpl_name, out_path in templates:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        console.print(
            f"🔧 Rendering template {tpl_name} → "
            f"{out_path.relative_to(Path.cwd())}"
        )
        render_template(tpl_name, context, out_path)

    # 8. Create example docs scaffold
    console.print(
        f"📝 Initializing example docs in {docs_dir.relative_to(Path.cwd())}"
    )
    # remove default root markdown files
    for child in docs_dir.iterdir():
        if child.is_file():
            console.print(f"🗑️  Removing default doc: {child.name}")
            child.unlink()
    # scaffold ExampleProject
    example_dir = docs_dir / "ExampleProject"
    example_dir.mkdir(parents=True, exist_ok=True)
    render_template(
        "example_index.md.j2",
        {"project_name": "ExampleProject"},
        example_dir / "index.md",
    )
    render_template(
        "example_getting_started.md.j2",
        {"project_name": "ExampleProject"},
        example_dir / "getting_started.md",
    )

    console.print("[green]✔ DocuLinkr site initialized![/green]")

            
@cli.command()
@click.option("--site", required=True, help="Git URL or local path of the main DocuLinkr site")
@click.option("--copy", "use_copy", is_flag=True, help="Copy docs instead of symlinking in the clone")
def link(site: str, use_copy: bool):
    """
    Link this project repository to a DocuLinkr main site for local preview.
    """
    cwd = Path.cwd()
    # 1. Git‐repo check
    try:
        Repo(cwd)
    except InvalidGitRepositoryError:
        console.print("[red]Error:[/red] must run inside the root of a Git repository")
        raise click.Abort()

    # 2. Prevent linking a main site
    if (cwd / "docusaurus.config.js").exists() or (cwd / "doculinkr.yaml").exists():
        console.print("[red]Error:[/red] this looks like a main site; use init-project or init")
        raise click.Abort()

    # 3. Ensure docs/ exists
    docs_dir = cwd / "docs"
    if not docs_dir.exists():
        if click.confirm("No docs/ found. Create an empty docs/ folder?", default=True):
            docs_dir.mkdir()
            console.print("📝 Created docs/ folder")
        else:
            console.print("[red]Aborted:[/red] docs/ is required to link")
            raise click.Abort()

    # 4. Clone or pull the main site
    cache_root = cwd / ".doculinkr" / "main"
    cache_root.parent.mkdir(parents=True, exist_ok=True)
    site_root = _clone_or_pull(console, site, cache_root)

    # 5. Render symlink-docs plugin
    plugin_dir = site_root / "src" / "plugins" / "symlink-docs"
    plugin_dir.mkdir(parents=True, exist_ok=True)
    plugin_index = plugin_dir / "index.js"
    console.print(f"🔧 Rendering symlink-docs plugin → {plugin_index.relative_to(cwd)}")
    render_template("symlink-docs-plugin.js.j2", {}, plugin_index)

    # 6. Inject into docusaurus.config.js
    config_js = site_root / "docusaurus.config.js"
    plugin_entry = "./src/plugins/symlink-docs"
    console.print(f"🔧 Injecting plugin into {config_js.relative_to(cwd)}")
    try:
        inject_plugin_linewise(config_js, plugin_entry)
        console.print("[green]✔ Plugin injected![/green]")
    except Exception as e:
        console.print(f"[red]Warning:[/red] failed to inject plugin: {e}")
        console.print("Please add to your `plugins` array:", plugin_entry)

    # 7. Seed project docs if empty
    clone_docs = site_root / "docs"
    if any(clone_docs.iterdir()) and not any(docs_dir.iterdir()):
        console.print("📥 Seeding your docs/ from the main site examples…")
        for entry in clone_docs.iterdir():
            tgt = docs_dir / entry.name
            if entry.is_dir():
                shutil.copytree(entry, tgt)
            else:
                shutil.copy2(entry, tgt)

    # 8. Replace the clone’s docs/ with a symlink or copy
    console.print("🔄 Re-linking the main site's docs/ to your local docs/")
    shutil.rmtree(clone_docs)
    if use_copy:
        console.print("📋 Copying your docs/ into the clone…")
        shutil.copytree(str(docs_dir), str(clone_docs))
    else:
        console.print("🔗 Symlinking your docs/ → docs/")
        try:
            os.symlink(str(docs_dir), str(clone_docs))
        except OSError:
            console.print("[yellow]Warning:[/yellow] symlink failed, falling back to copy")
            shutil.copytree(str(docs_dir), str(clone_docs))

    # 9. Update .gitignore
    gitignore = cwd / ".gitignore"
    ignore_line = ".doculinkr/"
    if gitignore.exists():
        lines = gitignore.read_text().splitlines()
        if ignore_line not in lines:
            lines.append(ignore_line)
            gitignore.write_text("\n".join(lines) + "\n")
            console.print("📝 Added .doculinkr/ to .gitignore")
    else:
        gitignore.write_text(ignore_line + "\n")
        console.print("📝 Created .gitignore and added .doculinkr/ to it")

    console.print("[green]✔ Linked to main site! Run `doculinkr serve` to preview.[/green]")

@cli.command()
@click.option(
    "--proj-name", "-n",
    required=True,
    help="Name of the project (used for folder name and front-matter)"
)
def startdocs(proj_name: str):
    """
    Scaffold a docs/<ProjectName>/ folder with index.md and getting_started.md.
    """
    cwd = Path.cwd()

    # 1. Ensure docs/ exists (create it if not)
    docs_root = cwd / "docs"
    if not docs_root.exists():
        docs_root.mkdir()
        console.print("📝 Created docs/ folder")
    else:
        console.print("📝 Found existing docs/ folder")

    # 2. Create project subfolder
    folder = docs_root / proj_name
    if folder.exists():
        console.print(f"[yellow]Warning:[/yellow] docs/{proj_name}/ already exists—skipping")
    else:
        folder.mkdir()
        console.print(f"🗂  Created docs/{proj_name}/")

    # 3. Render templates
    ctx = {"project_name": proj_name}
    templates = [
        ("example_index.md.j2", folder / "index.md"),
        ("example_getting_started.md.j2", folder / "getting_started.md"),
    ]
    for tpl_name, out_path in templates:
        if out_path.exists():
            console.print(f"[yellow]Skipping existing {out_path.relative_to(cwd)}[/yellow]")
        else:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            console.print(f"🔧 Rendering {tpl_name} → {out_path.relative_to(cwd)}")
            render_template(tpl_name, ctx, out_path)

    console.print("[green]✔ Docs scaffolded under docs/{proj_name}![/green]")

@cli.command()
@click.option("--site", help="(subproject mode) Git URL or local path of the main DocuLinkr site")
def merge(site: str = None):
    """
    If run in a sub-project (`--site`), refresh .doculinkr/main:
      • reclone/pull into .doculinkr/main
      • re-inject symlink-docs plugin
      • re-link docs/ → .doculinkr/main/docs/
    If run in a main site (no --site), pull docs from each project in doculinkr.yaml.
    """
    # 1) Find Git repo root
    try:
        repo = Repo(Path.cwd(), search_parent_directories=True)
    except InvalidGitRepositoryError:
        console.print("[red]Error:[/red] must run inside a Git repository")
        raise click.Abort()
    root = Path(repo.working_tree_dir)

    # 2) Decide mode
    if site:
        mode = "sub"
    else:
        mains = [
            p for p in [root] + list(root.iterdir())
            if p.is_dir() and (p/"docusaurus.config.js").exists() and (p/"doculinkr.yaml").exists()
        ]
        mode = "main" if len(mains) == 1 else "sub"

    # 3) Execute merge
    if mode == "sub":
        console.print("🔄 Subproject merge: updating .doculinkr/main/…")
        cwd = root
        cache = cwd / ".doculinkr" / "main"
        cache.parent.mkdir(parents=True, exist_ok=True)

        # reclone/pull main site
        site_root = _clone_or_pull(console, site, cache)

        # inject plugin if config changed
        cfg_js = site_root / "docusaurus.config.js"
        plugin_entry = "./src/plugins/symlink-docs"
        try:
            inject_plugin_linewise(cfg_js, plugin_entry)
        except Exception as e:
            console.print(f"[yellow]Warn:[/yellow] plugin injection failed: {e}")

        # re-link docs
        console.print("🔄 Re-linking docs/ → .doculinkr/main/docs/")
        shutil.rmtree(site_root / "docs", ignore_errors=True)
        docs_dir = cwd / "docs"
        if not docs_dir.exists():
            console.print("[red]Error:[/red] docs/ missing in project root")
            raise click.Abort()
        os.symlink(str(docs_dir), str(site_root / "docs"))

        console.print("[green]✔ .doculinkr/main refreshed[/green]")

    else:
        # main-site mode
        main_root = [
            p for p in [root] + list(root.iterdir())
            if p.is_dir() and (p/"docusaurus.config.js").exists() and (p/"doculinkr.yaml").exists()
        ][0]
        console.print(f"🔄 Main-site merge: importing docs under {main_root.relative_to(root)}/…")
        cwd = main_root
        data = yaml.safe_load((cwd/"doculinkr.yaml").read_text(encoding="utf-8"))

        for proj in data.get("projects", []):
            name = proj["name"]
            target = cwd / proj["path"]
            git_path = proj.get("git_path")
            if not git_path:
                console.print(f"[yellow]Skipping {name}: no git_path[/yellow]")
                continue

            console.print(f"🔧 Pulling docs for {name}…")
            with tempfile.TemporaryDirectory(prefix=f"doculinkr-{name}-") as td:
                tmp_path = Path(td)
                # clone the entire project into tmp_path
                _clone_project(console, git_path, tmp_path)

                # locate the docs folder inside that clone
                candidate = tmp_path / "docs" / name
                if candidate.exists() and candidate.is_dir():
                    src_docs = candidate
                else:
                    # fallback: maybe docs/ holds the files directly
                    src_docs = tmp_path / "docs"

                if not src_docs.exists():
                    console.print(f"[yellow]Warning:[/yellow] {name} has no docs/")
                    continue

                # overwrite existing target
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(src_docs, target)

        console.print("[green]✔ Main-site docs merged![/green]")

@cli.command()
@click.option("--site-name", help="(subproject mode) name of the main Docusaurus project folder", required=False)
@click.option("--install", "do_install", is_flag=True, help="Install npm dependencies before starting")
def serve(site_name: str, do_install: bool):
    """
    Serve either the linked main site for this project (subproject mode),
    or the main site itself if this is a main-site repo.
    """
    # 1) Locate the Git repo root
    try:
        repo = Repo(Path.cwd(), search_parent_directories=True)
    except InvalidGitRepositoryError:
        console.print("[red]Error:[/red] must run inside a Git repository")
        raise click.Abort()
    root = Path(repo.working_tree_dir)

    # 2) Detect main-site under root or one level down
    main_candidates = []
    if (root / "docusaurus.config.js").exists() and (root / "doculinkr.yaml").exists():
        main_candidates.append(root)
    for sub in root.iterdir():
        if not sub.is_dir():
            continue
        if (sub / "docusaurus.config.js").exists() and (sub / "doculinkr.yaml").exists():
            main_candidates.append(sub)

    if main_candidates and not site_name:
        # main-site mode
        main_root = main_candidates[0]  # if multiple, picks first
        console.print(f"ℹ️  Serving main site at: {main_root.relative_to(root)}")
        serve_root = main_root
    else:
        # subproject mode
        if not site_name:
            console.print("[red]Error:[/red] subproject serve requires --site-name")
            raise click.Abort()
        serve_root = root / ".doculinkr" / "main" / site_name
        if not serve_root.exists():
            console.print("[red]Error:[/red] no linked main site found at "
                          f"{serve_root}. Run `doculinkr link` first.")
            raise click.Abort()

        console.print(f"ℹ️  Serving linked site at: {serve_root.relative_to(root)}")

    # 3) Ensure npm is installed
    if shutil.which("npm") is None:
        console.print("[yellow]npm not found.[/yellow]")
        if click.confirm("Would you like to install Node.js/npm now?", default=False):
            console.print("Please install Node.js/npm manually; automatic install not implemented.")
        raise click.Abort()

    # 4) Install deps if needed
    if do_install or not (serve_root / "node_modules").exists():
        console.print("📦 Installing npm dependencies...")
        subprocess.run(["npm", "install"], cwd=serve_root, check=True)

    # 5) Start dev server
    console.print("🚀 Starting Docusaurus dev server...")
    subprocess.run(["npm", "run", "start"], cwd=serve_root)

if __name__ == '__main__':
    cli()
