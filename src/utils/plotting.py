"""Blog chart style (Plotly). Transparent background and neutral grey text, readable in light and dark themes.

Usage in a notebook or post:
    from src.utils.plotting import ACCENT, GREY, PALETTE, init_plotly, new_figure, add_source
    init_plotly()
    fig = new_figure(y_title="Personas")
    fig.add_scatter(x=..., y=..., name="...", mode="lines")
    add_source(fig, "Fuente: INE. Elaboración propia.")
    fig.show()
"""

import plotly.graph_objects as go
import plotly.io as pio

ACCENT = "#c2410c"
GREY = "#8a96a3"
PALETTE = ["#c2410c", "#2563eb", "#0d9488", "#a16207", "#7c3aed"]
TEXT = "#7a8794"
GRID = "rgba(127,127,127,0.18)"
FONT = "Inter, system-ui, sans-serif"


def init_plotly() -> None:
    """Register and activate the 'mirada' template. Call once at the top of each notebook/post."""
    from plotly.offline import init_notebook_mode

    pio.renderers.default = "notebook_connected"   # works in Jupyter and in Quarto HTML
    init_notebook_mode(connected=True)               # avoids the first figure being split in Quarto
    pio.templates["mirada"] = go.layout.Template(layout=dict(
        font=dict(family=FONT, color=TEXT, size=13),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        colorway=PALETTE, hovermode="x unified", separators=",.",
        xaxis=dict(showgrid=False, automargin=True, linecolor="rgba(127,127,127,.5)",
                   ticks="outside", tickcolor="rgba(127,127,127,.5)"),
        yaxis=dict(gridcolor=GRID, zeroline=False, automargin=True, tickformat=",.0f"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=70, r=20, t=40, b=10),
        hoverlabel=dict(font=dict(family=FONT)),
    ))
    pio.templates.default = "mirada"


def new_figure(y_title: str | None = None, height: int = 420, **layout) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(height=height, yaxis_title=y_title, **layout)
    return fig


def add_source(fig: go.Figure, text: str) -> None:
    """Source note under the chart."""
    fig.add_annotation(text=text, xref="paper", yref="paper", x=0, y=-0.14, showarrow=False,
                       xanchor="left", font=dict(size=11, color=TEXT))
    fig.update_layout(margin=dict(b=55))
