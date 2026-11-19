"""Double-layer intake form view (Layer 1: 18-item Traits, Layer 2: Preferences & Profile)."""

import flet as ft
from app.view.intake_questions import LAYER1_QUESTIONS


def build_intake_view(page: ft.Page, controller, on_results_ready, on_home) -> ft.Container:
    saved = controller.answers()
    saved_traits = saved.get("traits", {}).get("values", {})
    saved_prefs = saved.get("preferences", {})
    saved_profile = saved.get("profile", {})
    current_step = {"value": saved.get("step", 1)}

    # Initialize each of the 18 sub-items from the saved trait score (defaults to 3)
    item_scores: dict[str, int] = {}
    for trait_key, questions in LAYER1_QUESTIONS.items():
        base_val = int(saved_traits.get(trait_key, 3))
        for q in questions:
            item_scores[q["id"]] = base_val

    content_host = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=14)

    # ------------------------------------------------------------------
    # LAYER 1: 18-Item Assessment Grouped Under the 6 Core Traits
    # ------------------------------------------------------------------
    def build_layer1_controls() -> list[ft.Control]:
        controls: list[ft.Control] = [
            ft.Text("Step 1 of 2: Interests, Strengths & Subjects", size=18, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Rate each statement from 1 (Strongly Disagree) to 5 (Strongly Agree).",
                size=12,
                color=ft.Colors.GREY_700,
            ),
        ]

        for trait in controller.trait_catalog():
            t_key = trait["key"]
            questions = LAYER1_QUESTIONS.get(t_key, [])
            q_ids = [q["id"] for q in questions]

            init_trait_avg = int(round(sum(item_scores[qid] for qid in q_ids) / len(q_ids))) if q_ids else 3
            trait_badge = ft.Container(
                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                border_radius=10,
                bgcolor=ft.Colors.BLUE_50,
                content=ft.Text(
                    f"Score: {init_trait_avg} / 5",
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_800,
                ),
            )

            question_widgets: list[ft.Control] = []
            for q in questions:
                qid = q["id"]
                init_q_val = item_scores[qid]
                q_val_text = ft.Text(f"{init_q_val}/5", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)

                def make_item_handler(
                    item_id: str,
                    trait_k: str,
                    trait_qids: list[str],
                    item_label: ft.Text,
                    summary_badge: ft.Container,
                ):
                    async def on_slide(e):
                        val = int(round(e.control.value))
                        item_scores[item_id] = val
                        item_label.value = f"{val}/5"

                        avg_score = int(round(sum(item_scores[k] for k in trait_qids) / len(trait_qids)))
                        saved_traits[trait_k] = avg_score
                        summary_badge.content.value = f"Score: {avg_score} / 5"
                        await controller.set_trait(trait_k, avg_score)
                        page.update()

                    return on_slide

                slider = ft.Slider(
                    min=1,
                    max=5,
                    divisions=4,
                    value=init_q_val,
                    label="{value}",
                    on_change=make_item_handler(qid, t_key, q_ids, q_val_text, trait_badge),
                )

                question_widgets.append(
                    ft.Container(
                        padding=ft.Padding.only(top=6),
                        content=ft.Column(
                            spacing=2,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(
                                            f"{qid} • {q['dimension']}",
                                            size=11,
                                            weight=ft.FontWeight.W_600,
                                            color=ft.Colors.BLUE_GREY_700,
                                        ),
                                        q_val_text,
                                    ],
                                ),
                                ft.Text(q["prompt"], size=13),
                                slider,
                            ],
                        ),
                    )
                )

            controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=14,
                        content=ft.Column(
                            spacing=6,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(trait["label"], weight=ft.FontWeight.BOLD, size=16),
                                        trait_badge,
                                    ],
                                ),
                                ft.Text(trait["hint"], size=12, color=ft.Colors.GREY_600),
                                ft.Divider(height=6),
                                *question_widgets,
                            ],
                        ),
                    )
                )
            )

        async def go_next(e):
            await controller.set_step(2)
            current_step["value"] = 2
            render_step()

        async def go_home(e):
            await on_home()

        controls.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.TextButton("Home", icon=ft.Icons.HOME_OUTLINED, on_click=go_home),
                    ft.FilledButton("Next: Preferences", icon=ft.Icons.ARROW_FORWARD, on_click=go_next),
                ],
            )
        )
        return controls

    # ------------------------------------------------------------------
    # LAYER 2: Practical Preferences & Optional Student Profile
    # ------------------------------------------------------------------
    def build_layer2_controls() -> list[ft.Control]:
        available_locations = ["Any"] + list(controller.locations())
        cur_loc = saved_prefs.get("location") or "Any"
        if cur_loc not in available_locations:
            cur_loc = "Any"

        async def on_location_change(e):
            await controller.set_preferences(
                location=None if e.control.value == "Any" else e.control.value
            )

        location_dropdown = ft.Dropdown(
            label="Preferred Municipality / City in Camarines Sur",
            value=cur_loc,
            options=[ft.dropdown.Option(key=loc, text=loc) for loc in available_locations],
            on_text_change=on_location_change,
        )

        async def on_tuition_free_change(e):
            await controller.set_preferences(prefers_tuition_free=e.control.value)

        tuition_free_switch = ft.Switch(
            label="Prefer free tuition (State Universities / RA 10931)",
            value=bool(saved_prefs.get("prefers_tuition_free", False)),
            on_change=on_tuition_free_change,
        )

        async def on_relocate_change(e):
            await controller.set_preferences(willing_to_relocate=e.control.value)

        relocate_switch = ft.Switch(
            label="Willing to relocate or commute outside preferred town",
            value=bool(saved_prefs.get("willing_to_relocate", False)),
            on_change=on_relocate_change,
        )

        async def on_scholarship_change(e):
            await controller.set_preferences(scholarship_need=e.control.value)

        scholarship_switch = ft.Switch(
            label="Actively seeking scholarships or financial aid",
            value=bool(saved_prefs.get("scholarship_need", False)),
            on_change=on_scholarship_change,
        )

        strand_options = [
            "STEM",
            "ABM",
            "HUMSS",
            "GAS",
            "TVL - ICT",
            "TVL - Home Economics",
            "TVL - Agri-Fishery",
            "TVL - Industrial Arts",
            "Arts & Design / Sports",
            "Prefer not to say",
        ]

        async def on_strand_change(e):
            await controller.set_profile(
                strand=None if e.control.value == "Prefer not to say" else e.control.value
            )

        strand_dropdown = ft.Dropdown(
            label="SHS Strand (Optional)",
            value=saved_profile.get("strand") or "Prefer not to say",
            options=[ft.dropdown.Option(key=s, text=s) for s in strand_options],
            on_text_change=on_strand_change,
        )

        grade_options = ["95-100", "90-94", "85-89", "80-84", "75-79", "Prefer not to say"]

        async def on_grade_change(e):
            await controller.set_profile(
                grade_band=None if e.control.value == "Prefer not to say" else e.control.value
            )

        grade_dropdown = ft.Dropdown(
            label="Latest GWA Band (Optional)",
            value=saved_profile.get("grade_band") or "Prefer not to say",
            options=[ft.dropdown.Option(key=g, text=g) for g in grade_options],
            on_text_change=on_grade_change,
        )

        gender_options = ["Female", "Male", "Non-binary / Other", "Prefer not to say"]

        async def on_gender_change(e):
            await controller.set_profile(
                gender=None if e.control.value == "Prefer not to say" else e.control.value
            )

        gender_dropdown = ft.Dropdown(
            label="Gender (Optional — excluded from matching)",
            value=saved_profile.get("gender") or "Prefer not to say",
            options=[ft.dropdown.Option(key=gen, text=gen) for gen in gender_options],
            on_text_change=on_gender_change,
        )

        async def go_back(e):
            await controller.set_step(1)
            current_step["value"] = 1
            render_step()

        async def handle_submit(e):
            results = await controller.submit()
            on_results_ready(results)

        return [
            ft.Text("Step 2 of 2: Preferences & Background", size=18, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Preferences help rank schools in Camarines Sur. Profile fields are optional and never affect program matching.",
                size=12,
                color=ft.Colors.GREY_700,
            ),
            ft.Text("School & Financial Preferences", weight=ft.FontWeight.W_600, size=14),
            location_dropdown,
            tuition_free_switch,
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
                    ft.FilledButton("Get Recommendations", icon=ft.Icons.CHECK, on_click=handle_submit),
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