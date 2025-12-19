import streamlit as st
import requests
import json
import os
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
from typing import List, Dict, Any

# Configure Streamlit page
st.set_page_config(
    page_title="QA Agent - Test Case & Script Generator",
    page_icon="🤖",
    layout="wide"
)

# API base URL
API_BASE_URL = "http://localhost:8000"

def main():
    st.title("🤖 Autonomous QA Agent")
    st.markdown("Generate test cases and Selenium scripts from documentation")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["📁 Document Upload", "🧠 Knowledge Base", "📝 Test Case Generation", "🔧 Script Generation"]
    )
    
    if page == "📁 Document Upload":
        document_upload_page()
    elif page == "🧠 Knowledge Base":
        knowledge_base_page()
    elif page == "📝 Test Case Generation":
        test_case_generation_page()
    elif page == "🔧 Script Generation":
        script_generation_page()

def document_upload_page():
    st.header("📁 Document Upload")
    st.markdown("Upload support documents and HTML files to build the knowledge base.")
    
    # File upload section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Support Documents")
        uploaded_files = st.file_uploader(
            "Upload documentation files",
            type=['md', 'txt', 'json', 'pdf'],
            accept_multiple_files=True,
            help="Upload product specs, UI/UX guides, API docs, etc."
        )
        
        if uploaded_files:
            st.success(f"Selected {len(uploaded_files)} files")
            for file in uploaded_files:
                st.write(f"- {file.name} ({file.type})")
    
    with col2:
        st.subheader("HTML Content")
        html_input_method = st.radio(
            "Choose input method:",
            ["Upload HTML file", "Paste HTML content"]
        )
        
        html_content = ""
        if html_input_method == "Upload HTML file":
            html_file = st.file_uploader(
                "Upload checkout.html",
                type=['html'],
                help="Upload the target web page HTML file"
            )
            if html_file:
                html_content = html_file.read().decode('utf-8')
                st.success("HTML file uploaded successfully")
        else:
            html_content = st.text_area(
                "Paste HTML content:",
                height=200,
                placeholder="<html>...</html>"
            )
    
    # Process and upload documents
    if st.button("🚀 Process Documents", type="primary"):
        if not uploaded_files:
            st.error("Please upload at least one support document")
            return
        
        if not html_content:
            st.error("Please provide HTML content")
            return
        
        with st.spinner("Processing documents..."):
            try:
                # Upload documents to API
                files_data = []
                for file in uploaded_files:
                    files_data.append(('files', (file.name, file.read(), file.type)))
                
                response = requests.post(f"{API_BASE_URL}/upload-documents", files=files_data)
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.uploaded_docs = result['documents']
                    st.session_state.html_content = html_content
                    
                    st.success(f"✅ Processed {len(result['documents'])} documents successfully!")
                    
                    # Show document summary
                    with st.expander("📋 Document Summary"):
                        for doc in result['documents']:
                            st.write(f"**{doc['filename']}**")
                            st.write(f"- Type: {doc['content_type']}")
                            st.write(f"- Chunks: {doc['metadata']['chunk_count']}")
                            st.write("---")
                else:
                    st.error(f"Error processing documents: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure the FastAPI server is running on port 8000.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

def knowledge_base_page():
    st.header("🧠 Knowledge Base")
    st.markdown("Build and manage the vector database for document retrieval.")
    
    if not st.session_state.uploaded_docs:
        st.warning("⚠️ No documents uploaded yet. Please upload documents first.")
        return
    
    # Show uploaded documents
    st.subheader("📚 Uploaded Documents")
    for doc in st.session_state.uploaded_docs:
        with st.expander(f"📄 {doc['filename']}"):
            st.write(f"**Type:** {doc['content_type']}")
            st.write(f"**Chunks:** {doc['metadata']['chunk_count']}")
            st.write("**Preview:**")
            preview_text = doc['text_content'][:500] + "..." if len(doc['text_content']) > 500 else doc['text_content']
            st.text(preview_text)
    
    # Build knowledge base
    if st.button("🔨 Build Knowledge Base", type="primary"):
        with st.spinner("Building knowledge base..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/build-knowledge-base",
                    json=st.session_state.uploaded_docs
                )
                
                if response.status_code == 200:
                    st.session_state.knowledge_base_built = True
                    st.success("✅ Knowledge base built successfully!")
                    st.balloons()
                else:
                    st.error(f"Error building knowledge base: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure the FastAPI server is running.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Knowledge base status
    if st.session_state.knowledge_base_built:
        st.success("✅ Knowledge base is ready!")
    else:
        st.info("ℹ️ Knowledge base not built yet.")

def test_case_generation_page():
    st.header("📝 Test Case Generation")
    st.markdown("Generate comprehensive test cases based on your documentation.")
    
    if not st.session_state.knowledge_base_built:
        st.warning("⚠️ Knowledge base not built yet. Please build it first.")
        return
    
    # Query input
    st.subheader("🔍 Test Case Query")
    
    # Predefined queries
    predefined_queries = [
        "Generate test cases for discount code feature",
        "Generate test cases for form validation",
        "Generate test cases for shopping cart functionality",
        "Generate test cases for payment process",
        "Generate test cases for shipping options",
        "Generate comprehensive test suite for all features"
    ]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        query_method = st.radio(
            "Choose query method:",
            ["Use predefined query", "Enter custom query"]
        )
        
        if query_method == "Use predefined query":
            selected_query = st.selectbox("Select a query:", predefined_queries)
            query = selected_query
        else:
            query = st.text_area(
                "Enter your test case generation query:",
                placeholder="e.g., Generate test cases for user registration form",
                height=100
            )
    
    with col2:
        st.subheader("💡 Tips")
        st.info("""
        **Good queries:**
        - Focus on specific features
        - Mention positive/negative cases
        - Reference documentation elements
        
        **Examples:**
        - "Test discount code validation"
        - "Form error handling cases"
        - "Payment method selection"
        """)
    
    # Generate test cases
    if st.button("🎯 Generate Test Cases", type="primary"):
        if not query.strip():
            st.error("Please enter a query")
            return
        
        with st.spinner("Generating test cases..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/generate-test-cases",
                    json={"query": query}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.generated_test_cases = result['test_cases']
                    
                    st.success(f"✅ Generated {len(result['test_cases'])} test cases!")
                    
                else:
                    st.error(f"Error generating test cases: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure the FastAPI server is running.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Display generated test cases
    if st.session_state.generated_test_cases:
        st.subheader("📋 Generated Test Cases")
        
        for i, test_case in enumerate(st.session_state.generated_test_cases):
            with st.expander(f"🧪 {test_case['test_id']}: {test_case['test_scenario']}", expanded=i==0):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Feature:** {test_case['feature']}")
                    st.write(f"**Type:** {test_case.get('test_type', 'N/A')}")
                    st.write(f"**Expected Result:** {test_case['expected_result']}")
                    st.write(f"**Grounded In:** {test_case['grounded_in']}")
                
                with col2:
                    if 'steps' in test_case:
                        st.write("**Test Steps:**")
                        for step_num, step in enumerate(test_case['steps'], 1):
                            st.write(f"{step_num}. {step}")
                
                # JSON view
                with st.expander("📄 View JSON"):
                    st.json(test_case)

def script_generation_page():
    st.header("🔧 Selenium Script Generation")
    st.markdown("Convert test cases into executable Selenium Python scripts.")
    
    if not st.session_state.generated_test_cases:
        st.warning("⚠️ No test cases generated yet. Please generate test cases first.")
        return
    
    if not st.session_state.html_content:
        st.warning("⚠️ No HTML content available. Please upload HTML content first.")
        return
    
    # Test case selection
    st.subheader("🎯 Select Test Case")
    
    test_case_options = [
        f"{tc['test_id']}: {tc['test_scenario']}" 
        for tc in st.session_state.generated_test_cases
    ]
    
    selected_index = st.selectbox(
        "Choose a test case to convert:",
        range(len(test_case_options)),
        format_func=lambda x: test_case_options[x]
    )
    
    selected_test_case = st.session_state.generated_test_cases[selected_index]
    
    # Show selected test case details
    with st.expander("📋 Selected Test Case Details", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**ID:** {selected_test_case['test_id']}")
            st.write(f"**Feature:** {selected_test_case['feature']}")
            st.write(f"**Scenario:** {selected_test_case['test_scenario']}")
        
        with col2:
            st.write(f"**Expected Result:** {selected_test_case['expected_result']}")
            st.write(f"**Type:** {selected_test_case.get('test_type', 'N/A')}")
            st.write(f"**Source:** {selected_test_case['grounded_in']}")
    
    # Generate script
    if st.button("⚡ Generate Selenium Script", type="primary"):
        with st.spinner("Generating Selenium script..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/generate-script",
                    json={
                        "test_case": selected_test_case,
                        "html_content": st.session_state.html_content
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    script_content = result['script']
                    
                    st.success("✅ Selenium script generated successfully!")
                    
                    # Display script
                    st.subheader("🐍 Generated Python Script")
                    st.code(script_content, language='python')
                    
                    # Download button
                    script_filename = f"test_{selected_test_case['test_id'].lower().replace('-', '_')}.py"
                    st.download_button(
                        label="📥 Download Script",
                        data=script_content,
                        file_name=script_filename,
                        mime="text/x-python"
                    )
                    
                    # Usage instructions
                    with st.expander("📖 Usage Instructions"):
                        st.markdown(f"""
                        ### How to run this script:
                        
                        1. **Save the script** as `{script_filename}`
                        
                        2. **Install dependencies:**
                        ```bash
                        pip install selenium
                        ```
                        
                        3. **Install ChromeDriver:**
                        - Download from: https://chromedriver.chromium.org/
                        - Add to your PATH
                        
                        4. **Update the HTML path** in the script:
                        ```python
                        self.driver.get("file:///path/to/checkout.html")
                        ```
                        
                        5. **Run the script:**
                        ```bash
                        python {script_filename}
                        ```
                        
                        ### Notes:
                        - Remove `--headless` option to see the browser in action
                        - Adjust selectors if your HTML structure differs
                        - Add more assertions based on your specific requirements
                        """)
                
                else:
                    st.error(f"Error generating script: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure the FastAPI server is running.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Sidebar status
def show_sidebar_status():
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Status")
    
    # Document upload status
    if st.session_state.uploaded_docs:
        st.sidebar.success(f"✅ {len(st.session_state.uploaded_docs)} docs uploaded")
    else:
        st.sidebar.error("❌ No documents uploaded")
    
    # Knowledge base status
    if st.session_state.knowledge_base_built:
        st.sidebar.success("✅ Knowledge base ready")
    else:
        st.sidebar.error("❌ Knowledge base not built")
    
    # Test cases status
    if st.session_state.generated_test_cases:
        st.sidebar.success(f"✅ {len(st.session_state.generated_test_cases)} test cases")
    else:
        st.sidebar.error("❌ No test cases generated")
    
    # HTML content status
    if st.session_state.html_content:
        st.sidebar.success("✅ HTML content loaded")
    else:
        st.sidebar.error("❌ No HTML content")

if __name__ == "__main__":
    # Initialize session state first
    if 'knowledge_base_built' not in st.session_state:
        st.session_state.knowledge_base_built = False
    if 'uploaded_docs' not in st.session_state:
        st.session_state.uploaded_docs = []
    if 'generated_test_cases' not in st.session_state:
        st.session_state.generated_test_cases = []
    if 'html_content' not in st.session_state:
        st.session_state.html_content = ""
    
    show_sidebar_status()
    main()
