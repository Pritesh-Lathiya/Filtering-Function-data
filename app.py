import streamlit as st
import pandas as pd
import requests
import base64

# --- Title in sidebar ---
st.sidebar.title("Filter")

# --- GitHub secrets ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["GITHUB_REPO"]
FILE_PATH = st.secrets["GITHUB_FILE"]

headers = {"Authorization": f"token {TOKEN}"}

# --- GitHub helper functions ---
def get_file_content():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        content = base64.b64decode(data["content"]).decode("utf-8")
        sha = data["sha"]
        return [line.strip() for line in content.splitlines() if line.strip()], sha
    else:
        return [], None

def update_file(new_lines, sha):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    content = "\n".join(new_lines)
    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    data = {
        "message": "Update Value.txt from Streamlit",
        "content": encoded,
        "sha": sha
    }
    r = requests.put(url, headers=headers, json=data)
    return r.status_code == 200

# --- Sidebar inputs ---
uploaded_file = st.sidebar.file_uploader("Upload Excel file", type=["xlsx", "xls"])
skip_rows = st.sidebar.number_input("Enter number of rows to skip from top", min_value=0, value=0, step=1)

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, skiprows=skip_rows)
        st.sidebar.success("Excel file loaded successfully!")

        col_options = df.columns.tolist()

        # --- Column to filter on ---
        filter_col = st.sidebar.selectbox("Select column to filter", col_options)

        # --- Columns to exclude from display ---
        exclude_cols = st.sidebar.multiselect("Select columns to exclude from table", col_options)

        # --- Columns to store in Value.txt ---
        txt_cols = st.sidebar.multiselect("Select columns to save in Value.txt", col_options)

        # --- Main page: value selection ---
        values = st.multiselect(f"Select value(s) to filter **{filter_col}**", df[filter_col].dropna().unique())

        if values:
            filtered_df = df[df[filter_col].astype(str).isin(values)]

            # --- Check for duplicate bill numbers ---
            if 'Bill No' in filtered_df.columns:
                duplicate_bills = filtered_df['Bill No'].duplicated(keep=False)
                if duplicate_bills.any():
                    if st.checkbox("Filter duplicates by date"):
                        # Show date selection dropdown
                        if 'Date' in filtered_df.columns:
                            unique_dates = filtered_df.loc[duplicate_bills, 'BillDate'].dropna().unique()
                            selected_date = st.selectbox("Select date to filter duplicates", unique_dates)
                            filtered_df = filtered_df[filtered_df['BillDate'] == selected_date]

            # Drop excluded columns for table display
            display_df = filtered_df.drop(columns=exclude_cols) if exclude_cols else filtered_df
            st.table(display_df.T)   # Static, no scrollbars

            # --- GitHub update ---
            existing, sha = get_file_content()

            if st.checkbox("Mark selected values to Value.txt"):
                if txt_cols:  # Only save selected columns
                    df_to_save = filtered_df[txt_cols].astype(str)
                else:  # If nothing selected, save entire row
                    df_to_save = filtered_df.astype(str)

                # Convert rows to CSV lines
                lines_to_write = df_to_save.apply(lambda row: ",".join(row), axis=1).tolist()

                # Add header if file empty
                if not existing:
                    header = ",".join(df_to_save.columns)
                    updated = [header] + lines_to_write
                else:
                    updated = existing + lines_to_write

                if update_file(updated, sha):
                    st.success("✅ Value.txt updated on GitHub!")

    except Exception as e:
        st.error(f"Error: {e}")

