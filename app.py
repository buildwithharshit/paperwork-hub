import sqlite3
import html
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from database import (
    create_database,
    get_invoices,
    invoice_number_exists,
    save_invoice,
)
from invoice_processor import (
    InvoiceProcessingError,
    extract_invoice,
)
from ui.charts import (
    expected_vs_actual,
    invoice_volume,
    status_donut,
)
from ui.components import (
    empty_state,
    page_header,
    section_header,
    validation_row,
)
from ui.theme import (
    inject_theme,
    plotly_theme,
)


# =========================================================
# INITIALIZATION
# =========================================================

load_dotenv()

create_database()

st.set_page_config(
    page_title="Paperwork Hub",
    page_icon="▣",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# HELPERS
# =========================================================

def load_dataframe():
    rows = get_invoices()

    columns = [
        "id",
        "invoice_number",
        "vendor",
        "invoice_date",
        "subtotal",
        "tax",
        "total",
        "due_date",
        "payment_status",
        "validation_status",
        "difference",
        "audit_reason",
    ]

    return pd.DataFrame(
        rows,
        columns=columns,
    )


def format_currency(value):
    try:
        return f"₹{float(value):,.2f}"
    except (TypeError, ValueError):
        return "₹0.00"


def render_value_card(label, value, theme, value_color=None):
    color = value_color or theme["font_color"]

    st.markdown(
        f"""
        <div style="
            width:100%;
            min-height:112px;
            box-sizing:border-box;
            padding:18px 20px;
            border:1px solid {theme['border']};
            border-radius:16px;
            background:{theme['paper_bgcolor']};
            box-shadow:0 8px 24px {theme.get('shadow', 'rgba(15, 23, 42, 0.045)')};
        ">
            <div style="
                color:{theme['muted']};
                font-size:13px;
                font-weight:550;
                margin-bottom:10px;
            ">{html.escape(str(label))}</div>
            <div style="
                color:{color};
                font-size:clamp(24px, 2.25vw, 34px);
                font-weight:760;
                line-height:1.12;
                letter-spacing:-0.02em;
                white-space:normal;
                overflow-wrap:anywhere;
                word-break:break-word;
            ">{html.escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def delete_invoices(invoice_ids):
    if not invoice_ids:
        return

    connection = sqlite3.connect("invoices.db")

    try:
        cursor = connection.cursor()

        placeholders = ",".join(
            "?" for _ in invoice_ids
        )

        cursor.execute(
            f"""
            DELETE FROM invoices
            WHERE id IN ({placeholders})
            """,
            tuple(invoice_ids),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def delete_all_invoices():
    connection = sqlite3.connect("invoices.db")

    try:
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM invoices"
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def is_dark_mode():
    return st.session_state.get(
        "dark_mode",
        False,
    )


def download_dataframe(
    df,
    filename,
):
    data = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Download CSV",
        data=data,
        file_name=filename,
        mime="text/csv",
        use_container_width=False,
    )


def render_invoice_table(df, theme):
    if df.empty:
        return

    headers = [
        html.escape(str(column))
        for column in df.columns
    ]

    header_html = "".join(
        f"<th>{header}</th>"
        for header in headers
    )

    rows_html = []

    for _, row in df.iterrows():
        cells = []

        for column in df.columns:
            value = html.escape(str(row[column]))

            if column in {"Validation", "Payment"}:
                value_lower = value.lower()

                if value_lower == "approved":
                    badge_color = theme["success"]
                elif value_lower in {"human review", "unpaid"}:
                    badge_color = theme["warning"]
                elif value_lower == "paid":
                    badge_color = theme["success"]
                else:
                    badge_color = theme["muted"]

                value = (
                    f'<span style="'
                    f'color:{badge_color};'
                    f'font-weight:600;'
                    f'">{value}</span>'
                )

            cells.append(
                f"<td>{value}</td>"
            )

        rows_html.append(
            "<tr>"
            + "".join(cells)
            + "</tr>"
        )

    table_html = f"""
    <div class="invoice-table" style="
        width:100%;
        overflow:hidden;
        border:1px solid {theme['border']};
        border-radius:16px;
        background:{theme['paper_bgcolor']};
        box-shadow:0 8px 24px {theme.get('shadow', 'rgba(15, 23, 42, 0.045)')};
    ">
        <table style="
            width:100%;
            border-collapse:separate;
            border-spacing:0;
            font-size:14px;
            color:{theme['font_color']};
        ">
            <thead>
                <tr>
                    {header_html}
                </tr>
            </thead>
            <tbody>
                {''.join(rows_html)}
            </tbody>
        </table>
    </div>
    <style>
        .invoice-table table thead th {{
            background:{theme['plot_bgcolor']};
            color:{theme['font_color']};
            text-align:left;
            font-weight:600;
            padding:13px 12px;
            border-bottom:1px solid {theme['border']};
            white-space:nowrap;
        }}

        .invoice-table table tbody td {{
            background:{theme['paper_bgcolor']};
            color:{theme['font_color']};
            padding:13px 12px;
            border-bottom:1px solid {theme['border']};
            vertical-align:middle;
        }}

        .invoice-table table tbody tr:last-child td {{
            border-bottom:0;
        }}

        .invoice-table table tbody tr:hover td {{
            background:{theme['plot_bgcolor']};
        }}
    </style>
    """

    st.markdown(
        table_html,
        unsafe_allow_html=True,
    )


# =========================================================
# SIDEBAR
# =========================================================

def render_sidebar():

    with st.sidebar:

        st.markdown(
            "## Paperwork Hub"
        )

        st.caption(
            "Documents. Processed."
        )

        st.divider()

        pages = [
            "Dashboard",
            "Process Invoice",
            "Invoice History",
        ]

        current_page = st.session_state.get(
            "page",
            "Dashboard",
        )

        for page_name in pages:

            is_current = (
                current_page
                == page_name
            )

            if st.button(
                page_name,
                key=f"nav_{page_name}",
                use_container_width=True,
                type=(
                    "primary"
                    if is_current
                    else "secondary"
                ),
            ):

                st.session_state.page = (
                    page_name
                )

                st.rerun()

        st.divider()

        st.toggle(
            "Dark mode",
            key="dark_mode",
            value=False,
            help=(
                "Switch between light "
                "and dark appearance."
            ),
        )

        st.divider()

        st.caption(
            "Secure document processing "
            "and financial verification."
        )


# =========================================================
# APPLY UI
# =========================================================

render_sidebar()

inject_theme(
    is_dark_mode()
)

page = st.session_state.get(
    "page",
    "Dashboard",
)

theme = plotly_theme(
    is_dark_mode()
)


# =========================================================
# DASHBOARD
# =========================================================

def render_dashboard():

    df = load_dataframe()

    page_header(
        "Business Overview",
        "A focused view of invoice processing, verification and exceptions.",
    )

    # -----------------------------------------------------
    # TOP METRICS
    # -----------------------------------------------------

    total_invoices = len(df)

    approved_count = (
        int(
            (
                df["validation_status"]
                == "Approved"
            ).sum()
        )
        if not df.empty
        else 0
    )

    review_count = (
        int(
            (
                df["validation_status"]
                == "Human Review"
            ).sum()
        )
        if not df.empty
        else 0
    )

    total_value = (
        float(
            df["total"].sum()
        )
        if not df.empty
        else 0.0
    )

    unpaid_amount = 0.0

    if not df.empty:

        unpaid_mask = (
            df["payment_status"]
            .astype(str)
            .str.lower()
            .eq("unpaid")
        )

        unpaid_amount = float(
            df.loc[
                unpaid_mask,
                "total",
            ].sum()
        )

    # -----------------------------------------------------
    # KPI CARDS
    # -----------------------------------------------------

    metric_cols = st.columns(
        4,
        gap="medium",
    )

    with metric_cols[0]:
        render_value_card(
            "Invoices",
            f"{total_invoices:,}",
            theme,
            theme["primary"],
        )

    with metric_cols[1]:
        render_value_card(
            "Approved",
            f"{approved_count:,}",
            theme,
            theme["success"],
        )

    with metric_cols[2]:
        render_value_card(
            "Review Required",
            f"{review_count:,}",
            theme,
            theme["warning"],
        )

    with metric_cols[3]:
        render_value_card(
            "Unpaid Value",
            format_currency(unpaid_amount),
            theme,
            theme["purple"],
        )

    # -----------------------------------------------------
    # TOTAL INVOICE VALUE
    # -----------------------------------------------------

    st.markdown(
        f"""
        <div style="
            margin-top:18px;
            padding:20px 24px;
            border:1px solid {theme['border']};
            border-radius:18px;
            background:{theme['paper_bgcolor']};
            box-shadow:0 8px 24px {theme.get('shadow', 'rgba(15, 23, 42, 0.045)')};
        ">
            <div style="
                color:{theme['font_color']};
                font-size:13px;
                font-weight:650;
                margin-bottom:7px;
            ">Total Invoice Value</div>
            <div style="
                color:{theme['font_color']};
                font-size:clamp(28px, 4vw, 46px);
                font-weight:780;
                line-height:1.08;
                letter-spacing:-0.02em;
                overflow-wrap:anywhere;
                word-break:break-word;
            ">{format_currency(total_value)}</div>
            <div style="
                color:{theme['muted']};
                font-size:12px;
                margin-top:8px;
            ">Across {total_invoices:,} processed invoice(s) · Dashboard updates after every successful processing or deletion.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    last_refreshed = datetime.now().strftime("%d %b %Y, %I:%M %p")

    st.caption(
        f"Live overview · Last refreshed {last_refreshed}"
    )

    # -----------------------------------------------------
    # EMPTY DASHBOARD
    # -----------------------------------------------------

    if df.empty:

        st.divider()

        empty_state(
            "No invoices yet",
            "Process your first invoice to start building the dashboard.",
        )

        return

    st.divider()

    # =====================================================
    # MAIN CHART + SIDE PANEL
    # =====================================================

    main_col, side_col = st.columns(
        [3.0, 1.25],
        gap="large",
    )

    # -----------------------------------------------------
    # EXPECTED VS ACTUAL
    # -----------------------------------------------------

    with main_col:

        section_header(
            "Expected vs Actual",
            "Independent financial comparison across processed invoices.",
        )

        period_labels = {
            "Day": "day",
            "Week": "week",
            "Month": "month",
            "Year": "year",
        }

        selected_period = st.radio(
            "View by",
            options=list(period_labels.keys()),
            horizontal=True,
            label_visibility="collapsed",
        )

        period = period_labels[selected_period]

        fig = expected_vs_actual(
            df,
            theme,
            period=period,
        )

        if fig is not None:

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "displaylogo": False,
                    "responsive": True,
                    "scrollZoom": False,
                },
            )

            chart_data = df.copy()
            chart_data["invoice_date"] = pd.to_datetime(
                chart_data["invoice_date"],
                errors="coerce",
            )
            chart_data = chart_data.dropna(
                subset=["invoice_date"]
            )

            if period == "week":
                chart_data["period"] = chart_data["invoice_date"].dt.to_period("W").dt.start_time
            elif period == "month":
                chart_data["period"] = chart_data["invoice_date"].dt.to_period("M").dt.start_time
            elif period == "year":
                chart_data["period"] = chart_data["invoice_date"].dt.to_period("Y").dt.start_time
            else:
                chart_data["period"] = chart_data["invoice_date"].dt.floor("D")

            chart_data = (
                chart_data.groupby("period")
                .agg(
                    expected=("subtotal", "sum"),
                    actual=("total", "sum"),
                )
                .reset_index()
            )

            download_dataframe(
                chart_data,
                "expected_vs_actual.csv",
            )

        else:

            st.info(
                "There is not enough valid date information "
                "for this visualization."
            )

    # -----------------------------------------------------
    # RIGHT SIDE
    # -----------------------------------------------------

    with side_col:

        section_header(
            "Processing Status",
        )

        status_counts = (
            df[
                "validation_status"
            ].value_counts()
        )

        approved_value = int(
            status_counts.get(
                "Approved",
                0,
            )
        )

        review_value = int(
            status_counts.get(
                "Human Review",
                0,
            )
        )

        st.success(
            f"Approved  •  {approved_value}"
        )

        st.warning(
            f"Review  •  {review_value}"
        )

        st.divider()

        section_header(
            "Payment Status",
        )

        payment_counts = (
            df[
                "payment_status"
            ]
            .astype(str)
            .str.title()
            .value_counts()
        )

        for label, value in (
            payment_counts.items()
        ):

            st.write(
                f"**{label}**  "
                f"{int(value)}"
            )

        st.divider()

        section_header(
            "Review Queue",
        )

        review_df = df[
            df[
                "validation_status"
            ]
            == "Human Review"
        ]

        if review_df.empty:

            st.success(
                "Nothing requires attention."
            )

        else:

            st.warning(
                f"{len(review_df)} invoice(s) "
                "require review."
            )

            for _, row in (
                review_df.head(3)
                .iterrows()
            ):

                difference = (
                    format_currency(
                        row[
                            "difference"
                        ]
                    )
                )

                st.caption(
                    f"{row['invoice_number']} · "
                    f"{row['vendor']} · "
                    f"{difference} difference"
                )

    st.divider()

    # =====================================================
    # SECONDARY CHARTS
    # =====================================================

    chart_col, status_col = st.columns(
        2,
        gap="large",
    )

    # -----------------------------------------------------
    # INVOICE VOLUME
    # -----------------------------------------------------

    with chart_col:

        section_header(
            "Invoice Volume",
            "Processed invoices by month.",
        )

        fig = invoice_volume(
            df,
            theme,
        )

        if fig is not None:

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "displaylogo": False,
                    "responsive": True,
                    "scrollZoom": False,
                },
            )

    # -----------------------------------------------------
    # VALIDATION MIX
    # -----------------------------------------------------

    with status_col:

        section_header(
            "Validation Mix",
            "Current processing outcomes.",
        )

        fig = status_donut(
            df,
            theme,
        )

        if fig is not None:

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "displaylogo": False,
                    "responsive": True,
                    "scrollZoom": False,
                },
            )

    st.divider()

    # =====================================================
    # RECENT INVOICES
    # =====================================================

    section_header(
        "Recent Invoices",
        "Latest processed documents.",
    )

    recent = df.head(8).copy()

    display = recent[
        [
            "invoice_number",
            "vendor",
            "invoice_date",
            "total",
            "payment_status",
            "validation_status",
        ]
    ].copy()

    display.columns = [
        "Invoice",
        "Vendor",
        "Date",
        "Amount",
        "Payment",
        "Validation",
    ]

    display["Amount"] = (
        display["Amount"]
        .map(format_currency)
    )

    render_invoice_table(
        display,
        theme,
    )


