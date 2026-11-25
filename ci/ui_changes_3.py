"""Launch page changes. Runs after ui_changes.py and ui_changes_2.py."""
import re

PATH = "app/src/main/res/layout/activity_main.xml"

with open(PATH, encoding="utf-8") as f:
    text = f.read()


def sub(pattern, replacement, count=1):
    global text
    text, found = re.subn(pattern, replacement, text)
    if found != count:
        raise SystemExit(f"{PATH}: expected {count} match(es) for {pattern!r}, got {found}")


# Remove the "Minecraft" and "Bedrock Edition" text.
sub(r'android:id="@\+id/minecraft_title_text"', r'\g<0> android:visibility="gone"')
sub(r'android:text="@string/bedrock_edition"', r'\g<0> android:visibility="gone"')

# Hide the tips. "invisible" keeps their space free for later.
sub(r'android:gravity="center_vertical" android:orientation="horizontal" android:layout_gravity="center_vertical"',
    r'\g<0> android:visibility="invisible"')

# Take the Launch button out of the top row.
group = re.search(r'[ \t]*<LinearLayout android:id="@\+id/home_launch_group".*?</LinearLayout>\n', text, re.S)
if not group:
    raise SystemExit(f"{PATH}: launch button not found")
button = group.group(0)
text = text.replace(button, "")


def change(old, new, count=1):
    global button
    if button.count(old) != count:
        raise SystemExit(f"launch button: expected {count} of {old!r}")
    button = button.replace(old, new)


# Make it taller and as wide as the card.
change('android:layout_height="44dp"', 'android:layout_height="56dp"', 3)
change('android:layout_width="wrap_content" android:layout_height="56dp" android:layout_marginStart="10dp"',
       'android:layout_width="match_parent" android:layout_height="56dp" android:layout_marginBottom="10dp"')
change('android:layout_width="wrap_content" android:layout_height="56dp" android:minWidth="0dp"',
       'android:layout_width="0dp" android:layout_weight="1" android:layout_height="56dp" android:minWidth="0dp"')
change('android:textSize="13sp"', 'android:textSize="16sp"')

# Put it just above the line.
line = '<View android:layout_width="match_parent" android:layout_height="1dp" android:background="@color/divider" />'
if text.count(line) != 1:
    raise SystemExit(f"{PATH}: divider line not found")
text = text.replace(line, button.strip() + "\n            " + line)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(text)
