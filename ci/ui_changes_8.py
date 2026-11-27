
#!/usr/bin/env python3
"""Launcher home and account UI changes. Runs after ui_changes_7.py."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

ACCOUNT_LAYOUT = "app/src/main/res/layout/shell_account_cluster.xml"
BASE_ACTIVITY = (
    "app/src/main/java/org/levimc/launcher/ui/activities/BaseActivity.java"
)
MAIN_LAYOUT = "app/src/main/res/layout/activity_main.xml"
MAIN_ACTIVITY = (
    "app/src/main/java/org/levimc/launcher/ui/activities/MainActivity.java"
)
BUILD_SCRIPT = "ci/prepare_fork_build.sh"


def edit(rel, old, new, label):
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")

    if old not in text:
        if new in text:
            print(f"already applied: {label}")
            return
        sys.exit(f"Anchor missing for {label} in {rel}")

    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"ok: {label}")


def account_layout():
    path = ROOT / ACCOUNT_LAYOUT
    text = path.read_text(encoding="utf-8")

    marker = """    <FrameLayout
        android:id="@+id/nav_account_avatar_container" """

    if 'android:id="@+id/nav_account_name"' in text:
        print("already applied: account name view")
        return

    index = text.find(marker)
    if index == -1:
        sys.exit("Account avatar container anchor missing")

    # Add the username after the avatar container.
    end_marker = """    </FrameLayout>
</merge>"""
    replacement = """    </FrameLayout>

    <TextView
        android:id="@+id/nav_account_name"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginStart="7dp"
        android:ellipsize="end"
        android:fontFamily="@font/misans"
        android:maxWidth="110dp"
        android:maxLines="1"
        android:text="Log in"
        android:textColor="@color/text_primary"
        android:textSize="12sp"
        android:gravity="center_vertical" />
