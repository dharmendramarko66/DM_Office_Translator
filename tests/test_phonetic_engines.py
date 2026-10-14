"""Offline phonetic engines के unit tests।"""

import pytest


class TestE2HPhoneticEngine:
    @pytest.mark.parametrize(
        "word,expected",
        [
            ("jabalpur", "जबलपुर"),
            ("prakash", "प्रकाश"),
            ("chandra", "चंद्र"),
            ("krishna", "कृष्ण"),
            ("bharat", "भारत"),
            ("madhy", "मध्य"),
            ("adalat", "अदालत"),
            ("dharmendra", "धरमेन्द्र"),
            ("aage", "आगे"),
            ("nagar", "नगर"),
            ("ramesh", "रमेश"),
            ("pawan", "पवन"),
        ],
    )
    def test_known_words(self, e2h, word, expected):
        assert e2h.e2h_offline_transliterate_word(word) == expected

    @pytest.mark.parametrize(
        "word,expected",
        [
            ("olkar", "ओलकर"),
            ("arjun", "अरजुन"),
            ("inder", "इनदेर"),
            ("umesh", "उमेश"),
            ("amit", "अमित"),
            ("omprakash", "ओमप्रकाश"),
            ("aarti", "आरति"),
        ],
    )
    def test_vowel_start_words(self, e2h, word, expected):
        # v2.0.10: शब्द के आरम्भ में स्वतंत्र स्वर आना चाहिए।
        assert e2h.e2h_offline_transliterate_word(word) == expected

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("ोल्कर", "ओल्कर"),
            ("ारती", "आरती"),
            ("िन्दर", "इन्दर"),
            ("ूमेश", "ऊमेश"),
            ("ेकता", "एकता"),
            ("ैरावत", "ऐरावत"),
            ("ौरत", "औरत"),
            ("ुमर", "उमर"),
        ],
    )
    def test_leading_matra_normalized(self, e2h, raw, expected):
        assert e2h.fix_leading_matra(raw) == expected

    def test_leading_matra_idempotent(self, e2h):
        once = e2h.fix_leading_matra("ोल्कर")
        assert e2h.fix_leading_matra(once) == once

    def test_compound_correction_still_works(self, e2h):
        # Compound शब्द के भीतर सुधार लागू होना चाहिए।
        assert (
            e2h.e2h_offline_transliterate_word("prakashchandra")
            == "प्रकाशचंद्र"
        )
        assert (
            e2h.e2h_offline_transliterate_word("chandraprakash")
            == "चंद्रप्रकाश"
        )

    def test_matra_suffix_not_corrupted(self, e2h):
        # v2.1.0 fix: "भरत" सुधार अब मात्रा-युक्त शब्दों को नहीं बदलता।
        # नाम "Bharati" (भरति) अब "भारति" नहीं बनता।
        result = e2h.e2h_offline_transliterate_word("bharati")
        assert result == "भरति"
        assert "भारति" not in result


class TestH2EPhoneticEngine:
    @pytest.mark.parametrize(
        "word,expected",
        [
            ("कृष्ण", "krishn"),  # अंतिम inherent 'a' हट जाता है
            # phonetic output: ज(ba) ब(ba) ल(la) पु(pu) र(r)
            ("जबलपुर", "jabalapur"),
        ],
    )
    def test_known_words(self, h2e, word, expected):
        assert h2e.h2e_offline_transliterate_word(word) == expected

    def test_devanagari_digits_converted(self, h2e):
        result = h2e.h2e_offline_transliterate_word("२०२४")
        assert "2024" in result

    def test_unknown_chars_preserved(self, h2e):
        result = h2e.h2e_offline_transliterate_word("जबलपुर123")
        assert "123" in result
