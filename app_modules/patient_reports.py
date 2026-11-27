
import streamlit as st
import pandas as pd
import re
from reportlab.platypus import Image
from io import BytesIO

from database.database import get_user_predictions

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
)

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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
                    "Patient ID": r['patient_code'],
                    "Patient Name": r['patient_name'],
                    "Disease": r['condition'],
                    "Risk": risk_display,
                    "Date & Time": r['timestamp'],
                })

            df = pd.DataFrame(report_rows)
            
                        # Search by Patient ID or Patient Name
            search_query = st.text_input(
                "Search Patient",
                placeholder="Enter Patient ID or Patient Name...",
                key="patient_report_search"
            )

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

            # Apply filters and search
            filtered_pairs = [
                (r, row)
                for r, row in zip(records, report_rows)
                if row["Disease"] in condition_filter
                and (
                    risk_filter == "All"
                    or r["risk"] == risk_filter
                )
                and (
                    search_query.strip().lower() in str(row["Patient ID"]).lower()
                    or search_query.strip().lower() in str(row["Patient Name"]).lower()
                )
            ]
            filtered_records = [r for r, row in filtered_pairs]
            filtered_rows = [row for r, row in filtered_pairs]

            st.markdown(
                f"**{len(filtered_records)}** prediction record(s) found."
            )

            # Table headers
            header_cols = st.columns([1.5, 2, 1.5, 1.5, 2, 1.2])
            header_cols[0].markdown("**Patient ID**")
            header_cols[1].markdown("**Patient Name**")            
            header_cols[2].markdown("**Disease**")
            header_cols[3].markdown("**Risk**")
            header_cols[4].markdown("**Date & Time**")
            header_cols[5].markdown("**Report**")

            st.divider()

            # Table rows
            for record, row in zip(filtered_records, filtered_rows):

                cols = st.columns([1.5, 2, 1.5, 1.5, 2, 1.2])
                cols[0].write(row["Patient ID"])
                cols[1].write(row["Patient Name"])
                cols[2].write(row["Disease"])
                cols[3].write(row["Risk"])
                cols[4].write(row["Date & Time"])

                if cols[5].button("View", key=f"view_{record['id']}"):
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
            st.write("")            
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

        # ================================================================
        # PDF REPORT GENERATION
        # ================================================================

        pdf_buffer = BytesIO()

        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4
        )

        styles = getSampleStyleSheet()
        elements = []

        # ================================================================
        # PDF REPORT BRANDING
        # ================================================================

        logo = Image("assets/logo.png", width=350, height=100)
        logo.hAlign = "CENTER"

        elements.append(logo)
        elements.append(Spacer(1, 20))

        report_title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            alignment=0
        )

        elements.append(
            Paragraph(
                "PATIENT MEDICAL PREDICTION REPORT",
                report_title_style
            )
        )

        elements.append(Spacer(1, 20))

        # ================================================================
        # TABLE 1: PATIENT INFORMATION
        # ================================================================

        elements.append(
            Paragraph(
                "Patient Information",
                styles["Heading2"]
            )
        )

        patient_table_data = [
            ["Field", "Details"],
            ["Patient Name", str(patient_data["Patient Name"])],
            ["Patient ID", str(patient_data["Patient ID"])],
            ["Age", str(patient_data["Age"])],
            ["Gender", str(patient_data["Gender"])],
            ["Contact Number", str(patient_data["Contact Number"])],
        ]

        patient_table = Table(
            patient_table_data,
            colWidths=[180, 280]
        )
        patient_table.hAlign = "LEFT"

        elements.append(patient_table)
        elements.append(Spacer(1, 20))
        # ================================================================
        # TABLE 2: PREDICTION SUMMARY
        # ================================================================

        elements.append(
            Paragraph(
                "Prediction Summary",
                styles["Heading2"]
            )
        )

        prediction_table_data = [["Field", "Details"]]

        for key, value in prediction_data.items():
            prediction_table_data.append([
                str(key),
                str(value)
            ])

        prediction_table = Table(
            prediction_table_data,
            colWidths=[180, 280]
        )
        prediction_table.hAlign = "LEFT"

        elements.append(prediction_table)

        # ================================================================
        # TABLE 3: CLINICAL PARAMETERS
        # ================================================================

        elements.append(
            Paragraph(
                "Clinical Parameters",
                styles["Heading2"]
            )
        )

        clinical_table_data = [
            ["Parameter", "Value"]
        ]

        if clinical_data:
            for key, value in clinical_data.items():
                clinical_table_data.append([
                    str(key),
                    str(value)
                ])

            clinical_table = Table(
                clinical_table_data,
                colWidths=[280, 180]
            )
            clinical_table.hAlign = "LEFT"

            elements.append(clinical_table)
        else:
            elements.append(
                Paragraph(
                    "No clinical parameters available.",
                    styles["Normal"]
                )
            )

        elements.append(Spacer(1, 25))

        # ================================================================
        # MEDICAL DISCLAIMER
        # ================================================================

        disclaimer_style = ParagraphStyle(
            "Disclaimer",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            alignment=0
        )

        elements.append(
            Paragraph(
                "<b>Disclaimer:</b> This report is generated by a "
                "machine-learning prediction system and is not a "
                "confirmed medical diagnosis. Please consult a "
                "qualified healthcare professional.",
                disclaimer_style
            )
        )

        # ================================================================
        # BUILD PDF
        # ================================================================

        doc.build(elements)

        pdf_buffer.seek(0)

        st.download_button(
            label="Download Patient Report PDF",
            data=pdf_buffer.getvalue(),
            file_name=f"Patient_Report_{selected_record['id']}.pdf",
            mime="application/pdf",
            use_container_width=True
        )