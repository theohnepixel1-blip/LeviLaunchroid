#!/usr/bin/env python3
"""Rename Content Management to Storage, add a category top bar, drop servers."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def replace_once(rel, old, new, label):
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    if old not in text:
        if new in text:
            print(f"already applied: {label}")
            return
        sys.exit(f"anchor missing for {label} in {rel}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"ok: {label}")


def rename_strings():
    pattern = re.compile(
        r'(<string name="(?:content_management|content_mgmt_section_title|crumb_content)">)(.*?)(</string>)'
    )
    changed = 0
    for path in (ROOT / "app/src/main/res").rglob("*.xml"):
        text = path.read_text(encoding="utf-8")
        updated, n = pattern.subn(r"\1Storage\3", text)
        if n:
            path.write_text(updated, encoding="utf-8")
            changed += n
    print(f"ok: renamed {changed} content-management strings to Storage")


CATEGORY_BAR = """    <TextView android:layout_width="match_parent" android:layout_height="wrap_content" android:layout_marginTop="10dp" android:text="@string/content_management_subtitle" android:textAppearance="@style/TextAppearance.Levi.Caption" android:textSize="12sp" />
    <HorizontalScrollView android:layout_width="match_parent" android:layout_height="wrap_content" android:layout_marginTop="10dp" android:fillViewport="false" android:overScrollMode="never" android:scrollbars="none">
        <org.levimc.launcher.ui.widget.SegmentedControl android:id="@+id/category_tabs" android:layout_width="wrap_content" android:layout_height="wrap_content" />
    </HorizontalScrollView>
