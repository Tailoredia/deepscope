import os

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from ..config.constants import DIRECTORY_CONFIG, OUTPUT_BROWSER_URL, OUTPUT_VIZ_URL, OUTPUT_DISTANCES_URL
from ..config.loggers import get_and_set_logger
from ..urls.viz import viz_router
from ..urls.distances import distances_router
from ..urls.browser import browser_router

app = FastAPI()

# Mount static directories dynamically from config
for dir_name, config in DIRECTORY_CONFIG.items():
    os.makedirs(config["path"], exist_ok=True)
    app.mount(
        config["url_prefix"],
        StaticFiles(directory=config["path"]),
        name=config["mount_name"]
    )

logger = get_and_set_logger(__name__)
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_root(request: Request):
    # Redirect to the render_tsne endpoint with a default file path
    return RedirectResponse(
        url=request.url_for(
            "browse_directory_base"
        )
    )

app.include_router(distances_router, prefix=OUTPUT_DISTANCES_URL)
app.include_router(viz_router, prefix=OUTPUT_VIZ_URL)
app.include_router(browser_router, prefix=OUTPUT_BROWSER_URL)