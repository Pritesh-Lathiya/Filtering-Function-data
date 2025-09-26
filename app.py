import streamlit as st
import pandas as pd

st.title("Excel Filter App with Row Selection")

# Step 1: Upload Excel
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Step 2: Ask how many rows to remove
    skip_rows = st.number_input("Enter number of rows to skip from top", min_value=0, value=0, step=1)

    try:
        # Read Excel
        df = pd.read_excel(uploaded_file, skiprows=skip_rows)
        st.success("File uploaded and processed!")
        
        st.write("### Preview of Data")
        st.dataframe(df.head(20))  # preview

        # Step 3: Select column for filtering
        col_options = df.columns.tolist()
        filter_col = st.selectbox("Select column to filter", col_options)

        # Step 4: Enter value to filter
        filter_value = st.text_input(f"Enter value to filter {filter_col}")

        if filter_value:
            filtered_df = df[df[filter_col].astype(str).str.contains(filter_value, case=False, na=False)]
            
            st.write(f"### Filtered Data (where `{filter_col}` contains '{filter_value}')")
            
            # Step 5: Row checkboxes
            selected_rows = []
            for i, row in filtered_df.iterrows():
                if st.checkbox(f"Select row {i} → {row.to_dict()}", key=i):
                    selected_rows.append(row)

            if selected_rows:
                selected_df = pd.DataFrame(selected_rows)

                st.write("### Selected Rows")
                st.dataframe(selected_df)

                # Option to download as CSV
                csv = selected_df.to_csv(index=False).encode('utf-8')
                st.download_button("Download Selected Rows (CSV)", csv, "selected_rows.csv", "text/csv")

                # Option to download as TXT
                txt_data = selected_df.to_string(index=False)
                st.download_button("Download Selected Rows (TXT)", txt_data, "selected_rows.txt")

    except Exception as e:
        st.error(f"Error reading file: {e}")
