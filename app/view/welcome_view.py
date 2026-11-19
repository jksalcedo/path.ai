"""Welcome, privacy notice, and session resume/clear view."""

import flet as ft


def build_welcome_view(
    page: ft.Page,
    controller,
    on_start_new,
    on_resume_intake,
    on_view_results,
) -> ft.Container:
    has_saved = controller.has_saved()
    saved_results = controller.last_results()

    controls: list[ft.Control] = [
        ft.Icon(ft.Icons.SCHOOL_ROUNDED, size=48, color=ft.Colors.BLUE_700),
        ft.Text(
            "Path.AI",
            size=28,
            weight=ft.FontWeight.BOLD,
        ),
        ft.Text(
            "College Program & HEI Recommender for Camarines Sur",
            size=14,
            color=ft.Colors.GREY_700,
        ),
    ]

    # --- 30-Day Inactivity Auto-Purge Notice ---
    if getattr(controller, "auto_purged", False):
        controls.append(
            ft.Container(
                padding=12,
                border_radius=8,
                bgcolor=ft.Colors.AMBER_50,
                border=ft.border.all(1, ft.Colors.AMBER_300),
                content=ft.Row(
                    spacing=10,
                    controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.AMBER_800),
                        ft.Text(
                            "Your previous session was automatically deleted after 30 days of inactivity.",
                            size=12,
                            expand=True,
                        ),
                    ],
                ),
            )
        )

    # --- Offline & Privacy Notice Card ---
    controls.append(
        ft.Container(
            padding=14,
            border_radius=10,
            bgcolor=ft.Colors.BLUE_50,
            border=ft.border.all(1, ft.Colors.BLUE_200),
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.PRIVACY_TIP_OUTLINED, color=ft.Colors.BLUE_700),
                            ft.Text("100% Offline & Private", weight=ft.FontWeight.BOLD, size=14),
                        ],
                    ),
                    ft.Text(
                        "• No account, login, name, or contact details required.\n"
                        "• All answers and recommendations stay strictly on this device.\n"
                        "• Data auto-deletes after 30 days of inactivity or whenever you clear it.",
                        size=12,
                    ),
                ],
            ),
        )
    )

    # --- Clear My Data Confirmation Dialog ---
    def confirm_clear_data(e):
        def perform_clear(ev):
            page.close(confirm_dialog)
            controller.clear_my_data()
            page.open(ft.SnackBar(ft.Text("All saved intake data and results have been cleared.")))
            on_start_new(reset=False)

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Clear My Data?"),
            content=ft.Text(
                "This will permanently delete your saved answers and recent program recommendations from this device."
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda ev: page.close(confirm_dialog)),
                ft.ElevatedButton(
                    "Delete Data",
                    bgcolor=ft.Colors.RED_600,
                    color=ft.Colors.WHITE,
                    on_click=perform_clear,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(confirm_dialog)

    # --- Action Buttons ---
    action_buttons: list[ft.Control] = []

    if has_saved:
        action_buttons.append(
            ft.ElevatedButton(
                "Resume Saved Intake",
                icon=ft.Icons.PLAY_ARROW_ROUNDED,
                width=280,
                on_click=lambda _: on_resume_intake(),
            )
        )
        if saved_results:
            action_buttons.append(
                ft.OutlinedButton(
                    "View Last Recommendations",
                    icon=ft.Icons.LIST_ALT_ROUNDED,
                    width=280,
                    on_click=lambda _: on_view_results(saved_results),
                )
            )
        action_buttons.append(
            ft.OutlinedButton(
                "Start Fresh Assessment",
                icon=ft.Icons.REFRESH_ROUNDED,
                width=280,
                on_click=lambda _: on_start_new(reset=True),
            )
        )
        action_buttons.append(
            ft.TextButton(
                "Clear My Data",
                icon=ft.Icons.DELETE_OUTLINE,
                style=ft.ButtonStyle(color=ft.Colors.RED_600),
                on_click=confirm_clear_data,
            )
        )
    else:
        action_buttons.append(
            ft.ElevatedButton(
                "Start Assessment",
                icon=ft.Icons.ARROW_FORWARD_ROUNDED,
                width=280,
                on_click=lambda _: on_start_new(reset=False),
            )
        )

    controls.append(
        ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=action_buttons,
        )
    )

    return ft.Container(
        expand=True,
        padding=8,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            controls=controls,
        ),
    )