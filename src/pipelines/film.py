"""Film/Video Dubbing Pipeline — Subtitle + Translate + TTS + Sync."""
import os
import re
import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base import BasePipeline, PipelineResult


class FilmPipeline(BasePipeline):
    """
    Pipeline dịch phim + thuyết minh:
    1. Extract subtitles (từ file hoặc OCR embedded subs)
    2. Translate subtitles
    3. Generate TTS audio (edge-tts)
    4. Sync audio với video (FFmpeg)
    5. Export translated subtitle + dubbed video
    """

    name = "film"

    def __init__(self, provider=None, memory=None):
        super().__init__(provider, memory)

    def _find_subtitle(self, video_path: str, subtitle_path: str = "") -> Optional[Path]:
        """Tìm file subtitle (explicit hoặc tự tìm)."""
        if subtitle_path and os.path.exists(subtitle_path):
            return Path(subtitle_path)

        # Tìm subtitle cùng thư mục với video
        video = Path(video_path)
        sub_exts = {".ass", ".srt", ".vtt", ".sub", ".ssa"}
        for ext in sub_exts:
            candidate = video.with_suffix(ext)
            if candidate.exists():
                return candidate

        # Tìm trong thư mục con
        for f in video.parent.rglob("*"):
            if f.suffix.lower() in sub_exts and video.stem in f.stem:
                return f

        return None

    def _load_subtitles(self, sub_path: Path) -> List[Dict]:
        """Load subtitle file, trả về list events."""
        try:
            import pysubs2
            subs = pysubs2.load(str(sub_path), encoding="utf-8")
            events = []
            for line in subs:
                text = self._clean_ass_text(line.text)
                if text and len(text) >= 2:
                    events.append({
                        "start_ms": line.start,
                        "end_ms": line.end,
                        "text": text,
                        "original_text": line.text,  # Giữ nguyên format ASS
                    })
            return events
        except ImportError:
            print("  [film] Cần cài pysubs2: pip install pysubs2")
            return []
        except Exception as e:
            print(f"  [film] Lỗi load subtitle: {e}")
            return []

    def _clean_ass_text(self, text: str) -> str:
        """Làm sạch text ASS: loại bỏ tags, formatting."""
        text = re.sub(r'\{[^}]*\}', '', text)  # {\b1}, {\pos(x,y)}
        text = text.replace('\\N', ' ').replace('\\n', ' ')
        text = re.sub(r'\\[a-zA-Z]+\([^)]*\)', '', text)  # \fad(200,200)
        return text.strip()

    async def _translate_subtitles(self, events: List[Dict], source_lang: str, target_lang: str) -> List[Dict]:
        """Dịch tất cả subtitle events."""
        if not events:
            return []

        texts = [e["text"] for e in events]
        translations = [None] * len(texts)

        # Check TM cache
        uncached = []
        uncached_idx = []
        for i, text in enumerate(texts):
            cached = None
            if self.memory:
                cached = self.memory.get(text, source_lang, target_lang)
            if cached:
                translations[i] = cached
            else:
                uncached.append(text)
                uncached_idx.append(i)

        print(f"  [film] Cache: {len(texts) - len(uncached)} hits, {len(uncached)} cần dịch")

        # Dịch uncached
        if uncached and self.provider:
            try:
                batch_result = await self.provider.translate_batch(uncached, source_lang, target_lang)
                for j, idx in enumerate(uncached_idx):
                    translated = batch_result[j] if j < len(batch_result) else uncached[j]
                    translations[idx] = translated
                    if self.memory:
                        self.memory.put(uncached[j], translated, source_lang, target_lang)
            except Exception as e:
                print(f"  [film] Lỗi dịch batch: {e}")
                # Fallback: dịch từng câu
                for j, idx in enumerate(uncached_idx):
                    try:
                        translated = await self.provider.translate(uncached[j], source_lang, target_lang)
                        translations[idx] = translated
                    except Exception:
                        translations[idx] = uncached[j]
        else:
            for j, idx in enumerate(uncached_idx):
                translations[idx] = uncached[j]

        # Gán translation
        for i, event in enumerate(events):
            event["translated"] = translations[i] if translations[i] else event["text"]

        return events

    async def _generate_tts(self, events: List[Dict], output_dir: str, voice: str = "vi-VN-HoaiMyNeural") -> List[Dict]:
        """Tạo audio TTS cho mỗi subtitle event."""
        try:
            import edge_tts
        except ImportError:
            print("  [film] Cần cài edge-tts: pip install edge-tts")
            return events

        os.makedirs(output_dir, exist_ok=True)
        audio_files = []

        for i, event in enumerate(events):
            text = event.get("translated", event["text"])
            if not text or len(text) < 2:
                audio_files.append(None)
                continue

            audio_path = os.path.join(output_dir, f"tts_{i:04d}.mp3")
            try:
                communicate = edge_tts.Communicate(text, voice, rate="+15%", pitch="+0Hz")
                await communicate.save(audio_path)
                event["audio_path"] = audio_path
                audio_files.append(audio_path)
            except Exception as e:
                print(f"  [film] TTS lỗi [{i}]: {e}")
                audio_files.append(None)

        return events

    async def _generate_subtitle_file(self, events: List[Dict], output_path: str, format: str = "ass"):
        """Tạo file subtitle đã dịch."""
        try:
            import pysubs2

            subs = pysubs2.SSAFile()
            for event in events:
                line = pysubs2.SSAEvent()
                line.start = event["start_ms"]
                line.end = event["end_ms"]
                line.text = event.get("translated", event["text"])
                subs.events.append(line)

            subs.save(output_path, encoding="utf-8")
            print(f"  [film] Đã lưu subtitle: {output_path}")
        except ImportError:
            # Fallback: lưu SRT đơn giản
            self._save_srt_fallback(events, output_path)

    def _save_srt_fallback(self, events: List[Dict], output_path: str):
        """Lưu subtitle dạng SRT nếu không có pysubs2."""
        srt_path = Path(output_path).with_suffix(".srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, event in enumerate(events, 1):
                start = self._ms_to_srt_time(event["start_ms"])
                end = self._ms_to_srt_time(event["end_ms"])
                text = event.get("translated", event["text"])
                f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    def _ms_to_srt_time(self, ms: int) -> str:
        """Convert milliseconds sang SRT time format."""
        h = ms // 3600000
        m = (ms % 3600000) // 60000
        s = (ms % 60000) // 1000
        ms_r = ms % 1000
        return f"{h:02d}:{m:02d}:{s:02d},{ms_r:03d}"

    async def _merge_audio_video(self, video_path: str, audio_dir: str, events: List[Dict], output_path: str):
        """Merge TTS audio vào video bằng FFmpeg."""
        # Kiểm tra FFmpeg
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("  [film] FFmpeg không tìm thấy. Bỏ qua merge audio.")
            return

        # Tạo file concat audio
        concat_list = os.path.join(audio_dir, "concat.txt")
        with open(concat_list, "w", encoding="utf-8") as f:
            for event in events:
                audio = event.get("audio_path")
                if audio and os.path.exists(audio):
                    duration = (event["end_ms"] - event["start_ms"]) / 1000.0
                    f.write(f"file '{audio}'\n")
                    f.write(f"duration {duration}\n")

        # Merge audio tracks
        merged_audio = os.path.join(audio_dir, "merged_tts.mp3")
        try:
            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", concat_list, "-c", "copy", merged_audio
            ], capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"  [film] Lỗi merge audio: {e}")
            return

        # Overlay audio lên video
        try:
            subprocess.run([
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", merged_audio,
                "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[aout]",
                "-map", "0:v", "-map", "[aout]",
                "-c:v", "copy", "-c:a", "aac",
                output_path
            ], capture_output=True, check=True)
            print(f"  [film] Đã merge audio+video: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"  [film] Lỗi merge video: {e}")

    async def run(self, input_path: str, options: Dict[str, Any] = None) -> PipelineResult:
        opts = options or {}
        result = PipelineResult(pipeline="film", input_path=input_path)
        source_lang = opts.get("source_lang", "auto")
        target_lang = opts.get("target_lang", "vi")
        voice = opts.get("voice", "vi-VN-HoaiMyNeural")
        subtitle_path = opts.get("subtitle", "")
        output_dir = opts.get("output_dir", str(Path(input_path).parent / "output"))

        os.makedirs(output_dir, exist_ok=True)
        result.output_path = output_dir

        try:
            # Step 1: Find & load subtitle
            self.log("1/5", "Tìm file subtitle...")
            sub_path = self._find_subtitle(input_path, subtitle_path)
            if not sub_path:
                result.errors.append("Không tìm thấy file subtitle (.ass/.srt/.vtt)")
                return result

            events = self._load_subtitles(sub_path)
            result.total_items = len(events)
            self.log("1/5", f"Loaded {len(events)} subtitle events từ {sub_path.name}")

            if not events:
                result.errors.append("File subtitle rỗng hoặc không đọc được")
                return result

            # Step 2: Translate
            self.log("2/5", f"Translating {len(events)} events...")
            events = await self._translate_subtitles(events, source_lang, target_lang)
            result.translated_items = sum(1 for e in events if e.get("translated"))

            # Step 3: Save translated subtitle
            sub_output = os.path.join(output_dir, f"{Path(input_path).stem}_vi.ass")
            await self._generate_subtitle_file(events, sub_output)

            # Step 4: Generate TTS
            self.log("3/5", f"Generating TTS audio ({voice})...")
            tts_dir = os.path.join(output_dir, "tts_audio")
            events = await self._generate_tts(events, tts_dir, voice)
            tts_count = sum(1 for e in events if e.get("audio_path"))
            self.log("3/5", f"Generated {tts_count} audio files")

            # Step 5: Merge (nếu có video)
            video_exts = {".mkv", ".mp4", ".avi", ".mov"}
            if Path(input_path).suffix.lower() in video_exts:
                self.log("4/5", "Merging audio + video...")
                video_output = os.path.join(output_dir, f"{Path(input_path).stem}_vi.mp4")
                await self._merge_audio_video(input_path, tts_dir, events, video_output)
            else:
                self.log("4/5", "Không có video, chỉ xuất subtitle + audio")

            self.log("5/5", "Hoàn tất!")
            result.success = True
            result.details = {
                "subtitle_file": sub_output,
                "tts_count": tts_count,
                "total_events": len(events),
            }

        except Exception as e:
            result.errors.append(str(e))
            result.success = False

        return result

    async def validate(self, result: PipelineResult) -> List[str]:
        errors = []
        if not result.success:
            errors.append("Pipeline không thành công")
        if result.total_items > 0 and result.translated_items == 0:
            errors.append("Không có subtitle nào được dịch")
        if result.translated_items < result.total_items * 0.5:
            errors.append(f"Ít bản dịch: {result.translated_items}/{result.total_items}")
        return errors
