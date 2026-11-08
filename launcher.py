import json
import webbrowser
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

PRIMARY_REPO = ("krishnasaigaruda", "StormFallIO")
FALLBACK_REPO = ("crasebot1234", "StormFallIO")

BASE_DIR = Path(__file__).resolve().parent
GAME_DIR = BASE_DIR / "stormfall"
SHA_FILE = GAME_DIR / ".sha"


def json_get(url):
    request = Request(
        url,
        headers={
            "User-Agent": "StormFallLauncher"
        }
    )

    with urlopen(request, timeout=30) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


def bytes_get(url):
    request = Request(
        url,
        headers={
            "User-Agent": "StormFallLauncher"
        }
    )

    with urlopen(request, timeout=60) as response:
        return response.read()


def repo_exists(owner, repo):

    try:

        json_get(
            f"https://api.github.com/repos/{owner}/{repo}"
        )

        return True

    except:
        return False


def choose_repo():

    print(
        "Checking primary repository..."
    )

    if repo_exists(*PRIMARY_REPO):

        print(
            f"Using {PRIMARY_REPO[0]}/{PRIMARY_REPO[1]}"
        )

        return PRIMARY_REPO

    print(
        "Primary unavailable."
    )

    print(
        f"Using {FALLBACK_REPO[0]}/{FALLBACK_REPO[1]}"
    )

    return FALLBACK_REPO


def get_branch_and_sha(owner, repo):

    repo_info = json_get(
        f"https://api.github.com/repos/{owner}/{repo}"
    )

    branch = repo_info["default_branch"]

    commit_info = json_get(
        f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"
    )

    return branch, commit_info["sha"]


def get_tree(owner, repo, branch):

    data = json_get(
        f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    )

    return [
        item
        for item in data["tree"]
        if item["type"] == "blob"
    ]


def read_local_sha():

    if SHA_FILE.exists():

        return SHA_FILE.read_text(
            encoding="utf-8"
        ).strip()

    return None


def save_sha(sha):

    GAME_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    SHA_FILE.write_text(
        sha,
        encoding="utf-8"
    )


def download_repository(
    owner,
    repo,
    branch
):

    files = get_tree(
        owner,
        repo,
        branch
    )

    total = len(files)

    print(
        f"\nDownloading {total} files...\n"
    )

    GAME_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    for index, file_info in enumerate(files, start=1):

        relative_path = file_info["path"]

        raw_url = (
            "https://raw.githubusercontent.com/"
            f"{owner}/{repo}/{branch}/{relative_path}"
        )

        destination = (
            GAME_DIR / relative_path
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        try:

            data = bytes_get(raw_url)

            with open(
                destination,
                "wb"
            ) as file:

                file.write(data)

            print(
                f"[{index}/{total}] {relative_path}"
            )

        except Exception as error:

            print(
                f"FAILED: {relative_path}"
            )

            print(error)

    print(
        "\nDownload complete."
    )


def update_game():

    owner, repo = choose_repo()

    branch, remote_sha = (
        get_branch_and_sha(
            owner,
            repo
        )
    )

    local_sha = read_local_sha()

    print(
        f"\nLocal SHA : {local_sha}"
    )

    print(
        f"Remote SHA: {remote_sha}"
    )

    if local_sha == remote_sha:

        print(
            "\nAlready up to date."
        )

        return

    print(
        "\nUpdate found."
    )

    download_repository(
        owner,
        repo,
        branch
    )

    save_sha(remote_sha)

    print(
        "\nRepository updated."
    )


def launch_game():

    html_file = (
        GAME_DIR / "stormfall.html"
    )

    if not html_file.exists():

        raise FileNotFoundError(
            "stormfall.html not found."
        )

    print(
        "\nLaunching StormFall..."
    )

    webbrowser.open(
        html_file.resolve().as_uri()
    )


def main():

    update_game()

    launch_game()

    print(
        "\nDone."
    )


if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print(
            "\nLauncher Error:"
        )

        print(error)

        input(
            "\nPress Enter to exit..."
        )