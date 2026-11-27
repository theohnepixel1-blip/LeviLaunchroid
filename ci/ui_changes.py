"""UI changes for this fork. Run from the repository root during the build."""

RES = "app/src/main/res/layout/"
JAVA = "app/src/main/java/org/levimc/launcher/ui/activities/"


def edit(path, old, new):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if text.count(old) != 1:
        raise SystemExit(f"{path}: expected exactly one match for {old!r}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.replace(old, new))


# Views are hidden, not deleted, because the app's code still looks them up.
GONE = 'android:visibility="gone" '

# Launch page: hide the Mods, Content Management and Content download cards.
edit(RES + "activity_main.xml",
     'android:layout_marginTop="8dp" android:layout_weight="1" android:baselineAligned="false"',
     GONE + 'android:layout_marginTop="8dp" android:layout_weight="1" android:baselineAligned="false"')

# Sidebar: hide the back arrow and the Instances tab.
navbar = RES + "shell_navbar.xml"
for view in ("nav_back_button", "nav_tab_instances"):
    edit(navbar, f'android:id="@+id/{view}"', f'android:id="@+id/{view}"\n{GONE}')


# Sidebar: add Mods and Content Management tabs above About.
def tab(view, icon, label):
    return f'''<TextView
    android:id="@+id/{view}"
    style="@style/Widget.Levi.NavbarItem"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:drawableStart="@drawable/{icon}"
    android:gravity="center_vertical"
    android:paddingVertical="14dp"
    android:paddingStart="16dp"
    android:paddingEnd="12dp"
    android:singleLine="false"
    android:maxLines="2"
    android:text="@string/{label}" />
'''


about = '''<TextView
                    android:id="@+id/nav_tab_about"'''
edit(navbar, about,
     tab("nav_tab_mods", "ic_ui_puzzle", "mods_section_title")
     + tab("nav_tab_content", "ic_content", "content_mgmt_section_title")
     + about)

base = JAVA + "BaseActivity.java"
edit(base, "R.id.nav_tab_about, R.id.nav_tab_settings",
     "R.id.nav_tab_about, R.id.nav_tab_settings, R.id.nav_tab_mods, R.id.nav_tab_content")
about_bind = "bindNavTab(R.id.nav_tab_about, AboutActivity.class);"
edit(base, about_bind,
     about_bind
     + "\n        bindNavTab(R.id.nav_tab_mods, ModsFullscreenActivity.class);"
     + "\n        bindNavTab(R.id.nav_tab_content, ContentManagementActivity.class);")

# Highlight the new tab on its own page.
edit(JAVA + "ModsFullscreenActivity.java",
     "setContentView(R.layout.activity_mods_fullscreen);",
     "setContentView(R.layout.activity_mods_fullscreen);\n        setActiveNavTab(R.id.nav_tab_mods);")
edit(JAVA + "ContentManagementActivity.java",
     "setContentView(binding.getRoot());",
     "setContentView(binding.getRoot());\n        setActiveNavTab(R.id.nav_tab_content);")