# =========================================================
# PROCESS INVOICE
# =========================================================

def render_process_invoice():

    page_header(
        "Process Invoice",
        "Upload a text invoice, verify its financial values, and save the result.",
    )

    upload_col, info_col = st.columns(
        [2.5, 1],
        gap="large",
    )

    # -----------------------------------------------------
    # UPLOAD
    # -----------------------------------------------------

    with upload_col:

        uploaded_files = st.file_uploader(
            "Upload invoice",
            type=["txt"],
            accept_multiple_files=True,
            help=(
                "Select one or more TXT invoices. "
                "Maximum size: 5 MB per file."
            ),
        )

    # -----------------------------------------------------
    # MAXIMUM FILE LIMIT
    # -----------------------------------------------------

    if uploaded_files and len(uploaded_files) > 10:

        st.error(
            "You can process a maximum of 10 invoices at one time. "
            "Please remove some files and try again."
        )

        return

    # -----------------------------------------------------
    # FILE INFO
    # -----------------------------------------------------

    with info_col:

        st.caption(
            "Supported format"
        )

        st.write(
            "TXT"
        )

        st.caption(
            "Maximum size"
        )

        st.write(
            "5 MB"
        )

        st.caption(
            "Validation"
        )

        st.write(
            "Financial checks"
        )

    if not uploaded_files:

        st.divider()

        st.info(
            "Upload one or more TXT invoices to begin. "
            "Each document is processed, financially verified, "
            "and saved only after validation."
        )

        workflow_cols = st.columns(4, gap="medium")

        workflow_steps = [
            ("1", "Upload", "Add one or more invoice files."),
            ("2", "Extract", "Read the invoice details."),
            ("3", "Verify", "Check amounts and totals."),
            ("4", "Save", "Store the verified result."),
        ]

        for column, (number, title, description) in zip(
            workflow_cols,
            workflow_steps,
        ):
            with column:
                st.markdown(
                    f"**{number}. {title}**"
                )
                st.caption(description)

        st.caption(
            "Supports TXT invoices · Up to 10 files per batch · 5 MB per file"
        )

        return

    st.divider()

    first_file = uploaded_files[0]

    if len(uploaded_files) == 1:

        st.success(
            f"Processing Invoice: {first_file.name}"
        )

    else:

        st.success(
            f"Processing Invoice: {first_file.name} "
            f"and {len(uploaded_files) - 1} more"
        )

    # -----------------------------------------------------
    # PROCESS BUTTON
    # -----------------------------------------------------

    button_label = (
        "Process Invoice"
        if len(uploaded_files) == 1
        else f"Process {len(uploaded_files)} Invoices"
    )

    if not st.button(
        button_label,
        type="primary",
        use_container_width=True,
    ):

        return

    # -----------------------------------------------------
    # SINGLE INVOICE
    # -----------------------------------------------------

    if len(uploaded_files) == 1:

        uploaded_file = uploaded_files[0]

        # -------------------------------------------------
        # FILE SAFETY
        # -------------------------------------------------

        max_file_size = (
            5 * 1024 * 1024
        )

        if (
            uploaded_file.size
            > max_file_size
        ):

            st.error(
                "The uploaded file is too large. "
                "Maximum allowed size is 5 MB."
            )

            return

        raw_bytes = (
            uploaded_file.getvalue()
        )

        if not raw_bytes.strip():

            st.error(
                "The uploaded invoice is empty."
            )

            return

        try:

            invoice_text = (
                raw_bytes.decode(
                    "utf-8"
                )
            )

        except UnicodeDecodeError:

            st.error(
                "This invoice could not be read as UTF-8 text."
            )

            return

        # -------------------------------------------------
        # PROCESS
        # -------------------------------------------------

        progress = st.progress(
            0,
            text="Reading document",
        )

        try:

            progress.progress(
                25,
                text="Processing document",
            )

            invoice = extract_invoice(
                invoice_text
            )

            progress.progress(
                60,
                text="Validating financial values",
            )

            from validator import (
                validate_invoice
            )

            validation = (
                validate_invoice(
                    invoice
                )
            )

            progress.progress(
                100,
                text="Preparing result",
            )

        except InvoiceProcessingError as exc:

            progress.empty()

            st.error(
                str(exc)
            )

            return

        except Exception:

            progress.empty()

            st.error(
                "The invoice could not be processed safely. "
                "No record was saved."
            )

            return

        progress.empty()

        # -------------------------------------------------
        # DUPLICATE CHECK
        # -------------------------------------------------

        if invoice_number_exists(
            invoice.invoice_number
        ):

            st.warning(
                f"Invoice {invoice.invoice_number} "
                "has already been processed. "
                "No duplicate record was created."
            )

            return

        st.divider()

        # =================================================
        # INVOICE DETAILS
        # =================================================

        section_header(
            "Invoice Details",
        )

        info_cols = st.columns(
            4,
            gap="medium",
        )

        with info_cols[0]:

            st.metric(
                "Invoice",
                invoice.invoice_number,
            )

        with info_cols[1]:

            st.metric(
                "Vendor",
                invoice.vendor,
            )

        with info_cols[2]:

            st.metric(
                "Subtotal",
                format_currency(
                    invoice.subtotal
                ),
            )

        with info_cols[3]:

            st.metric(
                "Total",
                format_currency(
                    invoice.total
                ),
            )

        # -------------------------------------------------
        # SECONDARY DETAILS
        # -------------------------------------------------

        detail_cols = st.columns(
            4,
            gap="medium",
        )

        with detail_cols[0]:

            st.caption(
                "Invoice date"
            )

            st.write(
                invoice.invoice_date
            )

        with detail_cols[1]:

            st.caption(
                "Due date"
            )

            st.write(
                invoice.due_date
            )

        with detail_cols[2]:

            st.caption(
                "Tax"
            )

            st.write(
                format_currency(
                    invoice.tax
                )
            )

        with detail_cols[3]:

            st.caption(
                "Payment"
            )

            st.write(
                invoice.payment_status
            )

        st.divider()

        # =================================================
        # LINE ITEMS
        # =================================================

        section_header(
            "Line Items",
        )

        line_items = pd.DataFrame(
            [
                {
                    "Description": item.description,
                    "Quantity": item.quantity,
                    "Unit Price": format_currency(
                        item.unit_price
                    ),
                    "Amount": format_currency(
                        item.amount
                    ),
                }
                for item in invoice.items
            ]
        )

        st.dataframe(
            line_items,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        # =================================================
        # VALIDATION
        # =================================================

        section_header(
            "Validation",
            "Independent financial checks performed before saving.",
        )

        validation_row(
            "Line-item calculations",
            not validation.item_errors,
            (
                "All quantity × unit price checks passed."
                if not validation.item_errors
                else "; ".join(
                    validation.item_errors
                )
            ),
        )

        validation_row(
            "Subtotal",
            abs(
                validation.subtotal_difference
            ) < 0.01,
            (
                "Line items match the invoice subtotal."
                if abs(
                    validation.subtotal_difference
                ) < 0.01
                else (
                    "Difference: "
                    + format_currency(
                        validation.subtotal_difference
                    )
                )
            ),
        )

        validation_row(
            "Total",
            abs(
                validation.difference
            ) < 0.01,
            (
                "Subtotal + tax matches the invoice total."
                if abs(
                    validation.difference
                ) < 0.01
                else (
                    f"Expected "
                    f"{format_currency(validation.expected_total)}; "
                    f"actual "
                    f"{format_currency(invoice.total)}."
                )
            ),
        )

        st.divider()

        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        if validation.status == "Approved":

            st.success(
                "Approved — all financial checks passed."
            )

        else:

            st.warning(
                "Review required — one or more financial "
                "checks did not pass."
            )

            st.caption(
                validation.audit_reason
            )

        st.caption(
            "Recorded difference: "
            + format_currency(
                validation.difference
            )
        )

        # -------------------------------------------------
        # SAVE
        # -------------------------------------------------

        try:

            save_invoice(
                invoice,
                validation.status,
                validation.difference,
                validation.audit_reason,
            )

            st.success(
                "Invoice saved successfully."
            )

        except sqlite3.IntegrityError:

            st.warning(
                "This invoice already exists in the database. "
                "No duplicate record was created."
            )

        except Exception:

            st.error(
                "The invoice could not be saved. "
                "No partial database record was kept."
            )

        return

    # =====================================================
    # MULTIPLE INVOICES
    # =====================================================

    max_file_size = (
        5 * 1024 * 1024
    )

    from validator import (
        validate_invoice
    )

    results = []

    progress = st.progress(
        0,
        text="Preparing invoices",
    )

    total_files = len(uploaded_files)

    for index, uploaded_file in enumerate(
        uploaded_files,
        start=1,
    ):

        filename = uploaded_file.name

        try:

            progress.progress(
                int(
                    ((index - 1) / total_files)
                    * 100
                ),
                text=f"Processing {filename}",
            )

            # ---------------------------------------------
            # FILE SAFETY
            # ---------------------------------------------

            if uploaded_file.size > max_file_size:

                results.append(
                    {
                        "File": filename,
                        "Status": "Failed",
                        "Invoice": "—",
                        "Vendor": "—",
                        "Amount": "—",
                        "Reason": "File is larger than 5 MB.",
                    }
                )

                continue

            raw_bytes = (
                uploaded_file.getvalue()
            )

            if not raw_bytes.strip():

                results.append(
                    {
                        "File": filename,
                        "Status": "Failed",
                        "Invoice": "—",
                        "Vendor": "—",
                        "Amount": "—",
                        "Reason": "Invoice file is empty.",
                    }
                )

                continue

            try:

                invoice_text = (
                    raw_bytes.decode(
                        "utf-8"
                    )
                )

            except UnicodeDecodeError:

                results.append(
                    {
                        "File": filename,
                        "Status": "Failed",
                        "Invoice": "—",
                        "Vendor": "—",
                        "Amount": "—",
                        "Reason": "File could not be read as UTF-8 text.",
                    }
                )

                continue

            # ---------------------------------------------
            # PROCESS
            # ---------------------------------------------

            invoice = extract_invoice(
                invoice_text
            )

            validation = (
                validate_invoice(
                    invoice
                )
            )

            # ---------------------------------------------
            # DUPLICATE CHECK
            # ---------------------------------------------

            if invoice_number_exists(
                invoice.invoice_number
            ):

                results.append(
                    {
                        "File": filename,
                        "Status": "Duplicate",
                        "Invoice": invoice.invoice_number,
                        "Vendor": invoice.vendor,
                        "Amount": format_currency(
                            invoice.total
                        ),
                        "Reason": "Invoice already exists in the database.",
                    }
                )

                continue

            # ---------------------------------------------
            # SAVE
            # ---------------------------------------------

            try:

                save_invoice(
                    invoice,
                    validation.status,
                    validation.difference,
                    validation.audit_reason,
                )

                results.append(
                    {
                        "File": filename,
                        "Status": validation.status,
                        "Invoice": invoice.invoice_number,
                        "Vendor": invoice.vendor,
                        "Amount": format_currency(
                            invoice.total
                        ),
                        "Reason": (
                            validation.audit_reason
                            if validation.status != "Approved"
                            else "All financial checks passed."
                        ),
                    }
                )

            except sqlite3.IntegrityError:

                results.append(
                    {
                        "File": filename,
                        "Status": "Duplicate",
                        "Invoice": invoice.invoice_number,
                        "Vendor": invoice.vendor,
                        "Amount": format_currency(
                            invoice.total
                        ),
                        "Reason": "Invoice already exists in the database.",
                    }
                )

            except Exception:

                results.append(
                    {
                        "File": filename,
                        "Status": "Failed",
                        "Invoice": invoice.invoice_number,
                        "Vendor": invoice.vendor,
                        "Amount": format_currency(
                            invoice.total
                        ),
                        "Reason": "The invoice could not be saved safely.",
                    }
                )

        except InvoiceProcessingError as exc:

            results.append(
                {
                    "File": filename,
                    "Status": "Failed",
                    "Invoice": "—",
                    "Vendor": "—",
                    "Amount": "—",
                    "Reason": str(exc),
                }
            )

        except Exception:

            results.append(
                {
                    "File": filename,
                    "Status": "Failed",
                    "Invoice": "—",
                    "Vendor": "—",
                    "Amount": "—",
                    "Reason": "The invoice could not be processed safely.",
                }
            )

        finally:

            progress.progress(
                int(
                    (index / total_files)
                    * 100
                ),
                text=f"Processed {index} of {total_files}",
            )

    progress.empty()

    # =====================================================
    # BATCH RESULT
    # =====================================================

    st.divider()

    section_header(
        "Batch Processing Results",
        "Summary of the invoices processed in this upload.",
    )

    result_df = pd.DataFrame(
        results
    )

    approved_count = int(
        (
            result_df["Status"]
            == "Approved"
        ).sum()
    )

    review_count = int(
        (
            result_df["Status"]
            == "Human Review"
        ).sum()
    )

    duplicate_count = int(
        (
            result_df["Status"]
            == "Duplicate"
        ).sum()
    )

    failed_count = int(
        (
            result_df["Status"]
            == "Failed"
        ).sum()
    )

    result_cols = st.columns(
        4,
        gap="medium",
    )

    with result_cols[0]:

        st.metric(
            "Approved",
            approved_count,
        )

    with result_cols[1]:

        st.metric(
            "Review Required",
            review_count,
        )

    with result_cols[2]:

        st.metric(
            "Duplicates",
            duplicate_count,
        )

    with result_cols[3]:

        st.metric(
            "Failed",
            failed_count,
        )

    st.dataframe(
        result_df,
        use_container_width=True,
        hide_index=True,
    )

    download_dataframe(
        result_df,
        "batch_processing_results.csv",
    )


# =========================================================
# INVOICE HISTORY
# =========================================================

def render_history():

    page_header(
        "Invoice History",
        "Search and review previously processed invoices.",
    )

    df = load_dataframe()

    if df.empty:

        empty_state(
            "No invoices yet",
            "Processed invoices will appear here.",
        )

        return

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search = st.text_input(
        "Search",
        placeholder="Invoice number or vendor",
    )

    status_filter = st.selectbox(
        "Validation status",
        [
            "All",
            "Approved",
            "Human Review",
        ],
    )

    filtered = df.copy()

    # -----------------------------------------------------
    # TEXT FILTER
    # -----------------------------------------------------

    if search:

        query = (
            search
            .strip()
            .lower()
        )

        invoice_matches = (
            filtered[
                "invoice_number"
            ]
            .astype(str)
            .str.lower()
            .str.contains(
                query,
                na=False,
            )
        )

        vendor_matches = (
            filtered[
                "vendor"
            ]
            .astype(str)
            .str.lower()
            .str.contains(
                query,
                na=False,
            )
        )

        filtered = filtered[
            invoice_matches
            | vendor_matches
        ]

    # -----------------------------------------------------
    # STATUS FILTER
    # -----------------------------------------------------

    if status_filter != "All":

        filtered = filtered[
            filtered[
                "validation_status"
            ]
            == status_filter
        ]

    st.caption(
        f"{len(filtered)} invoice(s)"
    )

    # =====================================================
    # DATABASE MANAGEMENT
    # =====================================================

    with st.expander(
        "Database Management",
        expanded=False,
    ):

        st.caption(
            "Remove selected invoice records or clear the complete database."
        )

        selectable = filtered.copy()

        if not selectable.empty:

            selectable["selection_label"] = (
                selectable["invoice_number"].astype(str)
                + " · "
                + selectable["vendor"].astype(str)
            )

            selected_labels = st.multiselect(
                "Select invoices to delete",
                options=selectable[
                    "selection_label"
                ].tolist(),
                placeholder="Choose invoice(s)",
            )

            if selected_labels:

                selected_ids = selectable.loc[
                    selectable[
                        "selection_label"
                    ].isin(selected_labels),
                    "id",
                ].tolist()

                if st.button(
                    "Delete Selected",
                    type="secondary",
                    use_container_width=False,
                ):

                    try:
                        delete_invoices(selected_ids)
                        st.success(
                            f"{len(selected_ids)} invoice(s) deleted successfully."
                        )
                        st.rerun()

                    except Exception:
                        st.error(
                            "The selected invoices could not be deleted."
                        )

        st.divider()

        delete_all_confirmed = st.checkbox(
            "I understand that deleting all invoices is permanent.",
            key="delete_all_confirmed",
        )

        if st.button(
            "Delete All Invoices",
            type="secondary",
            use_container_width=False,
            disabled=not delete_all_confirmed,
        ):

            try:
                delete_all_invoices()
                st.success(
                    "All invoices have been deleted."
                )
                st.rerun()

            except Exception:
                st.error(
                    "The invoices could not be deleted."
                )

    st.divider()

    # -----------------------------------------------------
    # TABLE
    # -----------------------------------------------------

    display = filtered[
        [
            "invoice_number",
            "vendor",
            "invoice_date",
            "total",
            "payment_status",
            "validation_status",
            "difference",
        ]
    ].copy()

    display.columns = [
        "Invoice",
        "Vendor",
        "Date",
        "Amount",
        "Payment",
        "Validation",
        "Difference",
    ]

    display["Amount"] = (
        display["Amount"]
        .map(format_currency)
    )

    display["Difference"] = (
        display["Difference"]
        .map(format_currency)
    )

    render_invoice_table(
        display,
        theme,
    )

    st.divider()

    # =====================================================
    # DETAILS
    # =====================================================

    section_header(
        "Invoice Details",
        "Select an invoice to inspect its financial and validation details.",
    )

    detail_options = [
        (
            f"{row['invoice_number']} · {row['vendor']} · {format_currency(row['total'])}",
            int(row["id"]),
        )
        for _, row in filtered.iterrows()
    ]

    if not detail_options:
        st.info(
            "No invoices match the current search or filter."
        )
        return

    detail_labels = [label for label, _ in detail_options]

    selected_detail_label = st.selectbox(
        "Select invoice",
        options=detail_labels,
        index=0,
        placeholder="Choose an invoice",
    )

    selected_detail_id = dict(detail_options)[
        selected_detail_label
    ]

    selected_row = filtered.loc[
        filtered["id"] == selected_detail_id
    ].iloc[0]

    detail_cols = st.columns(4, gap="medium")

    with detail_cols[0]:
        render_value_card(
            "Invoice",
            str(selected_row["invoice_number"]),
            theme,
            theme["primary"],
        )

    with detail_cols[1]:
        render_value_card(
            "Vendor",
            str(selected_row["vendor"]),
            theme,
            theme.get("info", theme.get("primary", "#5C82B8")),
        )

    with detail_cols[2]:
        render_value_card(
            "Total",
            format_currency(selected_row["total"]),
            theme,
            theme["purple"],
        )

    with detail_cols[3]:
        payment_color = (
            theme["success"]
            if str(selected_row["payment_status"]).lower() == "paid"
            else theme["warning"]
        )

        render_value_card(
            "Payment",
            str(selected_row["payment_status"]),
            theme,
            payment_color,
        )

    st.divider()

    detail_left, detail_right = st.columns(2, gap="large")

    with detail_left:
        st.write(
            f"**Invoice date:** {selected_row['invoice_date']}"
        )
        st.write(
            f"**Due date:** {selected_row['due_date']}"
        )
        st.write(
            f"**Subtotal:** {format_currency(selected_row['subtotal'])}"
        )

    with detail_right:
        st.write(
            f"**Tax:** {format_currency(selected_row['tax'])}"
        )
        st.write(
            f"**Validation:** {selected_row['validation_status']}"
        )
        st.write(
            f"**Difference:** {format_currency(selected_row['difference'])}"
        )

    if selected_row["validation_status"] == "Approved":
        st.success("Approved — all financial checks passed.")
    else:
        st.warning("Human review required — one or more checks did not pass.")

    if selected_row["audit_reason"]:
        st.caption(
            f"Reason: {selected_row['audit_reason']}"
        )


# =========================================================
# ROUTER
# =========================================================

if page == "Dashboard":

    render_dashboard()

elif page == "Process Invoice":

    render_process_invoice()

elif page == "Invoice History":

    render_history()

else:

    render_dashboard()