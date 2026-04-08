# OpenKYCAML — External Actions Manual

> **Who this is for:** Repository maintainers with admin access to the GitHub repository,
> an npm organisation account, and a PyPI project account.
>
> **Why this file exists:** The following tasks cannot be automated entirely from within the
> repository because they require external credentials, organisation-level accounts, or
> repository settings that are not accessible to in-repo workflows alone. They correspond
> to technical debt items **§31–§34** recorded in `ROADMAP.md`.

---

## Table of Contents

1. [§31 — Creating GitHub Releases and Annotated Tags](#31--creating-github-releases-and-annotated-tags)
2. [§32 — Publishing to PyPI (`openkycaml`)](#32--publishing-to-pypi-openkycaml)
3. [§33 — Publishing to npm (`@openkycaml/tools`)](#33--publishing-to-npm-openkycamltools)
4. [§34 — Configuring GitHub Pages / `schema.openkycaml.org`](#34--configuring-github-pages--schemaopenkycamlorg)
5. [Release Checklist — Putting It All Together](#release-checklist--putting-it-all-together)

---

## §31 — Creating GitHub Releases and Annotated Tags

### Background

The repository already contains `.github/workflows/release.yml`, which is **automatically
triggered** when a maintainer pushes a `v*.*.*` annotated tag to `main`. It will:

- Publish `@openkycaml/tools` to npm.
- Publish `openkycaml` to PyPI.
- Create a GitHub Release with notes extracted from `CHANGELOG.md`.

No additional workflow authoring is needed. The only manual step is creating and pushing
the tag.

### Pre-release checks

Before tagging, verify:

```bash
# 1. Confirm the canonical schema version matches the intended release
python3 -c "import json; d=json.load(open('schema/kyc-aml-hybrid-extended.json')); print(d['version'])"
# Expected output: 1.9.1  (or whatever version you are releasing)

# 2. Confirm the versioned snapshot matches the canonical schema
diff <(python3 -c "import json; print(json.dumps(json.load(open('schema/kyc-aml-hybrid-extended.json')), indent=2, sort_keys=True))") \
     <(python3 -c "import json; print(json.dumps(json.load(open('schema/versions/v1.9.1.json')),        indent=2, sort_keys=True))")
# Expected output: (empty — files are identical)

# 3. Confirm pyproject.toml version matches
grep '^version' pyproject.toml
# Expected output: version = "1.9.1"

# 4. Confirm CHANGELOG.md has an entry for this version
grep '## \[1.9.1\]' CHANGELOG.md
# Expected output: ## [1.9.1] — April 2026  (or similar)

# 5. Run full validation suite locally
pip install -r tools/python/requirements.txt
python tools/python/validator.py examples/full-kyc-profile.json
```

### Creating the annotated tag

```bash
# Pull the latest main
git checkout main
git pull origin main

# Create a signed, annotated tag (preferred — requires GPG key)
git tag -s v1.9.1 -m "OpenKYCAML v1.9.1 — FATCA/CRS first-class fields

- taxStatus.crsTaxResidencies[] (OECD CRS per-jurisdiction self-certification)
- taxStatus.fatcaStatus (FATCA GIIN, Chapter 4 classification, IRS Notice 2024-78)
- api/openkycaml-v1.9.1.yaml (OpenAPI 3.1 reflecting all v1.9.1 components)
- examples/amlr2027-fatca-ai-act.json (combined AMLR + FATCA + EU AI Act example)

See CHANGELOG.md [1.9.1] for the full change log."

# Verify the tag
git tag -v v1.9.1

# Push the tag — this triggers release.yml
git push origin v1.9.1
```

> **Unsigned alternative** (if GPG is not set up yet):
> Replace `git tag -s` with `git tag -a`. Signed tags are strongly recommended for a
> security-sensitive specification.

### Catching up on missing historical tags

All versions from v1.0.0 through v1.9.0 are also untagged. To create lightweight tags
retroactively for all previously released commits, find the merge commit for each release
using `git log --oneline --merges` and tag them:

```bash
# Example: tag the merge commit for v1.8.0
git log --oneline | grep -i "v1.8"          # find the SHA
git tag -a v1.8.0 <SHA> -m "OpenKYCAML v1.8.0 — X.500 DN + X.509 PKI Evidence"
git push origin v1.8.0

# Repeat for v1.0.0, v1.1.0, v1.2.0, v1.3.0, v1.4.0, v1.5.0, v1.6.0, v1.7.0, v1.9.0
```

> **Important:** Do **not** push these historical tags using `v*.*.*` format if you do not
> want the release workflow to re-run PyPI/npm publishing for them. Either use a different
> tag format (e.g. `hist/v1.8.0`) for historical markers, or ensure the packages are not
> already published at those versions before pushing.

---

## §32 — Publishing to PyPI (`openkycaml`)

### One-time account and project setup

1. **Create a PyPI account** at <https://pypi.org/account/register/>.

2. **Create a Test PyPI account** at <https://test.pypi.org/account/register/> (for dry runs).

3. **Reserve the package name** by doing a first manual upload (see §Publishing for the
   first time below).

4. **Verify the project metadata** in `pyproject.toml`:

   ```toml
   [project]
   name = "openkycaml"           # must match PyPI project name exactly
   version = "1.9.1"             # bump this on every release
   ```

   > **Note:** `pyproject.toml` currently declares version `1.3.0`. Update it to `1.9.1`
   > before the next release commit.

### Recommended: configure PyPI Trusted Publishing (OIDC — no long-lived token)

Trusted Publishing lets GitHub Actions authenticate to PyPI using short-lived OIDC tokens,
eliminating the need to store a `PYPI_TOKEN` secret.

1. Log in to <https://pypi.org>, navigate to **Manage → Publishing**.

2. Click **Add a new pending publisher** and enter:

   | Field | Value |
   |---|---|
   | PyPI Project Name | `openkycaml` |
   | Owner | `Lazy-Jack-Ltd` |
   | Repository name | `OpenKYCAML` |
   | Workflow filename | `release.yml` |
   | Environment name | *(leave blank, or `pypi` if you create one)* |

3. Update `release.yml` to use the trusted publisher instead of `twine`:

   ```yaml
   - name: Publish to PyPI (Trusted Publishing — OIDC)
     uses: pypa/gh-action-pypi-publish@release/v1
     # No token needed — OIDC handles authentication
   ```

   Remove the existing `twine upload` step and the `TWINE_PASSWORD` env var.

### Alternative: token-based publishing (current `release.yml` approach)

If Trusted Publishing is not yet configured, the existing workflow uses a `PYPI_TOKEN`
secret. To enable it:

1. Log in to <https://pypi.org>, navigate to **Account settings → API tokens**.
2. Click **Add API token**. Scope it to the `openkycaml` project only (not account-wide).
3. Copy the token value (shown only once).
4. In the GitHub repository, go to **Settings → Secrets and variables → Actions**.
5. Click **New repository secret**. Name: `PYPI_TOKEN`. Value: the token from step 3.

### Publishing for the first time (initial upload)

The first upload must be done manually to reserve the package name before the CI workflow
takes over:

```bash
# Install build tooling
pip install build twine

# Build source distribution and wheel
python -m build
# Creates dist/openkycaml-1.9.1.tar.gz and dist/openkycaml-1.9.1-py3-none-any.whl

# Dry run against Test PyPI first
twine upload --repository testpypi dist/*
# Verify at https://test.pypi.org/project/openkycaml/

# Upload to production PyPI
twine upload dist/*
# Enter your API token when prompted, or set TWINE_USERNAME=__token__ TWINE_PASSWORD=<token>
```

After the first manual upload, all subsequent releases are handled automatically by
`release.yml` when a `v*.*.*` tag is pushed.

### Verifying the publication

```bash
pip install openkycaml==1.9.1
openkycaml-validate --help
```

---

## §33 — Publishing to npm (`@openkycaml/tools`)

### One-time account and organisation setup

1. **Create an npm account** at <https://www.npmjs.com/signup>.

2. **Create the `@openkycaml` organisation** (scoped packages require an org):
   - Go to <https://www.npmjs.com/org/create>.
   - Org name: `openkycaml` (all lowercase). This enables the `@openkycaml/` scope.
   - Choose the **free** plan (public packages).

3. **Verify `package.json`** in `tools/javascript/`:

   ```json
   {
     "name": "@openkycaml/tools",
     "version": "1.0.0"
   }
   ```

   > **Note:** The version should be bumped to match the schema release (e.g. `1.9.1`)
   > before the next release commit, to keep Python and JS package versions aligned.

4. **Verify the `prepublishOnly` script** runs tests before every `npm publish`:

   ```json
   "scripts": {
     "test": "node --test tests/*.js",
     "prepublishOnly": "npm test"
   }
   ```

   > **Prerequisite:** The `tests/` directory must exist with at least one `.js` test file.
   > See `tools/javascript/package.json` — the current `test` script references
   > `tests/*.js` which does not yet exist (CI gap #12 in `ROADMAP.md`). Create the
   > directory and a basic smoke test before publishing.

### Configure the `NPM_TOKEN` secret in GitHub

1. Log in to <https://www.npmjs.com>, click your avatar → **Access Tokens**.
2. Click **Generate New Token** → **Automation** (this token type is not invalidated
   by 2FA prompts and is safe for CI use).
3. Copy the token value.
4. In the GitHub repository, go to **Settings → Secrets and variables → Actions**.
5. Click **New repository secret**. Name: `NPM_TOKEN`. Value: the token from step 3.

### Publishing for the first time

```bash
cd tools/javascript

# Install dependencies
npm install

# Log in to npm (interactive — only needed once per machine)
npm login

# Dry run — check what would be published
npm publish --dry-run --access public

# Publish (first-time: must use --access public for scoped packages)
npm publish --access public
```

After the first manual publish, the CI `release.yml` workflow handles all subsequent
releases automatically on tag push.

### Verifying the publication

```bash
npm install @openkycaml/tools
node -e "const {OpenKYCAMLValidator} = require('@openkycaml/tools'); console.log(new OpenKYCAMLValidator());"
```

---

## §34 — Configuring GitHub Pages / `schema.openkycaml.org`

### Background

All examples and the canonical schema use `https://schema.openkycaml.org/v1.9.1/…` as
their `$schema` URL. This URL must resolve to the actual JSON Schema file. There are two
independent steps:

1. **Enable GitHub Pages** in repository settings to serve the `schema/` directory.
2. **Configure a custom domain** (`schema.openkycaml.org`) pointing to the GitHub Pages URL.

### Step 1 — Enable GitHub Pages via GitHub Actions (recommended)

Create the file `.github/workflows/pages.yml`:

```yaml
name: Deploy schema to GitHub Pages

on:
  push:
    branches: [main]
    paths:
      - "schema/**"
      - "api/**"
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Build Pages site
        run: |
          mkdir -p _site
          # Mirror schema/versions/ → /v<N>/ URL path
          for f in schema/versions/v*.json; do
            version=$(basename "$f" .json)
            mkdir -p "_site/${version}"
            cp "$f" "_site/${version}/kyc-aml-hybrid-extended.json"
          done
          # Copy canonical schema under latest version path
          LATEST=$(python3 -c "import json; print(json.load(open('schema/kyc-aml-hybrid-extended.json'))['version'])")
          mkdir -p "_site/v${LATEST}"
          cp schema/kyc-aml-hybrid-extended.json "_site/v${LATEST}/kyc-aml-hybrid-extended.json"
          # Copy OpenAPI specs
          mkdir -p _site/api
          cp api/*.yaml _site/api/
          # Simple index
          echo "<html><body><pre>$(ls _site/)</pre></body></html>" > _site/index.html

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

> **Alternative — simpler approach:** In repository **Settings → Pages**, choose
> **Source: Deploy from a branch**, select `main`, folder `/docs`. This serves `docs/` at
> `https://lazy-jack-ltd.github.io/OpenKYCAML/`. Schema files would then need to be
> symlinked or copied into `docs/`.

### Step 2 — Enable GitHub Pages in repository settings

1. Go to **Settings → Pages** (in the GitHub repository UI).
2. Under **Build and deployment**, select **Source: GitHub Actions** (to use the workflow
   above) or **Deploy from a branch** (for the simpler approach).
3. Note the generated URL: `https://lazy-jack-ltd.github.io/OpenKYCAML/`.
4. Verify a schema file resolves:
   `curl -I https://lazy-jack-ltd.github.io/OpenKYCAML/v1.9.1/kyc-aml-hybrid-extended.json`

### Step 3 — Configure the custom domain `schema.openkycaml.org`

1. **Register / verify the domain** `openkycaml.org` through a registrar (e.g. Namecheap,
   Cloudflare, Google Domains).

2. **Add the GitHub Pages custom domain** in repository **Settings → Pages → Custom domain**:
   - Enter `schema.openkycaml.org`.
   - Check **Enforce HTTPS**.
   - GitHub will create a `CNAME` file at the repository root automatically — commit it.

3. **Add a DNS CNAME record** at your DNS provider:

   | Type | Name | Value | TTL |
   |---|---|---|---|
   | `CNAME` | `schema` | `lazy-jack-ltd.github.io` | 3600 |

4. Wait for DNS propagation (up to 24 hours), then verify:

   ```bash
   curl -sI https://schema.openkycaml.org/v1.9.1/kyc-aml-hybrid-extended.json \
     | grep -E "HTTP|Content-Type"
   # Expected:
   # HTTP/2 200
   # content-type: application/json
   ```

5. Update the `$schema` `$id` URL in `schema/kyc-aml-hybrid-extended.json` if it is
   still referencing `openkycaml.org` rather than `schema.openkycaml.org`:

   ```json
   "$id": "https://schema.openkycaml.org/v1.9.1/kyc-aml-hybrid-extended.json"
   ```

---

## Release Checklist — Putting It All Together

Use this checklist for every release. Copy it into the GitHub Release description.

```markdown
## Pre-release (in-repo — PR required)

- [ ] `schema/kyc-aml-hybrid-extended.json` — `version` and `$id` bumped to vX.Y.Z
- [ ] `schema/versions/vX.Y.Z.json` — versioned snapshot added (must be byte-for-byte identical to canonical)
- [ ] `pyproject.toml` — `version` bumped to X.Y.Z
- [ ] `tools/javascript/package.json` — `version` bumped to X.Y.Z
- [ ] `CHANGELOG.md` — `## [X.Y.Z]` section added with all Added/Changed/Fixed entries
- [ ] All CI checks passing on `main` (validate-python, validate-node, validate-iso20022, lint-json, lint-naming)
- [ ] `examples/amlr2027-fatca-ai-act.json` (or equivalent combined example) updated if new fields added

## Tagging (local git — requires repo write access)

- [ ] `git tag -s vX.Y.Z -m "OpenKYCAML vX.Y.Z — <one-line summary>"`
- [ ] `git push origin vX.Y.Z`

## Automated (triggered by tag push — monitor in GitHub Actions)

- [ ] `release.yml` / Publish @openkycaml/tools to npm — ✅ / ❌
- [ ] `release.yml` / Publish openkycaml to PyPI — ✅ / ❌
- [ ] `release.yml` / Create GitHub Release — ✅ / ❌

## External verification

- [ ] `pip install openkycaml==X.Y.Z` installs without error
- [ ] `npm install @openkycaml/tools@X.Y.Z` installs without error
- [ ] GitHub Release page shows correct release notes and tag
- [ ] `https://schema.openkycaml.org/vX.Y.Z/kyc-aml-hybrid-extended.json` resolves (200 OK)

## One-time setup (first release only — §32–34 above)

- [ ] PyPI account created and `PYPI_TOKEN` or Trusted Publishing configured
- [ ] npm `@openkycaml` org created and `NPM_TOKEN` secret set
- [ ] GitHub Pages enabled (`Settings → Pages → GitHub Actions`)
- [ ] DNS `CNAME` record for `schema.openkycaml.org` → `lazy-jack-ltd.github.io` set
```

---

*Maintained by the OpenKYCAML Core Maintainers. Cross-reference: `ROADMAP.md` §31–§34.*