</merge>"""

    if end_marker not in text:
        sys.exit("Account avatar closing anchor missing")

    text = text.replace(end_marker, replacement, 1)
    path.write_text(text, encoding="utf-8")
    print("ok: added sidebar account name")


def base_activity():
    path = ROOT / BASE_ACTIVITY
    text = path.read_text(encoding="utf-8")

    old = """        View signIn = findViewById(R.id.nav_sign_in_button);
        View avatarContainer = findViewById(R.id.nav_account_avatar_container);
        if (active == null) {
            if (signIn != null) signIn.setVisibility(View.VISIBLE);
            if (avatarContainer != null) avatarContainer.setVisibility(View.GONE);
            clearNavAvatar();
        } else {
            if (signIn != null) signIn.setVisibility(View.GONE);
            if (avatarContainer != null) avatarContainer.setVisibility(View.VISIBLE);
            loadNavXboxAvatar(active);
        }"""

    new = """        View signIn = findViewById(R.id.nav_sign_in_button);
        View avatarContainer = findViewById(R.id.nav_account_avatar_container);
        TextView accountName = findViewById(R.id.nav_account_name);

        if (active == null) {
            if (signIn != null) signIn.setVisibility(View.VISIBLE);
            if (avatarContainer != null) avatarContainer.setVisibility(View.GONE);
            if (accountName != null) {
                accountName.setText("Log in");
                accountName.setVisibility(View.VISIBLE);
            }
            clearNavAvatar();
        } else {
            if (signIn != null) signIn.setVisibility(View.GONE);
            if (avatarContainer != null) avatarContainer.setVisibility(View.VISIBLE);
            if (accountName != null) {
                String gamertag = active.xboxGamertag;
                accountName.setText(
                        android.text.TextUtils.isEmpty(gamertag) ? "Xbox account" : gamertag
                );
                accountName.setVisibility(View.VISIBLE);
            }
            loadNavXboxAvatar(active);
        }"""

    edit(
        BASE_ACTIVITY,
        old,
        new,
        "show Xbox gamertag or Log in in sidebar",
    )


def main_layout():
    path = ROOT / MAIN_LAYOUT
    text = path.read_text(encoding="utf-8")

    # Remove the icon from the Launch button.
    text = text.replace(
        ' app:icon="@drawable/ic_nav_launch" app:iconPadding="6dp" app:iconSize="18dp"',
        "",
        1,
    )

    # Wrap the launch group in a vertical column.
    if 'android:id="@+id/home_launch_column"' not in text:
        old_start = (
            '<LinearLayout android:id="@+id/home_launch_group" '
            'android:layout_width="wrap_content"'
        )
        new_start = (
            '<LinearLayout android:id="@+id/home_launch_column" '
            'android:layout_width="wrap_content" '
            'android:layout_height="wrap_content" '
            'android:layout_marginStart="10dp" '
            'android:gravity="center_horizontal" '
            'android:orientation="vertical">'
            '<LinearLayout android:id="@+id/home_launch_group" '
            'android:layout_width="wrap_content"'
        )

        if old_start not in text:
            sys.exit("Launch group opening anchor missing")

        text = text.replace(old_start, new_start, 1)

        # Close the new vertical wrapper and add the version label.
        old_end = (
            'app:tint="@color/on_primary" />\n'
            '                </LinearLayout>\n'
            '            </LinearLayout>'
        )
        new_end = (
            'app:tint="@color/on_primary" />\n'
            '                </LinearLayout>\n'
            '                <TextView\n'
            '                    android:id="@+id/home_launch_version"\n'
            '                    android:layout_width="wrap_content"\n'
            '                    android:layout_height="wrap_content"\n'
            '                    android:layout_marginTop="3dp"\n'
            '                    android:ellipsize="end"\n'
            '                    android:fontFamily="@font/misans"\n'
            '                    android:maxWidth="150dp"\n'
            '                    android:maxLines="1"\n'
            '                    android:textColor="@color/text_secondary"\n'
            '                    android:textSize="10sp" />\n'
            '            </LinearLayout>\n'
            '            </LinearLayout>'
        )

        if old_end not in text:
            sys.exit("Launch group closing anchor missing")

        text = text.replace(old_end, new_end, 1)

    path.write_text(text, encoding="utf-8")
    print("ok: launch button layout and version label")


def main_activity():
    path = ROOT / MAIN_ACTIVITY
    text = path.read_text(encoding="utf-8")

    # Update the version label when the selected instance changes.
    old_null = """            InstanceIcons.bind(binding.homeInstanceIcon, null);
            return;"""

    new_null = """            InstanceIcons.bind(binding.homeInstanceIcon, null);
            updateLaunchVersionLabel(null);
            return;"""

    if new_null not in text:
        edit(
            MAIN_ACTIVITY,
            old_null,
            new_null,
            "update launch version when no instance is selected",
        )

    old_selected = """        InstanceIcons.bind(binding.homeInstanceIcon, selectedVersion);
    }

    private boolean isVersionManagerReady()"""

    new_selected = """        InstanceIcons.bind(binding.homeInstanceIcon, selectedVersion);
        updateLaunchVersionLabel(selectedVersion);
    }

    private void updateLaunchVersionLabel(GameVersion version) {
        TextView label = findViewById(R.id.home_launch_version);
        if (label == null) return;

        String versionText = version != null
                ? getInstanceVersionText(version)
                : getString(R.string.not_found_version);

        label.setText(versionText);
    }

    private boolean isVersionManagerReady()"""

    edit(
        MAIN_ACTIVITY,
        old_selected,
        new_selected,
        "show selected Minecraft version below Launch",
    )


def build_script():
    path = ROOT / BUILD_SCRIPT
    text = path.read_text(encoding="utf-8")

    command = "python3 ci/ui_changes_8.py"
    if command in text:
        print("already applied: build pipeline entry")
        return

    marker = "python3 ci/ui_changes_7.py"
    if marker not in text:
        sys.exit("ui_changes_7.py pipeline anchor missing")

    text = text.replace(
        marker,
        marker + "\n" + command,
        1,
    )

    path.write_text(text, encoding="utf-8")
    print("ok: added ui_changes_8.py to build pipeline")


def main():
    account_layout()
    base_activity()
    main_layout()
    main_activity()
    build_script()
    print("UI changes 8 complete.")


if __name__ == "__main__":
    main()
