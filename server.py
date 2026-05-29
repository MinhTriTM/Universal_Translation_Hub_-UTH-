"""
Universal Translation Hub (UTH) — FastAPI Backend Server
Cung cấp API cho web GUI: translate, TTS, pipeline, model management.
"""

import asyncio
import json
import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Body, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Thêm src vào path
sys.path.insert(0, str(Path(__file__).parent))

from src.providers import get_provider, MiMoProvider, LocalProvider
from src.memory import TranslationMemory
from src.pipelines import GamePipeline, MangaPipeline, FilmPipeline
from src.agents import TTSAgent, QAAgent
from src.utils.file_detector import detect_pipeline

# Load .env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

app = FastAPI(title="Universal Translation Hub", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
memory = TranslationMemory()
UPLOAD_DIR = Path(__file__).parent / "uploads"
OUTPUT_DIR = Path(__file__).parent / "output"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


# ==========================================
# SERVE FRONTEND
# ==========================================
@app.get("/")
async def index():
    html_path = Path(__file__).parent / "index.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>UTH — index.html not found</h1>")


# ==========================================
# SYSTEM STATUS
# ==========================================
@app.get("/api/status")
async def get_status():
    """Trạng thái hệ thống."""
    mimo = get_provider("mimo")
    local = get_provider("local")

    # Kiểm tra manga-image-translator
    manga_translator_available = False
    try:
        from src.pipelines.manga_image_translator_wrapper import MANGA_TRANSLATOR_PATH
        manga_translator_available = MANGA_TRANSLATOR_PATH.exists()
    except Exception:
        pass

    return {
        "version": "0.2.0",
        "providers": {
            "mimo": {
                "available": mimo.is_available(),
                "keys_count": len(mimo.api_keys) if hasattr(mimo, "api_keys") else 0,
                "models": mimo.list_models() if hasattr(mimo, "list_models") else {},
            },
            "local": {
                "available": local.is_available(),
                "backend_url": local.backend_url if hasattr(local, "backend_url") else "N/A",
            },
        },
        "manga_translator": {
            "available": manga_translator_available,
            "path": str(MANGA_TRANSLATOR_PATH) if manga_translator_available else "N/A",
        },
        "memory": memory.stats(),
        "upload_dir": str(UPLOAD_DIR),
        "output_dir": str(OUTPUT_DIR),
    }


# ==========================================
# TRANSLATION API
# ==========================================
@app.post("/api/translate")
async def translate(payload: dict = Body(...)):
    """Dịch text qua provider đã chọn."""
    text = payload.get("text", "")
    texts = payload.get("texts", [])
    source_lang = payload.get("source_lang", "auto")
    target_lang = payload.get("target_lang", "vi")
    provider_name = payload.get("provider", "auto")

    provider = get_provider(provider_name)

    if not provider.is_available():
        raise HTTPException(400, f"Provider '{provider_name}' không sẵn sàng")

    try:
        if texts:
            results = await provider.translate_batch(texts, source_lang, target_lang)
            return {"status": "success", "data": results, "provider": provider.get_name()}
        elif text:
            result = await provider.translate(text, source_lang, target_lang)
            return {"status": "success", "data": result, "provider": provider.get_name()}
        else:
            raise HTTPException(400, "Cần 'text' hoặc 'texts'")
    except Exception as e:
        raise HTTPException(500, f"Lỗi dịch: {str(e)}")


@app.post("/api/translate/subtitle")
async def translate_subtitle(payload: dict = Body(...)):
    """Dịch phụ đề (list events)."""
    events = payload.get("events", [])
    source_lang = payload.get("source_lang", "auto")
    target_lang = payload.get("target_lang", "vi")
    provider_name = payload.get("provider", "auto")

    if not events:
        raise HTTPException(400, "Cần 'events' list")

    provider = get_provider(provider_name)
    texts = [e.get("text", "") for e in events]

    try:
        translations = await provider.translate_batch(texts, source_lang, target_lang)
        for i, e in enumerate(events):
            e["translated"] = translations[i] if i < len(translations) else e["text"]
        return {"status": "success", "data": events, "provider": provider.get_name()}
    except Exception as e:
        raise HTTPException(500, f"Lỗi dịch subtitle: {str(e)}")


# ==========================================
# TTS API
# ==========================================
@app.post("/api/tts")
async def generate_tts(payload: dict = Body(...)):
    """Tạo audio TTS từ text."""
    text = payload.get("text", "")
    voice = payload.get("voice", "vi-VN-HoaiMyNeural")
    engine = payload.get("engine", "auto")  # "auto", "mimo", "edge"

    if not text:
        raise HTTPException(400, "Cần 'text'")

    provider = get_provider("auto")
    tts_agent = TTSAgent(provider=provider, tts_engine=engine)

    output_path = str(OUTPUT_DIR / f"tts_{hash(text) % 100000}.mp3")

    result = await tts_agent.execute({
        "text": text,
        "voice": voice,
        "output_path": output_path,
    })

    if result.get("success"):
        return FileResponse(output_path, media_type="audio/mpeg", filename="tts.mp3")
    else:
        raise HTTPException(500, result.get("error", "TTS lỗi"))


