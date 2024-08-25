import streamlit as st
from streamlit import session_state as state
from code_editor import code_editor
import subprocess
import sys
import ast
import time

# Function to capture the output of code execution
def run_python_code(code):
    try:
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
        output = result.stdout
        error = ""
    except subprocess.CalledProcessError as e:
        output = e.stdout
        error = e.stderr
    return output, error

# Function to extract imports and variable assignments from code
def extract_imports_and_vars(code):
    tree = ast.parse(code)
    imports = []
    vars = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(ast.unparse(node))
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    vars.append(f"{target.id} = {ast.unparse(node.value)}")
    return imports, vars

# Initialize session state
if 'imports' not in state:
    state.imports = []
if 'vars' not in state:
    state.vars = []
if 'last_activity' not in state:
    state.last_activity = time.time()

# Function to check and reset state if timeout occurred
def check_timeout():
    timeout = 300  # 5 minutes timeout
    if time.time() - state.last_activity > timeout:
        state.imports = []
        state.vars = []
    state.last_activity = time.time()

# Call check_timeout at the beginning of each Streamlit run
check_timeout()

# Display current imports and variables
st.sidebar.header("Current State")
st.sidebar.subheader("Imports")
for imp in state.imports:
    st.sidebar.code(imp)
st.sidebar.subheader("Variables")
for var in state.vars:
    st.sidebar.code(var)

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
response = code_editor(
    allow_reset=True,
    code="# Copy & Paste code here",  # Start with an empty editor
    buttons=custom_btns,
    height=[10, 10],
    props={"enableBasicAutocompletion": True, "enableLiveAutocompletion": False, "enableSnippets": False}
)

if response['type'] == "submit" and len(response['text']) != 0:
    new_code = response['text']
    
    # Extract imports and variable assignments
    new_imports, new_vars = extract_imports_and_vars(new_code)
    
    # Update session state
    state.imports = list(set(state.imports + new_imports))
    state.vars = list(set(state.vars + new_vars))
    
    # Run the entire new code along with saved imports and vars
    full_code = "\n".join(state.imports + state.vars + [new_code])
    output, error = run_python_code(full_code)
    
    # Display output
    if output:
        st.code(output, language='python')
    
    # Display error
    if error:
        st.error("Error")
        st.code(error, language='python')
    
    # Update last activity time
    state.last_activity = time.time()
