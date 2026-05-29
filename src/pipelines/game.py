"""Game Translation Pipeline — Dịch game qua AG-Translator backend."""
import httpx
import asyncio
import json
import csv
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base import BasePipeline, PipelineResult


class GamePipeline(BasePipeline):
    """
    Pipeline dịch game:
    1. Detect engine (auto hoặc manual)
    2. Scan game files
    3. Extract text → CSV
    4. Translate (qua provider + TM cache)
    5. Inject bản dịch về
    6. Validate
    """

    name = "game"

    def __init__(self, provider=None, memory=None, backend_url: str = "http://localhost:5000"):
        super().__init__(provider, memory)
        self.backend_url = backend_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(120.0))
        return self._client

    async def _api(self, method: str, path: str, **kwargs) -> dict:
        """Gọi AG-Translator backend API."""
        client = await self._get_client()
        url = f"{self.backend_url}{path}"
        try:
            resp = await client.request(method, url, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except httpx.ConnectError:
            raise RuntimeError(
                f"Không kết nối được AG-Translator backend tại {self.backend_url}. "
                "Hãy chạy: cd E:\\DichGame\\Backend && python server.py"
            )
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"API error {e.response.status_code}: {e.response.text}")

    async def run(self, input_path: str, options: Dict[str, Any] = None) -> PipelineResult:
        opts = options or {}
        result = PipelineResult(pipeline="game", input_path=input_path)
        source_lang = opts.get("source_lang", "auto")
        target_lang = opts.get("target_lang", "vi")
        engine_override = opts.get("engine", None)

        try:
            # Step 1: Detect engine
            self.log("1/6", f"Detect engine: {input_path}")
            if engine_override:
                engine = engine_override
                self.log("1/6", f"Engine override: {engine}")
            else:
                detect_data = await self._api("POST", "/api/pipeline/detect", json={"game_dir": input_path})
                engine = detect_data.get("engine", "unknown")
                self.log("1/6", f"Detected: {engine}")

            result.details["engine"] = engine

            # Step 2: Scan
            self.log("2/6", f"Scanning files ({engine})...")
            scan_data = await self._api("POST", f"/api/{engine}/scan", json={"source_dir": input_path})
            files = scan_data.get("files", scan_data.get("data", []))
            self.log("2/6", f"Found {len(files)} files")

            # Step 3: Extract text
            self.log("3/6", "Extracting text...")
            extract_data = await self._api("POST", f"/api/{engine}/extract", json={
                "source_dir": input_path,
                "files": files if isinstance(files, list) else None
            })
            entries = extract_data.get("entries", extract_data.get("data", []))

            # Build texts_dict từ entries
            texts_dict = {}
            if isinstance(entries, list):
                for i, entry in enumerate(entries):
                    if isinstance(entry, dict):
                        text = entry.get("original", entry.get("text", ""))
                    else:
                        text = str(entry)
                    if text.strip():
                        texts_dict[str(i)] = text
            elif isinstance(entries, dict):
                texts_dict = entries

            result.total_items = len(texts_dict)
            self.log("3/6", f"Extracted {len(texts_dict)} text entries")

            if not texts_dict:
                result.success = True
                return result

            # Step 4: Translate
            self.log("4/6", f"Translating {len(texts_dict)} entries...")
            translated_dict = {}

            if self.provider:
                # Dịch qua provider + TM cache
                texts_list = list(texts_dict.values())
                keys_list = list(texts_dict.keys())

                # Check TM cache
                uncached_texts = []
                uncached_indices = []
                for i, text in enumerate(texts_list):
                    cached = None
                    if self.memory:
                        cached = self.memory.get(text, source_lang, target_lang)
                    if cached:
                        translated_dict[keys_list[i]] = cached
                    else:
                        uncached_texts.append(text)
                        uncached_indices.append(i)

                self.log("4/6", f"Cache hits: {len(texts_list) - len(uncached_texts)}, need translate: {len(uncached_texts)}")

                if uncached_texts:
                    # Gọi provider dịch batch
                    try:
                        batch_result = await self.provider.translate_batch(
                            uncached_texts, source_lang, target_lang
                        )
                        for j, idx in enumerate(uncached_indices):
                            key = keys_list[idx]
                            translated = batch_result[j] if j < len(batch_result) else uncached_texts[j]
                            translated_dict[key] = translated
                            # Lưu vào TM
                            if self.memory:
                                self.memory.put(uncached_texts[j], translated, source_lang, target_lang)
                    except Exception as e:
                        self.log("4/6", f"Provider error: {e}, fallback to original")
                        for j, idx in enumerate(uncached_indices):
                            translated_dict[keys_list[idx]] = uncached_texts[j]

                result.translated_items = len(translated_dict)
            else:
                # Không có provider, giữ nguyên
                translated_dict = texts_dict
                result.translated_items = 0

            # Step 5: Inject
            self.log("5/6", "Injecting translations...")
            inject_result = await self._api("POST", f"/api/{engine}/inject", json={
                "source_dir": input_path,
                "translations": translated_dict
            })
            result.details["inject"] = inject_result

            # Step 6: Validate
            self.log("6/6", "Validating...")
            try:
                validate_result = await self._api("POST", f"/api/{engine}/validate", json={
                    "source_dir": input_path
                })
                result.details["validate"] = validate_result
            except Exception:
                self.log("6/6", "Validate endpoint không có, bỏ qua")

            result.success = True
            result.output_path = input_path

        except Exception as e:
            result.errors.append(str(e))
            result.success = False

        finally:
            if self._client:
                await self._client.aclose()
                self._client = None

        return result

    async def validate(self, result: PipelineResult) -> List[str]:
        errors = []
        if not result.success:
            errors.append("Pipeline không thành công")
        if result.total_items > 0 and result.translated_items == 0:
            errors.append("Không có câu nào được dịch")
        if result.failed_items > result.total_items * 0.5:
            errors.append(f"Quy nhiều lỗi: {result.failed_items}/{result.total_items}")
        return errors
