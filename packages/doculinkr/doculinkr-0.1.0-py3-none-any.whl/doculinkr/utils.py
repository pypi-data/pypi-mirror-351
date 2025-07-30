from jinja2 import Environment, PackageLoader
from pathlib import Path
import re
import subprocess
import click

def render_template(template_name: str, context: dict, output_path: Path):
    env = Environment(
        loader=PackageLoader('doculinkr', 'templates'),
        autoescape=False
    )
    template = env.get_template(template_name)
    rendered = template.render(**context)
    output_path.write_text(rendered, encoding='utf-8')


def inject_plugin_linewise(config_path: Path, plugin_path: str):
    """
    Injects `plugin_path` into the `plugins` array of a Docusaurus config,
    or adds a new `plugins: [ ... ],` block before the final `};`.
    """
    lines = config_path.read_text(encoding="utf-8").splitlines()
    out = []
    injected = False

    # Regex to detect single-line plugins array
    single_line_re = re.compile(r"^(\s*plugins\s*:\s*\[)(.*?)(\]\s*,?)\s*$")
    # Regex to detect start of multi-line plugins array
    multi_start_re = re.compile(r"^(\s*plugins\s*:\s*\[)\s*$")
    # Regex to detect end of object
    final_closing_re = re.compile(r"^(\s*)\}\s*;\s*$")

    i = 0
    while i < len(lines):
        line = lines[i]

        # 1) Single-line array: plugins: [ 'a', 'b' ],
        m1 = single_line_re.match(line)
        if m1:
            indent, inner, close = m1.groups()
            items = [item.strip().strip("'\"") for item in inner.split(",") if item.strip()]
            if plugin_path not in items:
                items.append(plugin_path)
                new_inner = ", ".join(f"'{itm}'" for itm in items)
                out.append(f"{indent}{new_inner}{close}")
            else:
                out.append(line)
            injected = True
            i += 1
            continue

        # 2) Multi-line array start
        m2 = multi_start_re.match(line)
        if m2:
            out.append(line)
            indent = m2.group(1)
            # scan until closing bracket of this array
            j = i + 1
            while j < len(lines):
                if re.match(r"^\s*\]\s*,?\s*$", lines[j]):
                    # insert plugin before this line
                    # infer indent (two spaces deeper than indent)
                    plug_indent = " " * (len(indent) + 2)
                    out.append(f"{plug_indent}'{plugin_path}',")
                    out.append(lines[j])
                    injected = True
                    i = j + 1
                    break
                else:
                    out.append(lines[j])
                    j += 1
            else:
                # no closing bracket found; fallback to plain
                i += 1
            continue

        # 3) Already done, just copy
        out.append(line)
        i += 1

    # 4) If we never injected, add a new plugins block before the final `};`
    if not injected:
        new_lines = []
        for line in out:
            m3 = final_closing_re.match(line)
            if m3:
                # Insert plugin line here
                indent = m3.group(1)
                new_lines.append(f"\tplugins: ['{plugin_path}'],")
                new_lines.append(line)
                injected = True
            else:
                new_lines.append(line)
        out = new_lines

    if not injected:
        raise RuntimeError("Failed to inject plugin into config")

    # Write back
    config_path.write_text("\n".join(out) + "\n", encoding="utf-8")

def _get_default_branch(clone_url: str) -> str:
    """
    Query the remote to find its default branch name.
    """
    cmd = ["git", "ls-remote", "--symref", clone_url, "HEAD"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    # Look for a line like: "ref: refs/heads/main\tHEAD"
    for line in proc.stdout.splitlines():
        if line.startswith("ref:"):
            # ref: refs/heads/main\tHEAD
            parts = line.split()
            ref = parts[1]           # e.g. "refs/heads/main"
            return ref.rsplit("/", 1)[-1]
    # Fallback
    return "master"

def _clone_project(console, repo_url: str, dest: Path):
    """
    Clone (or pull) a plain project repo into `dest`, shallow if remote.
    Prints exactly what URL and branch it’s using.
    """
    # Determine clone URL
    is_local = Path(repo_url).exists()
    clone_url = Path(repo_url).absolute().as_uri() if is_local else repo_url
    console.print(f"🎯 Using clone URL: [cyan]{clone_url}[/cyan]")

    # If already cloned, just pull
    if (dest / ".git").exists():
        console.print(f"🔄 Pulling latest in existing clone at {dest}…")
        try:
            # Show current branch
            current = subprocess.run(
                ["git", "-C", str(dest), "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, check=True
            ).stdout.strip()
            console.print(f"   on branch [bold]{current}[/bold]")
            subprocess.run(["git", "-C", str(dest), "pull"], check=True)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error:[/red] git pull failed: {e}")
            raise click.Abort()
        return

    # Otherwise, fresh shallow clone on default branch
    default_branch = _get_default_branch(repo_url)
    console.print(f"🔧 Cloning into {dest} …")
    cmd = ["git", "clone", "--depth", "1"]
    if default_branch:
        console.print(f"   ↪️  cloning branch [bold]{default_branch}[/bold]")
        cmd += ["-b", default_branch]
    else:
        console.print("   ↪️  cloning default HEAD")
    cmd += [clone_url, str(dest)]

    dest.parent.mkdir(parents=True, exist_ok=True)
    console.print(f"   ▶️  git {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error:[/red] git clone failed: {e}")
        raise click.Abort()

def _clone_or_pull(console, site: str, cache_root: Path) -> Path:
    """
    Clone the 'site' repo into cache_root (or pull updates if it exists),
    auto-detecting default branch and supporting shallow clones even for local repos.
    """
    is_local = Path(site).exists()
    clone_url = Path(site).absolute().as_uri() if is_local else site

    # 1) Determine default branch up front
    default_branch = _get_default_branch(clone_url)

    if not cache_root.exists():
        console.print(f"🔧 Cloning main site from {site} (branch={default_branch}) into {cache_root}…")
        subprocess.run([
            "git", "clone",
            "--depth", "1",
            "--branch", default_branch,
            clone_url,
            str(cache_root)
        ], check=True)
    else:
        console.print(f"🔄 Updating cached main site in {cache_root}…")
        # Fetch only that single branch, shallowly
        subprocess.run([
            "git", "-C", str(cache_root),
            "fetch",
            "--depth", "1",
            "origin",
            default_branch
        ], check=True)
        # Reset working tree onto the freshly fetched commit
        subprocess.run([
            "git", "-C", str(cache_root),
            "reset",
            "--hard",
            f"origin/{default_branch}"
        ], check=True)

    # 3) Detect nested project folder if needed
    site_root = cache_root
    if not (site_root / "package.json").exists():
        subs = [p for p in site_root.iterdir() if p.is_dir()]
        for subdir in subs:
            if (subdir / "package.json").exists() and (subdir / "docusaurus.config.js").exists():
                console.print(f"ℹ️  Detected nested site folder: {subdir.name}, adjusting root")
                site_root = subdir
                break
        else:
            console.print(
                "[red]Error:[/red] the main site at "
                f"{site} does not appear to be a valid Docusaurus project."
            )
            raise click.Abort()

    return site_root
