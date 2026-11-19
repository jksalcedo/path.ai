"""Recommendation results view displaying top-3 program matches and offered HEIs."""

import flet as ft


def build_results_view(
    page: ft.Page,
    results: list[dict],
    on_edit_answers,
    on_home,
) -> ft.Container:
    controls: list[ft.Control] = [
        ft.Text("Top Recommended Programs", size=20, weight=ft.FontWeight.BOLD),
        ft.Text(
            "Ranked by your trait alignment and Camarines Sur school preferences.",
            size=12,
            color=ft.Colors.GREY_700,
        ),
    ]

    if not results:
        controls.append(
            ft.Container(
                padding=16,
                border_radius=8,
                bgcolor=ft.Colors.GREY_100,
                content=ft.Text("No program recommendations available yet. Complete the intake form first."),
            )
        )
    else:
        for idx, item in enumerate(results, start=1):
            program = item.get("program", {})
            match_pct = int(item.get("match_pct", 0))
            badges = item.get("badges", [])
            rationale = item.get("rationale", "")
            heis = item.get("heis", [])

            # --- Preference & Fit Badges ---
            badge_chips = [
                ft.Chip(
                    label=ft.Text(badge, size=11),
                    bgcolor=ft.Colors.GREEN_50,
                )
                for badge in badges
            ]

            # --- Offered At HEIs List ---
            hei_items: list[ft.Control] = []
            if not heis:
                hei_items.append(
                    ft.Text("No matching institutions listed in the current dataset.", size=12, italic=True)
                )
            else:
                for hei in heis:
                    scholarship_tag = " • Scholarships available" if hei.get("scholarships") else ""
                    hei_items.append(
                        ft.Container(
                            padding=8,
                            border_radius=6,
                            bgcolor=ft.Colors.GREY_50,
                            border=ft.border.all(1, ft.Colors.GREY_200),
                            content=ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        f"{hei.get('name', 'Unknown HEI')} ({hei.get('municipality', '')})",
                                        weight=ft.FontWeight.W_600,
                                        size=13,
                                    ),
                                    ft.Text(
                                        f"Type: {hei.get('type', 'N/A')}{scholarship_tag}",
                                        size=11,
                                        color=ft.Colors.BLUE_GREY_700,
                                    ),
                                    ft.Text(
                                        hei.get("tuition_note", ""),
                                        size=11,
                                        color=ft.Colors.GREY_700,
                                    ),
                                ],
                            ),
                        )
                    )

            # --- Program Recommendation Card ---
            card_content = ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Text(
                                f"#{idx}  {program.get('name', 'Program')}",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                expand=True,
                            ),
                            ft.Container(
                                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                border_radius=12,
                                bgcolor=ft.Colors.BLUE_700,
                                content=ft.Text(
                                    f"{match_pct}% Fit",
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.BOLD,
                                    size=12,
                                ),
                            ),
                        ],
                    ),
                    ft.ProgressBar(
                        value=max(0.0, min(1.0, match_pct / 100.0)),
                        bar_height=8,
                        border_radius=4,
                        color=ft.Colors.BLUE_700,
                        bgcolor=ft.Colors.BLUE_100,
                    ),
                    ft.Row(wrap=True, spacing=6, controls=badge_chips) if badge_chips else ft.Container(),
                    ft.Text(rationale, size=13),
                    ft.Divider(height=6),
                    ft.Text("Offered at:", weight=ft.FontWeight.W_600, size=13),
                    ft.Column(spacing=6, controls=hei_items),
                ],
            )

            controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=14,
                        content=card_content,
                    )
                )
            )

    controls.append(
        ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.OutlinedButton("Edit Answers", icon=ft.Icons.EDIT_OUTLINED, on_click=lambda _: on_edit_answers()),
                ft.ElevatedButton("Done / Home", icon=ft.Icons.HOME_OUTLINED, on_click=lambda _: on_home()),
            ],
        )
    )

    return ft.Container(
        expand=True,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=14,
            controls=controls,
        ),
    )