#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SPECS_FILE = SCRIPT_DIR / "platform_specs.json"
DEFAULT_HOME = Path.home() / ".config" / "open-creator" / "social-publisher"
BLOCKING_STATUSES = {"published", "uncertain"}
ACCOUNT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


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


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_timestamp(moment: datetime | None = None) -> str:
    return (moment or utc_now()).isoformat().replace("+00:00", "Z")


def doctor() -> int:
    available = specs()
    google_ready = all(
        importlib.util.find_spec(module) is not None
        for module in ("googleapiclient", "google_auth_oauthlib")
    )
    playwright_ready = importlib.util.find_spec("playwright") is not None
    browser_path = browser_executable()
    if playwright_ready and not browser_path:
        browser_path = playwright_browser_executable()
    result = {
        "free_mode": True,
        "runtime_home": str(runtime_home()),
        "dependencies": {
            "python": sys.version.split()[0],
            "playwright": playwright_ready,
            "youtube_api": google_ready,
            "ffprobe": shutil.which("ffprobe"),
            "biliup": shutil.which("biliup"),
            "browser": browser_path,
        },
        "platforms": {
            name: {
                "route": data["default_route"],
                "free": data["free"],
                "ready": (
                    bool(shutil.which("biliup")) if name == "bilibili"
                    else google_ready if name == "youtube"
                    else playwright_ready and bool(browser_path)
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


def playwright_browser_executable() -> str | None:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            path = Path(playwright.chromium.executable_path)
            return str(path) if path.is_file() else None
    except Exception:
        return None


def require_playwright():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise PublishError(
            "缺少 Playwright。安装命令: python3 -m pip install -r scripts/requirements.txt"
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
    safe_account = safe_account_name(account)
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
    safe_account = safe_account_name(account)
    path = runtime_home() / "profiles" / platform / safe_account
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path


def safe_account_name(account: str) -> str:
    if not ACCOUNT_PATTERN.fullmatch(account):
        raise PublishError("账号别名只能包含英文字母、数字、连字符或下划线")
    return account


def normalize_text(value: str) -> str:
    return " ".join(value.split())


def locator_text(locator: Any) -> str:
    try:
        return str(locator.input_value(timeout=1000) or "")
    except Exception:
        try:
            return str(locator.inner_text(timeout=1000) or "")
        except Exception:
            return ""


def fill_first(page: Any, selectors: list[str], value: str) -> dict[str, Any]:
    result = {"requested": bool(value), "filled": False, "verified": False, "selector": None}
    if not value:
        return result
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
                page.wait_for_timeout(250)
                observed = locator_text(locator)
                expected_normalized = normalize_text(value)
                observed_normalized = normalize_text(observed)
                result.update({
                    "filled": True,
                    "verified": bool(observed_normalized) and (
                        observed_normalized == expected_normalized
                        or expected_normalized in observed_normalized
                    ),
                    "selector": selector,
                })
                return result
        except Exception:
            continue
    return result


def ledger_path(fingerprint: str) -> Path:
    path = runtime_home() / "ledgers" / f"{fingerprint}.json"
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path


def legacy_report_path(fingerprint: str) -> Path:
    return runtime_home() / "reports" / f"{fingerprint}.json"


def run_report_path(platform: str, account: str, fingerprint: str, moment: datetime | None = None) -> Path:
    current = moment or utc_now()
    stamp = current.strftime("%Y%m%dT%H%M%S.%fZ")
    safe_account = safe_account_name(account)
    path = runtime_home() / "runs" / platform / safe_account / f"{stamp}-{fingerprint}.json"
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path


def write_report(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(path, 0o600)


def load_previous_report(fingerprint: str) -> dict[str, Any] | None:
    for path in (ledger_path(fingerprint), legacy_report_path(fingerprint)):
        if path.is_file():
            return load_json(path)
    return None


def persist_run(data: dict[str, Any], fingerprint: str) -> Path:
    path = run_report_path(str(data["platform"]), str(data["account"]), fingerprint)
    write_report(path, data)
    write_report(ledger_path(fingerprint), data)
    return path


def visible_enabled(page: Any, selectors: list[str]) -> tuple[Any | None, str | None, int]:
    for selector in selectors:
        locator = page.locator(selector)
        visible: list[Any] = []
        try:
            for index in range(locator.count()):
                candidate = locator.nth(index)
                if candidate.is_visible(timeout=500) and candidate.is_enabled(timeout=500):
                    visible.append(candidate)
        except Exception:
            continue
        if len(visible) == 1:
            return visible[0], selector, 1
        if len(visible) > 1:
            return None, selector, len(visible)
    return None, None, 0


def wait_for_upload_ready(page: Any, selectors: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
    ready_selectors = selectors.get("upload_ready") or selectors.get("publish") or []
    error_selectors = selectors.get("upload_error") or []
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        for selector in error_selectors:
            try:
                locator = page.locator(selector).first
                if locator.count() and locator.is_visible(timeout=300):
                    return {"ready": False, "error": locator_text(locator) or selector}
            except Exception:
                continue
        button, selector, count = visible_enabled(page, ready_selectors)
        if button is not None:
            return {"ready": True, "selector": selector}
        if count > 1:
            return {"ready": False, "error": f"上传完成信号不唯一: {selector} 匹配 {count} 个元素"}
        page.wait_for_timeout(1000)
    return {"ready": False, "error": f"等待上传完成超过 {timeout_seconds} 秒"}


def success_evidence(page: Any, selectors: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        for selector in selectors.get("publish_error") or []:
            try:
                locator = page.locator(selector).first
                if locator.count() and locator.is_visible(timeout=300):
                    return {"confirmed": False, "error": locator_text(locator) or selector}
            except Exception:
                continue
        for selector in selectors.get("publish_success") or []:
            try:
                locator = page.locator(selector).first
                if locator.count() and locator.is_visible(timeout=300):
                    return {"confirmed": True, "selector": selector, "text": locator_text(locator)}
            except Exception:
                continue
        page.wait_for_timeout(1000)
    return {"confirmed": False, "error": f"{timeout_seconds} 秒内未获得明确成功反馈"}


def evaluate_stability(records: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(records, key=lambda item: float(item.get("finished_at_unix") or 0))
    published = [item for item in ordered if item.get("status") == "published"]
    prepared = [item for item in ordered if item.get("status") == "prepared"]
    executed = [item for item in ordered if item.get("execute") is True]
    latest_three = executed[-3:]
    days = {
        str(item.get("finished_at") or "")[:10]
        for item in published
        if item.get("finished_at")
    }
    stable = (
        len(latest_three) == 3
        and all(item.get("status") == "published" for item in latest_three)
        and len({str(item.get("finished_at") or "")[:10] for item in latest_three}) == 3
    )
    if stable:
        level = "stable"
    elif published or len(prepared) >= 3:
        level = "conditional"
    else:
        level = "unverified"
    return {
        "level": level,
        "runs": len(ordered),
        "prepared": len(prepared),
        "published": len(published),
        "uncertain": sum(item.get("status") == "uncertain" for item in ordered),
        "failed": sum(item.get("status") == "failed" for item in ordered),
        "published_days": len(days),
        "criterion": "latest 3 executed runs published on 3 distinct UTC dates",
    }


def stability(platform_names: list[str], account: str | None) -> int:
    root = runtime_home() / "runs"
    available = specs()
    targets = platform_names or sorted(available)
    output: dict[str, Any] = {}
    for platform in targets:
        if platform not in available:
            raise PublishError(f"不支持的平台: {platform}")
        records: list[dict[str, Any]] = []
        search_root = root / platform
        if search_root.is_dir():
            for path in search_root.rglob("*.json"):
                try:
                    item = load_json(path)
                except PublishError:
                    continue
                if account and item.get("account") != account:
                    continue
                records.append(item)
        output[platform] = evaluate_stability(records)
    print_json({"runtime_home": str(runtime_home()), "platforms": output})
    return 0


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


def browser_action(
    package_path: Path,
    platform: str,
    account: str,
    execute: bool,
    authorized: bool,
    dry_run: bool,
    force: bool,
    upload_timeout: int,
    result_timeout: int,
) -> int:
    account = safe_account_name(account)
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
    previous = load_previous_report(fingerprint)
    if execute and previous and previous.get("status") in BLOCKING_STATUSES and not force:
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
        "manual_review_fields": [
            "account",
            "video_preview",
            "cover" if cover else None,
            "visibility",
            "originality_and_rights",
            "interaction_permissions",
        ],
    }
    summary["manual_review_fields"] = [item for item in summary["manual_review_fields"] if item]
    if dry_run:
        print_json({"status": "validated", **summary, "actions": ["open visible browser", "upload video", "fill platform fields", "stop before final publish" if not execute else "click final publish"]})
        return 0

    spec = specs()[platform]
    sync_playwright = require_playwright()
    started = time.time()
    started_at = iso_timestamp()
    status = "failed"
    result_url = None
    error = None
    evidence: dict[str, Any] = {}
    screenshot_stamp = utc_now().strftime("%Y%m%dT%H%M%S.%fZ")
    screenshot_path = runtime_home() / "screenshots" / platform / account / f"{screenshot_stamp}-{fingerprint}.png"
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
            page.wait_for_timeout(1000)

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
                        filled["cover"] = {"requested": True, "filled": True, "verified": False}
                except Exception:
                    filled["cover"] = {"requested": True, "filled": False, "verified": False}

            missing_fields = [
                name for name, result in filled.items()
                if isinstance(result, dict) and result.get("requested") and not result.get("filled")
            ]
            if missing_fields:
                raise PublishError(f"页面字段未完成填写，已停止: {', '.join(missing_fields)}")

            upload = wait_for_upload_ready(page, selectors, upload_timeout)
            evidence["upload"] = upload
            if not upload.get("ready"):
                raise PublishError(str(upload.get("error") or "无法确认视频上传完成"))

            page.screenshot(path=str(screenshot_path), full_page=True)
            if not execute:
                print_json({
                    "status": "awaiting_review",
                    **summary,
                    "filled": filled,
                    "evidence": evidence,
                    "screenshot": str(screenshot_path),
                })
                confirmation = input(
                    "请检查账号、视频预览、封面、文案、声明和可见范围。不要点击发布；全部正确后输入 READY: "
                )
                if confirmation != "READY":
                    status = "awaiting_review"
                    raise PublishError("未输入 READY，本次 prepare 未通过人工验收")
                status = "prepared"
                evidence["manual_review"] = "READY"
                print_json({"status": status, **summary, "filled": filled, "evidence": evidence})
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
                button, publish_selector, count = visible_enabled(page, selectors.get("publish") or [])
                if count > 1:
                    raise PublishError(f"最终发布按钮匹配到 {count} 个可用元素，拒绝点击")
                if button is None:
                    raise PublishError("未找到唯一且可用的最终发布按钮，已停止")
                button.click()
                evidence["publish_button"] = publish_selector
                publish_result = success_evidence(page, selectors, result_timeout)
                evidence["publish_result"] = publish_result
                result_url = page.url
                status = "published" if publish_result.get("confirmed") else "uncertain"
                page.screenshot(path=str(screenshot_path), full_page=True)
                print_json({
                    "status": status,
                    **summary,
                    "result_url": result_url,
                    "evidence": evidence,
                    "screenshot": str(screenshot_path),
                })
            context.close()
    except Exception as exc:
        error = str(exc)
        if isinstance(exc, PublishError):
            raise
    finally:
        finished = time.time()
        report = {
            **summary,
            "fingerprint": fingerprint,
            "status": status,
            "result_url": result_url,
            "error": error,
            "evidence": evidence,
            "screenshot": str(screenshot_path) if screenshot_path.exists() else None,
            "started_at_unix": started,
            "finished_at_unix": finished,
            "started_at": started_at,
            "finished_at": iso_timestamp(),
        }
        persist_run(report, fingerprint)

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
    account = safe_account_name(account)
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
    previous = load_previous_report(fingerprint)
    if execute and previous and previous.get("status") in BLOCKING_STATUSES and not force:
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
    started_at = iso_timestamp()
    evidence: dict[str, Any] = {}
    created_video_id = None
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
        created_video_id = video_id
        result_url = f"https://youtu.be/{video_id}"
        evidence["video_id"] = video_id
        if cover:
            try:
                service.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(str(cover), resumable=False),
                ).execute()
                evidence["thumbnail"] = "set"
            except Exception as exc:
                evidence["thumbnail"] = "failed"
                evidence["thumbnail_error"] = str(exc)
        verification = service.videos().list(part="id,status,snippet", id=video_id).execute()
        items = verification.get("items") if isinstance(verification, dict) else None
        evidence["api_readback"] = bool(items)
        status = "published" if items else "uncertain"
        print_json({
            "status": status,
            **summary,
            "video_id": video_id,
            "result_url": result_url,
            "evidence": evidence,
        })
    except Exception as exc:
        error = str(exc)
        if created_video_id:
            status = "uncertain"
        elif status != "uncertain":
            status = "failed"
    finally:
        finished = time.time()
        persist_run({
            **summary,
            "fingerprint": fingerprint,
            "status": status,
            "result_url": result_url,
            "error": error,
            "evidence": evidence,
            "started_at_unix": started,
            "finished_at_unix": finished,
            "started_at": started_at,
            "finished_at": iso_timestamp(),
        }, fingerprint)
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

    stability_parser = subparsers.add_parser("stability")
    stability_parser.add_argument("--platform", action="append", default=[])
    stability_parser.add_argument("--account")

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
        action.add_argument("--upload-timeout", type=int, default=600)
        action.add_argument("--result-timeout", type=int, default=90)
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
        if args.command == "stability":
            return stability(args.platform, args.account)
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
            return browser_action(
                args.package.resolve(),
                args.platform,
                args.account,
                execute,
                args.authorized,
                args.dry_run,
                args.force,
                args.upload_timeout,
                args.result_timeout,
            )
        raise PublishError("未知命令")
    except PublishError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
