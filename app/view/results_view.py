"""Recommendation results view displaying top-3 degree matches and campus offerings."""

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
            "Ranked by your academic field fit and Camarines Sur school preferences.",
            size=12,
            color=ft.Colors.GREY_700,
        ),
        ft.Container(
            padding=10,
            border_radius=8,
            bgcolor=ft.Colors.AMBER_50,
            border=ft.Border.all(1, ft.Colors.AMBER_300),
            content=ft.Row(
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.SCIENCE_OUTLINED, size=18, color=ft.Colors.AMBER_800),
                    ft.Text(
                        "Prototype notice: Covers 26 Camarines Sur HEIs using draft rubric weights pending expert validation.",
                        size=11,
                        color=ft.Colors.AMBER_900,
                        expand=True,
                    ),
                ],
            ),
        ),
    ]

    def edit_answers(e):
        on_edit_answers()

    async def go_home(e):
        await on_home()

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
            degree = item.get("degree") or item.get("program", {})
            college = item.get("college", {})
            match_pct = int(item.get("match_pct", 0))
            fit_basis = item.get("fit_basis", "traits")
            badges = item.get("badges", [])
            rationale = item.get("rationale", "")
            offerings = item.get("offerings", [])

            basis_caption = (
                "Based on your skills"
                if fit_basis == "skills"
                else "Based on your interests"
            )

            # --- College Cluster Subtitle Chip ---
            college_name = college.get("name", "")
            college_chip = (
                ft.Chip(
                    label=ft.Text(
                        college_name,
                        size=11,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.BLUE_900,
                    ),
                    bgcolor=ft.Colors.BLUE_50,
                )
                if college_name
                else ft.Container()
            )

            # --- Preference & Fit Badges ---
            badge_chips = [
                ft.Chip(
                    label=ft.Text(badge, size=11),
                    bgcolor=ft.Colors.GREEN_50,
                )
                for badge in badges
            ]

            # --- Offered At Campus List (Relational Offerings) ---
            offering_items: list[ft.Control] = []
            if not offerings:
                offering_items.append(
                    ft.Text("No matching campus offerings listed in the current dataset.", size=12, italic=True)
                )
            else:
                for offering in offerings:
                    hei = offering.get("hei", {})
                    hei_name = hei.get("name", "Unknown HEI")
                    campus = offering.get("campus") or hei.get("municipality", "")
                    title_line = f"{hei_name} — {campus}" if campus else hei_name

                    hei_type = hei.get("type") or offering.get("type", "N/A")
                    requires_tuition = offering.get("requires_tuition", hei.get("requires_tuition", True))
                    scholarships = offering.get("scholarships", hei.get("scholarships", False))
                    tuition_note = offering.get("tuition_note") or hei.get("tuition_note", "")

                    tuition_label = (
                        "Tuition-free (RA 10931)"
                        if not requires_tuition
                        else "Tuition required"
                    )
                    scholarship_tag = " • Scholarships available" if scholarships else ""

                    offering_controls: list[ft.Control] = [
                        ft.Text(
                            title_line,
                            weight=ft.FontWeight.W_600,
                            size=13,
                        ),
                        ft.Text(
                            f"{hei_type} • {tuition_label}{scholarship_tag}",
                            size=11,
                            color=ft.Colors.BLUE_GREY_700,
                        ),
                    ]
                    if tuition_note:
                        offering_controls.append(
                            ft.Text(
                                tuition_note,
                                size=11,
                                color=ft.Colors.GREY_700,
                            )
                        )

                    offering_items.append(
                        ft.Container(
                            padding=8,
                            border_radius=6,
                            bgcolor=ft.Colors.GREY_50,
                            border=ft.Border.all(1, ft.Colors.GREY_200),
                            content=ft.Column(
                                spacing=2,
                                controls=offering_controls,
                            ),
                        )
                    )

            # --- Degree Recommendation Card ---
            card_content = ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Column(
                                spacing=4,
                                expand=True,
                                controls=[
                                    ft.Text(
                                        f"#{idx}  {degree.get('name', 'Program')}",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    college_chip,
                                ],
                            ),
                            ft.Container(
                                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
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
                    ft.Text(basis_caption, size=11, color=ft.Colors.GREY_600),
                    ft.Row(wrap=True, spacing=6, controls=badge_chips) if badge_chips else ft.Container(),
                    ft.Text(rationale, size=13),
                    ft.Divider(height=6),
                    ft.Text("Offered at:", weight=ft.FontWeight.W_600, size=13),
                    ft.Column(spacing=6, controls=offering_items),
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
                ft.OutlinedButton("Edit Answers", icon=ft.Icons.EDIT_OUTLINED, on_click=edit_answers),
                ft.FilledButton("Done / Home", icon=ft.Icons.HOME_OUTLINED, on_click=go_home),
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