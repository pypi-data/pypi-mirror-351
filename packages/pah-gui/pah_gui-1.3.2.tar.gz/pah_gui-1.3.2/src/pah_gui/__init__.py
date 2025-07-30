from pathlib import Path
import tempfile
from pah_core import PAH
import streamlit as st


def run():
    st.title("PDF Auto Highlighter (pah)")

    input_pdf = st.file_uploader(
        "Upload a PDF file",
        type=["pdf"],
        help="Select a PDF file to highlight.",
    )
    llm_model = st.text_input(
        "LLM Model",
        help="Enter the LLM model to use for highlighting. \nSee https://litellm.com/docs/models for available models",
    )
    llm_api_key = st.text_input(
        "LLM API Key",
        type="password",
        help="Enter your LLM API key if required.",
    )
    log_level = "WARNING"

    run_button = st.button("Run Highlighting", disabled=not input_pdf or not llm_model)
    if run_button and input_pdf is not None:
        with st.spinner("Processing..."):
            temp_dir = Path(tempfile.gettempdir())
            input_pdf_path = temp_dir / "input.pdf"
            with open(input_pdf_path, "wb") as f:
                f.write(input_pdf.getbuffer())
            output_pdf_path = temp_dir / "output.pdf"

            pah = PAH(
                input_pdf_path=input_pdf_path,
                output_pdf_path=output_pdf_path,
                llm_model=llm_model,
                llm_api_key=llm_api_key,
                log_level=log_level,
            )
            pah.highlight()

        st.success("Highlighting completed!")
        st.download_button(
            label="Download Highlighted PDF",
            data=output_pdf_path.read_bytes(),
            file_name="highlighted_output.pdf",
            mime="application/pdf",
        )
