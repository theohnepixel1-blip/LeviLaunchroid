"""Fifth round of UI changes: Randiance name, orange R logo, more Radiance colours.

Runs after ui_changes_4.py (registered in ci/prepare_fork_build.sh). Safe to run twice.
Package names, storage folder names and URLs are left alone.
"""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "app/src/main/res"

# The orange "R" traced from the logo image (1254 x 1254 viewport, even-odd so the counter is a hole).
R_PATH = (
    "M177,170 H700 C860,170 1005,260 1005,420 C1005,560 930,650 780,680 "
    "C840,697 875,715 905,750 C925,775 945,805 960,830 L1080,1080 H764 "
    "L600,790 C560,725 520,710 462,710 V1080 H177 Z "
    "M462,352 H595 C680,352 720,390 720,445 C720,495 690,522 655,530 "
    "C620,537 595,540 575,540 H462 Z"
)


def vector(size_dp, color, comment=None):
    head = '<?xml version="1.0" encoding="utf-8"?>\n'
    if comment:
        head += f"<!-- {comment} -->\n"
    return (
        head
        + '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
        + f'    android:width="{size_dp}dp"\n'
        + f'    android:height="{size_dp}dp"\n'
        + '    android:viewportWidth="1254"\n'
        + '    android:viewportHeight="1254">\n'
        + "    <path\n"
        + f'        android:fillColor="{color}"\n'
        + '        android:fillType="evenOdd"\n'
        + f'        android:pathData="{R_PATH}" />\n'
        + "</vector>\n"
    )


