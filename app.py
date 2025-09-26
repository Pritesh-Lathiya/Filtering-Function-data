import streamlit as st
import pandas as pd

st.title("Google Sheet Filter App with Colour Column")

# Step 1: Enter Google Sheet CSV export link
sheet_url = st.text_input("Enter Google Sheet CSV export link (make sure sharing is 'Anyone with the link can edit')")

if sheet_url:
    try:
        # Step 2: Ask how many rows to skip from top
        skip_rows = st.number_input("Enter number of rows to skip from top", min_value=0, value=0, step=1)

        # Load Google Sheet directly as CSV
        df = pd.read_csv(sheet_url, skiprows=skip_rows)

        # Add Colour column if not exists
        if "Colour" not in df.columns:
            df["Colour"] = ""

        st.success("Google Sheet loaded successfully!")

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

                # Show rows with checkbox to mark Colour as '-'
                for idx, row in filtered_df.iterrows():
                    col_checkbox = st.checkbox(f"Mark Row {idx} Colour as '-'", key=f"row_{idx}")
                    if col_checkbox:
                        df.at[idx, "Colour"] = "-"

                    # Show row vertically
                    st.dataframe(row.to_frame().T.transpose())

                # Show updated full sheet preview
                st.write("### Updated Sheet Preview")
                st.dataframe(df)

            else:
                st.warning("No matching rows found.")

    except Exception as e:
        st.error(f"Error loading Google Sheet: {e}")

