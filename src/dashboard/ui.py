from __future__ import annotations

import streamlit as st


def apply_global_style() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@500;700&family=Source+Sans+3:wght@400;600;700&display=swap');

        :root {
          --rele-accent: #0f766e;
          --rele-highlight: #d97706;
          --rele-surface: rgba(255, 255, 255, 0.7);
          --rele-border: rgba(15, 118, 110, 0.25);
        }

        .stApp {
          background:
            radial-gradient(
              1000px 420px at 0% -15%,
              rgba(15, 118, 110, 0.18),
              transparent 55%
            ),
            radial-gradient(
              900px 360px at 100% -20%,
              rgba(217, 119, 6, 0.16),
              transparent 58%
            ),
            linear-gradient(180deg, #f7f6f2 0%, #eef4f7 100%);
        }

        html,
        body,
        [class*="st-"] {
          font-family: "Source Sans 3", sans-serif;
        }

        h1,
        h2,
        h3 {
          font-family: "Fraunces", serif !important;
          letter-spacing: 0.01em;
        }

        .rele-hero {
          border: 1px solid var(--rele-border);
          background: linear-gradient(
            130deg,
            rgba(255, 255, 255, 0.92),
            var(--rele-surface)
          );
          padding: 1.1rem 1.2rem;
          border-radius: 1rem;
          margin-bottom: 0.6rem;
          box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        }

        .rele-hero-kicker {
          margin: 0;
          color: var(--rele-accent);
          font-weight: 700;
          letter-spacing: 0.04em;
          text-transform: uppercase;
          font-size: 0.78rem;
        }

        .rele-hero-title {
          margin: 0.2rem 0;
          color: #12263a;
          font-size: 1.5rem;
          line-height: 1.25;
        }

        .rele-hero-text {
          margin: 0;
          color: #274156;
          font-size: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str, description: str) -> None:
    st.markdown(
        f"""
        <section class="rele-hero">
          <p class="rele-hero-kicker">RELE Prozesszentrale</p>
          <h2 class="rele-hero-title">{title}</h2>
          <p class="rele-hero-text">{description}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def status_badge(done: bool) -> str:
    if done:
        return ":green-badge[abgeschlossen]"
    return ":orange-badge[offen]"
