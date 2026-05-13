import os
import unittest
import json

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSONAS_DIR = os.path.join(REPO_ROOT, "personas")
REGISTRY_PATH = os.path.join(REPO_ROOT, "personas.json")

VALID_TIERS = {"SOVEREIGN", "ADVANCED_INFRASTRUCTURE", "PRO", "ADVANCED_TOOL", "BASIC_TOOL", "ARCHETYPE"}
VALID_CATEGORIES = {
    "engineering", "design", "marketing", "finance", "product", "sales",
    "support", "strategy", "specialized",
    # Archetype categories (abstract behavioral patterns, not job roles)
    "security", "creative", "analysis", "execution", "wisdom",
}

class TestPersonaStructure(unittest.TestCase):
    def test_registry_valid(self):
        with open(REGISTRY_PATH, encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("personas", data)
        for p in data["personas"]:
            self.assertIn(p["tier"], VALID_TIERS, f"Invalid tier for {p['name']}")
            self.assertIn(p["category"], VALID_CATEGORIES, f"Invalid category for {p['name']}")
            path = os.path.join(REPO_ROOT, p["file"])
            self.assertTrue(os.path.isfile(path), f"ملف مفقود: {p['file']}")

    def test_frontmatter_has_required_fields(self):
        for root, _, files in os.walk(PERSONAS_DIR):
            for f in files:
                if not f.endswith(".md"): continue
                if f == "persona-template.md": continue

                with open(os.path.join(root, f), encoding="utf-8") as fh:
                    content = fh.read()

                self.assertIn("name:", content, f"{f} يفتقر إلى name")
                self.assertIn("tier:", content, f"{f} يفتقر إلى tier")
                self.assertIn("category:", content, f"{f} يفتقر إلى category")
                self.assertIn("## 🧠 الهوية والذاكرة", content, f"{f} يفتقر إلى قسم الهوية")
                self.assertIn("## 🎯 المهمة الأساسية", content, f"{f} يفتقر إلى قسم المهمة")
                self.assertIn("## 🚨 القواعد الحرجة", content, f"{f} يفتقر إلى قسم القواعد")

if __name__ == "__main__":
    unittest.main()
