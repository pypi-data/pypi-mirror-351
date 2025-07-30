from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import os

app = FastAPI()

FRONTEND_PATH = os.path.join(os.path.dirname(__file__), "frontend")

# Static files serving (JS, CSS, images)
app.mount("/_next", StaticFiles(directory=os.path.join(FRONTEND_PATH, "_next")), name="_next_static")
app.mount("/images", StaticFiles(directory=os.path.join(FRONTEND_PATH, "images")), name="images_static")

def get_injected_html_content(file_path_to_serve: str, api_url: str) -> str:
    with open(file_path_to_serve, "r", encoding="utf-8") as file:
        html_content = file.read()
    
    # Inject API_URL script tag. 
    script_tag = f"<script>window.__NEXT_PUBLIC_API_URL__ = '{api_url}';</script>"
    if "<head>" in html_content: 
        html_content = html_content.replace("<head>", f"<head>{script_tag}", 1)
    elif "</body>" in html_content: # Fallback
        html_content = html_content.replace("</body>", f"{script_tag}</body>", 1)
    else: # Fallback
        html_content += script_tag
    return html_content

@app.get("/{full_path:path}")
async def serve_frontend_catch_all(full_path: str):
    api_url = os.environ.get("API_URL", "http://localhost:4401")
    
    # Remove leading slash for path joining, handle empty path for root
    cleaned_path = full_path.lstrip('/')
    
    # Path to a potential direct file (e.g., frontend/favicon.ico, frontend/config.js)
    direct_file_path = os.path.join(FRONTEND_PATH, cleaned_path)

    # 1. Check if the request is for a specific asset file (non-HTML)
    #    This covers favicon.ico, config.js, individual images if not under /images, etc.
    if os.path.isfile(direct_file_path) and not direct_file_path.endswith(".html"):
        # Do not inject API_URL into non-HTML files like JS, CSS, images
        return FileResponse(direct_file_path)

    # 2. Check if there's a specific .html file for this route (e.g., dashboard.html for /dashboard)
    #    This is how `next export` typically structures pages.
    #    If cleaned_path is empty (root "/"), try "index.html" first via this logic.
    #    If cleaned_path is "dashboard", try "dashboard.html".
    page_html_name = f"{cleaned_path}.html" if cleaned_path else "index.html"
    specific_html_file = os.path.join(FRONTEND_PATH, page_html_name)

    if os.path.isfile(specific_html_file):
        html_content = get_injected_html_content(specific_html_file, api_url)
        return HTMLResponse(html_content)

    # 3. Fallback: If no specific .html file, serve the main index.html
    #    This is crucial for SPAs where client-side routing takes over for paths
    #    not matching a specific .html file (though with `next export` and your file structure,
    #    step 2 should catch most valid page routes).
    #    This also handles the root path "/" if index.html wasn't caught by page_html_name logic.
    index_path = os.path.join(FRONTEND_PATH, "index.html")
    if os.path.isfile(index_path):
        html_content = get_injected_html_content(index_path, api_url)
        return HTMLResponse(html_content)

    # 4. If all else fails, return a 404
    #    You might want to serve your custom 404.html here too.
    not_found_path = os.path.join(FRONTEND_PATH, "404.html")
    if os.path.isfile(not_found_path):
        html_content = get_injected_html_content(not_found_path, api_url) # Inject here too if needed
        return HTMLResponse(html_content, status_code=404)
        
    return HTMLResponse(content="Page not found.", status_code=404)
