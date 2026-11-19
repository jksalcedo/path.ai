"""Double-layer intake form view (Layer 1: Traits, Layer 2: Preferences & Profile)."""

import flet as ft


def build_intake_view(page: ft.Page, controller, on_results_ready, on_home) -> ft.Container:
    saved = controller.answers()
    saved_traits = saved.get("traits", {}).get("values", {})
    saved_prefs = saved.get("preferences", {})
    saved_profile = saved.get("profile", {})
    current_step = {"value": saved.get("step", 1)}

    content_host = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=14)

    # ------------------------------------------------------------------
    # LAYER 1: Core Traits & Strengths (1–5 Sliders from trait_catalog)
    # ------------------------------------------------------------------
    def build_layer1_controls() -> list[ft.Control]:
        controls: list[ft.Control] = [
            ft.Text("Step 1 of 2: Your Interests & Strengths", size=18, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Rate how strongly each statement describes you (1 = Low, 5 = High).",
                size=12,
                color=ft.Colors.GREY_700,
            ),
        ]

        for trait in controller.trait_catalog():
            key = trait["key"]
            init_val = int(saved_traits.get(key, 3))
            value_badge = ft.Text(f"{init_val} / 5", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)

            def make_slider_handler(t_key: str, badge: ft.Text):
                def on_slide(e):
                    val = int(round(e.control.value))
                    badge.value = f"{val} / 5"
                    saved_traits[t_key] = val
                    controller.set_trait(t_key, val)
                    page.update()
                return on_slide

            slider = ft.Slider(
                min=1,
                max=5,
                divisions=4,
                value=init_val,
                label="{value}",
                on_change=make_slider_handler(key, value_badge),
            )

            controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        content=ft.Column(
                            spacing=4,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(trait["label"], weight=ft.FontWeight.W_600, size=15),
                                        value_badge,
                                    ],
                                ),
                                ft.Text(trait["hint"], size=12, color=ft.Colors.GREY_700),
                                slider,
                            ],
                        ),
                    )
                )
            )

        def go_next(e):
            controller.set_step(2)
            current_step["value"] = 2
            render_step()

        controls.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.TextButton("Home", icon=ft.Icons.HOME_OUTLINED, on_click=lambda _: on_home()),
                    ft.ElevatedButton("Next: Preferences", icon=ft.Icons.ARROW_FORWARD, on_click=go_next),
                ],
            )
        )
        return controls

    # ------------------------------------------------------------------
    # LAYER 2: Practical Preferences & Optional Student Profile
    # ------------------------------------------------------------------
    def build_layer2_controls() -> list[ft.Control]:
        # --- Preferences (Soft ranking boosts in MatchingEngine) ---
        budget_map = {
            "none": None,
            "0": 0,
            "15000": 15000,
            "30000": 30000,
            "50000": 50000,
        }
        cur_budget = saved_prefs.get("budget_cap")
        budget_key = "none" if cur_budget is None else str(cur_budget)

        budget_dropdown = ft.Dropdown(
            label="Estimated Annual Tuition Budget",
            value=budget_key,
            options=[
                ft.dropdown.Option("none", "No budget limit / Prefer not to say"),
                ft.dropdown.Option("0", "Free Tuition Only (State Universities / RA 10931)"),
                ft.dropdown.Option("15000", "Up to ₱15,000 per year"),
                ft.dropdown.Option("30000", "Up to ₱30,000 per year"),
                ft.dropdown.Option("50000", "Up to ₱50,000 per year"),
            ],
            on_change=lambda e: controller.set_preferences(budget_cap=budget_map[e.control.value]),
        )

        available_locations = ["Any"] + list(controller.locations())
        cur_loc = saved_prefs.get("location") or "Any"
        if cur_loc not in available_locations:
            cur_loc = "Any"

        location_dropdown = ft.Dropdown(
            label="Preferred Municipality / City in Camarines Sur",
            value=cur_loc,
            options=[ft.dropdown.Option(loc) for loc in available_locations],
            on_change=lambda e: controller.set_preferences(
                location=None if e.control.value == "Any" else e.control.value
            ),
        )

        relocate_switch = ft.Switch(
            label="Willing to relocate or commute outside preferred town",
            value=bool(saved_prefs.get("willing_to_relocate", False)),
            on_change=lambda e: controller.set_preferences(willing_to_relocate=e.control.value),
        )

        scholarship_switch = ft.Switch(
            label="Actively seeking scholarships or financial aid",
            value=bool(saved_prefs.get("scholarship_need", False)),
            on_change=lambda e: controller.set_preferences(scholarship_need=e.control.value),
        )

        # --- Optional Student Profile (Privacy-isolated; never enters scoring) ---
        strand_dropdown = ft.Dropdown(
            label="SHS Strand (Optional)",
            value=saved_profile.get("strand") or "Prefer not to say",
            options=[
                ft.dropdown.Option("STEM"),
                ft.dropdown.Option("ABM"),
                ft.dropdown.Option("HUMSS"),
                ft.dropdown.Option("GAS"),
                ft.dropdown.Option("TVL - ICT"),
                ft.dropdown.Option("TVL - Home Economics"),
                ft.dropdown.Option("TVL - Agri-Fishery"),
                ft.dropdown.Option("TVL - Industrial Arts"),
                ft.dropdown.Option("Arts & Design / Sports"),
                ft.dropdown.Option("Prefer not to say"),
            ],
            on_change=lambda e: controller.set_profile(
                strand=None if e.control.value == "Prefer not to say" else e.control.value
            ),
        )

        grade_dropdown = ft.Dropdown(
            label="Latest GWA Band (Optional)",
            value=saved_profile.get("grade_band") or "Prefer not to say",
            options=[
                ft.dropdown.Option("95-100"),
                ft.dropdown.Option("90-94"),
                ft.dropdown.Option("85-89"),
                ft.dropdown.Option("80-84"),
                ft.dropdown.Option("75-79"),
                ft.dropdown.Option("Prefer not to say"),
            ],
            on_change=lambda e: controller.set_profile(
                grade_band=None if e.control.value == "Prefer not to say" else e.control.value
            ),
        )

        gender_dropdown = ft.Dropdown(
            label="Gender (Optional — excluded from matching)",
            value=saved_profile.get("gender") or "Prefer not to say",
            options=[
                ft.dropdown.Option("Female"),
                ft.dropdown.Option("Male"),
                ft.dropdown.Option("Non-binary / Other"),
                ft.dropdown.Option("Prefer not to say"),
            ],
            on_change=lambda e: controller.set_profile(
                gender=None if e.control.value == "Prefer not to say" else e.control.value
            ),
        )

        def go_back(e):
            controller.set_step(1)
            current_step["value"] = 1
            render_step()

        def handle_submit(e):
            results = controller.submit()
            on_results_ready(results)

        return [
            ft.Text("Step 2 of 2: Preferences & Background", size=18, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Preferences help rank schools in Camarines Sur. Profile fields are optional and never affect program matching.",
                size=12,
                color=ft.Colors.GREY_700,
            ),
            ft.Text("School & Budget Preferences", weight=ft.FontWeight.W_600, size=14),
            budget_dropdown,
            location_dropdown,
            relocate_switch,
            scholarship_switch,
            ft.Divider(),
            ft.Text("Optional Student Profile", weight=ft.FontWeight.W_600, size=14),
            strand_dropdown,
            grade_dropdown,
            gender_dropdown,
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.OutlinedButton("Back", icon=ft.Icons.ARROW_BACK, on_click=go_back),
                    ft.ElevatedButton("Get Recommendations", icon=ft.Icons.CHECK, on_click=handle_submit),
                ],
            ),
        ]

    def render_step():
        content_host.controls = (
            build_layer1_controls() if current_step["value"] == 1 else build_layer2_controls()
        )
        page.update()

    render_step()
    return ft.Container(content=content_host, expand=True)