@app.post("/api/tts/batch")
async def generate_tts_batch(payload: dict = Body(...)):
    """Tạo audio TTS cho nhiều text."""
    texts = payload.get("texts", [])
    voice = payload.get("voice", "vi-VN-HoaiMyNeural")
    engine = payload.get("engine", "auto")

    if not texts:
        raise HTTPException(400, "Cần 'texts' list")

    provider = get_provider("auto")
    tts_agent = TTSAgent(provider=provider, tts_engine=engine)

    tts_dir = str(OUTPUT_DIR / "tts_batch")
    results = await tts_agent.generate_audio_batch(texts, tts_dir, voice)

    return {"status": "success", "data": results}


# ==========================================
# FILE UPLOAD
# ==========================================
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload file (subtitle, image, video)."""
    dest = UPLOAD_DIR / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_type = detect_pipeline(str(dest))

    return {
        "status": "success",
        "filename": file.filename,
        "path": str(dest),
        "size": dest.stat().st_size,
        "detected_type": file_type,
    }


# ==========================================
# PIPELINE APIs
# ==========================================
@app.post("/api/pipeline/game")
async def run_game_pipeline(payload: dict = Body(...)):
    """Chạy game translation pipeline."""
    input_path = payload.get("input", "")
    provider_name = payload.get("provider", "auto")
    engine = payload.get("engine", "")

    if not input_path:
        raise HTTPException(400, "Cần 'input' path")

    provider = get_provider(provider_name)
    pipeline = GamePipeline(provider, memory)

    options = {"source_lang": payload.get("source_lang", "auto"), "target_lang": payload.get("target_lang", "vi")}
    if engine:
        options["engine"] = engine

    result = await pipeline.execute(input_path, options)
    return {"status": "success" if result.success else "error", "data": {
        "pipeline": result.pipeline,
        "total": result.total_items,
        "translated": result.translated_items,
        "failed": result.failed_items,
        "errors": result.errors,
        "elapsed": result.elapsed_seconds,
        "details": result.details,
    }}


@app.post("/api/pipeline/manga")
async def run_manga_pipeline(payload: dict = Body(...)):
    """Chạy manga translation pipeline."""
    input_path = payload.get("input", "")
    provider_name = payload.get("provider", "auto")
    use_manga_translator = payload.get("use_manga_translator", True)

    if not input_path:
        raise HTTPException(400, "Cần 'input' path")

    provider = get_provider(provider_name)
    pipeline = MangaPipeline(provider, memory, use_manga_translator=use_manga_translator)

    options = {
        "source_lang": payload.get("source_lang", "ja"),
        "target_lang": payload.get("target_lang", "vi"),
        "use_manga_translator": use_manga_translator,
    }
    if payload.get("output_dir"):
        options["output_dir"] = payload["output_dir"]

    result = await pipeline.execute(input_path, options)
    return {"status": "success" if result.success else "error", "data": {
        "pipeline": result.pipeline,
        "total": result.total_items,
        "translated": result.translated_items,
        "errors": result.errors,
        "elapsed": result.elapsed_seconds,
    }}


@app.post("/api/pipeline/film")
async def run_film_pipeline(payload: dict = Body(...)):
    """Chạy film translation pipeline."""
    input_path = payload.get("input", "")
    subtitle_path = payload.get("subtitle", "")
    provider_name = payload.get("provider", "auto")
    voice = payload.get("voice", "vi-VN-HoaiMyNeural")

    if not input_path:
        raise HTTPException(400, "Cần 'input' path")

    provider = get_provider(provider_name)
    pipeline = FilmPipeline(provider, memory)

    options = {
        "source_lang": payload.get("source_lang", "auto"),
        "target_lang": payload.get("target_lang", "vi"),
        "voice": voice,
    }
    if subtitle_path:
        options["subtitle"] = subtitle_path
    if payload.get("output_dir"):
        options["output_dir"] = payload["output_dir"]

    result = await pipeline.execute(input_path, options)
    return {"status": "success" if result.success else "error", "data": {
        "pipeline": result.pipeline,
        "total": result.total_items,
        "translated": result.translated_items,
        "errors": result.errors,
        "elapsed": result.elapsed_seconds,
        "details": result.details,
    }}


# ==========================================
# QA (Quality Assurance)
# ==========================================
@app.post("/api/qa")
async def quality_check(payload: dict = Body(...)):
    """Kiểm tra chất lượng bản dịch."""
    original = payload.get("original", "")
    translated = payload.get("translated", "")
    source_lang = payload.get("source_lang", "auto")

    qa = QAAgent()
    result = await qa.execute({
        "original": original,
        "translated": translated,
        "source_lang": source_lang,
    })

    return {"status": "success", "data": result}


# ==========================================
# TRANSLATION MEMORY
# ==========================================
@app.get("/api/memory/stats")
async def memory_stats():
    return {"status": "success", "data": memory.stats()}


@app.post("/api/memory/clear")
async def memory_clear():
    memory.clear()
    return {"status": "success", "message": "Đã xóa Translation Memory"}


# ==========================================
# STARTUP
# ==========================================
if __name__ == "__main__":
    import uvicorn
    print("╔══════════════════════════════════════════════╗")
    print("║  Universal Translation Hub — Server v0.2.0  ║")
    print("║  http://localhost:8000                       ║")
    print("╚══════════════════════════════════════════════╝")
    uvicorn.run(app, host="0.0.0.0", port=8000)
