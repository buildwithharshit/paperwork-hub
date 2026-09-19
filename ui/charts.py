import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def _layout(theme, height=320):
    return {
        "height": height,
        "margin": {
            "l": 12,
            "r": 12,
            "t": 18,
            "b": 12,
        },
        "paper_bgcolor": theme["paper_bgcolor"],
        "plot_bgcolor": theme["plot_bgcolor"],
        "font": {
            "color": theme["font_color"],
        },
        "hoverlabel": {
            "bgcolor": theme["paper_bgcolor"],
            "font_color": theme["font_color"],
        },
        "legend": {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
            "font": {
                "size": 11,
            },
        },
    }


def expected_vs_actual(df, theme, period="day"):
    data = df.copy()

    data["invoice_date"] = pd.to_datetime(
        data["invoice_date"],
        errors="coerce",
    )

    data = data.dropna(
        subset=["invoice_date"]
    )

    if data.empty:
        return None

    # ---------------------------------------------
    # Group according to selected period
    # ---------------------------------------------

    if period == "week":
        data["period"] = (
            data["invoice_date"]
            .dt.to_period("W")
            .dt.start_time
        )

    elif period == "month":
        data["period"] = (
            data["invoice_date"]
            .dt.to_period("M")
            .dt.start_time
        )

    elif period == "year":
        data["period"] = (
            data["invoice_date"]
            .dt.to_period("Y")
            .dt.start_time
        )

    else:
        data["period"] = (
            data["invoice_date"]
            .dt.floor("D")
        )

    grouped = (
        data.groupby("period")
        .agg(
            expected=("subtotal", "sum"),
            actual=("total", "sum"),
        )
        .reset_index()
        .sort_values("period")
    )

    # ---------------------------------------------
    # Clean labels
    # ---------------------------------------------

    if period == "week":
        grouped["label"] = (
            "Week of "
            + grouped["period"].dt.strftime("%d %b %Y")
        )

    elif period == "month":
        grouped["label"] = (
            grouped["period"]
            .dt.strftime("%b %Y")
        )

    elif period == "year":
        grouped["label"] = (
            grouped["period"]
            .dt.strftime("%Y")
        )

    else:
        grouped["label"] = (
            grouped["period"]
            .dt.strftime("%d %b %Y")
        )

    fig = go.Figure()

    # ---------------------------------------------
    # Actual
    # ---------------------------------------------

    fig.add_trace(
        go.Scatter(
            x=grouped["label"],
            y=grouped["actual"],
            name="Actual",
            mode="lines+markers",
            line=dict(
                color=theme["primary"],
                width=2.5,
            ),
            marker=dict(
                size=7,
                color=theme["primary"],
                line=dict(
                    color=theme["paper_bgcolor"],
                    width=3,
                ),
            ),
            fill="tozeroy",
            fillcolor="rgba(75, 131, 232, 0.10)",
            hovertemplate=(
                "Actual: ₹%{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    # ---------------------------------------------
    # Expected
    # ---------------------------------------------

    fig.add_trace(
        go.Scatter(
            x=grouped["label"],
            y=grouped["expected"],
            name="Expected",
            mode="lines+markers",
            line=dict(
                color=theme["pink"],
                width=1.8,
                dash="dot",
            ),
            marker=dict(
                size=6,
                color=theme["pink"],
                line=dict(
                    color=theme["paper_bgcolor"],
                    width=2,
                ),
            ),
            hovertemplate=(
                "Expected: ₹%{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        **_layout(theme, 340),
    )

    # ---------------------------------------------
    # X axis
    # ---------------------------------------------

    fig.update_xaxes(
        type="category",
        showgrid=False,
        showline=False,
        zeroline=False,
        title=None,

        # Keep the period slider.
        rangeslider=dict(
            visible=True,
            thickness=0.08,
            bgcolor=theme["plot_bgcolor"],
            bordercolor=theme["border"],
            borderwidth=1,
        ),

        # Remove Plotly crosshair/spike lines.
        showspikes=False,

        tickfont=dict(
            color=theme["font_color"],
            size=11,
        ),
    )

    # ---------------------------------------------
    # Y axis
    # ---------------------------------------------

    fig.update_yaxes(
        showgrid=True,
        gridcolor=theme["border"],
        gridwidth=1,
        showline=False,
        zeroline=False,
        title=None,

        # Remove Plotly crosshair/spike lines.
        showspikes=False,

        tickfont=dict(
            color=theme["font_color"],
            size=11,
        ),
    )

    return fig


def invoice_volume(df, theme):
    data = df.copy()

    data["invoice_date"] = pd.to_datetime(
        data["invoice_date"],
        errors="coerce",
    )

    data = data.dropna(
        subset=["invoice_date"]
    )

    if data.empty:
        return None

    monthly = (
        data.set_index("invoice_date")
        .resample("ME")
        .size()
        .reset_index(name="count")
    )

    fig = go.Figure()

    # =============================================
    # ONE MONTH
    # =============================================

    if len(monthly) == 1:

        month_date = monthly.iloc[0]["invoice_date"]
        count = int(
            monthly.iloc[0]["count"]
        )

        # Clean vertical guide
        fig.add_trace(
            go.Scatter(
                x=[
                    month_date,
                    month_date,
                ],
                y=[
                    0,
                    count,
                ],
                mode="lines",
                line=dict(
                    color=theme["border"],
                    width=2,
                ),
                hoverinfo="skip",
                showlegend=False,
            )
        )

        # Single clean data point
        fig.add_trace(
            go.Scatter(
                x=[month_date],
                y=[count],
                mode="markers+text",
                text=[
                    (
                        f"{count} invoice"
                        if count == 1
                        else f"{count} invoices"
                    )
                ],
                textposition="top center",
                textfont=dict(
                    color=theme["font_color"],
                    size=13,
                ),
                marker=dict(
                    size=15,
                    color=theme["primary"],
                    line=dict(
                        color=theme["paper_bgcolor"],
                        width=4,
                    ),
                ),
                hovertemplate=(
                    "%{y} invoices"
                    "<extra></extra>"
                ),
                showlegend=False,
            )
        )

        fig.update_layout(
            **_layout(theme, 260),
            showlegend=False,
        )

        fig.update_layout(
            margin=dict(
                l=25,
                r=25,
                t=30,
                b=35,
            ),
        )

        fig.update_xaxes(
            type="date",
            showgrid=False,
            showline=False,
            zeroline=False,
            title=None,
            tickformat="%b %Y",
            rangeslider=dict(
                visible=False,
            ),
            showspikes=False,
            tickfont=dict(
                size=11,
                color=theme["font_color"],
            ),
        )

        fig.update_yaxes(
            showgrid=True,
            gridcolor=theme["border"],
            gridwidth=1,
            showline=False,
            zeroline=False,
            title=None,
            rangemode="tozero",
            dtick=1,
            showspikes=False,
            tickfont=dict(
                size=10,
                color=theme["font_color"],
            ),
            fixedrange=True,
        )

        return fig

    # =============================================
    # MULTIPLE MONTHS
    # =============================================

    fig.add_trace(
        go.Scatter(
            x=monthly["invoice_date"],
            y=monthly["count"],
            mode="lines+markers",
            line=dict(
                color=theme["primary"],
                width=2.5,
                shape="spline",
            ),
            marker=dict(
                size=7,
                color=theme["primary"],
                line=dict(
                    color=theme["paper_bgcolor"],
                    width=3,
                ),
            ),
            fill="tozeroy",
            fillcolor="rgba(75, 131, 232, 0.10)",
            hovertemplate=(
                "%{y} invoices"
                "<extra></extra>"
            ),
            showlegend=False,
        )
    )

    fig.update_layout(
        **_layout(theme, 260),
        showlegend=False,
    )

    fig.update_layout(
        margin=dict(
            l=25,
            r=25,
            t=20,
            b=35,
        ),
    )

    fig.update_xaxes(
        type="date",
        showgrid=False,
        showline=False,
        zeroline=False,
        title=None,
        tickformat="%b %Y",

        # Only the horizontal period slider
        rangeslider=dict(
            visible=True,
            thickness=0.07,
            bgcolor=theme["plot_bgcolor"],
            bordercolor=theme["border"],
            borderwidth=1,
        ),

        # No crosshair
        showspikes=False,

        tickfont=dict(
            size=11,
            color=theme["font_color"],
        ),
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor=theme["border"],
        gridwidth=1,
        showline=False,
        zeroline=False,
        title=None,
        rangemode="tozero",

        dtick=(
            1
            if int(monthly["count"].max()) <= 5
            else None
        ),

        # No crosshair
        showspikes=False,

        tickfont=dict(
            size=10,
            color=theme["font_color"],
        ),

        fixedrange=True,
    )

    return fig


def status_donut(df, theme):
    counts = (
        df["validation_status"]
        .value_counts()
    )

    if counts.empty:
        return None

    color_map = {
        "Approved": theme["success"],
        "Human Review": theme["warning"],
    }

    colors = [
        color_map.get(
            str(label),
            theme["primary"],
        )
        for label in counts.index
    ]

    fig = px.pie(
        values=counts.values,
        names=counts.index,
        hole=0.72,
        color_discrete_sequence=colors,
    )

    fig.update_layout(
        **_layout(theme, 250),
    )

    fig.update_traces(
        textinfo="percent",
        hovertemplate=(
            "%{label}: %{value}"
            "<extra></extra>"
        ),
    )

    return fig


def payment_donut(df, theme):
    counts = (
        df["payment_status"]
        .astype(str)
        .str.title()
        .value_counts()
    )

    if counts.empty:
        return None

    palette = [
        theme["primary"],
        theme["purple"],
        theme["pink"],
    ]

    fig = px.pie(
        values=counts.values,
        names=counts.index,
        hole=0.72,
        color_discrete_sequence=palette,
    )

    fig.update_layout(
        **_layout(theme, 250),
    )

    fig.update_traces(
        textinfo="percent",
        hovertemplate=(
            "%{label}: %{value}"
            "<extra></extra>"
        ),
    )

    return fig