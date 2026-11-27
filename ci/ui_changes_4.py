"""Radiance name, orange theme, smaller Launch button. Runs after ui_changes_3.py."""
import pathlib
import re

MAIN = pathlib.Path("app/src/main")


def edit(path, old, new, count=1):
    text = path.read_text(encoding="utf-8")
    if text.count(old) != count:
        raise SystemExit(f"{path}: expected {count} of {old!r}, got {text.count(old)}")
    path.write_text(text.replace(old, new), encoding="utf-8")


# 1. Launch button: medium size, centred.
layout = MAIN / "res/layout/activity_main.xml"
edit(layout, 'android:layout_width="match_parent" android:layout_height="56dp" android:layout_marginBottom="10dp"',
     'android:layout_width="240dp" android:layout_height="56dp" android:layout_gravity="center_horizontal" android:layout_marginBottom="10dp"')
edit(layout, 'android:layout_height="56dp"', 'android:layout_height="50dp"', 3)

# 2. Name. Only text people see; package names, links and folders stay as they are.
for path in MAIN.glob("res/values*/*.xml"):
    text = path.read_text(encoding="utf-8")
    new = re.sub(r"LeviLauncher(?!-Android)", "Radiance", text)  # keeps repository links
    if new != text:
        path.write_text(new, encoding="utf-8")
news = MAIN / "java/org/levimc/launcher/core/news/LauncherNewsMessagingService.java"
edit(news, '"LeviLauncher news"', '"Radiance news"')
edit(news, '"Open LeviLauncher to', '"Open Radiance to')

# 3. Colours: swap each green for a yellow/orange shade.
COLOURS = {
    "10B981": "FF9F0A",  # main accent
    "059669": "D97706",
    "34D399": "FBBF24",  # highlights in dark mode
    "047857": "B45309",
    "E8F5E9": "FFF3E0",
    "F1F8E9": "FFF4E5",
    "F8FFF0": "FFF9F0",
    "1A3A2A": "3A2A10",
}
pattern = re.compile(r"(#|0x)((?:[0-9A-Fa-f]{2})?)(" + "|".join(COLOURS) + r")\b", re.I)
for path in [*MAIN.glob("res/**/*.xml"), *MAIN.glob("java/**/*.java"), *MAIN.glob("java/**/*.kt")]:
    text = path.read_text(encoding="utf-8")
    new = pattern.sub(lambda m: m[1] + m[2] + COLOURS[m[3].upper()], text)
    if new != text:
        path.write_text(new, encoding="utf-8")

# Dark text on bright accents, so the Launch label stays readable.
edit(MAIN / "java/org/levimc/launcher/util/ThemePalette.java",
     "return Color.WHITE;\n    }",
     "return luminance(accent) > 0.4 ? 0xFF231600 : Color.WHITE;\n    }")
for colours in ("res/values/colors.xml", "res/values-night/colors.xml"):
    edit(MAIN / colours, '<color name="on_primary">#FFFFFF</color>',
         '<color name="on_primary">#231600</color>')
