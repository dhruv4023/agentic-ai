import re
import httpx
from urllib.parse import urlparse, unquote
from dataclasses import dataclass
from schemas.note_schema import NoteState
from typing import Optional


LINE_REGEX = re.compile(r"^L(\d+)(?:-L(\d+))?$", re.IGNORECASE)


@dataclass
class CodeFrame:
    owner: str
    repo: str
    sha: str
    path: str
    startLine: int
    endLine: int
    url: str
    rawUrl: str


def parse_github_permalink(value: str) -> Optional[CodeFrame]:
    if not value:
        return None

    try:
        url = urlparse(value)
    except Exception:
        return None

    if url.hostname != "github.com":
        return None

    segments = [s for s in url.path.split("/") if s]
    if len(segments) < 5:
        return None

    owner, repo, blob_keyword, sha, *path_parts = segments

    if blob_keyword != "blob" or not path_parts:
        return None

    hash_value = url.fragment
    match = LINE_REGEX.match(hash_value)
    if not match:
        return None

    start_line = int(match.group(1))
    end_line = int(match.group(2) or match.group(1))

    path = unquote("/".join(path_parts))

    return CodeFrame(
        owner=owner,
        repo=repo,
        sha=sha,
        path=path,
        startLine=start_line,
        endLine=end_line,
        url=value,
        rawUrl=f"https://raw.githubusercontent.com/{owner}/{repo}/{sha}/{path}"
    )


async def fetch_github_content(value: str) -> Optional[str]:
    """
    Parses GitHub permalink and returns only the selected lines.
    """
    frame = parse_github_permalink(value)
    if not frame:
        return None

    async with httpx.AsyncClient() as client:
        response = await client.get(frame.rawUrl)
        response.raise_for_status()

    lines = response.text.splitlines()

    # GitHub lines are 1-based index
    start = max(0, frame.startLine - 1)
    end = min(len(lines), frame.endLine)

    selected_lines = lines[start:end]

    return "\n".join(selected_lines)


async def fetch_code(state: NoteState):

    for note in state["notes"]:
        note["github_content"] = await fetch_github_content(
            note["permanentLink"]
        )

    return state
