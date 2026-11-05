"""पूरे translation pipeline के end-to-end tests (offline mode में)।"""

import os


class TestE2HTranslate:
    def _patch_paths(self, monkeypatch, e2h, dict_dir):
        monkeypatch.setattr(e2h, "USER_DICT_DIR", str(dict_dir))
        monkeypatch.setattr(e2h, "SYSTEM_DICT_DIR", "/nonexistent")

    def test_dictionary_entries_applied(self, e2h, dict_dir, monkeypatch, offline):
        self._patch_paths(monkeypatch, e2h, dict_dir)
        result = e2h.translate("ramkumar shankar jabalpur nagar")
        assert result == "रामकुमार शंकर जबलपुर नगर"

    def test_mixed_offline(self, e2h, dict_dir, monkeypatch, offline):
        self._patch_paths(monkeypatch, e2h, dict_dir)
        result = e2h.translate("madhyapradesh adalat mein 123 case")
        assert "मध्यप्रदेश" in result
        assert "अदालत" in result
        assert "123" in result

    def test_hindi_passthrough(self, e2h, dict_dir, monkeypatch, offline):
        self._patch_paths(monkeypatch, e2h, dict_dir)
        text = "केवल हिन्दी टेक्स्ट"
        assert e2h.translate(text) == text

    def test_empty_input(self, e2h):
        assert e2h.translate("") is None
        assert e2h.translate("   ") is None

    def test_offline_mode_via_marker_file(self, e2h, dict_dir, monkeypatch, tmp_path):
        self._patch_paths(monkeypatch, e2h, dict_dir)
        monkeypatch.delenv("SOHT_OFFLINE", raising=False)
        monkeypatch.setattr(e2h, "USER_DATA_DIR", str(tmp_path))
        marker = tmp_path / "offline_mode"
        marker.write_text("", encoding="utf-8")
        assert e2h.offline_only_mode() is True
        marker.unlink()
        assert e2h.offline_only_mode() is False


class TestE2HOnlineMode:
    """v3.0.0: English → Hindi में Alt+T का "Online mode" dictionary
    skip करके पूरा अनुवाद Google से करता है।"""

    def _patch(self, monkeypatch, e2h, dict_dir, tmp_path):
        monkeypatch.setattr(e2h, "USER_DICT_DIR", str(dict_dir))
        monkeypatch.setattr(e2h, "SYSTEM_DICT_DIR", "/nonexistent")
        monkeypatch.setattr(e2h, "USER_DATA_DIR", str(tmp_path))

    def test_env_var_enables_mode(self, e2h, monkeypatch, tmp_path, offline):
        monkeypatch.setattr(e2h, "USER_DATA_DIR", str(tmp_path))
        monkeypatch.setenv("SOHT_TRANSLIT", "1")
        assert e2h.transliteration_mode() is True

    def test_marker_enables_mode(self, e2h, monkeypatch, tmp_path, offline):
        monkeypatch.setattr(e2h, "USER_DATA_DIR", str(tmp_path))
        monkeypatch.delenv("SOHT_TRANSLIT", raising=False)
        assert e2h.transliteration_mode() is False
        (tmp_path / "transliteration_mode").write_text("", encoding="utf-8")
        assert e2h.transliteration_mode() is True

    def test_dictionary_skipped_google_used(self, e2h, dict_dir, monkeypatch, tmp_path):
        self._patch(monkeypatch, e2h, dict_dir, tmp_path)
        monkeypatch.delenv("SOHT_OFFLINE", raising=False)
        monkeypatch.setenv("SOHT_TRANSLIT", "1")

        class FakeResponse:
            def raise_for_status(self):
                pass

            def json(self):
                # dictionary "jabalpur" का "जबलपुर" देती है;
                # Online mode में Google का पूरा वाक्य मान्य होगा।
                return [[["जबलपुर शहर में अदालत", "jabalpur city court", None, None]]]

        monkeypatch.setattr(e2h.requests, "get", lambda *a, **k: FakeResponse())
        assert e2h.translate("jabalpur city court") == "जबलपुर शहर में अदालत"

    def test_offline_falls_back_to_transliteration(self, e2h, dict_dir, monkeypatch, tmp_path, offline):
        self._patch(monkeypatch, e2h, dict_dir, tmp_path)
        monkeypatch.setenv("SOHT_TRANSLIT", "1")
        # offline — Google नहीं, phonetic transliteration।
        assert e2h.translate("jabalpur") == "जबलपुर"

    def test_default_mode_uses_dictionary(self, e2h, dict_dir, monkeypatch, tmp_path, offline):
        self._patch(monkeypatch, e2h, dict_dir, tmp_path)
        monkeypatch.delenv("SOHT_TRANSLIT", raising=False)
        assert e2h.translate("jabalpur") == "जबलपुर"


