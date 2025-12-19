from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import os
import secrets
from src.utils.config_manager import config_manager
import logging
import aiohttp
from typing import Optional

logger = logging.getLogger(__name__)

app = FastAPI()

# Mount templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# Session Middleware
SECRET_KEY = os.getenv("SESSION_SECRET", secrets.token_hex(32))
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# OAuth Settings
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")
OWNER_ID = os.getenv("OWNER_ID") # For OAuth verification

def is_authenticated(request: Request):
    return request.session.get("user") is not None

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("dashboard.html", {"request": request, "config": config_manager.config})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    oauth_enabled = bool(DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET and DISCORD_REDIRECT_URI)
    return templates.TemplateResponse("login.html", {"request": request, "oauth_enabled": oauth_enabled})

@app.post("/login")
async def login_submit(request: Request, password: str = Form(...)):
    # Simple password auth fallback
    # In production, use a secure hash comparison.
    # Here we check against an env var or config value
    admin_password = os.getenv("ADMIN_PASSWORD", "admin")
    
    if password == admin_password:
        request.session["user"] = "admin"
        return RedirectResponse(url="/", status_code=303)
    
    oauth_enabled = bool(DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET and DISCORD_REDIRECT_URI)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid password", "oauth_enabled": oauth_enabled})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")

@app.post("/config/update")
async def update_config(
    request: Request,
    minecraft_ip: str = Form(...),
    minecraft_port: int = Form(...),
    link_website: str = Form(...),
    link_store: str = Form(...),
    link_vote: str = Form(...),
    rules: str = Form(...),
    welcome_enabled: bool = Form(False),
    welcome_channel_id: int = Form(0),
    welcome_message: str = Form(...),
):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")

    # Update config
    # Minecraft
    await config_manager.set("minecraft.ip", minecraft_ip)
    await config_manager.set("minecraft.port", minecraft_port)
    
    # Links
    await config_manager.set("links.website", link_website)
    await config_manager.set("links.store", link_store)
    vote_links = [line.strip() for line in link_vote.split("\n") if line.strip()]
    await config_manager.set("links.vote", vote_links)
    
    # Rules
    await config_manager.set("rules", rules)
    
    # Welcome
    await config_manager.set("welcome.enabled", welcome_enabled)
    await config_manager.set("welcome.channel_id", welcome_channel_id)
    await config_manager.set("welcome.message", welcome_message)
    
    # Commands - Handle dynamic form fields
    form_data = await request.form()
    for key in config_manager.config["commands"].keys():
        enabled = f"cmd_{key}" in form_data
        await config_manager.set(f"commands.{key}", enabled)
    
    return RedirectResponse(url="/", status_code=303)

# OAuth Routes (Simplified)
@app.get("/oauth/login")
async def oauth_login():
    if not (DISCORD_CLIENT_ID and DISCORD_REDIRECT_URI):
        return RedirectResponse(url="/login")
    
    url = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify"
    return RedirectResponse(url=url)

@app.get("/oauth/callback")
async def oauth_callback(request: Request, code: str):
    if not (DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET and DISCORD_REDIRECT_URI):
         return RedirectResponse(url="/login")

    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post("https://discord.com/api/oauth2/token", data=data) as resp:
            if resp.status != 200:
                return RedirectResponse(url="/login?error=oauth_failed")
            token_data = await resp.json()
            access_token = token_data["access_token"]
        
        # Get User Info
        async with session.get("https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {access_token}"}) as resp:
            if resp.status != 200:
                 return RedirectResponse(url="/login?error=oauth_failed")
            user_data = await resp.json()
            
            # Verify Owner
            if str(user_data["id"]) == str(OWNER_ID):
                request.session["user"] = user_data["username"]
                return RedirectResponse(url="/")
            else:
                return RedirectResponse(url="/login?error=unauthorized")
