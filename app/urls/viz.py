from pathlib import Path
from typing import Optional

from fastapi import Request, APIRouter, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from ..config.loggers import get_and_set_logger

logger = get_and_set_logger(__name__)
viz_router = APIRouter()


templates = Jinja2Templates(directory="templates/viz")

@viz_router.get("/", name="viz_home")
async def viz_home(request: Request):
    """Home endpoint for visualization routes."""
    try:
        return JSONResponse(content={"status": "ok", "message": "Visualization API is running"})
    except Exception as e:
        logger.error(f"Error in viz_home: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@viz_router.get("/tsne/{file_path:path}", name="render_tsne")
async def render_tsne(request: Request, file_path: Path):
    """Render t-SNE visualization for the given file path."""
    try:
        # Validate file path
        if not isinstance(file_path, Path):
            file_path = Path(str(file_path))

        # Check if file exists (if needed)
        # if not file_path.exists():
        #     raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

        return templates.TemplateResponse(
            "leaflet_custom.html",
            {
                "request": request,
                "json_filename": file_path.name,
                "title": f"t-SNE Visualization - {file_path.name}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rendering t-SNE visualization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))