class TestE2HVowelStart:
    """v2.0.10: vowel से शुरू होने वाले शब्द (जैसे Olkar) अब
    स्वतंत्र स्वर से शुरू होते हैं — मात्रा से नहीं।"""

    def _patch_paths(self, monkeypatch, e2h, dict_dir):
        monkeypatch.setattr(e2h, "USER_DICT_DIR", str(dict_dir))
        monkeypatch.setattr(e2h, "SYSTEM_DICT_DIR", "/nonexistent")

    def test_offline_vowel_start_word(self, e2h, dict_dir, monkeypatch, offline):
        self._patch_paths(monkeypatch, e2h, dict_dir)
        assert e2h.translate("Olkar") == "ओलकर"

    def test_google_batch_leading_matra_fixed(self, e2h, monkeypatch):
        """Google का असली response structure mock करके देखें कि
        मात्रा-से-शुरू output ठीक हो जाता है।"""

        class FakeResponse:
            def raise_for_status(self):
                pass

            def json(self):
                # Google Input Tools का वास्तविक structure:
                # ["SUCCESS", [["olkar", ["ोल्कर"], [], {"num": 1}]]]
                return ["SUCCESS", [["olkar", ["ोल्कर"], [], {"num": 1}]]]

        monkeypatch.setattr(e2h.requests, "get", lambda *a, **k: FakeResponse())
        assert e2h.google_transliterate_batch(["olkar"]) == ["ओल्कर"]


class TestH2ETranslate:
    def _patch_paths(self, monkeypatch, h2e, dict_dir):
        monkeypatch.setattr(h2e, "USER_DICT_DIR", str(dict_dir))
        monkeypatch.setattr(h2e, "SYSTEM_DICT_DIR", "/nonexistent")

    def test_dictionary_entries_applied(self, h2e, dict_dir, monkeypatch, offline):
        self._patch_paths(monkeypatch, h2e, dict_dir)
        result = h2e.translate("जबलपुर जिला में")
        assert "Jabalpur" in result
        assert "Dist" in result

    def test_offline_phonetic_fallback(self, h2e, dict_dir, monkeypatch, offline):
        self._patch_paths(monkeypatch, h2e, dict_dir)
        result = h2e.translate("यह एक परीक्षण है")
        # Offline-only mode में कोई network call नहीं —
        # phonetic fallback चलता है।
        assert result
        assert result.isascii()

    def test_capitalization(self, h2e, dict_dir, monkeypatch, offline):
        self._patch_paths(monkeypatch, h2e, dict_dir)
        result = h2e.translate("यह एक परीक्षण है")
        words = result.split()
        assert all(w[0].isupper() for w in words if w[0].isalpha())

    def test_empty_input(self, h2e):
        assert h2e.translate("") is None
        assert h2e.translate("   ") is None


