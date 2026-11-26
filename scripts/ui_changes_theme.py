#!/usr/bin/env python3
"""Lock the launcher to its default dark colour and add a Radiance swatch group."""

from pathlib import Path
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


RADIANCE = """
    /** Extra Radiance accent colours, shown after the preset and Windows groups. */
    public static final int[] RADIANCE = {
            0xFFFF4D6D, // rose
            0xFFFF6B35, // flame
            0xFFFFB703, // gold
            0xFFFB8500, // mango
            0xFF80B918, // lime
            0xFF2DC653, // spring
            0xFF06D6A0, // mint
            0xFF1B9AAA, // lagoon
            0xFF4CC9F0, // ice
            0xFF00BBF9, // sky
            0xFF3A86FF, // cobalt
            0xFF4361EE, // royal
            0xFF7209B7, // grape
            0xFF8338EC, // violet
            0xFFC77DFF, // lavender
            0xFF9D4EDD, // amethyst
            0xFFF72585, // magenta
            0xFFFF006E, // neon pink
            0xFFB5179E, // orchid
            0xFFEF476F, // watermelon
            0xFFFF5D8F, // blush
            0xFFFB5607, // burnt orange
            0xFFFFD166, // sunflower
            0xFF8AC926, // chartreuse
    };
"""


def palette():
    replace_once(
        "app/src/main/java/org/levimc/launcher/util/ThemePalette.java",
        "    /** Mixes {@code color} toward {@code target} by {@code amount} (0..1), like CSS color-mix. */",
        RADIANCE + "\n    /** Mixes {@code color} toward {@code target} by {@code amount} (0..1), like CSS color-mix. */",
        "radiance palette",
    )


def personalization():
    replace_once(
        "app/src/main/java/org/levimc/launcher/util/PersonalizationManager.java",
        "    public static final int[] MORE_COLORS = ThemePalette.MORE;\n}",
        "    public static final int[] MORE_COLORS = ThemePalette.MORE;\n\n"
        "    public static final int[] RADIANCE_COLORS = ThemePalette.RADIANCE;\n}",
        "radiance colors field",
    )


def theme_manager():
    replace_once(
        "app/src/main/java/org/levimc/launcher/util/ThemeManager.java",
        """    public void applyTheme() {
        updateNightMode();
    }

    public void setThemeMode(int mode) {
        int previous = prefs.getInt(THEME_MODE_KEY, MODE_DARK);
        prefs.edit().putInt(THEME_MODE_KEY, mode).apply();
        updateNightMode();
        if (previous != mode) {
            sThemeChangeGeneration++;
        }
        if (activity != null && previous != mode) {
            activity.recreate();
        }
    }""",
        """    public void applyTheme() {
        // Appearance is locked to the default dark colour.
        AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES);
    }

    public void setThemeMode(int mode) {
        prefs.edit().putInt(THEME_MODE_KEY, MODE_DARK).apply();
        applyTheme();
    }""",
        "lock applyTheme",
    )
    replace_once(
        "app/src/main/java/org/levimc/launcher/util/ThemeManager.java",
        """    public int getCurrentMode() {
        int mode = prefs.getInt(THEME_MODE_KEY, MODE_DARK);
        if (mode < MODE_FOLLOW_SYSTEM || mode > MODE_SUN) {
            mode = MODE_DARK;
            prefs.edit().putInt(THEME_MODE_KEY, mode).apply();
        }
        return mode;
    }

    /** Quick toggle in the navigation, shown only for the manual light and dark modes (as on Windows). */
    public boolean canQuickToggle() {
        int mode = getCurrentMode();
        return mode == MODE_LIGHT || mode == MODE_DARK;
    }""",
        """    public int getCurrentMode() {
        return MODE_DARK;
    }

    /** Theme selection is removed; the default dark colour stays on. */
    public boolean canQuickToggle() {
        return false;
    }""",
        "lock current mode",
    )
    replace_once(
        "app/src/main/java/org/levimc/launcher/util/ThemeManager.java",
        """    public static int getSavedMode(Context context) {
        return context.getSharedPreferences(THEME_PREFS, Context.MODE_PRIVATE)
                .getInt(THEME_MODE_KEY, MODE_DARK);
    }""",
        """    public static int getSavedMode(Context context) {
        return MODE_DARK;
    }""",
        "lock saved mode",
    )


def strings():
    rel = "app/src/main/res/values/strings.xml"
    replace_once(
        rel,
        '    <string name="more_colors">MORE COLORS</string>\n',
        '    <string name="more_colors">MORE COLORS</string>\n'
        '    <string name="radiance_colors">RADIANCE</string>\n',
        "radiance string",
    )


