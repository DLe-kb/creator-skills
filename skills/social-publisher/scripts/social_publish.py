#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SPECS_FILE = SCRIPT_DIR / "platform_specs.json"
DEFAULT_HOME = Path.home() / ".config" / "open-creator" / "social-publisher"


class PublishError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PublishError(f"文件不存在: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PublishError(f"JSON 格式错误: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise PublishError(f"JSON 顶层必须是对象: {path}")
    return data


def specs() -> dict[str, Any]:
    return load_json(SPECS_FILE)


def runtime_home() -> Path:
    return Path(os.environ.get("SOCIAL_PUBLISHER_HOME", DEFAULT_HOME)).expanduser()


def resolve_asset(package_path: Path, value: Any) -> Path | None:
    if not value:
        return None
    path = Path(str(value)).expanduser()
    return path if path.is_absolute() else (package_path.parent / path).resolve()


def metadata_for(package: dict[str, Any], platform: str) -> dict[str, Any]:
    merged = dict(package.get("defaults") or {})
    platform_data = (package.get("platforms") or {}).get(platform) or {}
    if not isinstance(platform_data, dict):
        raise PublishError(f"platforms.{platform} 必须是对象")
    merged.update(platform_data)
    tags = merged.get("tags") or []
    if isinstance(tags, str):
        tags = [item.strip().lstrip("#") for item in tags.split(",") if item.strip()]
    if not isinstance(tags, list):
        raise PublishError(f"{platform} 的 tags 必须是数组或逗号分隔字符串")
    merged["tags"] = [str(tag).strip().lstrip("#") for tag in tags if str(tag).strip()]
    return merged


def ffprobe(path: Path) -> dict[str, Any] | None:
    executable = shutil.which("ffprobe")
    if not executable:
        return None
    command = [
        executable,
        "-v", "error",
        "-show_entries", "format=duration,bit_rate:stream=codec_type,codec_name,width,height,bit_rate",
        "-of", "json",
        str(path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise PublishError(f"ffprobe 无法读取素材: {path}: {result.stderr.strip()}")
    return json.loads(result.stdout)


def media_summary(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {"path": str(path), "bytes": path.stat().st_size}
    probe = ffprobe(path)
    if not probe:
        return result
    format_data = probe.get("format") or {}
    result["duration_seconds"] = float(format_data.get("duration") or 0)
    result["bit_rate"] = int(float(format_data.get("bit_rate") or 0))
    for stream in probe.get("streams") or []:
        if stream.get("codec_type") == "video":
            result.update({
                "codec": stream.get("codec_name"),
                "width": int(stream.get("width") or 0),
                "height": int(stream.get("height") or 0),
            })
            break
    return result


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_package(package_path: Path, platform_names: list[str], metadata_only: bool) -> dict[str, Any]:
    package = load_json(package_path)
    available = specs()
    errors: list[str] = []
    warnings: list[str] = []

    if package.get("version") != 1:
        errors.append("version 必须为 1")
    content_id = str(package.get("content_id") or "").strip()
    if not content_id:
        errors.append("缺少 content_id")

    configured = package.get("platforms") or {}
    if not isinstance(configured, dict):
        errors.append("platforms 必须是对象")
        configured = {}
    targets = platform_names or list(configured)
    if not targets:
        errors.append("没有目标平台")

    video_path = resolve_asset(package_path, package.get("video"))
    cover_path = resolve_asset(package_path, package.get("cover"))
    video_info: dict[str, Any] = {}
    cover_info: dict[str, Any] = {}
    if not metadata_only:
        if not video_path or not video_path.is_file():
            errors.append(f"视频文件不存在: {video_path}")
        else:
            video_info = media_summary(video_path)
        if cover_path:
            if not cover_path.is_file():
                errors.append(f"封面文件不存在: {cover_path}")
            else:
                cover_info = media_summary(cover_path)

    platform_results: dict[str, Any] = {}
    for platform in targets:
        if platform not in available:
            errors.append(f"不支持的平台: {platform}")
            continue
        meta = metadata_for(package, platform)
        limits = available[platform].get("limits") or {}
        platform_errors: list[str] = []
        platform_warnings: list[str] = []

        for field in available[platform].get("required_fields") or []:
            value = meta.get(field)
            if field not in meta or value is None or isinstance(value, str) and not value.strip():
                platform_errors.append(f"缺少必填字段 {field}")

        for field in ("title", "description", "short_title"):
            value = str(meta.get(field) or "")
            maximum = limits.get(f"{field}_max")
            minimum = limits.get(f"{field}_min")
            if maximum and len(value) > maximum:
                platform_errors.append(f"{field} 长度 {len(value)} 超过 {maximum}")
            if minimum and value and len(value) < minimum:
                platform_errors.append(f"{field} 长度 {len(value)} 少于 {minimum}")

        tag_text = ",".join(meta.get("tags") or [])
        if limits.get("tags_total_max") and len(tag_text) > limits["tags_total_max"]:
            platform_errors.append(f"标签总长度 {len(tag_text)} 超过 {limits['tags_total_max']}")
        if platform != "youtube" and limits.get("description_max") and meta.get("tags"):
            combined = (str(meta.get("description") or "") + "\n" + " ".join(
                f"#{tag}" for tag in meta["tags"]
            )).strip()
            if len(combined) > limits["description_max"]:
                platform_errors.append(
                    f"正文加标签长度 {len(combined)} 超过 {limits['description_max']}"
                )

        if video_info:
            if limits.get("video_max_bytes") and video_info["bytes"] > limits["video_max_bytes"]:
                platform_errors.append("视频文件大小超过平台预检上限")
            if limits.get("duration_max_seconds") and video_info.get("duration_seconds", 0) > limits["duration_max_seconds"]:
                platform_errors.append("视频时长超过平台预检上限")
            if limits.get("min_width") and video_info.get("width", 0) < limits["min_width"]:
                platform_warnings.append("视频宽度低于平台建议值")
            if limits.get("max_width") and video_info.get("width", 0) > limits["max_width"]:
                platform_errors.append("视频宽度超过平台预检上限")
            if limits.get("max_video_bitrate") and video_info.get("bit_rate", 0) > limits["max_video_bitrate"]:
                platform_warnings.append("视频总码率高于平台建议值")

        if platform == "youtube" and cover_info:
            width, height = cover_info.get("width", 0), cover_info.get("height", 0)
            if width and width < limits.get("cover_min_width", 0):
                platform_warnings.append("YouTube 缩略图宽度低于建议值")
            if width and height and abs(width / height - limits["cover_aspect_ratio"]) > 0.08:
                platform_warnings.append("YouTube 缩略图不是接近 16:9")

        errors.extend(f"{platform}: {item}" for item in platform_errors)
        warnings.extend(f"{platform}: {item}" for item in platform_warnings)
        platform_results[platform] = {
            "route": available[platform]["default_route"],
            "metadata": meta,
            "errors": platform_errors,
            "warnings": platform_warnings,
        }

    return {
        "ok": not errors,
        "content_id": content_id,
        "video": video_info,
        "cover": cover_info,
        "platforms": platform_results,
        "errors": errors,
        "warnings": warnings,
    }


def print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def doctor() -> int:
    available = specs()
    google_ready = all(
        importlib.util.find_spec(module) is not None
        for module in ("googleapiclient", "google_auth_oauthlib")
    )
    playwright_ready = importlib.util.find_spec("playwright") is not None
    result = {
        "free_mode": True,
        "runtime_home": str(runtime_home()),
        "dependencies": {
            "python": sys.version.split()[0],
            "playwright": playwright_ready,
            "youtube_api": google_ready,
            "ffprobe": shutil.which("ffprobe"),
            "biliup": shutil.which("biliup"),
        },
        "platforms": {
            name: {
                "route": data["default_route"],
                "free": data["free"],
                "ready": (
                    bool(shutil.which("biliup")) if name == "bilibili"
                    else google_ready if name == "youtube"
                    else playwright_ready
                ),
            }
            for name, data in available.items()
        },
    }
    print_json(result)
    return 0


def browser_executable() -> str | None:
    candidates = [
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def require_playwright():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise PublishError(
            "缺少 Playwright。安装命令: python3 -m pip install playwright && python3 -m playwright install chromium"
        ) from exc
    return sync_playwright


def require_youtube_api():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError as exc:
        raise PublishError(
            "缺少 YouTube API 依赖。安装命令: python3 -m pip install -r scripts/requirements.txt"
        ) from exc
    return Request, Credentials, InstalledAppFlow, build, MediaFileUpload


def youtube_token_path(account: str) -> Path:
    safe_account = "".join(char for char in account if char.isalnum() or char in "-_")
    if not safe_account:
        raise PublishError("账号别名只能包含字母、数字、连字符或下划线")
    path = runtime_home() / "oauth" / "youtube" / f"{safe_account}.json"
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path


def youtube_client_secrets(explicit: Path | None) -> Path:
    raw = str(explicit) if explicit else os.environ.get("YOUTUBE_CLIENT_SECRETS", "")
    if not raw:
        raise PublishError("请使用 --client-secrets 或 YOUTUBE_CLIENT_SECRETS 指定 Google OAuth 客户端文件")
    path = Path(raw).expanduser().resolve()
    if not path.is_file():
        raise PublishError(f"Google OAuth 客户端文件不存在: {path}")
    return path


def youtube_service(account: str, client_secrets: Path | None):
    Request, Credentials, InstalledAppFlow, build, MediaFileUpload = require_youtube_api()
    token_path = youtube_token_path(account)
    credentials = None
    if token_path.is_file():
        credentials = Credentials.from_authorized_user_file(
            str(token_path), ["https://www.googleapis.com/auth/youtube.upload"]
        )
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(youtube_client_secrets(client_secrets)),
            ["https://www.googleapis.com/auth/youtube.upload"],
        )
        credentials = flow.run_local_server(port=0)
    token_path.write_text(credentials.to_json() + "\n", encoding="utf-8")
    os.chmod(token_path, 0o600)
    return build("youtube", "v3", credentials=credentials), MediaFileUpload


def profile_dir(platform: str, account: str) -> Path:
    safe_account = "".join(char for char in account if char.isalnum() or char in "-_")
    if not safe_account:
        raise PublishError("账号别名只能包含字母、数字、连字符或下划线")
    path = runtime_home() / "profiles" / platform / safe_account
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path


def fill_first(page: Any, selectors: list[str], value: str) -> bool:
    if not value:
        return False
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            if locator.count() and locator.is_visible(timeout=1000):
                locator.click()
                try:
                    locator.fill(value)
                except Exception:
                    page.keyboard.press("Meta+A")
                    page.keyboard.type(value, delay=5)
                return True
        except Exception:
            continue
    return False


def report_path(fingerprint: str) -> Path:
    path = runtime_home() / "reports" / f"{fingerprint}.json"
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path


def write_report(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(path, 0o600)


def task_fingerprint(content_id: str, platform: str, account: str, video_hash: str) -> str:
    raw = f"{content_id}\0{platform}\0{account}\0{video_hash}".encode()
    return hashlib.sha256(raw).hexdigest()[:24]


def login(platform: str, account: str, client_secrets: Path | None) -> int:
    data = specs().get(platform)
    if not data or platform == "bilibili":
        raise PublishError("B站登录态由 biliup 管理，其他情况请检查平台名称")
    if platform == "youtube":
        youtube_service(account, client_secrets)
        print_json({"platform": "youtube", "account": account, "status": "authorized"})
        return 0
    sync_playwright = require_playwright()
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            str(profile_dir(platform, account)),
            headless=False,
            executable_path=browser_executable(),
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(data["login_url"], wait_until="domcontentloaded", timeout=60000)
        input("完成登录并确认进入创作者后台后，按 Enter 保存本地登录态...")
        context.close()
    return 0


def browser_action(package_path: Path, platform: str, account: str, execute: bool, authorized: bool, dry_run: bool, force: bool) -> int:
    if execute and not authorized:
        raise PublishError("正式发布必须同时提供 --execute 和 --authorized")
    if platform == "bilibili":
        raise PublishError("B站继续使用已有 biliup；本命令不接管其发布配置")
    if platform == "youtube":
        raise PublishError("YouTube 必须使用官方 API 路线")

    validation = validate_package(package_path, [platform], metadata_only=False)
    if not validation["ok"]:
        print_json(validation)
        raise PublishError("发布包校验失败")

    package = load_json(package_path)
    meta = validation["platforms"][platform]["metadata"]
    video = Path(validation["video"]["path"])
    cover = Path(validation["cover"]["path"]) if validation["cover"] else None
    video_hash = sha256(video)
    fingerprint = task_fingerprint(validation["content_id"], platform, account, video_hash)
    ledger = report_path(fingerprint)
    previous = load_json(ledger) if ledger.exists() else None
    if execute and previous and previous.get("status") in {"published", "uncertain"} and not force:
        raise PublishError(f"任务已有 {previous['status']} 记录，拒绝重复发布；确认后可使用 --force")

    summary = {
        "content_id": validation["content_id"],
        "platform": platform,
        "account": account,
        "route": "browser-local-free",
        "video": str(video),
        "video_sha256": video_hash,
        "title": meta.get("title") or meta.get("short_title"),
        "visibility": meta.get("visibility", "public"),
        "execute": execute,
    }
    if dry_run:
        print_json({"status": "validated", **summary, "actions": ["open visible browser", "upload video", "fill platform fields", "stop before final publish" if not execute else "click final publish"]})
        return 0

    spec = specs()[platform]
    sync_playwright = require_playwright()
    started = time.time()
    status = "failed"
    result_url = None
    error = None
    screenshot_path = runtime_home() / "screenshots" / f"{fingerprint}.png"
    screenshot_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

    try:
        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                str(profile_dir(platform, account)),
                headless=False,
                executable_path=browser_executable(),
                viewport={"width": 1440, "height": 1000},
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(spec["publish_url"], wait_until="domcontentloaded", timeout=60000)

            file_input = page.locator("input[type='file']").first
            file_input.wait_for(state="attached", timeout=30000)
            file_input.set_input_files(str(video))
            page.wait_for_timeout(6000)

            selectors = spec.get("selectors") or {}
            title = str(meta.get("title") or "")
            short_title = str(meta.get("short_title") or title)
            description = str(meta.get("description") or "")
            tags = meta.get("tags") or []
            combined_description = description
            if tags and platform not in {"youtube"}:
                combined_description = (description + "\n" + " ".join(f"#{tag}" for tag in tags)).strip()

            filled = {
                "title": fill_first(page, selectors.get("title") or [], title),
                "short_title": fill_first(page, selectors.get("short_title") or [], short_title),
                "description": fill_first(page, selectors.get("description") or [], combined_description),
                "tags": fill_first(page, selectors.get("tags") or [], ",".join(tags)),
            }
            if cover:
                image_input = page.locator("input[type='file'][accept*='image']").first
                try:
                    if image_input.count():
                        image_input.set_input_files(str(cover))
                        filled["cover"] = True
                except Exception:
                    filled["cover"] = False

            page.screenshot(path=str(screenshot_path), full_page=True)
            if not execute:
                status = "prepared"
                print_json({"status": status, **summary, "filled": filled, "screenshot": str(screenshot_path)})
                input("请在浏览器检查账号、封面、文案、声明和可见范围。不要点击发布；检查后按 Enter 退出...")
            else:
                print_json({
                    "status": "awaiting_confirmation",
                    **summary,
                    "filled": filled,
                    "screenshot": str(screenshot_path),
                })
                confirmation = input(
                    "请检查当前浏览器页面。确认账号、封面、文案、声明和可见范围无误后，输入 PUBLISH: "
                )
                if confirmation != "PUBLISH":
                    status = "awaiting_confirmation"
                    raise PublishError("用户未输入 PUBLISH，已停止最终发布")
                clicked = False
                for selector in selectors.get("publish") or []:
                    button = page.locator(selector).first
                    try:
                        if button.count() and button.is_visible(timeout=1000) and button.is_enabled(timeout=1000):
                            button.click()
                            clicked = True
                            break
                    except Exception:
                        continue
                if not clicked:
                    raise PublishError("未找到唯一且可用的最终发布按钮，已停止")
                page.wait_for_timeout(5000)
                result_url = page.url
                success_text = page.get_by_text("发布成功", exact=False)
                status = "published" if success_text.count() else "uncertain"
                page.screenshot(path=str(screenshot_path), full_page=True)
                print_json({"status": status, **summary, "result_url": result_url, "screenshot": str(screenshot_path)})
            context.close()
    except Exception as exc:
        error = str(exc)
        if isinstance(exc, PublishError):
            raise
    finally:
        write_report(ledger, {
            **summary,
            "fingerprint": fingerprint,
            "status": status,
            "result_url": result_url,
            "error": error,
            "screenshot": str(screenshot_path) if screenshot_path.exists() else None,
            "started_at_unix": started,
            "finished_at_unix": time.time(),
        })

    if error:
        raise PublishError(error)
    return 0


def youtube_action(
    package_path: Path,
    account: str,
    execute: bool,
    authorized: bool,
    dry_run: bool,
    force: bool,
    client_secrets: Path | None,
) -> int:
    if execute and not authorized:
        raise PublishError("正式发布必须同时提供 --execute 和 --authorized")
    validation = validate_package(package_path, ["youtube"], metadata_only=False)
    if not validation["ok"]:
        print_json(validation)
        raise PublishError("发布包校验失败")

    meta = validation["platforms"]["youtube"]["metadata"]
    if "made_for_kids" not in meta:
        raise PublishError("YouTube 必须明确设置 made_for_kids")
    visibility = str(meta.get("visibility") or "private")
    if visibility not in {"private", "unlisted", "public"}:
        raise PublishError("YouTube visibility 必须是 private、unlisted 或 public")

    video = Path(validation["video"]["path"])
    cover = Path(validation["cover"]["path"]) if validation["cover"] else None
    video_hash = sha256(video)
    fingerprint = task_fingerprint(validation["content_id"], "youtube", account, video_hash)
    ledger = report_path(fingerprint)
    previous = load_json(ledger) if ledger.exists() else None
    if execute and previous and previous.get("status") in {"published", "uncertain"} and not force:
        raise PublishError(f"任务已有 {previous['status']} 记录，拒绝重复发布；确认后可使用 --force")

    summary = {
        "content_id": validation["content_id"],
        "platform": "youtube",
        "account": account,
        "route": "youtube-data-api-free-quota",
        "video": str(video),
        "video_sha256": video_hash,
        "title": meta.get("title"),
        "visibility": visibility,
        "execute": execute,
    }
    if dry_run or not execute:
        print_json({
            "status": "validated" if dry_run else "awaiting_confirmation",
            **summary,
            "actions": [
                "OAuth authorize",
                "upload video with videos.insert",
                "set thumbnail" if cover else "skip custom thumbnail",
                "return video ID and URL",
            ],
        })
        return 0

    status = "failed"
    result_url = None
    error = None
    started = time.time()
    try:
        service, MediaFileUpload = youtube_service(account, client_secrets)
        body = {
            "snippet": {
                "title": str(meta.get("title") or ""),
                "description": str(meta.get("description") or ""),
                "tags": meta.get("tags") or [],
                "categoryId": str(meta.get("category_id") or "22"),
            },
            "status": {
                "privacyStatus": visibility,
                "selfDeclaredMadeForKids": bool(meta["made_for_kids"]),
            },
        }
        request = service.videos().insert(
            part="snippet,status",
            body=body,
            media_body=MediaFileUpload(str(video), chunksize=-1, resumable=True),
            notifySubscribers=bool(meta.get("notify_subscribers", True)),
        )
        response = None
        while response is None:
            progress, response = request.next_chunk()
            if progress:
                print_json({"platform": "youtube", "upload_progress": round(progress.progress(), 4)})
        video_id = response.get("id") if isinstance(response, dict) else None
        if not video_id:
            status = "uncertain"
            raise PublishError("YouTube API 未返回 video ID")
        if cover:
            service.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(cover), resumable=False),
            ).execute()
        result_url = f"https://youtu.be/{video_id}"
        status = "published"
        print_json({"status": status, **summary, "video_id": video_id, "result_url": result_url})
    except Exception as exc:
        error = str(exc)
        if status != "uncertain":
            status = "failed"
    finally:
        write_report(ledger, {
            **summary,
            "fingerprint": fingerprint,
            "status": status,
            "result_url": result_url,
            "error": error,
            "started_at_unix": started,
            "finished_at_unix": time.time(),
        })
    if error:
        raise PublishError(error)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Free local-first social video publisher")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor")

    validate = subparsers.add_parser("validate")
    validate.add_argument("package", type=Path)
    validate.add_argument("--platform", action="append", default=[])
    validate.add_argument("--metadata-only", action="store_true")

    login_parser = subparsers.add_parser("login")
    login_parser.add_argument("platform", choices=sorted(specs()))
    login_parser.add_argument("--account", default="main")
    login_parser.add_argument("--client-secrets", type=Path)

    for command in ("prepare", "publish"):
        action = subparsers.add_parser(command)
        action.add_argument("package", type=Path)
        action.add_argument("--platform", required=True, choices=sorted(specs()))
        action.add_argument("--account", default="main")
        action.add_argument("--dry-run", action="store_true")
        action.add_argument("--execute", action="store_true")
        action.add_argument("--authorized", action="store_true")
        action.add_argument("--force", action="store_true")
        action.add_argument("--client-secrets", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "doctor":
            return doctor()
        if args.command == "validate":
            result = validate_package(args.package.resolve(), args.platform, args.metadata_only)
            print_json(result)
            return 0 if result["ok"] else 1
        if args.command == "login":
            return login(args.platform, args.account, args.client_secrets)
        if args.command in {"prepare", "publish"}:
            execute = args.command == "publish" or args.execute
            if args.platform == "youtube":
                return youtube_action(
                    args.package.resolve(),
                    args.account,
                    execute,
                    args.authorized,
                    args.dry_run,
                    args.force,
                    args.client_secrets,
                )
            return browser_action(args.package.resolve(), args.platform, args.account, execute, args.authorized, args.dry_run, args.force)
        raise PublishError("未知命令")
    except PublishError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
