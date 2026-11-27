"""Second round of UI changes. Runs after ui_changes.py."""

RES = "app/src/main/res/layout/"
SRC = "app/src/main/java/org/levimc/launcher/"
GONE = 'android:visibility="gone" '


def edit(path, old, new):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if text.count(old) != 1:
        raise SystemExit(f"{path}: expected exactly one match for {old!r}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.replace(old, new))


def hide(path, view):
    marker = f'android:id="@+id/{view}"'
    edit(path, marker, f"{marker}\n{GONE}")


# Launch page: the card fills the page; no instance picker or settings gear.
main = RES + "activity_main.xml"
edit(main,
     'android:id="@+id/main_card" style="@style/Widget.Levi.Card" android:layout_width="match_parent" android:layout_height="wrap_content"',
     'android:id="@+id/main_card" style="@style/Widget.Levi.Card" android:layout_width="match_parent" android:layout_height="0dp" android:layout_weight="1"')
edit(main, 'android:layout_marginTop="8dp" android:layout_weight="1" android:baselineAligned="false"',
     'android:layout_marginTop="8dp" android:layout_weight="0" android:baselineAligned="false"')
hide(main, "select_version_button")
hide(main, "home_instance_settings_button")

# Sidebar: no Download, About, theme button or notifications.
hide(RES + "shell_navbar.xml", "nav_tab_download")
hide(RES + "shell_navbar.xml", "nav_tab_about")
hide(RES + "shell_account_cluster.xml", "nav_news_container")
# The code re-shows the theme button, so change that too.
edit(SRC + "ui/activities/BaseActivity.java",
     "themeToggle.setVisibility(View.VISIBLE);",
     "themeToggle.setVisibility(View.GONE);")

# Only the Minecraft app installed on the phone. Other instances stay on disk.
edit(SRC + "core/versions/VersionManager.java",
     "File[] dirs = baseDir.listFiles(File::isDirectory);\n\n        if (dirs != null) {\n            for (File dir : dirs) {\n                File apk",
     "File[] dirs = null; // imported instances are not listed\n\n        if (dirs != null) {\n            for (File dir : dirs) {\n                File apk")

# Settings: add a row that opens the instance settings.
ROW = '''<LinearLayout style="@style/settings_Row">
    <LinearLayout style="@style/settings_RowText">
        <TextView style="@style/settings_RowTitle" android:text="@string/instance_settings_title" />
    </LinearLayout>
    <com.google.android.material.button.MaterialButton
        android:id="@+id/settings_instance_button"
        style="@style/Widget.Levi.Button.Secondary"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@string/home_manage" />
</LinearLayout>
<View style="@style/settings_Divider" />
'''
sections = RES + "view_settings_sections.xml"
with open(sections, encoding="utf-8") as f:
    text = f.read()
body = 'style="@style/settings_CardBody">'
at = text.index(body, text.index('android:id="@+id/section_basic"')) + len(body)
with open(sections, "w", encoding="utf-8") as f:
    f.write(text[:at] + "\n" + ROW + text[at:])

CLICK = '''findViewById(R.id.settings_instance_button).setOnClickListener(v -> {
            org.levimc.launcher.core.versions.GameVersion current =
                    org.levimc.launcher.core.versions.VersionManager.get(this).getSelectedVersion();
            if (current == null) {
                android.widget.Toast.makeText(this, R.string.not_found_version,
                        android.widget.Toast.LENGTH_SHORT).show();
                return;
            }
            Intent intent = new Intent(this, InstanceSettingsActivity.class);
            intent.putExtra("version", current);
            startActivity(intent);
        });
        '''
language = "findViewById(R.id.language_change).setOnClickListener"
edit(SRC + "ui/activities/SettingsActivity.java", language, CLICK + language)

# Highlight Settings while the instance settings page is open.
edit(SRC + "ui/activities/InstanceSettingsActivity.java",
     "setActiveNavTab(R.id.nav_tab_instances);",
     "setActiveNavTab(R.id.nav_tab_settings);")