class TestH2EOnlineMode:
    """v2.0.12: Alt+T का "Online mode" dictionary पूरी तरह skip करके
    Google से translation करता है (नाम transliterate, शब्द translate)।
    Network न हो तो phonetic transliteration fallback चलता है।"""

    def _patch(self, monkeypatch, h2e, dict_dir, tmp_path):
        monkeypatch.setattr(h2e, "USER_DICT_DIR", str(dict_dir))
        monkeypatch.setattr(h2e, "SYSTEM_DICT_DIR", "/nonexistent")
        monkeypatch.setattr(h2e, "USER_DATA_DIR", str(tmp_path))
        monkeypatch.setattr(h2e, "GOOGLE_FAILURE_FILE", "/nonexistent/f")
        monkeypatch.setattr(h2e, "set_google_failure_cooldown", lambda: None)
        monkeypatch.setattr(h2e, "clear_google_failure_cooldown", lambda: None)
        monkeypatch.setattr(h2e, "google_temporarily_disabled", False)

    def test_env_var_enables_mode(self, h2e, dict_dir, monkeypatch, tmp_path, offline):
        self._patch(monkeypatch, h2e, dict_dir, tmp_path)
        monkeypatch.setenv("SOHT_TRANSLIT", "1")
        assert h2e.transliteration_mode() is True

    def test_marker_file_enables_mode(self, h2e, dict_dir, monkeypatch, tmp_path, offline):
        self._patch(monkeypatch, h2e, dict_dir, tmp_path)
        monkeypatch.delenv("SOHT_TRANSLIT", raising=False)
        assert h2e.transliteration_mode() is False
        marker = tmp_path / "transliteration_mode"
        marker.write_text("", encoding="utf-8")
        assert h2e.transliteration_mode() is True

    def test_offline_falls_back_to_transliteration(
        self, h2e, dict_dir, monkeypatch, tmp_path, offline
    ):
        # Network नहीं है — phonetic transliteration ही चलेगा।
        self._patch(monkeypatch, h2e, dict_dir, tmp_path)
        monkeypatch.setenv("SOHT_TRANSLIT", "1")
        assert h2e.translate("निर्भय") == "Nirbhay"

    def test_dictionary_skipped_google_used(
        self, h2e, dict_dir, monkeypatch, tmp_path
    ):
        """ON mode में dictionary नहीं, Google का output मान्य होना चाहिए।"""
        self._patch(monkeypatch, h2e, dict_dir, tmp_path)
        monkeypatch.delenv("SOHT_OFFLINE", raising=False)
        monkeypatch.setenv("SOHT_TRANSLIT", "1")

        class FakeResponse:
            status_code = 200

            def raise_for_status(self):
                pass

            def json(self):
                # dictionary "जिला जबलपुर" का "Dist Jabalpur" देती है;
                # Google से अलग output आना चाहिए।
                return [[["District Jabalpur"]]]

        class SuccessSession:
            def get(self, url, timeout=None):
                return FakeResponse()

        monkeypatch.setattr(h2e, "session", SuccessSession())
        assert h2e.translate("जिला जबलपुर") == "District Jabalpur"

    def test_default_mode_uses_dictionary(self, h2e, dict_dir, monkeypatch, tmp_path, offline):
        self._patch(monkeypatch, h2e, dict_dir, tmp_path)
        monkeypatch.delenv("SOHT_TRANSLIT", raising=False)
        # सामान्य मोड में dictionary translation ही चलता है।
        assert h2e.translate("जबलपुर") == "Jabalpur"


class TestH2EOnlinePath:
    """v3.0.3: default (dictionary) मोड में बचे शब्दों का लिप्यांतरण होता है —
    कोई Google भाषांतरण नहीं, इसलिए network भी नहीं।"""

    def _patch_paths(self, monkeypatch, h2e, dict_dir):
        monkeypatch.delenv("SOHT_OFFLINE", raising=False)
        monkeypatch.setattr(h2e, "USER_DICT_DIR", str(dict_dir))
        monkeypatch.setattr(h2e, "SYSTEM_DICT_DIR", "/nonexistent")
        monkeypatch.setattr(h2e, "GOOGLE_FAILURE_FILE", "/nonexistent/f")
        monkeypatch.setattr(h2e, "set_google_failure_cooldown", lambda: None)
        monkeypatch.setattr(h2e, "clear_google_failure_cooldown", lambda: None)
        monkeypatch.setattr(h2e, "google_temporarily_disabled", False)

    def test_default_mode_never_calls_network(self, h2e, dict_dir, monkeypatch):
        class ExplodingSession:
            def get(self, *args, **kwargs):
                raise AssertionError("network should not be called")

        self._patch_paths(monkeypatch, h2e, dict_dir)
        monkeypatch.setattr(h2e, "session", ExplodingSession())

        # गोहचर dictionary में नहीं है → लिप्यांतरण (Gohchar), भाषांतरण नहीं।
        result = h2e.translate("ग्राम गोहचर जिला जबलपुर")
        assert result == "Gram Gohachar Dist Jabalpur"

    def test_unknown_word_transliterated(self, h2e, dict_dir, monkeypatch):
        self._patch_paths(monkeypatch, h2e, dict_dir)
        assert h2e.translate("गोहचर") == "Gohachar"

    def test_all_dictionary_no_network_call(self, h2e, dict_dir, monkeypatch):
        class ExplodingSession:
            def get(self, *args, **kwargs):
                raise AssertionError("network should not be called")

        self._patch_paths(monkeypatch, h2e, dict_dir)
        monkeypatch.setattr(h2e, "session", ExplodingSession())

        result = h2e.translate("सिद्ध बाबा के पास जिला जबलपुर म.प्र.")
        assert result == "Siddh Baba Ke Pas Dist Jabalpur M.P."

