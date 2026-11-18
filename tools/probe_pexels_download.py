#!/usr/bin/env python3
"""Validate that licensed Pexels video can be acquired by an automation runner.
No video is published or committed. The probe never downloads third-party
content to the GitHub repository or changes TikTok/Buffer.
"""
import urllib.request
import urllib.parse
import urllib.error
import sys

IDS = ["37501763", "37563630", "36082299", "35995795"]
def main():
    for clip in IDS:
        url = "https://www.pexels.com/video/" + clip + "/download/"
        request = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 (compatible; LicensedFootageProbe/1.0)","Accept":"video/mp4,*/*"})
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                target = response.geturl()
                hostname = (urllib.parse.urlsplit(target).hostname or "").lower()
                kind = response.headers.get("Content-Type","")
                sample = response.read(1024)
                allowed = (hostname == "pexels.com" or hostname.endswith(".pexels.com"))
                video = b"ftyp" in sample[:100] or "video/" in kind.lower()
                print("PEXELS_PROBE",clip,"STATUS",response.status,"HOST",hostname,"TYPE",kind,"VIDEO",video,"HOST_APPROVED",allowed, flush=True)
        except urllib.error.HTTPError as error:
            print("PEXELS_PROBE",clip,"HTTP",error.code,flush=True)
        except Exception as error:
            print("PEXELS_PROBE",clip,"FAILED",type(error).__name__,flush=True)
if __name__=="__main__":
    main()
