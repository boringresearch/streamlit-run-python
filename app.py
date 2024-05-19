import streamlit as st
from code_editor import code_editor
import subprocess
import sys
import json

# Function to capture the output of code execution
def run_python_code(code):
    try:
        # Running the code as a separate process
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
        output = result.stdout
        error = ""
    except subprocess.CalledProcessError as e:
        output = e.stdout
        error = e.stderr
    return output, error

# Default code to display in the code editor
default_code = """




"""

custom_btns = [
    {
    "name": "Run",
        "feather": "Play",
        "primary": True,
        "hasText": True,
        "showWithIcon": True,
        "commands": ["submit"],
        "style": {"bottom": "0.44rem", "right": "0.4rem"}
    }
]
# Code Editor
response = code_editor(allow_reset=True, code=default_code, buttons=custom_btns, height=[10,10])

if response['type'] == "submit" and len(response['text']) != 0:
    output, error = run_python_code(response['text'])
    # Display output
    if output:
        st.success("Output")
        st.code(output, language='python')
    
    # Display error
    if error:
        st.error("Error")
        st.code(error, language='python')
