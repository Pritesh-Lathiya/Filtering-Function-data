import streamlit as st
import pandas as pd
import requests
import base64

st.title("Google Sheet Filter App with Value.txt Logging")

# Load secrets
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["GITHUB_REPO"]
FILE_PATH = st.secrets["GITHUB_FILE"]

headers = {"Authorization": f"token {TOKEN}"}

def get_file_content():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        content = base64.b64decode(data["content"]).decode("utf-8")
        sha = data["sha"]
        return content.splitlines(), sha
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

# UI
sheet_url = st.text_input("Enter Google Sheet CSV export link (make sure sharing is 'Anyone with the link can view')")
skip_rows = st.number_input("Enter number of rows to skip from top", min_value=0, value=0, step=1)

if sheet_url:
    try:
        df = pd.read_csv(sheet_url, skiprows=skip_rows)
        st.success("Google Sheet loaded successfully!")

        col_options = df.columns.tolist()
        filter_col = st.selectbox("Select column to filter", col_options)

        values = st.multiselect(f"Select value(s) to filter {filter_col}", df[filter_col].dropna().unique())

        if values:
            filtered_df = df[df[filter_col].astype(str).isin(values)]
            st.write("### Filtered Data")
            st.dataframe(filtered_df)

            # Load current txt values
            existing, sha = get_file_content()

            # Checkbox for marking
            if st.checkbox("Mark selected values to Value.txt"):
                updated = existing + values
                if update_file(updated, sha):
                    st.success("✅ Value.txt updated on GitHub!")
                else:
                    st.error("❌ Failed to update Value.txt")

            st.write("### Current Marked Values in Value.txt")
            st.write(existing)

    except Exception as e:
        st.error(f"Error: {e}")
