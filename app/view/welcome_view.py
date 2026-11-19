"""Welcome, privacy notice, and session resume/clear view."""

import flet as ft


async def build_welcome_view(
    page: ft.Page,
    controller,
    on_start_new,
    on_resume_intake,
    on_view_results,
    on_home,
) -> ft.Container:
    has_saved = await controller.has_saved()
    saved_results = await controller.last_results()

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
                border=ft.Border.all(1, ft.Colors.AMBER_300),
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
            border=ft.Border.all(1, ft.Colors.BLUE_200),
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
        def close_confirm_dialog():
            if hasattr(page, "pop_dialog"):
                page.pop_dialog()
            else:
                confirm_dialog.open = False
                page.update()

        async def perform_clear(ev):
            close_confirm_dialog()
            await controller.clear_my_data()
            snack_bar = ft.SnackBar(ft.Text("All saved intake data and results have been cleared."))
            if hasattr(page, "show_dialog"):
                page.show_dialog(snack_bar)
            elif hasattr(page, "snack_bar"):
                page.snack_bar = snack_bar
                snack_bar.open = True
                page.update()
            else:
                page.overlay.append(snack_bar)
                page.update()
            await on_home()

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Clear My Data?"),
            content=ft.Text(
                "This will permanently delete your saved answers and recent program recommendations from this device."
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda ev: close_confirm_dialog()),
                ft.FilledButton(
                    "Delete Data",
                    bgcolor=ft.Colors.RED_600,
                    color=ft.Colors.WHITE,
                    on_click=perform_clear,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        if hasattr(page, "show_dialog"):
            page.show_dialog(confirm_dialog)
        else:
            page.dialog = confirm_dialog
            confirm_dialog.open = True
            page.update()

    # --- Action Buttons ---
    action_buttons: list[ft.Control] = []

    async def resume_intake(e):
        await on_resume_intake()

    async def view_results(e):
        on_view_results(saved_results)

    async def start_fresh(e):
        await on_start_new(reset=True)

    async def start_assessment(e):
        await on_start_new(reset=False)

    if has_saved:
        action_buttons.append(
            ft.FilledButton(
                "Resume Saved Intake",
                icon=ft.Icons.PLAY_ARROW_ROUNDED,
                width=280,
                on_click=resume_intake,
            )
        )
        if saved_results:
            action_buttons.append(
                ft.OutlinedButton(
                    "View Last Recommendations",
                    icon=ft.Icons.LIST_ALT_ROUNDED,
                    width=280,
                    on_click=view_results,
                )
            )
        action_buttons.append(
            ft.OutlinedButton(
                "Start Fresh Assessment",
                icon=ft.Icons.REFRESH_ROUNDED,
                width=280,
                on_click=start_fresh,
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
            ft.FilledButton(
                "Start Assessment",
                icon=ft.Icons.ARROW_FORWARD_ROUNDED,
                width=280,
                on_click=start_assessment,
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