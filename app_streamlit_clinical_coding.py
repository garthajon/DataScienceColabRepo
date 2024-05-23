import streamlit as st
from vertexai.language_models import TextGenerationModel
from google.cloud import aiplatform
import pandas as pd
import tensorflow as tf
import os
import tempfile
from six.moves import urllib

# Initialize the Vertex AI SDK
aiplatform.init(project='YOUR_PROJECT_ID', location='us-central1')

# Create the Vertex AI model
generation_model = TextGenerationModel.from_pretrained("text-bison@001")

# Load and preprocess the clinical coding sample dataframe
DATA_DIR = os.path.join(tempfile.gettempdir(), 'census_data')
tf.io.gfile.makedirs(DATA_DIR)

DATA_URL = 'https://raw.githubusercontent.com/garthajon/DataScienceColabRepo/main'
TRAINING_FILE = 'NCCS_CLINICAL_CODING_EXAMPLES_NOHEAD.csv'
TRAINING_URL = f'{DATA_URL}/{TRAINING_FILE}'

training_file_path = os.path.join(DATA_DIR, TRAINING_FILE)
temp_file, _ = urllib.request.urlretrieve(TRAINING_URL)
with tf.io.gfile.GFile(temp_file, 'r') as temp_file_object:
    with tf.io.gfile.GFile(training_file_path, 'w') as file_object:
        for line in temp_file_object:
            line = line.strip()
            line = line.replace(', ', ',')
            if not line or ',' not in line:
                continue
            if line[-1] == '.':
                line = line[:-1]
            line += '\n'
            file_object.write(line)
tf.io.gfile.remove(temp_file)

CSV_COLUMNS = [
    'IDFIELD', 'NCCS_CLINICAL_TEXT', 'NCCS_PRIM_DIAG',
    'NCCS_PRIM_DIAG_DESC', 'NCCS_SEC_DIAG', 'NCCS_SEC_DIAG_DESC',
    'NCCS_DOC_VERSION', 'PAGE', 'NOTES'
]

df = pd.read_csv(training_file_path, names=CSV_COLUMNS, na_values='?')
df['Diag1_Derived'] = ''
df['Diag2_Derived'] = ''

def generate_icd_codes(text):
    prompt = f"""
    Output a notation's primary and secondary ICD10 code.

    Notation: Patient is admitted with cellulitis of the leg and a severe leg ulcer
    ICD10 codes: L97.X, L03.1

    Notation: {text}
    ICD10 codes:
    """
    var_output = generation_model.predict(prompt=prompt, max_output_tokens=256).text
    prim_diag = var_output[0:5]
    sec_diag = var_output[7:]
    return prim_diag, sec_diag

# Streamlit app interface
st.title("Medical Issue to ICD-10 Code Converter")

issue = st.text_input("Enter the medical issue description:")

if st.button("Get ICD-10 Codes"):
    if issue:
        prim_diag, sec_diag = generate_icd_codes(issue)
        st.write(f"Primary Diagnosis ICD-10 Code: {prim_diag}")
        st.write(f"Secondary Diagnosis ICD-10 Code: {sec_diag}")
    else:
        st.write("Please enter a medical issue description.")

# Display the dataframe for reference
st.write("Sample Clinical Coding Data:")
st.dataframe(df)

# Ensure Streamlit listens on the correct port
if __name__ == '__main__':
    st._is_running_with_streamlit = True
    from streamlit.cli import main
    main(prog_name='streamlit', args=['run', 'app.py', '--server.port=8080'])
