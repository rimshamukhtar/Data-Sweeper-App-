import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Set up page
st.set_page_config(page_title="💽Data Sweeper", layout='wide')
st.title("💽Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualizations!")

# File uploader
uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

# Initialize session state for storing cleaned data
if "cleaned_data" not in st.session_state:
    st.session_state.cleaned_data = {}

# Process uploaded files
if uploaded_files:
    for file in uploaded_files:
        file_name = file.name
        file_ext = os.path.splitext(file_name)[-1].lower()
        file_size = file.getbuffer().nbytes / 1024  # ✅ Fixed size calculation

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file, engine="openpyxl")
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # Store the original dataframe in session state if not already stored
        if file_name not in st.session_state.cleaned_data:
            st.session_state.cleaned_data[file_name] = df.copy()

        # Use the stored dataframe
        df = st.session_state.cleaned_data[file_name]

        # Display file details
        st.write(f"**File Name:** {file_name}")
        st.write(f"**File Size:** {file_size:.2f} KB")

        # Show Data Preview
        st.write("🔍 Preview the Head of Dataframe")
        st.dataframe(df.head())

        # ✅ Data Cleaning Section with Checkbox
        st.subheader("🛠️ Data Cleaning Options")
        show_cleaning = st.checkbox(f"Enable Data Cleaning for {file_name}")

        if show_cleaning:
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {file_name}", key=f"dup_{file_name}"):
                    df.drop_duplicates(inplace=True)
                    st.session_state.cleaned_data[file_name] = df  # Update session state
                    st.success("✅ Duplicates Removed!")

            with col2:
                if st.button(f"Fill Missing Values for {file_name}", key=f"fill_{file_name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.session_state.cleaned_data[file_name] = df  # Update session state
                    st.success("✅ Missing Values have been Filled!")

        # Select Columns to Convert
        st.subheader("🎯 Select Columns to Convert")
        if not df.empty:  # Ensure dataframe exists
            columns = st.multiselect(f"Choose Columns for {file_name}", df.columns, default=list(df.columns))
            if columns:
                df = df[columns]

        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show Visualization for {file_name}"):
            st.bar_chart(df.select_dtypes(include='number').iloc[:, :2])


        # Convert the File -> CSV to Excel
        st.subheader("🔄 Conversion Options")
        conversion_type = st.radio(f"Convert {file_name} to:", ["CSV", "Excel"], key=file_name)
        if st.button(f"Convert {file_name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                new_file_name = file_name.replace(file_ext, ".csv")
                mime_type = "text/csv"

            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False, engine='openpyxl')
                new_file_name = file_name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            buffer.seek(0)

            # Download Button
            st.download_button(
                label=f"⬇️ Download {new_file_name} as {conversion_type}",
                data=buffer,
                file_name=new_file_name,
                mime=mime_type
            )

st.success("🎉 All files processed")


