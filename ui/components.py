import streamlit as st


def page_header(title, subtitle=None):
    st.title(title)

    if subtitle:
        st.caption(subtitle)


def section_header(title, subtitle=None):
    st.subheader(title)

    if subtitle:
        st.caption(subtitle)


def validation_row(
    label,
    passed,
    detail=None,
):
    columns = st.columns(
        [3, 1, 5],
        gap="small",
    )

    with columns[0]:
        st.write(label)

    with columns[1]:
        if passed:
            st.success(
                "Passed"
            )
        else:
            st.warning(
                "Review"
            )

    with columns[2]:
        if detail:
            st.caption(detail)


def compact_info(
    label,
    value,
):
    st.caption(label)
    st.write(
        f"**{value}**"
    )


def empty_state(
    title,
    message,
):
    with st.container(
        border=True
    ):
        st.subheader(title)
        st.caption(message)