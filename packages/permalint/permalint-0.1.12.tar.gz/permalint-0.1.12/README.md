# permalint

Lint URLs (mostly for teaxyz/chai, but hopefully other uses too)

## Features

- Ignores protocol (http, https, etc.)
- Normalizes GitHub URLs to owner/repo
- Removes query strings and fragments
- Lowercases domains and removes www

## Usage

```python
from permalint import normalize_url

url = "https://github.com/user/repo?utm_source=foo#readme"
print(normalize_url(url))  # Output: github.com/user/repo
```

## Development

- Install dependencies: `pkgx rye sync`
- Run tests: `pkgx rye run pytest`
- Lint: `pkgx ruff check src/`
- Type check: `pkgx ty src/`

## Contributing / Wishlist

- `guess-canonical-url` to guess the correct URL based on a passed list of URLs
- actual source of Homepages for
