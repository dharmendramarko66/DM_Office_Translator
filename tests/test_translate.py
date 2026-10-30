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


class TestH2ETransliterationMode:
    """v2.0.11: transliteration mode में translation नहीं, transliteration
    होता है — निर्भय → Nirbhay (न कि Fearless)।"""

    def _patch(self, monkeypatch, h2e, dict_dir, tmp_path):
        monkeypatch.setattr(h2e, "USER_DICT_DIR", str(dict_dir))
        monkeypatch.setattr(h2e, "SYSTEM_DICT_DIR", "/nonexistent")
        monkeypatch.setattr(h2e, "USER_DATA_DIR", str(tmp_path))

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

    def test_transliteration_output(self, h2e, dict_dir, monkeypatch, tmp_path, offline):
        self._patch(monkeypatch, h2e, dict_dir, tmp_path)
        monkeypatch.setenv("SOHT_TRANSLIT", "1")
        assert h2e.translate("निर्भय") == "Nirbhay"

    def test_default_mode_uses_dictionary(self, h2e, dict_dir, monkeypatch, tmp_path, offline):
        self._patch(monkeypatch, h2e, dict_dir, tmp_path)
        monkeypatch.delenv("SOHT_TRANSLIT", raising=False)
        # सामान्य मोड में dictionary translation ही चलता है।
        assert h2e.translate("जबलपुर") == "Jabalpur"


class TestH2EOnlinePath:
    """Online (Google) branch के regression tests।

    v2.0.7 से पहले एक variable-scoping bug (UnboundLocalError)
    था — जिन पतों में कोई शब्द dictionary से बाहर था, translation
    पूरी तरह fail हो जाता था। ये tests online path को mock करके
    उसी स्थिति को cover करते हैं।"""

    def _patch_paths(self, monkeypatch, h2e, dict_dir):
        monkeypatch.delenv("SOHT_OFFLINE", raising=False)
        monkeypatch.setattr(h2e, "USER_DICT_DIR", str(dict_dir))
        monkeypatch.setattr(h2e, "SYSTEM_DICT_DIR", "/nonexistent")
        monkeypatch.setattr(h2e, "GOOGLE_FAILURE_FILE", "/nonexistent/f")
        monkeypatch.setattr(h2e, "set_google_failure_cooldown", lambda: None)
        monkeypatch.setattr(h2e, "clear_google_failure_cooldown", lambda: None)
        monkeypatch.setattr(h2e, "google_temporarily_disabled", False)

    def test_online_failure_falls_back(self, h2e, dict_dir, monkeypatch):
        import requests

        class FailingSession:
            def get(self, *args, **kwargs):
                raise requests.exceptions.ConnectTimeout("no network")

        self._patch_paths(monkeypatch, h2e, dict_dir)
        monkeypatch.setattr(h2e, "session", FailingSession())

        # गोहचर dictionary में नहीं है — पहले यहाँ crash होता था।
        result = h2e.translate("ग्राम गोहचर जिला जबलपुर")
        assert result == "Gram Gohachar Dist Jabalpur"

    def test_online_success_replaces_in_place(self, h2e, dict_dir, monkeypatch):
        class FakeResponse:
            status_code = 200

            def raise_for_status(self):
                pass

            def json(self):
                # translate.googleapis.com का वास्तविक structure:
                # data[0] = [["translated", "source", ...], ...]
                return [[["Gohchar"]]]

        class SuccessSession:
            def get(self, url, timeout=None):
                return FakeResponse()

        self._patch_paths(monkeypatch, h2e, dict_dir)
        monkeypatch.setattr(h2e, "session", SuccessSession())

        result = h2e.translate("ग्राम गोहचर जिला जबलपुर")
        # दोनों occurrences अपनी जगह पर replace होनी चाहिए।
        assert result == "Gram Gohchar Dist Jabalpur"

    def test_all_dictionary_no_network_call(self, h2e, dict_dir, monkeypatch):
        class ExplodingSession:
            def get(self, *args, **kwargs):
                raise AssertionError("network should not be called")

        self._patch_paths(monkeypatch, h2e, dict_dir)
        monkeypatch.setattr(h2e, "session", ExplodingSession())

        # सारे शब्द dictionary में हैं — Google को बिल्कुल call नहीं।
        result = h2e.translate("सिद्ध बाबा के पास जिला जबलपुर म.प्र.")
        assert result == "Siddh Baba Ke Pas Dist Jabalpur M.P."
