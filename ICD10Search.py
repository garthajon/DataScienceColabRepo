import pandas as pd
import streamlit as st
import re
 

url = f"https://raw.githubusercontent.com/AMohabeer/DataScienceColabRepo/main/ICD-10_Medical_Code.csv" 
df = pd.read_csv(url, dtype=str, header=None).fillna("")

# Show the dataframe  
#st.write(df)

st.title('Find ICD10 Codes & Descriptions')

# Use a text_input to get the keywords to filter the dataframe
text_search1 = st.text_input("Enter a single keyword or ICD10 code (without dots)", value="")

# Filter the dataframe
m1 = df[2].str.contains(text_search1, flags=re.IGNORECASE, regex=True)   
m2 = df[1].str.contains(text_search1, flags=re.IGNORECASE, regex=True)  
df_search = df[m1 | m2]

# Show the results, if you have a text_search
#if text_search1:
#    st.write(df_search)  
    
N_results_per_row = 1
if text_search1:
    for n_row, row in df_search.reset_index().iterrows():
        i = n_row
        if i==0:
            st.write("---")
            cols = st.columns(N_results_per_row)
        with cols[n_row%N_results_per_row]:
            st.markdown(f" ICD10 Code: {row[1].strip()} - {row[2].strip()}") 