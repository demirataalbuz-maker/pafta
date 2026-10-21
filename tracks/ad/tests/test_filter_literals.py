"""A19 regressions: quoted literal stars stay distinct from LDAP presence.

Run from the project root: python tracks/ad/tests/test_filter_literals.py
Source: https://learn.microsoft.com/en-us/powershell/module/activedirectory/about/about_activedirectory_filter#ldap-special-characters
"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from sandbox.ad_engine import execute_code, explain_ldap, translate_ps_filter_to_ldap


class FilterLiteralTests(unittest.TestCase):
    def test_literal_and_wildcard_translations_for_both_quote_styles(self):
        for quote in ('"', "'"):
            for operator, expected in (
                ("-eq", r"(Department=\2a)"),
                ("-ne", r"(!(Department=\2a))"),
                ("-like", "(Department=*)"),
                ("-notlike", "(!(Department=*))"),
            ):
                expression = f"Department {operator} {quote}*{quote}"
                with self.subTest(expression=expression):
                    self.assertEqual(translate_ps_filter_to_ldap(expression), expected)
        self.assertEqual(translate_ps_filter_to_ldap("*"), "(objectClass=*)")

    def run_filter(self, operator, value):
        fields = [{"department": "*"}, {"department": "SOC"}, {"department": "S*OC"},
                  {"department": "**"}, {}, {"department": None}, {"department": []}]
        users = []
        for name, attributes in zip(("star", "soc", "embedded", "double", "absent", "null", "empty"), fields):
            users.append({"distinguishedName": f"CN={name},DC=pafta,DC=local",
                          "sAMAccountName": name, "name": name,
                          "objectCategory": "person", "objectClass": ["top", "person", "user"],
                          **attributes})
        result = execute_code(f'Get-ADUser -Filter \'Department {operator} "{value}"\'', raw_directory=users)
        self.assertEqual(result["status"], "ok", result)
        return [obj["sAMAccountName"] for obj in result["results"][0]["objects"]]

    def test_eq_ne_are_not_presence_or_absence_queries(self):
        self.assertEqual(self.run_filter("-eq", "*"), ["star"])
        self.assertEqual(self.run_filter("-ne", "*"), ["soc", "embedded", "double", "absent", "null", "empty"])

    def test_like_notlike_keep_presence_semantics(self):
        self.assertEqual(self.run_filter("-like", "*"), ["star", "soc", "embedded", "double"])
        self.assertEqual(self.run_filter("-notlike", "*"), ["absent", "null", "empty"])

    def test_embedded_stars_and_ldap_explanation_remain_literal(self):
        self.assertEqual(self.run_filter("-eq", "S*OC"), ["embedded"])
        self.assertEqual(translate_ps_filter_to_ldap('Department -eq "S*OC"'), r"(Department=S\2aOC)")
        for operator, fragment in (("-eq", r"(Department=\2a)"), ("-ne", r"(!(Department=\2a))")):
            with self.subTest(operator=operator):
                result = explain_ldap(f'Get-ADUser -Filter \'Department {operator} "*"\'')
                self.assertEqual(result["status"], "ok", result)
                self.assertIn(fragment, result["text"])
                self.assertNotIn("(Department=*)", result["text"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