"""


def storage_layout():
    path = ROOT / "app/src/main/res/layout/activity_content_management.xml"
    text = path.read_text(encoding="utf-8")
    if 'android:id="@+id/category_tabs"' in text and "servers_button" not in text:
        print("already applied: storage layout")
        return
    start = text.find("    <ScrollView ")
    end = text.find("    </ScrollView>", start)
    if start < 0 or end < 0:
        sys.exit("content management scroll view not found")
    end += len("    </ScrollView>\n")
    path.write_text(text[:start] + CATEGORY_BAR + text[end:], encoding="utf-8")
    print("ok: storage layout")


def storage_activity():
    replace_once(
        "app/src/main/java/org/levimc/launcher/ui/activities/ContentManagementActivity.java",
        """        setupStorageSelector();
        setupCategoryButtons();
        contentManager.getCountsLiveData().observe(this, counts -> {
            if (counts == null) return;
            binding.worldsCount.setText(getString(R.string.content_category_count, getString(R.string.worlds_category), counts.worlds));
            binding.resourcePacksCount.setText(getString(R.string.content_category_count, getString(R.string.resource_packs_category), counts.resourcePacks));
            binding.skinPacksCount.setText(getString(R.string.content_category_count, getString(R.string.skin_packs_category), counts.skinPacks));
            binding.behaviorPacksCount.setText(getString(R.string.content_category_count, getString(R.string.behavior_packs_category), counts.behaviorPacks));
        });
    }""",
        """        setupStorageSelector();
        setupCategoryBar();
    }""",
        "storage setupUI",
    )
    replace_once(
        "app/src/main/java/org/levimc/launcher/ui/activities/ContentManagementActivity.java",
        """    private void setupCategoryButtons() {
        UiKit.tintIconChip(binding.worldsChip, binding.worldsIcon, UiKit.BLUE);
        UiKit.tintIconChip(binding.resourcePacksChip, binding.resourcePacksIcon, UiKit.PURPLE);
        UiKit.tintIconChip(binding.behaviorPacksChip, binding.behaviorPacksIcon, UiKit.ORANGE);
        UiKit.tintIconChip(binding.skinPacksChip, binding.skinPacksIcon, UiKit.PINK);
        UiKit.tintIconChip(binding.serversChip, binding.serversIcon, UiKit.INDIGO);
        UiKit.tintIconChip(binding.screenshotsChip, binding.screenshotsIcon, UiKit.TEAL);
        binding.worldsButton.setOnClickListener(v -> openContentList(ContentListActivity.TYPE_WORLDS));
        binding.skinPacksButton.setOnClickListener(v -> openContentList(ContentListActivity.TYPE_SKIN_PACKS));
        binding.resourcePacksButton.setOnClickListener(v -> openContentList(ContentListActivity.TYPE_RESOURCE_PACKS));
        binding.behaviorPacksButton.setOnClickListener(v -> openContentList(ContentListActivity.TYPE_BEHAVIOR_PACKS));
        binding.screenshotsButton.setOnClickListener(v -> openContentList(ContentListActivity.TYPE_SCREENSHOTS));
        binding.serversButton.setOnClickListener(v -> openContentList(ContentListActivity.TYPE_SERVERS));
    }""",
        """    private static final int[] STORAGE_TYPES = {
            ContentListActivity.TYPE_WORLDS,
            ContentListActivity.TYPE_RESOURCE_PACKS,
            ContentListActivity.TYPE_BEHAVIOR_PACKS,
            ContentListActivity.TYPE_SKIN_PACKS,
            ContentListActivity.TYPE_SCREENSHOTS
    };

    private void setupCategoryBar() {
        binding.categoryTabs.setEqualWidth(false);
        binding.categoryTabs.setTextSizeSp(12f);
        binding.categoryTabs.setItems(
                getString(R.string.worlds_category),
                getString(R.string.resource_packs_category),
                getString(R.string.behavior_packs_category),
                getString(R.string.skin_packs_category),
                getString(R.string.content_ui_screenshots));
        binding.categoryTabs.setSelectedIndex(0, false);
        binding.categoryTabs.setOnSegmentSelectedListener(index -> openContentList(STORAGE_TYPES[index]));
    }""",
        "storage category bar",
    )
    replace_once(
        "app/src/main/java/org/levimc/launcher/ui/activities/ContentManagementActivity.java",
        """        contentManager.configureStorageDirectories(worldsDir, resourcePacksDir, behaviorPacksDir, skinPacksDir, screenshotsDir, minecraftPeDir);
        contentManager.refreshCounts();
        refreshExtraCounts(screenshotsDir, minecraftPeDir);
    }

    private void refreshExtraCounts(File screenshotsDir, File minecraftPeDir) {
        long generation = countGeneration.incrementAndGet();
        if (countExecutor.isShutdown()) return;
        countExecutor.execute(() -> {
            int screenshots = 0;
            int servers = 0;
            try {
                ScreenshotManager shots = new ScreenshotManager();
                shots.setScreenshotsDirectory(screenshotsDir);
                screenshots = shots.getScreenshots().size();
            } catch (Exception ignored) {
            }
            try {
                ServerManager serverManager = new ServerManager();
                serverManager.setMinecraftPeDirectory(minecraftPeDir);
                servers = serverManager.getServers().size();
            } catch (Exception ignored) {
            }
            int screenshotCount = screenshots;
            int serverCount = servers;
            mainHandler.post(() -> {
                if (generation != countGeneration.get() || isFinishing() || isDestroyed()) return;
                binding.screenshotsCount.setText(getString(R.string.content_category_count, getString(R.string.content_ui_screenshots), screenshotCount));
                binding.serversCount.setText(getString(R.string.content_category_count, getString(R.string.servers_category), serverCount));
            });
        });
    }""",
        """        contentManager.configureStorageDirectories(worldsDir, resourcePacksDir, behaviorPacksDir, skinPacksDir, screenshotsDir, minecraftPeDir);
        contentManager.refreshCounts();
    }""",
        "remove server counts",
    )


LIST_BAR = """            </LinearLayout>
            <HorizontalScrollView android:layout_width="match_parent" android:layout_height="wrap_content" android:layout_marginTop="8dp" android:fillViewport="false" android:overScrollMode="never" android:scrollbars="none">
                <org.levimc.launcher.ui.widget.SegmentedControl android:id="@+id/category_tabs" android:layout_width="wrap_content" android:layout_height="wrap_content" />
            </HorizontalScrollView>
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:gravity="center_vertical" android:id="@+id/search_row\""""


def list_layout():
    rel = "app/src/main/res/layout/activity_content_list.xml"
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    if 'android:id="@+id/category_tabs"' in text:
        print("already applied: list layout")
        return
    old = """            </LinearLayout>
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal" android:gravity="center_vertical" android:id="@+id/search_row\""""
    if old not in text:
        sys.exit("list toolbar anchor missing")
    path.write_text(text.replace(old, LIST_BAR, 1), encoding="utf-8")
    print("ok: list layout")


