import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Set up our App
st.set_page_config(page_title="💿 Data Sweeper", page_icon=":cd:", layout="wide")

# Add a title
st.title("Data Sweeper")

# Add a description
st.write("This app allows you to sweep data from an Excel file and save it as a CSV file.")

# Add a file uploader
uploaded_file = st.file_uploader("Upload your files (Excel, CSV)", type=["xlsx", "csv"], accept_multiple_files=True)

if uploaded_file:
    for file in uploaded_file:
        file_ext = os.path.splitext(file.name)[-1].lower()
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error("Unsupported file type:(file_ext)")
            continue

        #Display info about the file
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size/1024}")

        #Display the first 5 rows of the dataframe
        st.write("**Preview the Head of the Dataframe:")
        st.dataframe(df.head())

        #Options for data cleaning
        st.subheader('Data Cleaning Options')
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                #Remove duplicate rows
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates removed successfully")

            with col2:
                if st.button(f"Fill Missing values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    df[numeric_cols] =df [numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Missing values filled successfully")

            #Choose specific Columns to keep or Convert
            st.subheader("Select Columns to Convert")
            columns = st.multiselect("Choose Coloums for {file.name}", df.columns, default=df.columns)
            df = df[columns]

            #Create Some Visualizations
            st.subheader("Data Visualizations")
            if st.checkbox(f"Show Visualizations for {file.name}"):
                st.bar_chart(df.select_dtypes(include='number').iloc[:, :2])

            #Convert the File ~ CSV or Excel
            st.subheader(f"Conversion Options")
            conversion_type = st.radio(f"Convert {file.name} to:", ("CSV", "Excel"), key=file.name)
            if st.button(f"Convert {file.name}"):
                buffer = BytesIO()
                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"

                elif conversion_type == "Excel":
                    df.to_excel(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                buffer.seek(0)

                #Download Button
                st.download_button(
                    label=f"⬇ Click to Download {file.name} as {conversion_type}",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )
            
            #Multi-File Merge Option
            st.subheader("Multi-File Merge Option")
            if st.checkbox("Merge Multiple Files"):
                merge_files = st.file_uploader("Upload files to merge", type=["xlsx", "csv"], accept_multiple_files=True)
                if st.button("Merge Files") and merge_files is not None:
                    all_dataframes = []
                    for file in merge_files:
                        file_ext = os.path.splitext(file.name)[-1].lower()
                        if file_ext == ".csv":
                            df = pd.read_csv(file)
                        elif file_ext == ".xlsx":
                            df = pd.read_excel(file)
                        else:
                            st.error(f"Unsupported file type: {file_ext}")
                            continue
                        all_dataframes.append(df)

                    merged_df = pd.concat(all_dataframes, ignore_index=True)
                    
                    st.write("Merged DataFrame:")
                    st.dataframe(merged_df)

                    #Download Merged File
                    buffer = BytesIO()
                    merged_df.to_csv(buffer, index=False)
                    file_name = "merged_file.csv"
                    mime_type = "text/csv"

                    st.download_button(
                        label=f"⬇ Click to Download Merged File",
                        data=buffer,
                        file_name=file_name,
                        mime=mime_type
                    )

            # Column Renaming Helper       
            st.subheader("Column Renaming Helper")
            if st.checkbox("Rename Columns"):
                col_mapping = {}
                for col in df.columns:
                    new_name = st.text_input(f"Enter new name for {col}", value=col)
                    col_mapping[col] = new_name

                df.rename(columns=col_mapping, inplace=True)
                st.write("Columns renamed successfully")

                #Download the Renamed File
                buffer = BytesIO()
                df.to_csv(buffer, index=False)
                file_name = "renamed_file.csv"
                mime_type = "text/csv"

                st.download_button(
                    label=f"⬇ Click to Download Renamed File",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )
                
            # Data Filtering and Sorting
            st.subheader("Data Filtering and Sorting")
            if st.checkbox("Filter and Sort Data"):
                # Column Filtering
                col_filter = st.multiselect("Select Columns to Filter", df.columns, default=df.columns, key=f"colfilter_{file.name}")
                if col_filter:
                    df = df[col_filter]

                # Filtering Options (Only Text Filter)
                text_col = st.selectbox("Select Text Column", df.columns, key=f"textcol_{file.name}")
                text_filter = st.text_input("Enter Text to Filter", key=f"textfilter_{file.name}")
                if text_filter:
                    df = df[df[text_col].str.contains(text_filter, case=False, na=False)]

                # Sorting Options
                sort_type = st.radio("Select Sort Type", ("Ascending", "Descending"), key=f"sorttype_{file.name}")
                sort_column = st.selectbox("Select Column to Sort", df.columns, key=f"sortcol_{file.name}")
                ascending = sort_type == "Ascending"
                df = df.sort_values(by=sort_column, ascending=ascending)

                st.write("Sorted DataFrame:")
                st.dataframe(df)

                # Download the Sorted File
                buffer = BytesIO()
                df.to_csv(buffer, index=False)
                file_name = "sorted_file.csv"
                mime_type = "text/csv"

                st.download_button(
                    label="⬇ Click to Download Sorted File",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )

                st.success("🎉All Files Processed Successfully!")