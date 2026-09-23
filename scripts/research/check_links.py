"""Check documentation links with explicit, nonempty input/link discovery."""
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INPUTS = ["README.md", "paper/README.md", "docs/", "design/", "results/"]
# Hidden enclosing folders and global ignores must not silently erase a checkout.
# The release URL is in a code span, so verbatim URLs must be included too.
BASE = ["lychee", "--hidden", "--no-ignore", "--include-verbatim"]


def authenticated_private_release(url):
    """Check a specific private release resource, not merely its repository.

GitHub deliberately returns anonymous 404s for private repositories. Use
the existing GitHub authentication through gh; never print or pass tokens
on the command line or to non-GitHub hosts.
"""
    match = re.fullmatch(r"https://github\.com/([^/]+)/([^/]+)/releases/tag/([^/?#]+)", url)
    if not match:
        return None
    owner, repository, tag = match.groups()
    try:
        repo = subprocess.run(["gh", "api", f"repos/{owner}/{repository}", "--jq", "{private,full_name}"],
                              cwd=REPO, capture_output=True, text=True, timeout=20, check=False)
        data = json.loads(repo.stdout)
        if repo.returncode or data.get("private") is not True or data.get("full_name") != f"{owner}/{repository}":
            return None
        release = subprocess.run(["gh", "api", f"repos/{owner}/{repository}/releases/tags/{tag}",
                                  "--jq", "{html_url,tag_name,id}"], cwd=REPO,
                                 capture_output=True, text=True, timeout=20, check=False)
        resource = json.loads(release.stdout)
        if release.returncode or resource.get("html_url") != url or resource.get("tag_name") != tag or not resource.get("id"):
            return None
        return {"url": url, "method": "authenticated GitHub release API", "release_id": resource["id"]}
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def main():
    directory = REPO / "build/research"
    directory.mkdir(parents=True, exist_ok=True)
    for flag, filename in (("--dump-inputs", "link-inputs.txt"), ("--dump", "link-targets.txt")):
        discovery = subprocess.run(BASE + [flag] + INPUTS, cwd=REPO, text=True, capture_output=True, check=False)
        (directory / filename).write_text(discovery.stdout, encoding="utf-8")
        if discovery.returncode or not discovery.stdout.strip():
            print(f"links: {flag} returned no valid inputs/links: {discovery.stderr}", file=sys.stderr)
            return 1
    report = directory / "links.json"
    result = subprocess.run(BASE + ["--no-progress", "--timeout", "20", "--max-retries", "1",
                                   "--format", "json", "--output", str(report)] + INPUTS,
                            cwd=REPO, check=False)
    if not report.is_file():
        print("links: checker produced no status report", file=sys.stderr)
        return 1
    data = json.loads(report.read_text(encoding="utf-8"))
    if not isinstance(data.get("total"), int) or data["total"] <= 0:
        print("links: checker reported zero checked links", file=sys.stderr)
        return 1
    authenticated = []
    unresolved = []
    for source, failures in data.get("error_map", {}).items():
        for failure in failures:
            evidence = authenticated_private_release(failure["url"]) if failure.get("status", {}).get("code") == 404 else None
            if evidence:
                authenticated.append(evidence)
            else:
                unresolved.append(f"{source}: {failure['url']}: {failure.get('status')}")
    (directory / "links-authenticated.json").write_text(json.dumps(authenticated, indent=2) + "\n", encoding="utf-8")
    if unresolved or data.get("timeouts") or (result.returncode and not authenticated):
        for failure in unresolved:
            print(f"links: {failure}", file=sys.stderr)
        return result.returncode or 1
    if data.get("errors", 0) != len(authenticated):
        print("links: unresolved error count in report", file=sys.stderr)
        return 1
    print(f"links: {data['total']} links checked successfully; {len(authenticated)} private releases verified via authenticated API")
    return 0


if __name__ == "__main__":
    sys.exit(main())
