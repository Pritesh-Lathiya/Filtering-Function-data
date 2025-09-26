import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.title("Google Sheet Filter App with Colour Column")

# Step 0: Google Sheet setup
# Provide your Google Service Account JSON and Sheet URL
sheet_url = st.text_input("Enter Google Sheet URL")
if sheet_url:
    try:
        # Authenticate with Google Sheets
        creds = Credentials.from_service_account_file("service_account.json")
        gc = gspread.authorize(creds)

        # Get the sheet
        sheet_id = sheet_url.split("/")[5]
        sh = gc.open_by_key(sheet_id)
        worksheet = sh.sheet1

        # Get data as DataFrame
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)

        # Add Colour column if not exists
        if "Colour" not in df.columns:
            df["Colour"] = ""

        st.success("Google Sheet loaded successfully!")

        # Step 1: Select column to filter
        col_options = df.columns.tolist()
        filter_col = st.selectbox("Select column to filter", col_options)

        # Step 2: Select filter values
        unique_values = df[filter_col].dropna().astype(str).unique().tolist()
        filter_values = st.multiselect(f"Select value(s) to filter {filter_col}", unique_values)

        if filter_values:
            # Filter DataFrame
            mask = df[filter_col].astype(str).apply(lambda x: any(val.lower() in x.lower() for val in filter_values))
            filtered_df = df[mask]

            if not filtered_df.empty:
                st.write(f"### Filtered Data (where `{filter_col}` contains {filter_values})")

                # Show rows with checkbox to mark Colour as '-'
                for idx, row in filtered_df.iterrows():
                    col_checkbox = st.checkbox(f"Mark Row {idx} Colour as '-'", key=f"row_{idx}")
                    if col_checkbox:
                        df.at[idx, "Colour"] = "-"

                    # Show row vertically
                    st.dataframe(row.to_frame().T.transpose())

                # Optional: Show updated full sheet
                st.write("### Updated Sheet Preview")
                st.dataframe(df)

                # Optional: Write back to Google Sheet
                # worksheet.update([df.columns.values.tolist()] + df.values.tolist())

            else:
                st.warning("No matching rows found.")

    except Exception as e:
        st.error(f"Error loading Google Sheet: {e}")
