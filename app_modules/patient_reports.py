
import streamlit as st
import pandas as pd
import re

from io import BytesIO

from database.database import get_user_predictions

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
)

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet



def show_patient_reports():

    # Initialize selected report
    if "selected_report_id" not in st.session_state:
        st.session_state.selected_report_id = None

    if st.session_state.selected_report_id is not None:
        report_page = "details"
    else:
        report_page = "list"

    # ================================================================
    # SCREEN 1: PATIENT REPORTS LIST
    # ================================================================
    if report_page == "list":

        st.title("Patient Reports")
        st.write(
            "View patient prediction history and download individual reports."
        )

        records = get_user_predictions(st.session_state.user_id)

        if not records:
            st.info(
                "No predictions yet. Head to Disease Prediction "
                "to run your first test."
            )

        else:
            report_rows = []

            for r in records:

                risk_match = re.search(
                    r'(\d+(?:\.\d+)?)\s*%',
                    r['result'] or ''
                )

                risk_percentage = (
                    f"{risk_match.group(1)}%"
                    if risk_match else "N/A"
                )

                risk_display = f"{risk_percentage} · {r['risk']}"

                report_rows.append({
                    "Patient Name": r['patient_name'],
                    "Disease": r['condition'],
                    "Risk": risk_display,
                    "Date & Time": r['timestamp'],
                })

            df = pd.DataFrame(report_rows)

            # Filters
            col1, col2 = st.columns(2)

            with col1:
                condition_filter = st.multiselect(
                    "Filter by Disease",
                    options=sorted(df["Disease"].unique()),
                    default=sorted(df["Disease"].unique()),
                )

            with col2:
                risk_filter = st.selectbox(
                    "Filter by Risk",
                    options=["All", "High", "Low"],
                    index=0,
                    key="patient_reports_risk_v2"
                )

            # Apply filters
            filtered_pairs = [
                (r, row)
                for r, row in zip(records, report_rows)
                if row["Disease"] in condition_filter
                and (
                    risk_filter == "All"
                    or r["risk"] == risk_filter
                )
            ]

            filtered_records = [r for r, row in filtered_pairs]
            filtered_rows = [row for r, row in filtered_pairs]

            st.markdown(
                f"**{len(filtered_records)}** prediction record(s) found."
            )

            # Table headers
            header_cols = st.columns([2, 1.5, 1.5, 2, 1.2])

            header_cols[0].markdown("**Patient Name**")
            header_cols[1].markdown("**Disease**")
            header_cols[2].markdown("**Risk**")
            header_cols[3].markdown("**Date & Time**")
            header_cols[4].markdown("**Report**")

            st.divider()

            # Table rows
            for record, row in zip(filtered_records, filtered_rows):

                cols = st.columns([2, 1.5, 1.5, 2, 1.2])

                cols[0].write(row["Patient Name"])
                cols[1].write(row["Disease"])
                cols[2].write(row["Risk"])
                cols[3].write(row["Date & Time"])

                if cols[4].button(
                    "View",
                    key=f"view_{record['id']}"
                ):
                    st.session_state.selected_report_id = record["id"]
                    st.rerun()

    # ================================================================
    # SCREEN 2: PATIENT DETAILS
    # ================================================================
    elif report_page == "details":

        all_records = get_user_predictions(st.session_state.user_id)

        selected_record = next(
            (
                r for r in all_records
                if r["id"] == st.session_state.selected_report_id
            ),
            None
        )

        if selected_record is None:
            st.error("Prediction record not found.")
            st.session_state.selected_report_id = None
            st.rerun()

        else:
            if st.button("← Back to Reports"):
                st.session_state.selected_report_id = None
                st.rerun()

            st.title("Patient Details")

            # Patient Information
            st.subheader("Patient Information")

            patient_data = {
                "Patient Name": selected_record["patient_name"],
                "Patient ID": selected_record["patient_code"],
                "Age": selected_record["age"],
                "Gender": selected_record["sex"],
                "Contact Number": selected_record["contact"],
            }

            patient_df = pd.DataFrame(
                list(patient_data.items()),
                columns=["Field", "Details"]
            )

            st.table(patient_df)

            st.divider()

            # Prediction Summary
            st.subheader("Prediction Summary")

            prediction_data = {
                "Disease": selected_record["condition"],
                "Prediction Result": selected_record["result"],
                "Risk Classification": selected_record["risk"],
                "Date & Time": selected_record["timestamp"],
            }

            prediction_df = pd.DataFrame(
                list(prediction_data.items()),
                columns=["Field", "Details"]
            )

            st.table(prediction_df)

            st.divider()

            # Clinical Parameters
            st.subheader("Clinical Parameters")

            clinical_data = selected_record["inputs"]

            if clinical_data:
                clinical_df = pd.DataFrame(
                    list(clinical_data.items()),
                    columns=["Parameter", "Value"]
                )

                st.table(clinical_df)
            else:
                st.info("No clinical parameters available.")

            st.divider()

            # Individual PDF Download
            pdf_buffer = BytesIO()

            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4
            )

            styles = getSampleStyleSheet()
            elements = []

            elements.append(
                Paragraph(
                    "Patient Medical Prediction Report",
                    styles["Title"]
                )
            )

            elements.append(Spacer(1, 20))

            elements.append(
                Paragraph("Patient Information", styles["Heading2"])
            )

            patient_table_data = [["Field", "Details"]]

            for key, value in patient_data.items():
                patient_table_data.append([key, str(value)])

            elements.append(Table(patient_table_data))
            elements.append(Spacer(1, 20))

            elements.append(
                Paragraph("Prediction Summary", styles["Heading2"])
            )

            prediction_table_data = [["Field", "Details"]]

            for key, value in prediction_data.items():
                prediction_table_data.append([key, str(value)])

            elements.append(Table(prediction_table_data))
            elements.append(Spacer(1, 20))

            elements.append(
                Paragraph("Clinical Parameters", styles["Heading2"])
            )

            clinical_table_data = [["Parameter", "Value"]]

            for key, value in clinical_data.items():
                clinical_table_data.append([str(key), str(value)])

            elements.append(Table(clinical_table_data))

            doc.build(elements)

            pdf_buffer.seek(0)

            st.download_button(
                label="Download Patient Report PDF",
                data=pdf_buffer.getvalue(),
                file_name=f"Patient_Report_{selected_record['id']}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
