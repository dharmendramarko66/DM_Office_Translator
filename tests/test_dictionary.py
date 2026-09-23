"""Dictionary loading और combined-regex behavior के tests।"""

import os


class TestE2HDictionary:
    def test_project_dictionary_loads(self, e2h, dict_dir):
        combined, key_to_marker, protected = e2h.load_dictionary(
            dict_dirs=[str(dict_dir)]
        )
        assert combined is not None
        assert len(protected) > 5000

    def test_longest_match_wins(self, e2h, tmp_path):
        (tmp_path / "english_to_hindi_dictionary.txt").write_text(
            "raj=राज\nrajkumar=राजकुमार\n", encoding="utf-8"
        )
        combined, key_to_marker, protected = e2h.load_dictionary(
            dict_dirs=[str(tmp_path)]
        )
        text = "rajkumar"
        out = combined.sub(
            lambda m: key_to_marker.get(m.group(0).lower(), m.group(0)), text
        )
        assert protected[out] == "राजकुमार"

    def test_word_boundary_respected(self, e2h, tmp_path):
        # "Ashoknagar" के भीतर "nagar" match नहीं होना चाहिए।
        (tmp_path / "english_to_hindi_dictionary.txt").write_text(
            "nagar=नगर\n", encoding="utf-8"
        )
        combined, key_to_marker, protected = e2h.load_dictionary(
            dict_dirs=[str(tmp_path)]
        )
        assert combined.search("Ashoknagar") is None
        assert combined.search("nagar") is not None

    def test_user_dictionary_takes_priority(self, e2h, tmp_path):
        user_dir = tmp_path / "user"
        system_dir = tmp_path / "system"
        for d in (user_dir, system_dir):
            d.mkdir()
        (user_dir / "english_to_hindi_dictionary.txt").write_text(
            "kamla=कमला\n", encoding="utf-8"
        )
        (system_dir / "english_to_hindi_dictionary.txt").write_text(
            "kamla=SYSTEM_VALUE\njabalpur=जबलपुर\n", encoding="utf-8"
        )
        _, key_to_marker, protected = e2h.load_dictionary(
            dict_dirs=[str(user_dir), str(system_dir)]
        )
        # user entry जीतती है...
        assert protected[key_to_marker["kamla"]] == "कमला"
        # ...और system की unique entries भी मिलती हैं।
        assert protected[key_to_marker["jabalpur"]] == "जबलपुर"


class TestH2EDictionary:
    def test_project_dictionary_loads(self, h2e, dict_dir):
        combined, dictionary = h2e.load_dictionary(dict_dirs=[str(dict_dir)])
        assert combined is not None
        assert len(dictionary) > 5000

    def test_reverse_lookup_from_e2h(self, h2e, dict_dir):
        # e2h dictionary (ramkumar=रामकुमार) reverse lookup देती है।
        combined, dictionary = h2e.load_dictionary(dict_dirs=[str(dict_dir)])
        assert dictionary.get("रामकुमार") is not None

    def test_devanagari_boundary(self, h2e, tmp_path):
        (tmp_path / "hindi_to_english_dictionary.txt").write_text(
            "के=Ke\n", encoding="utf-8"
        )
        combined, dictionary = h2e.load_dictionary(dict_dirs=[str(tmp_path)])
        # "इके" के भीतर "के" match नहीं होना चाहिए।
        assert combined.search("इके") is None
        assert combined.search("के") is not None