def list_activity():
    rel = "app/src/main/java/org/levimc/launcher/ui/activities/ContentListActivity.java"
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    if "setupCategoryBar()" in text:
        print("already applied: list activity")
        return
    import_line = "import org.levimc.launcher.ui.widget.ContentStorageSelector;\n"
    if "import org.levimc.launcher.ui.widget.SegmentedControl;" not in text:
        text = text.replace(
            import_line,
            import_line + "import org.levimc.launcher.ui.widget.SegmentedControl;\n",
            1,
        )
    start = text.find("        switch (contentType) {")
    end = text.find("        binding.customFlatButton.setOnClickListener", start)
    if start < 0 or end < 0:
        sys.exit("content list switch not found")
    switch_block = text[start:end]
    for line in (
        "                binding.titleText.setText(getString(R.string.content_ui_worlds_title));\n",
        "                binding.titleText.setText(getString(R.string.skin_packs_title));\n",
        "                binding.titleText.setText(getString(R.string.resource_packs_title));\n",
        "                binding.titleText.setText(getString(R.string.behavior_packs_title));\n",
        "                binding.titleText.setText(getString(R.string.content_ui_screenshots));\n",
        "                binding.titleText.setText(getString(R.string.servers_category));\n",
    ):
        switch_block = switch_block.replace(line, "")
    method = (
        "    private static final int[] STORAGE_TYPES = {\n"
        "            TYPE_WORLDS, TYPE_RESOURCE_PACKS, TYPE_BEHAVIOR_PACKS, TYPE_SKIN_PACKS, TYPE_SCREENSHOTS\n"
        "    };\n\n"
        "    private void setupCategoryBar() {\n"
        "        binding.categoryTabs.setEqualWidth(false);\n"
        "        binding.categoryTabs.setTextSizeSp(12f);\n"
        "        binding.categoryTabs.setItems(\n"
        "                getString(R.string.worlds_category),\n"
        "                getString(R.string.resource_packs_category),\n"
        "                getString(R.string.behavior_packs_category),\n"
        "                getString(R.string.skin_packs_category),\n"
        "                getString(R.string.content_ui_screenshots));\n"
        "        int selected = 0;\n"
        "        for (int i = 0; i < STORAGE_TYPES.length; i++) {\n"
        "            if (STORAGE_TYPES[i] == contentType) selected = i;\n"
        "        }\n"
        "        binding.categoryTabs.setSelectedIndex(selected, false);\n"
        "        binding.categoryTabs.setOnSegmentSelectedListener(this::switchCategory);\n"
        "    }\n\n"
        "    private void switchCategory(int index) {\n"
        "        int type = STORAGE_TYPES[index];\n"
        "        if (type == contentType) return;\n"
        "        if (isSelectionMode()) exitSelectionMode();\n"
        "        contentType = type;\n"
        "        applyCategoryChrome();\n"
        "        binding.searchEditText.setText(\"\");\n"
        "        binding.contentRecyclerView.stopScroll();\n"
        "        binding.contentRecyclerView.scrollToPosition(0);\n"
        "        loadContent();\n"
        "    }\n\n"
        "    private void applyCategoryChrome() {\n"
        "        binding.titleText.setText(getString(R.string.content_management));\n"
        "        binding.customFlatButton.setVisibility(View.GONE);\n"
        "        binding.selectButton.setVisibility(View.GONE);\n"
        "        binding.searchRow.setVisibility(View.VISIBLE);\n"
        + switch_block
        + "    }\n\n"
    )
    text = (
        text[:start]
        + "        if (contentType == TYPE_SERVERS) contentType = TYPE_WORLDS;\n"
        + "        setupCategoryBar();\n"
        + "        applyCategoryChrome();\n\n"
        + text[end:]
    )
    marker = "    private void setupObservers() {"
    if marker not in text:
        sys.exit("setupObservers missing")
    text = text.replace(marker, method + marker, 1)
    old_obs = """    private void setupObservers() {
        switch (contentType) {
            case TYPE_WORLDS:
                contentManager.getWorldsLiveData().observe(this, worlds -> {
                    allWorlds = worlds != null ? worlds : new ArrayList<>();
                    if (worldsAdapter != null) {
                        worldsAdapter.retainSelections(allWorlds);
                        filterContent(binding.searchEditText.getText().toString());
                    }
                    showLoading(false);
                });
                break;
            case TYPE_SKIN_PACKS:
                contentManager.getSkinPacksLiveData().observe(this, packs -> updatePacksFromObserver(packs));
                break;
            case TYPE_RESOURCE_PACKS:
                contentManager.getResourcePacksLiveData().observe(this, packs -> updatePacksFromObserver(packs));
                break;
            case TYPE_BEHAVIOR_PACKS:
                contentManager.getBehaviorPacksLiveData().observe(this, packs -> updatePacksFromObserver(packs));
                break;
            case TYPE_SCREENSHOTS:
                contentManager.getScreenshotsLiveData().observe(this, screenshots -> {
                    List<org.levimc.launcher.core.content.ScreenshotItem> items = screenshots != null ? screenshots : new ArrayList<>();
                    if (screenshotsAdapter != null) screenshotsAdapter.updateData(items);
                    updateListState(items.size(), items.size(), "");
                    showLoading(false);
                });
                break;
            case TYPE_SERVERS:
                contentManager.getServersLiveData().observe(this, servers -> {
                    allServers = servers != null ? servers : new ArrayList<>();
                    if (serversAdapter != null) filterContent(binding.searchEditText.getText().toString());
                    showLoading(false);
                });
                break;
        }
    }"""
    new_obs = """    private void setupObservers() {
        contentManager.getWorldsLiveData().observe(this, worlds -> {
            allWorlds = worlds != null ? worlds : new ArrayList<>();
            if (contentType != TYPE_WORLDS || worldsAdapter == null) return;
            worldsAdapter.retainSelections(allWorlds);
            filterContent(binding.searchEditText.getText().toString());
            showLoading(false);
        });
        contentManager.getSkinPacksLiveData().observe(this, packs -> {
            if (contentType == TYPE_SKIN_PACKS) updatePacksFromObserver(packs);
        });
        contentManager.getResourcePacksLiveData().observe(this, packs -> {
            if (contentType == TYPE_RESOURCE_PACKS) updatePacksFromObserver(packs);
        });
        contentManager.getBehaviorPacksLiveData().observe(this, packs -> {
            if (contentType == TYPE_BEHAVIOR_PACKS) updatePacksFromObserver(packs);
        });
        contentManager.getScreenshotsLiveData().observe(this, screenshots -> {
            if (contentType != TYPE_SCREENSHOTS || screenshotsAdapter == null) return;
            List<org.levimc.launcher.core.content.ScreenshotItem> items = screenshots != null ? screenshots : new ArrayList<>();
            screenshotsAdapter.updateData(items);
            updateListState(items.size(), items.size(), "");
            showLoading(false);
        });
    }"""
    if old_obs not in text:
        sys.exit("observer block missing")
    text = text.replace(old_obs, new_obs, 1)
    old_views = """        final MaterialButton sortButton;
        final TextView stripInstanceValue;"""
    new_views = """        final MaterialButton sortButton;
        final SegmentedControl categoryTabs;
        final TextView stripInstanceValue;"""
    if old_views not in text:
        sys.exit("views field anchor missing")
    text = text.replace(old_views, new_views, 1)
    old_bind = """            sortButton = a.findViewById(R.id.sort_button);
            stripInstanceValue = a.findViewById(R.id.strip_instance_value);"""
    new_bind = """            sortButton = a.findViewById(R.id.sort_button);
            categoryTabs = a.findViewById(R.id.category_tabs);
            stripInstanceValue = a.findViewById(R.id.strip_instance_value);"""
    if old_bind not in text:
        sys.exit("views bind anchor missing")
    text = text.replace(old_bind, new_bind, 1)
    path.write_text(text, encoding="utf-8")
    print("ok: list activity")


def main():
    rename_strings()
    storage_layout()
    storage_activity()
    list_layout()
    list_activity()


if __name__ == "__main__":
    main()
