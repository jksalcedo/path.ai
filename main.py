"""Path.AI Flet entry point and screen router (View layer)."""

import flet as ft

from app.controller.pathai_controller import PathAIController
from app.view.flet_storage_adapter import FletStorageAdapter
from app.view.intake_view import build_intake_view
from app.view.results_view import build_results_view
from app.view.welcome_view import build_welcome_view


async def main(page: ft.Page):
    page.title = "Path.AI — Camarines Sur Program Recommender"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE_800)
    page.padding = 0

    # Mobile-proportioned window dimensions for Windows desktop demo
    if hasattr(page, "window"):
        page.window.width = 430
        page.window.height = 820
    else:
        page.window_width = 430
        page.window_height = 820

    # Single controller instance backed by device persistent storage
    controller = PathAIController(FletStorageAdapter(page))
    await controller.initialize()

    def render_screen(view: ft.Control):
        page.controls.clear()
        page.add(
            ft.SafeArea(
                expand=True,
                content=ft.Container(
                    padding=18,
                    expand=True,
                    content=view,
                ),
            )
        )
        page.update()

    async def show_welcome():
        render_screen(
            await build_welcome_view(
                page=page,
                controller=controller,
                on_start_new=start_new_intake,
                on_resume_intake=show_intake,
                on_view_results=show_results,
                on_home=show_welcome,
            )
        )

    async def start_new_intake(reset: bool = True):
        if reset:
            await controller.clear_my_data()
        await controller.set_step(1)
        show_intake()

    def show_intake():
        render_screen(
            build_intake_view(
                page=page,
                controller=controller,
                on_results_ready=show_results,
                on_home=show_welcome,
            )
        )

    def show_results(results: list[dict]):
        render_screen(
            build_results_view(
                page=page,
                results=results,
                on_edit_answers=show_intake,
                on_home=show_welcome,
            )
        )

    await show_welcome()


if __name__ == "__main__":
    ft.run(main)