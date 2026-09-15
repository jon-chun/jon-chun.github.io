# jon-chun.github.io

The source for Jon A. Chun's personal academic homepage: a static, five-page site
covering research, open-source software, teaching and biography.

It is plain HTML5, one CSS file and one small JavaScript file. There is no framework,
no build step and no package manifest. The only network dependencies are Google Fonts
and an optional live GitHub API call on the software page; the site is fully readable
with both blocked.

## Structure

```
index.html            Hero, research focus, current roles, featured software,
                      selected papers, news
research.html         Grants, publications, work under review, recognition, talks
software.html         Featured open-source projects and every public repository
teaching.html         Courses, student projects, impact metrics, program timeline
about.html            Biography, career, patents, honors, organizations, press,
                      writing, contact
404.html              Minimal not-found page
assets/css/style.css  The whole stylesheet, with light and dark themes
assets/js/main.js     Mobile nav toggle and the optional GitHub fetch
assets/img/           Images, all under 600 KB
favicon.svg           "JC" monogram
scripts/build_repos.py  Regenerates the repository list on software.html
.nojekyll             Tells GitHub Pages to serve these files as they are
robots.txt            Allows all crawlers, points at the sitemap
sitemap.xml           The five main pages
```

Every internal link and asset path is relative, so the site works unchanged whether it
is served from the domain root or from a subpath.

## Preview locally

```bash
python3 -m http.server 8000
```

Then open <http://127.0.0.1:8000/>. Serve it over HTTP rather than opening the files
directly, so that relative paths and the fetch call behave the way they will in
production.

## Deploy

**As a user site at `https://jon-chun.github.io/`:** the repository must be named
`jon-chun.github.io`. Push to `main` and GitHub Pages publishes it. In the repository
settings, under Pages, set the source to "Deploy from a branch" with branch `main` and
folder `/ (root)`.

**As a project site:** enable Pages the same way on this repository under its current
name. The site then lives at `https://jon-chun.github.io/<repository-name>/`. No file
changes are needed because all paths are relative, though the canonical, Open Graph and
sitemap URLs in the HTML assume the root domain and would want updating.

The `.nojekyll` file keeps GitHub Pages from running the files through Jekyll.

## Regenerate the repository list

The "All public repositories" section of `software.html` is static HTML generated from
the GitHub API. To refresh it:

```bash
python3 scripts/build_repos.py > /tmp/repos.html
```

Then replace everything between the `<!-- BEGIN all-repos -->` and
`<!-- END all-repos -->` markers in `software.html` with that output.

The script is standard-library only. It drops forks, archived repositories, empty
repositories and scaffolding (names starting with `test-`, `demo-`, `sample` or
`remote-test`, or containing `-copy`), then groups what remains into six themed
categories by keyword. Useful flags:

```bash
python3 scripts/build_repos.py --help
python3 scripts/build_repos.py --from-file repos.json   # work from a saved API dump
python3 scripts/build_repos.py --token "$GITHUB_TOKEN"  # raise the rate limit
```

Adjust the `CATEGORIES` list at the top of the script to change how repositories are
grouped.

## License

See [LICENSE](LICENSE).