def write_if_changed(path, text, label):
    if path.exists() and path.read_text(encoding="utf-8") == text:
        print(f"already applied: {label}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"ok: {label}")


def sub_once(rel, pattern, repl, label, flags=0):
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    new, n = re.subn(pattern, repl, text, count=1, flags=flags)
    if n == 0:
        sys.exit(f"anchor missing for {label} in {rel}")
    if new == text:
        print(f"already applied: {label}")
        return
    path.write_text(new, encoding="utf-8")
    print(f"ok: {label}")


# ---------------------------------------------------------------- logo

def logos():
    d = RES / "drawable"
    write_if_changed(d / "ic_leaf_logo.xml", vector(108, "#FFFFAA00", "Randiance logo: the orange R."), "R logo")
    write_if_changed(
        d / "ic_leaf_logo_mono.xml",
        vector(108, "#FFFFFFFF", "Randiance logo, single colour, for themed launcher icons."),
        "R mono logo",
    )
    write_if_changed(d / "ic_notification_leaf.xml", vector(24, "#FFFFFFFF"), "R notification icon")

    removed = 0
    for png in sorted(RES.glob("drawable*/ic_leaf_logo*.png")):
        png.unlink()
        removed += 1
    print(f"ok: removed {removed} leaf logo PNGs")

    # Same resource names are kept, so every layout that used the leaf now shows the R.
    sub_once(
        "app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml",
        r'android:inset="2[06]\.0%"',
        'android:inset="20.0%"',
        "launcher icon inset",
    )
    # The monochrome tag has its own inset, so run the substitution for it as well.
    path = RES / "mipmap-anydpi-v26/ic_launcher.xml"
    path.write_text(path.read_text(encoding="utf-8").replace('android:inset="26.0%"', 'android:inset="20.0%"'), encoding="utf-8")

    sub_once(
        "app/src/main/res/values/colors.xml",
        r'(<color name="ic_launcher_adaptive_back">)[^<]*(</color>)',
        r"\1#000000\2",
        "black launcher icon background",
    )


# ---------------------------------------------------------------- colours

RADIANCE = [
    ("FFFFAA00", "Randiance orange (logo)"), ("FFFF4D6D", "rose"), ("FFFF6B35", "flame"),
    ("FFFFB703", "gold"), ("FFFB8500", "mango"), ("FF80B918", "lime"),
    ("FF2DC653", "spring"), ("FF06D6A0", "mint"), ("FF1B9AAA", "lagoon"),
    ("FF4CC9F0", "ice"), ("FF00BBF9", "sky"), ("FF3A86FF", "cobalt"),
    ("FF4361EE", "royal"), ("FF7209B7", "grape"), ("FF8338EC", "violet"),
    ("FFC77DFF", "lavender"), ("FF9D4EDD", "amethyst"), ("FFF72585", "magenta"),
    ("FFFF006E", "neon pink"), ("FFB5179E", "orchid"), ("FFEF476F", "watermelon"),
    ("FFFF5D8F", "blush"), ("FFFB5607", "burnt orange"), ("FFFFD166", "sunflower"),
    ("FF8AC926", "chartreuse"), ("FFFF8FA3", "petal"), ("FFE63946", "crimson"),
    ("FFD00000", "ruby"), ("FFDC2F02", "vermilion"), ("FFE85D04", "ember"),
    ("FFF48C06", "tangerine"), ("FFFFBA08", "honey"), ("FFFAA307", "saffron"),
    ("FFD4A373", "sand"), ("FFBC6C25", "copper"), ("FF9C6644", "clay"),
    ("FF55A630", "fern"), ("FF38B000", "clover"), ("FF008000", "forest"),
    ("FF2A9D8F", "sea teal"), ("FF48CAE4", "aqua"), ("FF0096C7", "azure"),
    ("FF0077B6", "deep ocean"), ("FF023E8A", "navy"), ("FF5E60CE", "indigo"),
    ("FF6930C9", "ultraviolet"), ("FFE0AAFF", "lilac"), ("FFFF99C8", "bubblegum"),
    ("FFADB5BD", "silver"), ("FF6C757D", "slate"),
]


def colours():
    palette = ROOT / "app/src/main/java/org/levimc/launcher/util/ThemePalette.java"
    if "int[] RADIANCE" not in palette.read_text(encoding="utf-8"):
        print("skipped: this branch has no Radiance colour list yet (run ui_changes_theme.py first)")
        return
    body = "\n".join(f"            0x{c}, // {name}" for c, name in RADIANCE)
    sub_once(
        "app/src/main/java/org/levimc/launcher/util/ThemePalette.java",
        r"(public static final int\[\] RADIANCE = \{\n).*?(\n    \};)",
        lambda m: m.group(1) + body + m.group(2),
        f"{len(RADIANCE)} Radiance colours",
        flags=re.DOTALL,
    )


# ---------------------------------------------------------------- name

# Matches LeviLauncher / Levi Launcher / Levilauncher / LeviLaunchroid, but not names like
# Theme.LeviLauncher, @string/levilauncher_x or file paths.
NAME = re.compile(r"(?<![\w.@/\\-])Levi ?[Ll]aunch(?:er|roid)(?![\w])")
TEXT = re.compile(r">([^<>]*)<")


def rename_text(text):
    return TEXT.sub(lambda m: ">" + NAME.sub("Randiance", m.group(1)) + "<", text)


def rename():
    changed = 0
    for path in sorted(RES.glob("values*/*.xml")):
        text = path.read_text(encoding="utf-8")
        new = rename_text(text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1
    print(f"ok: renamed visible text in {changed} resource files")

    gradle = ROOT / "app/build.gradle"
    text = gradle.read_text(encoding="utf-8")
    new = text.replace('"LeviLauncher Beta"', '"Randiance Beta"')
    if new != text:
        gradle.write_text(new, encoding="utf-8")
        print("ok: beta app name")
    else:
        print("already applied: beta app name")

    for rel in (
        "app/src/main/java/org/levimc/launcher/util/ThemePalette.java",
        "app/src/main/res/values/colors.xml",
    ):
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        new = text.replace("LeviLauncher for Windows", "the Randiance Windows launcher")
        if new != text:
            path.write_text(new, encoding="utf-8")


def main():
    logos()
    colours()
    rename()


if __name__ == "__main__":
    main()
      
