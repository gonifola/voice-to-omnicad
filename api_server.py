#!/usr/bin/env python3
"""
OmniCAD Design API — v0.1
POST /design  →  {spec, format, material}  →  STL/STEP bytes or job_id

Run:  python api_server.py
Env:  ANTHROPIC_API_KEY, XAI_API_KEY, SECRET_KEY (optional auth token)

Agents submit a natural-language spec; OmniCAD runs Blender headless,
generates the geometry, and returns the file URL.

Pricing: $0.10/call (Stripe webhook integration — Phase 2)
"""

import os
import json
import uuid
import tempfile
import subprocess
import hashlib
import time
from pathlib import Path

try:
    from flask import Flask, request, jsonify, send_file
    from flask_cors import CORS
except ImportError:
    raise SystemExit("pip install flask flask-cors")

try:
    import requests as req_lib
except ImportError:
    raise SystemExit("pip install requests")

app     = Flask(__name__)
CORS(app)

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
XAI_KEY       = os.environ.get("XAI_API_KEY", "")
SECRET_KEY    = os.environ.get("SECRET_KEY", "")   # optional bearer token
OUTPUT_DIR    = Path(tempfile.gettempdir()) / "omnicad_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

BLENDER_EXEC  = os.environ.get("BLENDER_PATH", "blender")  # or full path


SYSTEM_PROMPT = """You are the AI brain inside OmniCAD.
Convert the user's design spec into a self-contained Blender Python script.
The script must:
1. Create the geometry using bpy
2. Select the created object(s)
3. Export to the path provided by the variable OUTPUT_PATH (already set in scope)
4. Use format: bpy.ops.export_mesh.stl(filepath=OUTPUT_PATH, use_selection=True)
Output ONLY the Python script. No markdown. No explanation."""


def ai_to_blender_script(spec: str, output_path: str) -> str:
    """Ask Claude (or Grok fallback) to produce a Blender bpy script."""
    messages = [{"role": "user", "content": f"Design spec: {spec}\nOUTPUT_PATH = '{output_path}'"}]

    # Try Claude
    if ANTHROPIC_KEY:
        try:
            r = req_lib.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01",
                         "content-type": "application/json"},
                json={"model": "claude-opus-4-5", "max_tokens": 2048,
                      "system": SYSTEM_PROMPT, "messages": messages},
                timeout=30,
            )
            r.raise_for_status()
            return r.json()["content"][0]["text"].strip()
        except Exception as e:
            print(f"[API] Claude error: {e}")

    # Fallback: Grok
    if XAI_KEY:
        try:
            r = req_lib.post(
                "https://api.x.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {XAI_KEY}", "Content-Type": "application/json"},
                json={"model": "grok-3-latest", "max_tokens": 2048,
                      "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages},
                timeout=30,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[API] Grok error: {e}")

    return ""


def run_blender_headless(script_path: str) -> tuple[bool, str]:
    """Run Blender headlessly with the given script."""
    cmd = [BLENDER_EXEC, "--background", "--python", script_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            return False, result.stderr[-2000:]
        return True, result.stdout[-500:]
    except subprocess.TimeoutExpired:
        return False, "Blender execution timed out (120s)"
    except FileNotFoundError:
        return False, f"Blender not found at '{BLENDER_EXEC}'. Set BLENDER_PATH env var."


# ── Auth helper ─────────────────────────────────────────────

def _check_auth():
    if not SECRET_KEY:
        return True
    auth = request.headers.get("Authorization", "")
    return auth == f"Bearer {SECRET_KEY}"


# ── Routes ──────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "version": "0.1.0"})


@app.route("/design", methods=["POST"])
def design():
    """
    POST /design
    Body: {
        "spec": "a 10mm cube with rounded corners",
        "format": "stl",          # stl | step (step = Phase 2)
        "material": "gold"        # optional hint for AI
    }
    Returns: { "job_id": "...", "file_url": "/download/<job_id>" }
    """
    if not _check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(force=True)
    if not data or "spec" not in data:
        return jsonify({"error": "Missing 'spec' field"}), 400

    spec     = data["spec"]
    fmt      = data.get("format", "stl").lower()
    material = data.get("material", "")

    if fmt not in ("stl",):
        return jsonify({"error": "Only 'stl' format supported in v0.1"}), 400

    job_id   = str(uuid.uuid4())[:8]
    out_file = OUTPUT_DIR / f"{job_id}.stl"

    # Build full prompt
    full_spec = spec
    if material:
        full_spec += f" Apply a {material} material."

    # Generate Blender script
    script_code = ai_to_blender_script(full_spec, str(out_file))
    if not script_code:
        return jsonify({"error": "AI backend unavailable — check API keys"}), 503

    # Write temp script
    script_path = OUTPUT_DIR / f"{job_id}_script.py"
    script_path.write_text(
        f"OUTPUT_PATH = {repr(str(out_file))}\n" + script_code
    )

    # Run Blender
    ok, log = run_blender_headless(str(script_path))
    script_path.unlink(missing_ok=True)

    if not ok or not out_file.exists():
        return jsonify({"error": "Geometry generation failed", "log": log}), 500

    file_size = out_file.stat().st_size
    return jsonify({
        "job_id":    job_id,
        "spec":      spec,
        "format":    fmt,
        "file_url":  f"/download/{job_id}",
        "size_bytes": file_size,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })


@app.route("/download/<job_id>", methods=["GET"])
def download(job_id):
    # Sanitize
    safe_id = "".join(c for c in job_id if c.isalnum() or c == "-")[:16]
    f = OUTPUT_DIR / f"{safe_id}.stl"
    if not f.exists():
        return jsonify({"error": "Not found"}), 404
    return send_file(str(f), as_attachment=True,
                     download_name=f"omnicad_{safe_id}.stl",
                     mimetype="application/octet-stream")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[OmniCAD API] Starting on port {port}")
    print(f"[OmniCAD API] POST /design  — agent endpoint")
    app.run(host="0.0.0.0", port=port, debug=False)
