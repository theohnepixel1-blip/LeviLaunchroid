
#!/usr/bin/env python3
"""Storage UI refinements. Runs after ui_changes_6.py."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

CONTENT_LIST = (
    "app/src/main/java/org/levimc/launcher/ui/activities/"
    "ContentListActivity.java"
)
CONTENT_MANAGEMENT = (
    "app/src/main/java/org/levimc/launcher/ui/activities/"
    "ContentManagementActivity.java"
)
MAIN_ACTIVITY = (
    "app/src/main/java/org/levimc/launcher/ui/activities/MainActivity.java"
)
LIST_LAYOUT = "app/src/main/res/layout/activity_content_list.xml"
MAIN_LAYOUT = "app/src/main/res/layout/activity_main.xml"


def edit(rel, old, new, label):
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")

    if old not in text:
        if new in text:
            print(f"already applied: {label}")
            return
        sys.exit(f"anchor missing for {label} in {rel}")

    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"ok: {label}")


def edit_regex(rel, pattern, replacement, label):
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)

    if count == 0:
        if replacement in text:
            print(f"already applied: {label}")
            return
        sys.exit(f"anchor missing for {label} in {rel}")

    path.write_text(updated, encoding="utf-8")
    print(f"ok: {label}")


def remove_method(rel, method_name, next_method, label):
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")

    start = text.find(method_name)
    if start == -1:
        print(f"already removed: {label}")
        return

    end = text.find(next_method, start)
    if end == -1:
        sys.exit(f"Could not find end of {label}")

    path.write_text(text[:start] + text[end:], encoding="utf-8")
    print(f"ok: removed {label}")


# ---------------------------------------------------------------------
# 1. ContentListActivity
# ---------------------------------------------------------------------

def list_activity():
    path = ROOT / CONTENT_LIST
    text = path.read_text(encoding="utf-8")

    # Remove the custom flat-world launcher field.
    text = text.replace(
        "    private ActivityResultLauncher<Intent> customFlatWorldLauncher;\n",
        ""
    )

    # Remove its Activity Result registration.
    text, count = re.subn(
        r"        customFlatWorldLauncher = registerForActivityResult\(.*?"
        r"        \);\n\n",
        "",
        text,
        count=1,
        flags=re.S,
    )
    if count:
        print("ok: removed flat-world launcher registration")

    # Remove the custom flat-world button listener.
    text = text.replace(
        "        binding.customFlatButton.setOnClickListener(v -> {\n"
        "            if (contentType == TYPE_SERVERS) showAddServerDialog();\n"
        "            else openCustomFlatWorld();\n"
        "        });\n",
        ""
    )

    # Remove its primary-button styling.
    text = text.replace(
        "        UiKit.applyPrimary(binding.customFlatButton);\n",
        ""
    )

    # Keep sorting permanently set to name ascending.
    old_sort = (
        '        SharedPreferences prefs = getSharedPreferences("content_management", MODE_PRIVATE);\n'
        '        sortField = prefs.getInt("sort_field_" + contentType, SORT_NAME);\n'
        '        if (!supportsTimeSort()) sortField = SORT_NAME;\n'
        '        sortAscending = prefs.getBoolean("sort_asc_" + contentType, true);'
    )
    new_sort = (
        '        sortField = SORT_NAME;\n'
        '        sortAscending = true;'
    )

    if old_sort in text:
        text = text.replace(old_sort, new_sort, 1)
        print("ok: force name ascending")
    elif new_sort in text:
        print("already applied: force name ascending")
    else:
        sys.exit("sort preference anchor missing")

    # Hide the sort button.
    text = text.replace(
        "        binding.sortButton.setOnClickListener(v -> showSortMenu());\n",
        ""
    )
    text = text.replace(
        "        loadSortPreference();\n"
        "        updateSortLabel();",
        "        loadSortPreference();\n"
        "        binding.sortButton.setVisibility(View.GONE);"
    )

    # All categories use the same Search placeholder.
    marker = (
        "    private void applyCategoryChrome() {\n"
        "        binding.titleText.setText(getString(R.string.content_management));"
    )
    replacement = (
        "    private void applyCategoryChrome() {\n"
        "        binding.titleText.setText(getString(R.string.content_management));\n"
        '        binding.searchEditText.setHint("Search");'
    )
    if marker in text:
        text = text.replace(marker, replacement, 1)
    elif replacement not in text:
        sys.exit("applyCategoryChrome anchor missing")

    # Persist the selected category when changing tabs.
    old_switch = (
        "        contentType = type;\n"
        "        applyCategoryChrome();"
    )
    new_switch = (
        "        contentType = type;\n"
        '        getSharedPreferences("content_management", MODE_PRIVATE).edit()\n'
        '                .putInt("last_content_type", contentType).apply();\n'
        "        applyCategoryChrome();"
    )
    if old_switch in text:
        text = text.replace(old_switch, new_switch, 1)
    elif new_switch not in text:
        sys.exit("switchCategory persistence anchor missing")

    # Remove the custom flat-world function.
    start = text.find("    private void openCustomFlatWorld() {")
    if start != -1:
        end = text.find(
            "    private void showExtractStructuresDialog(",
            start
        )
        if end == -1:
            sys.exit("flat-world method end anchor missing")
        text = text[:start] + text[end:]
        print("ok: removed custom flat-world function")

    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------
# 2. Storage category persistence
# ---------------------------------------------------------------------

def storage_activity():
    # The Storage overview remembers its last selected category.
    old = (
        "        binding.categoryTabs.setSelectedIndex(0, false);\n"
        "        binding.categoryTabs.setOnSegmentSelectedListener(index -> openContentList(STORAGE_TYPES[index]));"
    )

    new = (
        '        int lastType = getSharedPreferences("content_management", MODE_PRIVATE)\n'
        '                .getInt("last_content_type", ContentListActivity.TYPE_WORLDS);\n'
        "        int selected = 0;\n"
        "        for (int i = 0; i < STORAGE_TYPES.length; i++) {\n"
        "            if (STORAGE_TYPES[i] == lastType) selected = i;\n"
        "        }\n"
        "        binding.categoryTabs.setSelectedIndex(selected, false);\n"
        "        binding.categoryTabs.setOnSegmentSelectedListener(index -> {\n"
        "            int type = STORAGE_TYPES[index];\n"
        '            getSharedPreferences("content_management", MODE_PRIVATE).edit()\n'
        '                    .putInt("last_content_type", type).apply();\n'
        "            openContentList(type);\n"
        "        });"
    )

    edit(
        CONTENT_MANAGEMENT,
        old,
        new,
        "remember selected Storage category",
    )

    # Restore the saved category when returning from a content list.
    old_resume = (
        "        loadStorageType();\n"
        "        updateStorageLabel();\n"
        "        loadCurrentVersion();"
    )

    new_resume = (
        "        loadStorageType();\n"
        "        updateStorageLabel();\n"
        "        loadCurrentVersion();\n"
        "        restoreStorageCategory();"
    )

    edit(
        CONTENT_MANAGEMENT,
        old_resume,
        new_resume,
        "restore Storage category on return",
    )

    restore_method = (
        "    private void restoreStorageCategory() {\n"
        '        int lastType = getSharedPreferences("content_management", MODE_PRIVATE)\n'
        '                .getInt("last_content_type", ContentListActivity.TYPE_WORLDS);\n'
        "        int selected = 0;\n"
        "        for (int i = 0; i < STORAGE_TYPES.length; i++) {\n"
        "            if (STORAGE_TYPES[i] == lastType) selected = i;\n"
        "        }\n"
        "        binding.categoryTabs.setSelectedIndex(selected, false);\n"
        "    }\n\n"
    )

    path = ROOT / CONTENT_MANAGEMENT
    text = path.read_text(encoding="utf-8")

    if "private void restoreStorageCategory()" not in text:
        marker = "    @Override\n    protected void onSaveInstanceState("
        if marker not in text:
            sys.exit("Storage restore method insertion anchor missing")
        text = text.replace(marker, restore_method + marker, 1)
        path.write_text(text, encoding="utf-8")
        print("ok: added Storage category restoration")


# ---------------------------------------------------------------------
# 3. Move Internal / External beside Search
# ---------------------------------------------------------------------

def list_layout():
    path = ROOT / LIST_LAYOUT
    text = path.read_text(encoding="utf-8")

    # Remove the storage button from the instance information row.
    storage_button = re.search(
        r'        <com\.google\.android\.material\.button\.MaterialButton '
        r'[^>]*android:id="@\+id/strip_storage_value"[^>]*/>\n',
        text,
    )

    if storage_button:
        button = storage_button.group(0).strip()
        text = text[:storage_button.start()] + text[storage_button.end():]

        search_end = (
            ' android:id="@+id/search_edit_text"'
        )
        index = text.find(search_end)
        if index == -1:
            sys.exit("Search input not found")

        line_end = text.find("\n", index)
        text = text[:line_end] + "\n                " + button + text[line_end:]
        print("ok: moved storage toggle beside Search")
    elif text.count('android:id="@+id/strip_storage_value"') == 1:
        print("already applied: storage toggle position")
    else:
        sys.exit("Storage toggle view missing or duplicated")

    # Remove the visible item count beside the Storage title.
    text = re.sub(
        r'(android:id="@\+id/item_count_text"[^>]*?)(\s*/>)',
        r'\1 android:visibility="gone"\2',
        text,
        count=1,
    )

    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------
# 4. Internal / External toggle
# ---------------------------------------------------------------------

def storage_toggle():
    old = (
        '        binding.stripStorageValue.setOnClickListener(v -> ContentStorageSelector.show(\n'
        '                binding.stripStorageValue, versionManager.getSelectedVersion(), currentStorageType, type -> {\n'
        '                    exitSelectionMode();\n'
        '                    currentStorageType = type;\n'
        '                    getSharedPreferences("content_management", MODE_PRIVATE).edit()\n'
        '                            .putString("storage_type", type.name()).apply();\n'
        '                    worldsDirectory = getWorldsDirectoryForType(type);\n'
        '                    configureContentDirectories();\n'
        '                    updateInfoStrip();\n'
        '                    binding.contentRecyclerView.stopScroll();\n'
        '                    binding.contentRecyclerView.scrollToPosition(0);\n'
        '                    loadContent();\n'
        '                }));'
    )

    new = (
        '        binding.stripStorageValue.setOnClickListener(v -> toggleStorageType());'
    )

    edit(
        CONTENT_LIST,
        old,
        new,
        "replace storage selector with toggle",
    )

    method = (
        "    private void toggleStorageType() {\n"
        "        GameVersion version = versionManager.getSelectedVersion();\n"
        "        if (version == null) return;\n\n"
        "        boolean external = currentStorageType == FeatureSettings.StorageType.EXTERNAL\n"
        "                || currentStorageType == FeatureSettings.StorageType.VERSION_ISOLATION_EXTERNAL\n"
        "                || currentStorageType == FeatureSettings.StorageType.VERSION_ISOLATION;\n\n"
        "        FeatureSettings.StorageType requested = external\n"
        "                ? FeatureSettings.StorageType.INTERNAL\n"
        "                : FeatureSettings.StorageType.EXTERNAL;\n\n"
        "        currentStorageType = LauncherStorage.normalizeContentStorageType(\n"
        "                requested, version.versionIsolation);\n\n"
        '        getSharedPreferences("content_management", MODE_PRIVATE).edit()\n'
        '                .putString("storage_type", currentStorageType.name()).apply();\n\n'
        "        exitSelectionMode();\n"
        "        worldsDirectory = getWorldsDirectoryForType(currentStorageType);\n"
        "        configureContentDirectories();\n"
        "        updateInfoStrip();\n"
        "        binding.contentRecyclerView.stopScroll();\n"
        "        binding.contentRecyclerView.scrollToPosition(0);\n"
        "        loadContent();\n"
        "    }\n\n"
    )

    path = ROOT / CONTENT_LIST
    text = path.read_text(encoding="utf-8")

    if "private void toggleStorageType()" not in text:
        marker = "    private void updateInfoStrip() {"
        if marker not in text:
            sys.exit("toggle insertion anchor missing")
        text = text.replace(marker, method + marker, 1)
        path.write_text(text, encoding="utf-8")
        print("ok: added Internal/External toggle")


# ---------------------------------------------------------------------
# 5. Hide home Storage counts
# ---------------------------------------------------------------------

def home_layout():
    path = ROOT / MAIN_LAYOUT
    text = path.read_text(encoding="utf-8")

    for view in (
        "content_worlds_count",
        "content_resource_packs_count",
        "content_skin_packs_count",
    ):
        marker = f'android:id="@+id/{view}"'
        if marker not in text:
            sys.exit(f"Missing home count: {view}")

        # Only add visibility if it is not already present.
        pattern = re.compile(
            r'(<TextView\b[^>]*android:id="@\+id/'
            + re.escape(view)
            + r'"[^>]*)(\s*/>)'
        )

        def hide(match):
            attrs = match.group(1)
            if "android:visibility=" in attrs:
                return match.group(0)
            return attrs + ' android:visibility="gone"' + match.group(2)

        text = pattern.sub(hide, text, count=1)

    path.write_text(text, encoding="utf-8")
    print("ok: hid Storage category counts")


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    list_activity()
    storage_activity()
    list_layout()
    storage_toggle()
    home_layout()
    print("Storage UI refinements complete.")


if __name__ == "__main__":
    main()
  
