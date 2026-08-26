"""ATS adapters. Each returns a list of normalized job dicts.

Normalized shape:
    {company, title, location, url, description, job_id, posted}

Stdlib only on purpose: this runs unattended from cron, so it must not
depend on a virtualenv that can silently rot.
"""
import html as _html
import http.client
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " \
     "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
TIMEOUT = 30


class _Strip(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out = []

    def handle_data(self, d):
        self.out.append(d)


def strip_html(s):
    """Job descriptions arrive as HTML blobs; the scorer wants prose."""
    if not s:
        return ""
    # Greenhouse double-encodes: its `content` is escaped HTML, so unescaping
    # once turns &lt;div&gt; into a literal <div> that still needs stripping.
    if "&lt;" in s:
        s = _html.unescape(s)
    s = re.sub(r"<(br|/p|/li|/div|/h[1-6])\s*/?>", "\n", s, flags=re.I)
    p = _Strip()
    try:
        p.feed(s)
    except Exception:
        return re.sub(r"<[^>]+>", " ", s)
    txt = "".join(p.out)
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r"\n\s*\n+", "\n\n", txt)
    return txt.strip()


def _get(url, data=None, headers=None):
    hdrs = {"User-Agent": UA, "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=hdrs)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def _get_retry(url, headers=None, tries=4, base_wait=3):
    """_get with backoff for rate-limited endpoints.

    The Eightfold pcsx API returns 429 under load -- easy to trigger, since a
    sweep there is ~80 requests (its `num` cap is 10). 4xx other than 429 are
    not retried: they mean the request is wrong, not early.
    """
    for attempt in range(tries):
        try:
            return _get(url, headers=headers)
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt == tries - 1:
                raise
            time.sleep(base_wait * (attempt + 1))
        except (urllib.error.URLError, TimeoutError, http.client.IncompleteRead):
            # IncompleteRead: a chunked response truncated mid-stream. Seen
            # intermittently on large (~1MB) JSON bodies -- transient, and a
            # retry or a smaller page usually gets it.
            if attempt == tries - 1:
                raise
            time.sleep(base_wait * (attempt + 1))


# --- attribution ----------------------------------------------------------
# Where each kind's data comes from, so runs can credit their sources. The
# descriptions themselves are written by, and remain the property of, the
# employer that posted them -- this names the platform the data was read
# through, which is what the platforms ask for.

ATTRIBUTION = {
    # First-party applicant tracking systems. The employer publishes here; the
    # platform is the pipe, and the posting is the employer's.
    "greenhouse":      ("Greenhouse", "https://www.greenhouse.io"),
    "lever":           ("Lever", "https://www.lever.co"),
    "ashby":           ("Ashby", "https://www.ashbyhq.com"),
    "smartrecruiters": ("SmartRecruiters", "https://www.smartrecruiters.com"),
    "workday":         ("Workday", "https://www.workday.com"),
    "phenom":          ("Phenom", "https://www.phenom.com"),
    "radancy":         ("Radancy / TalentBrew", "https://www.radancy.com"),
    "pageup":          ("PageUp", "https://www.pageuppeople.com"),
    "eightfold":       ("Eightfold", "https://eightfold.ai"),
    "paradox":         ("Paradox", "https://www.paradox.ai"),
    "clearcompany":    ("ClearCompany", "https://www.clearcompany.com"),
    # Aggregators, which index many employers.
    "themuse":         ("The Muse", "https://www.themuse.com"),
    "himalayas":       ("Himalayas", "https://himalayas.app"),
}

# Credit lines a source explicitly asks for. Himalayas' API docs request a
# visible link back and a statement of where the data came from; verified
# 2026-08-24. Nothing else shipped here documents such a requirement -- do not
# invent one, and re-check before assuming.
REQUIRED_CREDIT = {
    "himalayas": "Job data sourced from Himalayas (https://himalayas.app).",
}


# --- adapters -------------------------------------------------------------

def greenhouse(cfg):
    tok = cfg["token"]
    d = _get(f"https://boards-api.greenhouse.io/v1/boards/{tok}/jobs?content=true")
    out = []
    for j in d.get("jobs", []):
        out.append({
            "company": cfg["company"],
            "title": j.get("title", ""),
            "location": (j.get("location") or {}).get("name", ""),
            "url": j.get("absolute_url", ""),
            "description": strip_html(j.get("content", "")),
            "job_id": f"gh:{tok}:{j.get('id')}",
            "posted": j.get("updated_at", ""),
        })
    return out


def lever(cfg):
    tok = cfg["token"]
    d = _get(f"https://api.lever.co/v0/postings/{tok}?mode=json")
    out = []
    for j in d:
        cat = j.get("categories") or {}
        out.append({
            "company": cfg["company"],
            "title": j.get("text", ""),
            "location": cat.get("location", ""),
            "url": j.get("hostedUrl", ""),
            "description": strip_html(j.get("descriptionPlain") or j.get("description", "")),
            "job_id": f"lv:{tok}:{j.get('id')}",
            "posted": str(j.get("createdAt", "")),
        })
    return out


def ashby(cfg):
    tok = cfg["token"]
    d = _get(f"https://api.ashbyhq.com/posting-api/job-board/{tok}?includeCompensation=true")
    out = []
    for j in d.get("jobs", []):
        out.append({
            "company": cfg["company"],
            "title": j.get("title", ""),
            "location": j.get("location", ""),
            "url": j.get("jobUrl", ""),
            "description": strip_html(j.get("descriptionHtml") or j.get("descriptionPlain", "")),
            "job_id": f"ab:{tok}:{j.get('id')}",
            "posted": j.get("publishedAt", ""),
        })
    return out


def smartrecruiters(cfg):
    tok = cfg["token"]
    out = []
    offset = 0
    while True:
        d = _get(f"https://api.smartrecruiters.com/v1/companies/{tok}/postings"
                 f"?limit=100&offset={offset}")
        items = d.get("content", [])
        for j in items:
            loc = j.get("location") or {}
            out.append({
                "company": cfg["company"],
                "title": j.get("name", ""),
                "location": ", ".join(x for x in [loc.get("city"), loc.get("country")] if x),
                "url": f"https://jobs.smartrecruiters.com/{tok}/{j.get('id')}",
                "description": "",  # detail endpoint needed; filled lazily
                "job_id": f"sr:{tok}:{j.get('id')}",
                "posted": j.get("releasedDate", ""),
            })
        offset += len(items)
        if not items or offset >= d.get("totalFound", 0):
            break
    return out


def workday(cfg):
    """Workday's own frontend POSTs to this endpoint. tenant+site come from
    the careers URL: https://{tenant}.wd{N}.myworkdayjobs.com/{site}

    `total` IS ONLY REPORTED ON THE FIRST PAGE -- later pages return 0 for it.
    Hence `total` is captured once and never overwritten below. Recomputing it
    each page looks tidier and silently truncates a 700-role board to 40; that
    happened, and this comment exists so it does not happen twice.
    """
    tenant, wd, site = cfg["tenant"], cfg.get("wd", "wd1"), cfg["site"]
    host = f"https://{tenant}.{wd}.myworkdayjobs.com"
    api = f"{host}/wday/cxs/{tenant}/{site}/jobs"
    out = []
    offset = 0
    total = None
    while offset < cfg.get("max", 500):
        d = _get(api, data={"appliedFacets": {}, "limit": 20,
                            "offset": offset, "searchText": cfg.get("q", "")},
                 headers={"Referer": f"{host}/{site}"})
        posts = d.get("jobPostings", [])
        # Workday reports `total` on the first page only; later pages say 0.
        if total is None:
            total = d.get("total", 0)
        for j in posts:
            path = j.get("externalPath", "")
            out.append({
                "company": cfg["company"],
                "title": j.get("title", ""),
                "location": j.get("locationsText", ""),
                "url": f"{host}/{site}{path}",
                "description": "",  # detail endpoint needed; filled lazily
                "job_id": f"wd:{tenant}:{path}",
                "posted": j.get("postedOn", ""),
            })
        offset += len(posts)
        if not posts or offset >= total:
            break
    return out


def phenom(cfg):
    """Phenom-style: an `/api/jobs` feed with descriptions inline."""
    base = cfg["base"].rstrip("/")
    out, page, limit = [], 1, 100
    while len(out) < cfg.get("max", 1500):
        d = _get(f"{base}/api/jobs?page={page}&limit={limit}",
                 headers={"Referer": base + "/"})
        rows = d.get("jobs", [])
        for r in rows:
            j = r.get("data", {})
            loc = ", ".join(x for x in [j.get("city"), j.get("state")] if x)
            out.append({
                "company": cfg["company"],
                "title": j.get("title", ""),
                "location": loc or j.get("location_name", ""),
                "url": j.get("apply_url", ""),
                "description": strip_html(j.get("description", "")),
                "job_id": f"ph:{cfg['company']}:{j.get('req_id')}",
                "posted": j.get("create_date", ""),
            })
        page += 1
        if not rows or len(out) >= d.get("totalCount", 0):
            break
        time.sleep(0.3)
    return out


_RADANCY_HREF = re.compile(r'href="(/job/[^"]+)"')
_RADANCY_H2 = re.compile(r'<h2>(.*?)</h2>', re.S)
_RADANCY_LOC = re.compile(r'class="job-location">(?:<img[^>]*>)?(.*?)</span>', re.S)


def radancy(cfg):
    """Radancy/TalentBrew search. Returns JSON wrapping an HTML
    result list, so the listing is parsed out of markup rather than a feed."""
    base = cfg["base"].rstrip("/")
    q = ("ActiveFacetID=0&CurrentPage={p}&RecordsPerPage=100&Distance=50"
         "&RadiusUnitType=0&Keywords=&Location=&ShowRadius=False&IsPagination=True"
         "&CustomFacetName=&FacetTerm=&FacetType=0"
         "&SearchResultsModuleName=Search+Results&SearchFiltersModuleName=Search+Filters"
         "&SortCriteria=0&SortDirection=0&SearchType=5&PostalCode=&fc=&fl=&fcf=&afc=&afl=&afcf=")
    out, page = [], 1
    seen = set()
    while len(out) < cfg.get("max", 800):
        d = _get(f"{base}/search-jobs/results?" + q.format(p=page),
                 headers={"Referer": f"{base}/search-jobs"})
        htm = d.get("results", "")
        if not htm.strip():
            break
        # Markup varies between TalentBrew tenants (sr-job-link vs sr-item), so
        # parse per <li> block rather than matching one anchor shape.
        before = len(out)
        for block in htm.split("<li")[1:]:
            href = _RADANCY_HREF.search(block)
            h2 = _RADANCY_H2.search(block)
            if not href or not h2:
                continue
            path = _html.unescape(href.group(1))
            if path in seen:
                continue
            seen.add(path)
            loc = _RADANCY_LOC.search(block)
            out.append({
                "company": cfg["company"],
                "title": strip_html(h2.group(1)),
                "location": strip_html(loc.group(1)) if loc else "",
                "url": base + path,
                "description": "",  # detail page needed; hydrated lazily
                "job_id": f"rd:{cfg['company']}:{path.rsplit('/', 1)[-1]}",
                "posted": "",
            })
        if len(out) == before:
            break
        page += 1
        time.sleep(0.3)
    return out


_PAGEUP_ROW = re.compile(
    r'<a class="job-link" href="([^"]+)">(.*?)</a>.*?<span class="location">(.*?)</span>'
    r'(?:.*?<tr class="summary">\s*<td[^>]*>(.*?)</td>)?', re.S)


def pageup(cfg):
    """University/CSU-style PageUp board: a plain HTML results table."""
    base = cfg["base"].rstrip("/")
    req = urllib.request.Request(f"{base}/cw/en-us/listing/",
                                 headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        page = r.read().decode("utf-8", "replace")
    out = []
    for path, title, loc, summary in _PAGEUP_ROW.findall(page):
        out.append({
            "company": cfg["company"],
            "title": strip_html(title),
            "location": strip_html(loc),
            "url": base + _html.unescape(path),
            "description": strip_html(summary or ""),
            "job_id": f"pu:{cfg['company']}:{path.split('/')[4] if len(path.split('/')) > 4 else path}",
            "posted": "",
        })
    return out


def eightfold(cfg):
    """Eightfold-hosted career sites.

    The endpoint the *frontend* calls, /api/apply/v2/jobs, returns
    `{"message": "Not authorized for PCSX"}` in its list form without a
    session, which is what makes these portals look unreachable. But the
    sites' own robots.txt typically allows /api/pcsx, and
    /api/pcsx/search answers unauthenticated. Descriptions come from
    /api/pcsx/position_details, one request per job.

    Two constraints shape the config:
      * `num` is capped server-side at 10 regardless of what you ask for, so
        a full sweep is one request per ten roles. Filter, don't enumerate.
      * `location` is radius-based and NOT repeatable -- passing it twice
        keeps one value. Santa Clara, San Jose, Sunnyvale and San Francisco
        all return the same Bay Area bucket, so list one city per region, not
        one per office.
    """
    base = cfg["base"].rstrip("/")
    domain = cfg["domain"]
    ref = f"{base}/careers"
    out, seen = [], set()
    for loc in cfg.get("locations", [""]):
        start, cap = 0, cfg.get("max_per_location", 400)
        while start < cap:
            q = {"domain": domain, "start": start, "num": 10}
            if loc:
                q["location"] = loc
            d = _get_retry(f"{base}/api/pcsx/search?" + urllib.parse.urlencode(q),
                           headers={"Referer": ref})
            data = d.get("data") or {}
            rows = data.get("positions") or []
            for p in rows:
                pid = p.get("id")
                if pid in seen:
                    continue
                seen.add(pid)
                out.append({
                    "company": cfg["company"],
                    "title": p.get("name", ""),
                    "location": "; ".join(p.get("locations") or []),
                    "url": f"{base}/careers/job/{pid}",
                    "description": "",  # position_details needed; hydrated lazily
                    "job_id": f"ef:{domain}:{pid}",
                    "posted": p.get("postedTs", ""),
                })
            start += len(rows)
            if not rows or start >= data.get("count", 0):
                break
            time.sleep(0.5)
    return out


def paradox(cfg):
    """Paradox.ai careersites.

    Not a bespoke JS portal: each /jobs page is server-rendered with the whole
    result set in a window.__PRELOAD_STATE__ blob, so no browser is needed and
    no bot-detection fires. Plain GETs with a normal User-Agent suffice.

    List rows carry no description -- the detail page does, in a
    .job-description-content container. Boards are paginated ten to a page,
    so a full sweep of a few hundred roles is cheap.
    """
    base = cfg["base"].rstrip("/")
    out, seen = [], set()
    page, cap = 1, cfg.get("max", 400)
    while len(out) < cap:
        url = f"{base}/jobs" if page == 1 else f"{base}/jobs/page/{page}"
        d = _preload_state(url)
        js = (d or {}).get("jobSearch") or {}
        rows = js.get("jobs") or []
        for j in rows:
            uid = j.get("uniqueID")
            if uid in seen:
                continue
            seen.add(uid)
            locs = j.get("locations") or []
            loc = ""
            if locs:
                l0 = locs[0]
                loc = ", ".join(x for x in [l0.get("city"), l0.get("stateAbbr")] if x)
            if j.get("isRemote"):
                loc = (loc + "; Remote").lstrip("; ")
            out.append({
                "company": cfg["company"],
                "title": j.get("title", ""),
                "location": loc,
                "url": f"{base}/{j.get('originalURL', '')}",
                "description": "",  # detail page needed; hydrated lazily
                "job_id": f"px:{cfg['company']}:{uid}",
                "posted": "",
            })
        page += 1
        if not rows or len(seen) >= js.get("totalJob", 0):
            break
        time.sleep(0.3)
    return out


def _preload_state(url):
    """Paradox pages embed their data as `window.__PRELOAD_STATE__ = {...}`.
    The blob is not terminated predictably, so decode from the opening brace
    with raw_decode rather than trying to regex the closing one."""
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "identity",
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        page = r.read().decode("utf-8", "replace")
    i = page.find("window.__PRELOAD_STATE__")
    if i < 0:
        return None
    return json.JSONDecoder().raw_decode(page[page.find("{", i):])[0]


ADAPTERS = {
    "greenhouse": greenhouse,
    "lever": lever,
    "ashby": ashby,
    "smartrecruiters": smartrecruiters,
    "workday": workday,
    "phenom": phenom,
    "radancy": radancy,
    "pageup": pageup,
    "eightfold": eightfold,
    "paradox": paradox,
}


# --- lazy description backfill -------------------------------------------
# Workday and SmartRecruiters list endpoints omit the description. Fetching
# it per job is one request each, so we only do it for jobs that already
# survived the prescreen -- a few dozen, not a few thousand.

def _hydrate_workday(job):
    """Fetch the description -- and, for free, the REAL locations.

    Workday's list endpoint reports multi-site postings as a bare count
    ("2 Locations"), which location_ok() keeps at step 1 because dropping
    them would lose genuine in-region roles. The detail page we are already
    fetching here carries `location` plus `additionalLocations`, so we
    overwrite the vague string with the concrete list. jobscan.py re-checks
    the region filter after hydration; this is what makes that possible at
    no extra request cost.
    """
    _, tenant, path = job["job_id"].split(":", 2)
    host = re.match(r"https://[^/]+", job["url"]).group(0)
    site = job["url"][len(host) + 1:].split("/")[0]
    d = _get(f"{host}/wday/cxs/{tenant}/{site}{path}",
             headers={"Referer": job["url"]})
    info = d.get("jobPostingInfo", {}) or {}
    places = [info.get("location") or ""] + list(info.get("additionalLocations") or [])
    places = [p for p in places if p]
    if places:
        job["location"] = "; ".join(places)
    return strip_html(info.get("jobDescription", ""))


def _hydrate_smartrecruiters(job):
    _, tok, jid = job["job_id"].split(":", 2)
    d = _get(f"https://api.smartrecruiters.com/v1/companies/{tok}/postings/{jid}")
    ad = (d.get("jobAd") or {}).get("sections") or {}
    parts = [(ad.get(k) or {}).get("text", "")
             for k in ("companyDescription", "jobDescription", "qualifications")]
    return strip_html("\n\n".join(p for p in parts if p))


def _hydrate_radancy(job):
    req = urllib.request.Request(job["url"], headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        page = r.read().decode("utf-8", "replace")
    # TalentBrew puts the ATS-supplied text in .ats-description; some tenants
    # only have the outer .job-description section.
    for marker in ('ats-description', 'class="job-description'):
        i = page.find(marker)
        if i > 0:
            i = page.find('>', i) + 1  # start after the tag, not mid-attribute
            txt = strip_html(page[i:i + 20000])
            if len(txt) > 400:
                return txt[:6000]
    return strip_html(page)[:6000]


def _hydrate_eightfold(job):
    """/api/pcsx/position_details carries the full text. Note the sibling
    /api/apply/v2/jobs/{pid} works too, but its *list* form 403s, so prefer
    the pcsx route that robots.txt actually advertises."""
    _, domain, pid = job["job_id"].split(":", 2)
    host = re.match(r"https://[^/]+", job["url"]).group(0)
    d = _get_retry(f"{host}/api/pcsx/position_details?"
                   + urllib.parse.urlencode({"domain": domain, "position_id": pid}),
                   headers={"Referer": job["url"]})
    return strip_html((d.get("data") or {}).get("jobDescription", ""))


_PARADOX_DESC = 'class="job-description-grid job-description-content"'


def _hydrate_paradox(job):
    """The detail page's JSON-LD block is malformed (unescaped control
    characters inside the description string, so json.loads rejects it even
    with strict=False). The rendered container is the reliable route."""
    req = urllib.request.Request(job["url"], headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "identity",
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        page = r.read().decode("utf-8", "replace")
    i = page.find(_PARADOX_DESC)
    if i < 0:
        return strip_html(page)[:6000]
    i = page.find(">", i) + 1  # start after the tag, not mid-attribute
    return strip_html(page[i:i + 40000])[:6000]


_HYDRATORS = {"wd": _hydrate_workday, "sr": _hydrate_smartrecruiters,
              "rd": _hydrate_radancy, "ef": _hydrate_eightfold,
              "px": _hydrate_paradox}


def hydrate(job):
    """Fill in job['description'] in place if the feed left it empty."""
    if job.get("description"):
        return job
    fn = _HYDRATORS.get(job["job_id"].split(":", 1)[0])
    if not fn:
        return job
    try:
        job["description"] = fn(job)
    except Exception as e:
        job["description"] = f"_(could not fetch description: {type(e).__name__})_"
    return job


# --- aggregator -----------------------------------------------------------
# The Adzuna adapter lived here and was removed on 2026-08-24. Its API caps
# `description` at exactly 500 characters with a trailing ellipsis, there is
# no other text field on the result object and no per-job detail endpoint,
# and its redirect chain ends at a third-party aggregator behind a JavaScript
# bot check -- so full text was unreachable by any route. See PLATFORMS.md.


def themuse(cfg):
    """The Muse public API. Unlike Adzuna it returns the FULL description, so
    so companies reachable here can be scored properly. No key required.

    location and category accept repeated values with OR semantics, so one
    query covers the whole target region -- iterating them separately meant
    60 requests per company and got us rate-limited into 504s.
    """
    q = {"descending": "true"}
    # company_query is optional: omit it and this becomes a discovery search
    # across every employer The Muse indexes. There is no free-text parameter
    # (unknown params are silently ignored), so the title prescreen does the
    # topical filtering downstream.
    if cfg.get("company_query"):
        q["company"] = cfg["company_query"]
    if cfg.get("levels"):
        q["level"] = cfg["levels"]
    if cfg.get("locations"):
        q["location"] = cfg["locations"]
    if cfg.get("categories"):
        q["category"] = cfg["categories"]

    out, seen = [], set()
    for page in range(cfg.get("pages", 6)):
        q["page"] = page
        url = "https://www.themuse.com/api/public/jobs?" + urllib.parse.urlencode(q, doseq=True)
        d = None
        for attempt in range(3):  # unauthenticated endpoint 504s under load
            try:
                d = _get(url)
                break
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
                code = getattr(e, "code", None)
                if code in (400, 404):
                    return out
                if attempt == 2:
                    raise
                time.sleep(2 * (attempt + 1))
        rows = (d or {}).get("results", [])
        for r in rows:
            jid = r.get("id")
            if jid in seen:
                continue
            seen.add(jid)
            # Always prefer the employer the API reports. For a discovery
            # search cfg["company"] is just a label like "(discovery)", and
            # using it would collapse every employer into one bucket -- which
            # breaks both dedupe and the per-company round-robin.
            emp = (r.get("company") or {}).get("name") or cfg["company"]
            out.append({
                "company": emp,
                "title": r.get("name", ""),
                "location": "; ".join(l.get("name", "") for l in r.get("locations", [])),
                "url": (r.get("refs") or {}).get("landing_page", ""),
                "description": strip_html(r.get("contents", "")),
                "job_id": f"tm:{jid}",
                "posted": r.get("publication_date", ""),
            })
        if not rows or page + 1 >= d.get("page_count", 0):
            break
        time.sleep(1.0)
    return out


ADAPTERS["themuse"] = themuse


def clearcompany(cfg):
    """ClearCompany-hosted career sites. First-party board, no key, full
    descriptions inline.

    Config needs `site_id`, a UUID. Get it from the careers page: the board is
    injected by a script tag whose src carries it --

        <script src=https://careers-content.clearcompany.com/js/v1/career-site.js?siteId=UUID>

    Note that tag has an UNQUOTED src on at least one site, so a regex
    expecting src="..." will miss it. Grep for `clearcompany` in the raw HTML
    instead.

    Endpoints (from the career-site bundle, both unauthenticated):

        /v1/{siteId}            list, with descriptions
        /v1/{siteId}/{jobId}    detail -- not needed, list text is complete

    PAGINATION IS INVERTED FROM THE OBVIOUS, AND WE PAGE ANYWAY. Requesting no
    pagination params returns the ENTIRE board in one response; passing
    `pageIndex` switches the server to 50-per-page. So fewer requests means
    omitting the param -- but that single body is ~1.2MB of chunked JSON, and
    it intermittently truncates mid-stream (http.client.IncompleteRead; curl
    handled the same URL fine, urllib did not, and it reproduced roughly one
    call in four). Four small requests are worth more than one fragile one.

    LOCATIONS ARE "City ST" WITH NO COMMA ("Briggs TX"). Region tokens written
    as ", tx" / "tx," / " tx " all fail to match that, which silently drops
    every role at such a site -- 64 of 169 on the first board tried. Include a
    bare " tx" form in regions.wanted. See README "Locations".
    """
    site = cfg["site_id"]
    base = f"https://careers-api.clearcompany.com/v1/{site}"
    rows, page, total, cap = [], 0, None, cfg.get("max", 1000)
    while len(rows) < cap:
        d = _get_retry(f"{base}?pageIndex={page}")
        got = d.get("results", [])
        if not got:
            break
        rows.extend(got)
        total = d.get("totalCount", len(rows)) if total is None else total
        page += 1
        if len(rows) >= total:
            break
        time.sleep(0.3)
    out = []
    for j in rows:
        url = j.get("applyLink", "")
        # applyLink points straight at the application form. This tool finds
        # roles, it does not apply to them -- link to the posting instead.
        if url.endswith("/apply"):
            url = url[: -len("/apply")]
        posted = (j.get("postedDate") or j.get("openDate") or "")[:10]
        out.append({
            "company": cfg["company"],
            "title": j.get("positionTitle", ""),
            "location": j.get("location", ""),
            "url": url,
            "description": strip_html(j.get("description", "")),
            "job_id": f"cc:{site}:{j.get('id')}",
            "posted": posted,
        })
    return out


ADAPTERS["clearcompany"] = clearcompany


# --- aggregator: remote-only ----------------------------------------------

_HIMALAYAS_US = {"united states", "usa", "u.s.", "us"}


def _himalayas_location(restrictions):
    """Map Himalayas' country-level `locationRestrictions` onto a string that
    location_ok() can actually read.

    Himalayas is remote-only, so it reports *eligibility* ("who may hold this
    job") rather than an office. Three cases, and the middle one is a
    deliberate lossy transform:

      []                        -> "Remote"                 (worldwide)
      ["United States", ...]    -> "Remote, United States"  (other countries dropped)
      ["Germany", "France"]     -> "Remote, Germany, France"

    Dropping the co-listed countries when the US is present matters: a role
    open to both the US and Canada would otherwise contain "canada", trip the
    FOREIGN check in location_ok(), and be dropped -- even though a US-based
    applicant is eligible. The foreign-only case keeps every country so that
    the filter can reject it for the right reason.

    Passing the raw field through would drop EVERYTHING: bare "United States"
    matches no WANTED token, so it falls through to the final rule and is
    rejected. Silent, and it would look like the source was simply empty.
    """
    countries = [c.strip() for c in (restrictions or []) if c and c.strip()]
    if not countries:
        return "Remote"
    if any(c.lower() in _HIMALAYAS_US for c in countries):
        return "Remote, United States"
    return "Remote, " + ", ".join(countries)


def himalayas(cfg):
    """Himalayas remote-job aggregator. No key, descriptions inline (~4.9k
    chars median), ~108k open roles.

    Complements The Muse on a different axis: metro-indexed aggregators miss
    remote-first employers entirely, because those companies have no office to
    be indexed against. Everything here is remote by construction.

    TWO ENDPOINTS, and the difference decides whether this source is worth
    having:

      /jobs/api         browse. Newest-first firehose, NO filtering.
      /jobs/api/search  filtered search. `q`, `country`, `seniority`, ...

    Set `queries` in config and this uses the search endpoint, one sweep per
    keyword, deduped by guid. Omit it and you get the raw browse feed, which
    is mostly remote sales and support -- one verified run was 400 fetched ->
    265 past the location filter -> 1 past the discovery prescreen. The same
    budget spent on `queries` returns overwhelmingly on-topic rows. Prefer
    `queries`.

    Constraints, verified by probing rather than assumed:

    * `limit` is capped at 20 server-side on BOTH endpoints, so cost is one
      request per twenty roles. Budget with `pages` and `max`.

    * Browse paginates by CURSOR; search paginates by 1-based `page`.
      `nextCursor` is a keyset cursor (base64 `timestamp|id`) and gives zero
      overlap. Browse `offset` is documented as deprecated and behaves like
      it: `offset=0` and `offset=20` returned four of the same jobs, because
      the feed shifts while you read it. Do not use offset.

    * `q` IS FUZZY AND MORE WORDS BROADEN, NOT NARROW. `q=engineer` returns 31
      hits; `q=mechanical engineer` returns 147. It ranks by relevance across
      the terms rather than requiring all of them, which is the opposite of
      the Adzuna AND-matching trap and the opposite of what you will assume.
      Write `queries` as specific phrases, not as one broad word.

    * The two endpoints validate differently. On browse, unknown params are
      silently ignored -- `q` and `seniority` there LOOK like they work,
      because any unrecognised param perturbs the page, while `q=mechanical
      engineer` returns religion tutors. On search, a bad `seniority` or
      `sort` returns HTTP 400, while a bad `employment_type` is accepted
      quietly. Never conclude a filter works from the ids changing; read the
      rows.

    * Valid `seniority`: Entry-level, Mid-level, Senior, Manager, Director,
      Executive. Note it is `Senior`, not `Senior-level`. `country` accepts
      US / USA / us / "United States" interchangeably, and INCLUDES
      worldwide-eligible roles unless you also pass `exclude_worldwide`.

    * Data is cached and refreshed every 24 hours upstream, so running this
      more than once a day fetches nothing new.

    Rate limited (429), handled by _get_retry. Attribution: Himalayas asks for
    a visible link back if you republish their data; every row's `url` already
    points at himalayas.app, which covers local use -- see README "Conduct".

    Mark this source `"group": "discovery"`. It spans every employer it
    indexes, so it belongs on the discovery budget with the stricter
    discovery_* prescreen, exactly like a company-less Muse sweep.
    """
    cap = cfg.get("max", 400)
    queries = cfg.get("queries") or []
    out, seen = [], set()

    def collect(rows):
        for r in rows:
            jid = r.get("guid")
            if not jid or jid in seen:
                continue
            seen.add(jid)
            posted = r.get("pubDate")
            try:
                posted = datetime.fromtimestamp(int(posted), timezone.utc).strftime("%Y-%m-%d")
            except (TypeError, ValueError):
                posted = ""
            out.append({
                # Multi-employer feed: always take the employer from the row.
                # cfg["company"] here is a label like "(remote)", and using it
                # would collapse every employer into one bucket, breaking
                # dedupe and the per-company round-robin.
                "company": r.get("companyName") or cfg["company"],
                "title": r.get("title", ""),
                "location": _himalayas_location(r.get("locationRestrictions")),
                "url": r.get("applicationLink") or jid,
                "description": strip_html(r.get("description", "")),
                "job_id": f"hi:{jid}",
                "posted": posted,
            })

    if queries:
        base = {"limit": 20}
        for key in ("country", "seniority", "employment_type", "timezone", "sort"):
            if cfg.get(key):
                base[key] = cfg[key]
        if cfg.get("exclude_worldwide"):
            base["exclude_worldwide"] = "true"
        for term in queries:
            for page in range(1, cfg.get("pages", 3) + 1):  # `page` is 1-based
                if len(out) >= cap:
                    return out[:cap]
                q = dict(base, q=term, page=page)
                url = ("https://himalayas.app/jobs/api/search?"
                       + urllib.parse.urlencode(q, doseq=True))
                d = _get_retry(url)
                rows = d.get("jobs", [])
                collect(rows)
                # Search reports no cursor; stop when the page comes up short.
                if len(rows) < 20:
                    break
                time.sleep(0.3)
        return out[:cap]

    # No `queries`: newest-first browse feed, cursor-paginated.
    cursor = None
    while len(out) < cap:
        url = "https://himalayas.app/jobs/api?limit=20"
        if cursor:
            url += "&cursor=" + urllib.parse.quote(cursor)
        d = _get_retry(url)
        rows = d.get("jobs", [])
        if not rows:
            break
        collect(rows)
        cursor = d.get("nextCursor")
        if not cursor:
            break
        time.sleep(0.3)
    return out[:cap]


ADAPTERS["himalayas"] = himalayas
