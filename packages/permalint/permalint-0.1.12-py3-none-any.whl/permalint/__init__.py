"""permalint: Lint URLs.

Exports:
    - normalize_url: Normalize URLs so it's easy to figure out canonical
      sources of truth for packages
"""

from __future__ import annotations

import warnings
from urllib.parse import ParseResult, urlparse

MIN_GITHUB_URL_PARTS = 2
MULTIPLE_DOMAINS = 2


def normalize_url(url: str) -> str:
    """Normalize a URL according to CHAI database rules.

    It could return an empty string if the URL is only the protocol

    - Ignore protocol (http, https, etc.)
    - For GitHub URLs, keep only owner/repo
    - Remove query strings and fragments
    - Remove trailing slashes
    - Lowercase the domain
    - Remove .git suffix
    - Handle SSH GitHub URLs (git@github.com:user/repo)
    - Handle git+ssh and git+https GitHub URLs.
    """
    # early warnings
    if url.strip() in (
        "http://",
        "https://",
        "git://",
        "ssh://",
        "git+ssh://",
        "git+https://",
    ):
        warnings.warn(
            f"Malformed URL with only protocol: '{url}', returning ''",
            UserWarning,
            stacklevel=2,
        )
        return ""

    # first, remove the .git suffix if it exists
    url = url.removesuffix(".git")

    # now, handle specific git style URLs: ssh, https, and git

    # ssh-style GitHub URLs
    if url.startswith("git@github.com:"):
        url = url.replace("git@github.com:", "github.com/")

    # git+ssh style GitHub URLs
    if url.startswith("git+ssh://git@github.com/"):
        url = url.replace("git+ssh://git@github.com/", "github.com/")

    # git+https style GitHub URLs
    if url.startswith("git+https://github.com/"):
        url = url.replace("git+https://github.com/", "github.com/")

    try:
        parsed = urlparse(url)
    except ValueError as e:
        warnings.warn(
            f"Malformed URL: '{url}', error: {e}, returning ''",
            UserWarning,
            stacklevel=2,
        )
        return ""

    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")

    # Remove www. for consistency
    netloc = netloc.removeprefix("www.")

    # GitHub special handling
    if netloc == "github.com":
        parts = [p for p in path.split("/") if p]
        if len(parts) >= MIN_GITHUB_URL_PARTS:
            path = f"{parts[0]}/{parts[1]}"
        elif parts:
            path = parts[0]
        else:
            path = ""
        return f"github.com/{path}".rstrip("/")

    # Remove query and fragment, ignore protocol
    result = f"{netloc}{path}" if netloc else path

    # Remove .git suffix if present - handle this once at the end
    return result.removesuffix(".git")


def guess_url(urls: list[str]) -> str | None:
    """Given a list of URLs, return the most likely canonical URL."""
    results: set[ParseResult] = set()
    for url in urls:
        normalized = normalize_url(url)
        if normalized in urls:
            results.add(normalized)

    if len(results) == 1:
        return results.pop()
    return None


def possible_names(url: str) -> list[str]:
    """Given a URL, return a list of possible names for the package.

    The list is ordered by relevance to the input.
    """
    from urllib.parse import urlparse

    # NOTE: I don't like this, ideally upstream application should handle
    # searching by whatever case, but this is fine for now

    # Handle URLs without scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    path = parsed.path.strip("/")

    # Remove www. for consistency
    netloc = netloc.removeprefix("www.")

    names = []

    # Full path (netloc + path)
    if path:
        full_path = f"{netloc}/{path}"
        names.append(full_path)
        last_segment = path.split("/")[-1]
        names.append(last_segment)
        # Add lowercase version if original has uppercase
        if last_segment.lower() != last_segment:
            names.append(last_segment.lower())
    else:
        # Domain-only URLs
        names.append(netloc)
        # For domains like elfutils.org, extract the name part
        domain_parts = netloc.split(".")
        if len(domain_parts) > 1:
            if len(domain_parts) > MULTIPLE_DOMAINS:
                # For cases like poppler.freedesktop.org
                names.append(domain_parts[0])  # e.g., "poppler"
                names.append(domain_parts[1])  # e.g., "freedesktop"
            else:
                # For cases like elfutils.org
                names.append(domain_parts[0])  # e.g., "elfutils"

    return names


def is_canonical_url(url: str) -> bool:
    """Check if a URL is canonical."""
    return normalize_url(url) == url
