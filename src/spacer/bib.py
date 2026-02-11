import re
import time
import click
import requests
import xml.etree.ElementTree as ET

S2_SEARCH = "https://api.semanticscholar.org/graph/v1/paper/search"
S2_PAPER = "https://api.semanticscholar.org/graph/v1/paper"
CROSSREF = "https://api.crossref.org/works"
ARXIV_API = "http://export.arxiv.org/api/query"

HEADERS = {"User-Agent": "spacer-cli/0.1"}

def _s2_get(url, params, timeout=15):
    """GET with retry on 429."""
    for attempt in range(3):
        r = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
        if r.status_code == 429:
            wait = 2 ** attempt
            click.echo(f"  (rate limited, retrying in {wait}s...)", err=True)
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r
    r.raise_for_status()
    return r

def _s2_fields():
    return "title,authors,year,venue,externalIds,citationCount"

def _make_bibtex(paper, key=None):
    """Construct bibtex from Semantic Scholar paper dict."""
    authors = " and ".join(a.get("name", "") for a in paper.get("authors", []))
    title = paper.get("title", "")
    year = paper.get("year", "")
    venue = paper.get("venue", "")
    eids = paper.get("externalIds") or {}
    doi = eids.get("DOI", "")

    if not key:
        first_author = paper.get("authors", [{}])[0].get("name", "unknown").split()[-1].lower()
        key = f"{first_author}{year}"

    lines = [f"@article{{{key},"]
    lines.append(f"  title = {{{title}}},")
    lines.append(f"  author = {{{authors}}},")
    lines.append(f"  year = {{{year}}},")
    if venue:
        lines.append(f"  journal = {{{venue}}},")
    if doi:
        lines.append(f"  doi = {{{doi}}},")
    lines.append("}")
    return "\n".join(lines)


@click.group()
def bib_group():
    """Bibliography tools — search, fetch, verify."""
    pass


@bib_group.command("search")
@click.argument("query")
@click.option("--limit", default=10, help="Number of results")
def search(query, limit):
    """Search Semantic Scholar for papers."""
    r = _s2_get(S2_SEARCH, params={"query": query, "limit": limit, "fields": _s2_fields()})
    r.raise_for_status()
    data = r.json().get("data", [])
    if not data:
        click.echo("No results found.")
        return
    for i, p in enumerate(data, 1):
        authors = ", ".join(a["name"] for a in p.get("authors", [])[:3])
        if len(p.get("authors", [])) > 3:
            authors += " et al."
        cite = p.get("citationCount", 0)
        click.echo(f"\n[{i}] {p.get('title', '?')} ({p.get('year', '?')})")
        click.echo(f"    {authors}")
        click.echo(f"    {p.get('venue', '')}  |  citations: {cite}")
        eids = p.get("externalIds") or {}
        if eids.get("DOI"):
            click.echo(f"    doi: {eids['DOI']}")
        if eids.get("ArXiv"):
            click.echo(f"    arxiv: {eids['ArXiv']}")


@bib_group.command("get")
@click.option("--doi", default=None, help="Fetch by DOI")
@click.option("--arxiv", default=None, help="Fetch by arXiv ID")
@click.option("--title", default=None, help="Fetch by exact title search")
def get(doi, arxiv, title):
    """Fetch a bibtex entry."""
    if doi:
        _get_by_doi(doi)
    elif arxiv:
        _get_by_arxiv(arxiv)
    elif title:
        _get_by_title(title)
    else:
        click.echo("Provide --doi, --arxiv, or --title")


def _get_by_doi(doi):
    r = requests.get(f"{CROSSREF}/{doi}", headers=HEADERS, timeout=15)
    r.raise_for_status()
    msg = r.json()["message"]
    authors = " and ".join(
        f"{a.get('family', '')}, {a.get('given', '')}" for a in msg.get("author", [])
    )
    title = " ".join(msg.get("title", [""]))
    year = ""
    for dp in ["published-print", "published-online", "created"]:
        if dp in msg and "date-parts" in msg[dp]:
            year = str(msg[dp]["date-parts"][0][0])
            break
    venue = " ".join(msg.get("container-title", [""]))
    first_author = msg.get("author", [{}])[0].get("family", "unknown").lower()
    key = f"{first_author}{year}"

    bib = f"@article{{{key},\n"
    bib += f"  title = {{{title}}},\n"
    bib += f"  author = {{{authors}}},\n"
    bib += f"  year = {{{year}}},\n"
    bib += f"  journal = {{{venue}}},\n"
    bib += f"  doi = {{{doi}}},\n"
    bib += "}"
    click.echo(bib)


def _get_by_arxiv(arxiv_id):
    r = requests.get(ARXIV_API, params={"id_list": arxiv_id}, headers=HEADERS, timeout=15)
    r.raise_for_status()
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(r.text)
    entry = root.find("a:entry", ns)
    if entry is None:
        click.echo("Not found.")
        return
    title = entry.findtext("a:title", "", ns).strip().replace("\n", " ")
    authors = " and ".join(a.findtext("a:name", "", ns) for a in entry.findall("a:author", ns))
    published = entry.findtext("a:published", "", ns)
    year = published[:4] if published else ""
    first_author = entry.find("a:author", ns).findtext("a:name", "unknown", ns).split()[-1].lower()
    key = f"{first_author}{year}"

    bib = f"@article{{{key},\n"
    bib += f"  title = {{{title}}},\n"
    bib += f"  author = {{{authors}}},\n"
    bib += f"  year = {{{year}}},\n"
    bib += f"  eprint = {{{arxiv_id}}},\n"
    bib += f"  archivePrefix = {{arXiv}},\n"
    bib += "}"
    click.echo(bib)


def _get_by_title(title):
    r = _s2_get(S2_SEARCH, params={"query": title, "limit": 1, "fields": _s2_fields()})
    r.raise_for_status()
    data = r.json().get("data", [])
    if not data:
        click.echo("No results found.")
        return
    click.echo(_make_bibtex(data[0]))


@bib_group.command("verify")
@click.argument("bibfile", type=click.Path(exists=True))
def verify(bibfile):
    """Verify entries in a .bib file against Semantic Scholar."""
    with open(bibfile) as f:
        content = f.read()

    entries = re.findall(r'@\w+\{([^,]+),.*?title\s*=\s*\{([^}]+)\}', content, re.DOTALL)
    if not entries:
        click.echo("No entries found in bib file.")
        return

    for key, title in entries:
        title_clean = re.sub(r'\s+', ' ', title.strip())
        try:
            r = _s2_get(S2_SEARCH, params={"query": title_clean, "limit": 1, "fields": "title,year"})
            r.raise_for_status()
            data = r.json().get("data", [])
            if data and data[0].get("title", "").lower().strip() == title_clean.lower().strip():
                click.echo(f"  ✓ {key}: verified")
            elif data:
                click.echo(f"  ? {key}: closest match: \"{data[0].get('title', '')}\"")
            else:
                click.echo(f"  ✗ {key}: not found")
        except Exception as e:
            click.echo(f"  ! {key}: error — {e}")
