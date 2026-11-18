#!/usr/bin/env python3
"""Optional Auto-Editor cut of explicitly authorized local source footage.

No network downloads. Never trims other creators' unlicensed uploads.
Output is always unpublished. The manifest must be independently completed.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path.cwd().resolve()
SOURCES=(ROOT/"licensed-inputs").resolve()
OUTPUTS=(ROOT/"work-products").resolve()
MANIFEST=ROOT/"series/approved_raw_footage.json"

def inside(path:Path,parent:Path)->bool:
    try:
        path.resolve().relative_to(parent)
        return True
    except ValueError:
        return False

def is_https(s):
    try:
        parsed=urlsplit(str(s))
        return parsed.scheme=="https" and bool(parsed.hostname) and not parsed.username and not parsed.password
    except ValueError:
        return False

def checksum(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
    return h.hexdigest()

def authorized(src,manifest):
    if not inside(src,SOURCES):
        return False,"source_not_in_authorized_input_directory"
    if src.suffix.lower() not in (".mp4",".mov",".mkv") or not src.is_file():
        return False,"source_missing_or_invalid_container"
    if not isinstance(manifest.get("approved"),list):
        return False,"invalid_license_manifest"
    entries=[item for item in manifest["approved"] if item.get("file")==src.relative_to(ROOT).as_posix()]
    if len(entries)!=1:
        return False,"missing_unique_asset_approval"
    item=entries[0]
    requirements=[
       item.get("status")=="approved",
       item.get("commercial_and_derivative_rights_confirmed") is True,
       item.get("editorial_reviewed") is True,
       isinstance(item.get("creator"),str) and len(item["creator"])>=2,
       is_https(item.get("source_url")),
       is_https(item.get("license_url")),
       isinstance(item.get("file_sha256"),str) and len(item["file_sha256"])==64,
       item.get("license_type") in ("original","CC0_verified","CC_BY_attributed","CC_BY_SA_terms_verified","commercial_stock_verified","explicit_owner_permission")
    ]
    if not all(requirements):
        return False,"rights_or_editorial_approval_incomplete"
    if item["file_sha256"] != checksum(src):
        return False,"source_checksum_differs_from_approved_asset"
    return True,"rights_manifest_passed"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",required=True,help="Local file inside licensed-inputs/")
    parser.add_argument("--output",default="",help="Local output inside work-products/")
    args=parser.parse_args()
    src=(ROOT/args.source).resolve()
    if not MANIFEST.is_file():
        raise SystemExit("MISSING_APPROVED_RAW_FOOTAGE_LEDGER")
    try:
        ledger=json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError,ValueError) as exc:
        raise SystemExit("BAD_APPROVAL_MANIFEST") from exc
    ok,reason=authorized(src,ledger)
    if not ok:
        raise SystemExit("STOP_UNLICENSED_OR_UNAPPROVED_SOURCE:"+reason)
    target=(ROOT/args.output).resolve() if args.output else (OUTPUTS/(src.stem+"_trimmed.mp4")).resolve()
    if not inside(target,OUTPUTS) or target==src or target.suffix.lower()!=".mp4":
        raise SystemExit("UNSAFE_OUTPUT_PATH")
    target.parent.mkdir(parents=True,exist_ok=True)
    # Auto-Editor cuts silent/dead parts by its defaults and preserves padding
    # to reduce the chance of chopping off a spoken syllable.
    cmd=["auto-editor",str(src),"--margin","0.25sec","-o",str(target)]
    subprocess.run(cmd,check=True,timeout=360)
    if not target.is_file() or target.stat().st_size < 40000:
        raise SystemExit("AUTO_EDITOR_NO_VALID_OUTPUT")
    receipt={"source":args.source,"source_sha256":checksum(src),
            "trimmed_file":str(target.relative_to(ROOT)),"trimmed_sha256":checksum(target),
            "publication_authorized":False,"status":"NEEDS_VIDEO_AUDIO_AND_EDITORIAL_REVIEW"}
    receipt_path=target.with_suffix(".editing-receipt.json")
    receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("APPROVED_SOURCE_AUTO_EDIT_DONE_REVIEW_REQUIRED:",target,flush=True)
if __name__=="__main__":
    main()
