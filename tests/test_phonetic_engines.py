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
