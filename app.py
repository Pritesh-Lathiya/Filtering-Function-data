import streamlit as st
import pandas as pd

st.title("Excel Filter App")

# Step 1: Upload Excel
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Step 2: Ask how many rows to remove
    skip_rows = st.number_input("Enter number of rows to skip from top", min_value=0, value=0, step=1)

    try:
        # Read Excel
        df = pd.read_excel(uploaded_file, skiprows=skip_rows)
        st.success("File uploaded and processed!")

        # Step 3: Select column
        col_options = df.columns.tolist()
        filter_col = st.selectbox("Select column to filter", col_options)

        # Step 4: Enter value
        filter_value = st.text_input(f"Enter value to filter {filter_col}")

        if filter_value:
            # Case-insensitive filter
            filtered_df = df[df[filter_col].astype(str).str.contains(filter_value, case=False, na=False)]

            if not filtered_df.empty:
                st.write(f"### Filtered Data (where `{filter_col}` contains '{filter_value}')")

                # Show transposed view (vertical)
                for idx, row in filtered_df.iterrows():
                    st.write(f"#### Row {idx}")
                    st.dataframe(row.to_frame().T.transpose())  # transpose row

                # Prepare transposed data for download
                transposed_df = filtered_df.transpose()

                # Download button
                csv = transposed_df.to_csv(header=False).encode("utf-8")
                st.download_button("Download Transposed Data", csv, "filtered_data.csv", "text/csv")
            else:
                st.warning("No matching rows found.")

    except Exception as e:
        st.error(f"Error reading file: {e}")
