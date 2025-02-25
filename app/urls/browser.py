from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from ..config.loggers import get_and_set_logger
from ..config.constants import DIRECTORY_CONFIG, STATIC

logger = get_and_set_logger(__name__)

browser_router = APIRouter()
templates = Jinja2Templates(directory="templates/browser")

ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.svg'}

def get_file_info(path: Path, request: Request, bname: str) -> Dict:
    """Get file information including size and last modified date."""
    stats = path.stat()
    size_bytes = stats.st_size

    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            break
        size_bytes /= 1024
    size = f"{size_bytes:.1f} {unit}"

    modified = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    base_path = Path(DIRECTORY_CONFIG[bname]["path"])
    rel_path = str(path.relative_to(base_path))

    return {
        "name": path.name,
        "size": size,
        "modified": modified,
        "rel_path": rel_path,
        "is_image": path.suffix.lower() in ALLOWED_IMAGE_EXTENSIONS,
        "type": "directory" if path.is_dir() else "file",
        "mount_point": DIRECTORY_CONFIG[bname]["mount_name"]  # Use mount_name from config
    }

def get_breadcrumbs(request: Request, bname: str, path: str) -> List[Dict]:
    """Generate breadcrumb navigation items with proper URLs."""
    parts = [p for p in path.split('/') if p]
    breadcrumbs = [{
        "name": DIRECTORY_CONFIG[bname]["description"],
        "url": request.url_for('browse_directory', bname=bname, path="")
    }]

    current_path = ""
    for part in parts:
        current_path = f"{current_path}/{part}" if current_path else part
        breadcrumbs.append({
            "name": part,
            "url": request.url_for('browse_directory', bname=bname, path=current_path)
        })

    return breadcrumbs

def verify_path_access(bname: str, path: str, user: Optional[dict] = None) -> Path:
    """Verify path access and return resolved path."""
    if bname not in DIRECTORY_CONFIG:
        raise HTTPException(status_code=404, detail="Directory not found")

    config = DIRECTORY_CONFIG[bname]

    if config["requires_auth"] and not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        base_path = Path(config["path"])
        full_path = (base_path / path.lstrip('/')).resolve()

        if not str(full_path).startswith(str(base_path)):
            raise HTTPException(status_code=403, detail="Access denied")

        return full_path
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@browser_router.get("/{bname}{path:path}", response_class=HTMLResponse, name="browse_directory")
@browser_router.get("/", response_class=HTMLResponse, name="browse_directory_base")
async def browse_directory(
        request: Request,
        bname: str = STATIC,
        path: str = "",
        # user: Optional[dict] = Depends(get_current_user)
):
    logger.info("Running browse_directory")
    """Browse directory contents with authentication support."""
    user = None
    try:
        full_path = verify_path_access(bname, path, user)

        files = []
        if full_path.is_dir():
            for item in sorted(full_path.iterdir()):
                if not item.name.startswith('.'):
                    files.append(get_file_info(item, request, bname))

        files.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
        logger.info("Getting breadcrumbs")
        breadcrumbs = get_breadcrumbs(request, bname, path)

        available_dirs = {
            name: config["description"]
            for name, config in DIRECTORY_CONFIG.items()
            if not config["requires_auth"] or user
        }

        return templates.TemplateResponse(
            "browser.html",
            {
                "request": request,
                "files": files,
                "breadcrumbs": breadcrumbs,
                "current_dir": bname,
                "available_dirs": available_dirs,
                "user": user
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))