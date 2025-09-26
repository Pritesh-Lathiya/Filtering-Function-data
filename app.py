import streamlit as st
import pandas as pd

st.title("Google Sheet Filter App with Colour Column and Value.txt Logging")

# Step 1: Enter Google Sheet CSV export link
sheet_url = st.text_input("Enter Google Sheet CSV export link (make sure sharing is 'Anyone with the link can view')")

# TXT file to store marked values
txt_file_path = "Value.txt"

if sheet_url:
    try:
        # Step 2: Ask how many rows to skip from top
        skip_rows = st.number_input("Enter number of rows to skip from top", min_value=0, value=0, step=1)

        # Load Google Sheet directly as CSV
        df = pd.read_csv(sheet_url, skiprows=skip_rows)

        # Step 3: Select column to filter
        col_options = df.columns.tolist()
        filter_col = st.selectbox("Select column to filter", col_options)

        # Step 4: Select filter values
        unique_values = df[filter_col].dropna().astype(str).unique().tolist()
        filter_values = st.multiselect(f"Select value(s) to filter {filter_col}", unique_values)

        if filter_values:
            # Filter DataFrame
            mask = df[filter_col].astype(str).apply(lambda x: any(val.lower() in x.lower() for val in filter_values))
            filtered_df = df[mask]

            if not filtered_df.empty:
                st.write(f"### Filtered Data (where `{filter_col}` contains {filter_values})")

                for idx, row in filtered_df.iterrows():
                    # Checkbox for each filtered row
                    col_checkbox = st.checkbox(f"Mark '{row[filter_col]}'", key=f"row_{idx}")
                    if col_checkbox:
                        # Append value to Value.txt
                        with open(txt_file_path, "a") as f:
                            f.write(str(row[filter_col]) + "\n")

                    st.dataframe(row.to_frame().T.transpose())

                # Show current content of Value.txt
                st.write("### Current Marked Values in Value.txt")
                try:
                    with open(txt_file_path, "r") as f:
                        st.text(f.read())
                except FileNotFoundError:
                    st.text("No values marked yet.")

            else:
                st.warning("No matching rows found.")

    except Exception as e:
        st.error(f"Error loading Google Sheet: {e}")
