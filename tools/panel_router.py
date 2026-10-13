VALID_PANELS = {"jazz", "falcon", "connect"}


def select_panel(panel_name: str) -> dict:
    panel = panel_name.strip().lower()

    if panel not in VALID_PANELS:
        return {
            "valid": False,
            "panel": None,
            "message": (
                "Barah-e-karam Jazz, Falcon "
                "ya Connect mein se panel batayein."
            )
        }

    return {
        "valid": True,
        "panel": panel,
        "message": f"{panel.title()} panel selected."
    }


if __name__ == "__main__":
    for name in ["Falcon", "Jazz", "Connect", "Unknown"]:
        print(select_panel(name))