"""Safety checks for a local Auto-Editor input rights ledger; no external calls."""
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("trim_owned_video", Path("tools/trim_owned_video.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class LicenseGateTests(unittest.TestCase):
    def test_denies_not_approved(self):
        with tempfile.TemporaryDirectory() as root:
            base=Path(root)
            mod.ROOT=base
            mod.SOURCES=base/"licensed-inputs"
            mod.SOURCES.mkdir()
            src=mod.SOURCES/"example.mp4"
            src.write_bytes(b"test")
            ok,_=mod.authorized(src, {"approved":[]})
            self.assertFalse(ok)
    def test_rejects_path_outside_authorized_directory(self):
        with tempfile.TemporaryDirectory() as root:
            base=Path(root)
            mod.ROOT=base
            mod.SOURCES=base/"licensed-inputs"
            mod.SOURCES.mkdir()
            src=base/"untrusted.mp4"
            src.write_bytes(b"test")
            ok,_=mod.authorized(src, {"approved":[]})
            self.assertFalse(ok)
    def test_all_rights_required_and_checksum_matched(self):
        with tempfile.TemporaryDirectory() as root:
            base=Path(root)
            mod.ROOT=base
            mod.SOURCES=base/"licensed-inputs"
            mod.SOURCES.mkdir()
            src=mod.SOURCES/"approved.mp4"
            payload=b"synthetic bytes for ledger test"
            src.write_bytes(payload)
            record={
              "file":"licensed-inputs/approved.mp4",
              "file_sha256":hashlib.sha256(payload).hexdigest(),
              "status":"approved",
              "commercial_and_derivative_rights_confirmed":False,
              "editorial_reviewed":True,
              "creator":"Test creator",
              "source_url":"https://example.org/source",
              "license_url":"https://example.org/license",
              "license_type":"original"
            }
            self.assertFalse(mod.authorized(src,{"approved":[record]})[0])
            record["commercial_and_derivative_rights_confirmed"]=True
            self.assertTrue(mod.authorized(src,{"approved":[record]})[0])
            record["file_sha256"]="0"*64
            self.assertFalse(mod.authorized(src,{"approved":[record]})[0])
    def test_https_validation(self):
        self.assertTrue(mod.is_https("https://example.org/source"))
        self.assertFalse(mod.is_https("http://example.org/source"))
        self.assertFalse(mod.is_https("https://user:pass@example.org/source"))

if __name__ == "__main__":
    unittest.main(verbosity=2)