def settings_layout():
    replace_once(
        "app/src/main/res/layout/view_settings_sections.xml",
        """                <com.google.android.material.card.MaterialCardView
                    style="@style/settings_Card">

                    <LinearLayout
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:orientation="vertical"
                        style="@style/settings_CardBody"
                        android:paddingTop="12dp"
                        android:paddingBottom="12dp">

                        <LinearLayout
                            android:id="@+id/theme_mode_row\"""",
        """                <com.google.android.material.card.MaterialCardView
                    android:id="@+id/theme_mode_card"
                    style="@style/settings_Card"
                    android:visibility="gone">

                    <LinearLayout
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:orientation="vertical"
                        style="@style/settings_CardBody"
                        android:paddingTop="12dp"
                        android:paddingBottom="12dp">

                        <LinearLayout
                            android:id="@+id/theme_mode_row\"""",
        "hide theme mode card",
    )
    replace_once(
        "app/src/main/res/layout/view_settings_sections.xml",
        """                        <LinearLayout
                            style="@style/settings_Row"
                            android:layout_marginTop="4dp">

                            <ImageView
                                android:id="@+id/edit_mode_icon\"""",
        """                        <LinearLayout
                            android:id="@+id/edit_mode_row"
                            style="@style/settings_Row"
                            android:layout_marginTop="4dp"
                            android:visibility="gone">

                            <ImageView
                                android:id="@+id/edit_mode_icon\"""",
        "hide light/dark color mode",
    )
    replace_once(
        "app/src/main/res/layout/view_settings_sections.xml",
        """                            <LinearLayout
                                android:id="@+id/color_more_grid"
                                android:layout_width="match_parent"
                                android:layout_height="wrap_content"
                                android:layout_marginTop="4dp"
                                android:orientation="vertical"
                                android:padding="0dp" />
                        </LinearLayout>""",
        """                            <LinearLayout
                                android:id="@+id/color_more_grid"
                                android:layout_width="match_parent"
                                android:layout_height="wrap_content"
                                android:layout_marginTop="4dp"
                                android:orientation="vertical"
                                android:padding="0dp" />
                            <TextView
                                style="@style/settings_Label"
                                android:layout_marginTop="10dp"
                                android:text="@string/radiance_colors"
                                android:textSize="11sp" />
                            <LinearLayout
                                android:id="@+id/color_radiance_grid"
                                android:layout_width="match_parent"
                                android:layout_height="wrap_content"
                                android:layout_marginTop="4dp"
                                android:orientation="vertical"
                                android:padding="0dp" />
                        </LinearLayout>""",
        "radiance swatch grid",
    )


def settings_activity():
    replace_once(
        "app/src/main/java/org/levimc/launcher/ui/activities/SettingsActivity.java",
        """    private LinearLayout presetGrid;
    private LinearLayout moreGrid;""",
        """    private LinearLayout presetGrid;
    private LinearLayout moreGrid;
    private LinearLayout radianceGrid;""",
        "radiance field",
    )
    replace_once(
        "app/src/main/java/org/levimc/launcher/ui/activities/SettingsActivity.java",
        """            if (savedInstanceState.getBoolean(KEY_WAS_DARK, dark) == dark) {
                editDark = savedInstanceState.getBoolean(KEY_EDIT_DARK, dark);
            }
        }""",
        """            if (savedInstanceState.getBoolean(KEY_WAS_DARK, dark) == dark) {
                editDark = savedInstanceState.getBoolean(KEY_EDIT_DARK, dark);
            }
        }
        editDark = true;""",
        "lock color editing to dark",
    )
    replace_once(
        "app/src/main/java/org/levimc/launcher/ui/activities/SettingsActivity.java",
        """        presetGrid = findViewById(R.id.color_preset_grid);
        moreGrid = findViewById(R.id.color_more_grid);
        View.OnLayoutChangeListener widthListener = (v, l, t, r, b, ol, ot, or, ob) -> {
            if (r - l != or - ol) v.post(this::rebuildSwatches);
        };
        presetGrid.addOnLayoutChangeListener(widthListener);
        moreGrid.addOnLayoutChangeListener(widthListener);""",
        """        presetGrid = findViewById(R.id.color_preset_grid);
        moreGrid = findViewById(R.id.color_more_grid);
        radianceGrid = findViewById(R.id.color_radiance_grid);
        View.OnLayoutChangeListener widthListener = (v, l, t, r, b, ol, ot, or, ob) -> {
            if (r - l != or - ol) v.post(this::rebuildSwatches);
        };
        presetGrid.addOnLayoutChangeListener(widthListener);
        moreGrid.addOnLayoutChangeListener(widthListener);
        radianceGrid.addOnLayoutChangeListener(widthListener);""",
        "wire radiance grid",
    )
    replace_once(
        "app/src/main/java/org/levimc/launcher/ui/activities/SettingsActivity.java",
        """        int selected = personalizationManager.getAccentColor(editDark) | 0xFF000000;
        boolean custom = !contains(PersonalizationManager.PRESET_COLORS, selected)
                && !contains(PersonalizationManager.MORE_COLORS, selected);
        fillSwatchGrid(presetGrid, PersonalizationManager.PRESET_COLORS, false, selected, custom);
        fillSwatchGrid(moreGrid, PersonalizationManager.MORE_COLORS, true, selected, custom);""",
        """        int selected = personalizationManager.getAccentColor(editDark) | 0xFF000000;
        boolean custom = !contains(PersonalizationManager.PRESET_COLORS, selected)
                && !contains(PersonalizationManager.MORE_COLORS, selected)
                && !contains(PersonalizationManager.RADIANCE_COLORS, selected);
        fillSwatchGrid(presetGrid, PersonalizationManager.PRESET_COLORS, false, selected, custom);
        fillSwatchGrid(moreGrid, PersonalizationManager.MORE_COLORS, false, selected, custom);
        fillSwatchGrid(radianceGrid, PersonalizationManager.RADIANCE_COLORS, true, selected, custom);""",
        "fill radiance swatches",
    )


def main():
    palette()
    personalization()
    theme_manager()
    strings()
    settings_layout()
    settings_activity()


if __name__ == "__main__":
    main()
