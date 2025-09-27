import streamlit as st
import pandas as pd
import requests
import base64
import json

# GitHub settings
GITHUB_REPO = "your-username/your-repo"  # e.g., priteshlathiya/myapp
FILE_PATH = "Value.txt"
BRANCH = "main"
TOKEN = "your_personal_access_token"  # create from GitHub Developer Settings

st.title("Google Sheet Filter App with GitHub Value.txt Logging")

# Input Google Sheet link
sheet_url = st.text_input("Enter Google Sheet CSV export link (make sure sharing is 'Anyone with the link can view')")
skip_rows = st.number_input("Enter number of rows to skip from top", min_value=0, step=1)

if sheet_url:
    try:
        df = pd.read_csv(sheet_url, skiprows=skip_rows)
        column = st.selectbox("Select column to filter", df.columns)
        values = st.multiselect(f"Select value(s) to filter {column}", df[column].unique())

        if values:
            filtered_df = df[df[column].astype(str).str.contains('|'.join(values), case=False, na=False)]
            st.write("Filtered Data (where", column, "contains", values, ")", filtered_df)

            # Load current Value.txt from GitHub
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}?ref={BRANCH}"
            headers = {"Authorization": f"token {TOKEN}"}
            response = requests.get(url, headers=headers).json()

            sha = response.get("sha", None)
            if "content" in response:
                current_content = base64.b64decode(response["content"]).decode("utf-8").splitlines()
            else:
                current_content = []

            # Append new values if not already in file
            updated_content = current_content + [v for v in values if v not in current_content]
            new_file_content = "\n".join(updated_content)

            # Push updated file to GitHub
            data = {
                "message": "Updated Value.txt from Streamlit app",
                "content": base64.b64encode(new_file_content.encode("utf-8")).decode("utf-8"),
                "branch": BRANCH
            }
            if sha:
                data["sha"] = sha

            put_response = requests.put(url, headers=headers, data=json.dumps(data))

            if put_response.status_code in [200, 201]:
                st.success("Value.txt updated successfully in GitHub!")
            else:
                st.error(f"Error updating file: {put_response.json()}")

            st.write("Current Marked Values in Value.txt")
            st.write(updated_content)

    except Exception as e:
        st.error(f"Error: {e}")
