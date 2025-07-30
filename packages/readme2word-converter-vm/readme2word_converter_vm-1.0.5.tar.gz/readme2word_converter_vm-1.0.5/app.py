import os
import time
from pathlib import Path

import streamlit as st
from converter import ReadmeToWordConverter


def load_custom_css(theme="light"):
    """Load custom CSS for clean black/white theme"""

    if theme == "dark":
        colors = {
            "bg_primary": "#0d1117",
            "bg_secondary": "#161b22",
            "bg_card": "#21262d",
            "text_primary": "#f0f6fc",
            "text_secondary": "#8b949e",
            "border": "#30363d",
            "accent": "#238636",
            "accent_hover": "#2ea043",
        }
    else:
        colors = {
            "bg_primary": "#ffffff",
            "bg_secondary": "#f6f8fa",
            "bg_card": "#ffffff",
            "text_primary": "#24292f",
            "text_secondary": "#656d76",
            "border": "#d0d7de",
            "accent": "#1f883d",
            "accent_hover": "#1a7f37",
        }

    st.markdown(
        f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {{
        background-color: {colors['bg_primary']};
        color: {colors['text_primary']};
        font-family: 'Inter', sans-serif;
    }}

    .theme-toggle {{
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 1000;
        background: {colors['bg_card']};
        border: 1px solid {colors['border']};
        border-radius: 8px;
        padding: 0.5rem;
        cursor: pointer;
    }}

    .app-header {{
        text-align: center;
        padding: 3rem 0 2rem 0;
        margin-bottom: 2rem;
    }}

    .app-title {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {colors['text_primary']};
        margin-bottom: 0.5rem;
    }}

    .app-subtitle {{
        font-size: 1.1rem;
        color: {colors['text_secondary']};
        max-width: 600px;
        margin: 0 auto;
    }}

    .features-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }}

    .feature-card {{
        background: {colors['bg_card']};
        border: 1px solid {colors['border']};
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.2s ease;
    }}

    .feature-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border-color: {colors['accent']};
    }}

    .content-section {{
        background: {colors['bg_card']};
        border: 1px solid {colors['border']};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }}

    .section-title {{
        font-size: 1.25rem;
        font-weight: 600;
        color: {colors['text_primary']};
        margin-bottom: 1rem;
    }}

    .stButton > button {{
        background: {colors['accent']} !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }}

    .stButton > button:hover {{
        background: {colors['accent_hover']} !important;
        transform: translateY(-1px) !important;
    }}

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background-color: {colors['bg_secondary']} !important;
        border: 1px solid {colors['border']} !important;
        border-radius: 8px !important;
        color: {colors['text_primary']} !important;
    }}

    .stFileUploader > div > div {{
        background: {colors['bg_secondary']} !important;
        border: 2px dashed {colors['border']} !important;
        border-radius: 12px !important;
    }}

    .css-1d391kg {{
        background: {colors['bg_secondary']} !important;
        border-right: 1px solid {colors['border']} !important;
    }}

    .status-success {{
        background: rgba(31, 136, 61, 0.1) !important;
        border: 1px solid {colors['accent']} !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
    }}

    .status-error {{
        background: rgba(207, 34, 46, 0.1) !important;
        border: 1px solid #cf222e !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
    }}

    .status-info {{
        background: rgba(9, 105, 218, 0.1) !important;
        border: 1px solid #0969da !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
    }}

    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }}

    .stat-card {{
        background: {colors['bg_card']};
        border: 1px solid {colors['border']};
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }}

    .stat-number {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {colors['accent']};
    }}

    .stat-label {{
        font-size: 0.75rem;
        color: {colors['text_secondary']};
        margin-top: 0.25rem;
        text-transform: uppercase;
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    </style>
    """,
        unsafe_allow_html=True,
    )


def create_theme_toggle():
    """Create theme toggle"""
    if "theme" not in st.session_state:
        st.session_state.theme = "light"

    col1, col2, col3 = st.columns([1, 8, 1])
    with col1:
        if st.button("🌓", help="Toggle theme"):
            st.session_state.theme = (
                "dark" if st.session_state.theme == "light" else "light"
            )
            st.rerun()

    return st.session_state.theme


def create_feature_cards():
    """Create feature cards"""
    st.markdown(
        """
    <div class="features-grid">
        <div class="feature-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">📝</div>
            <div style="font-weight: 600; margin-bottom: 0.5rem;">Smart Conversion</div>
            <div style="color: #656d76; font-size: 0.875rem;">Intelligent Markdown to Word conversion</div>
        </div>
        <div class="feature-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">📊</div>
            <div style="font-weight: 600; margin-bottom: 0.5rem;">Diagram Support</div>
            <div style="color: #656d76; font-size: 0.875rem;">Automatic Mermaid diagram conversion</div>
        </div>
        <div class="feature-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">⚡</div>
            <div style="font-weight: 600; margin-bottom: 0.5rem;">Fast Processing</div>
            <div style="color: #656d76; font-size: 0.875rem;">Quick conversion with progress tracking</div>
        </div>
        <div class="feature-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🎯</div>
            <div style="font-weight: 600; margin-bottom: 0.5rem;">Professional Output</div>
            <div style="color: #656d76; font-size: 0.875rem;">Clean, professional Word documents</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def create_stats_display(stats):
    """Create stats display"""
    st.markdown(
        f"""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number">{stats['headings']}</div>
            <div class="stat-label">Headings</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['tables']}</div>
            <div class="stat-label">Tables</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['code_blocks']}</div>
            <div class="stat-label">Code Blocks</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['mermaid_diagrams']}</div>
            <div class="stat-label">Diagrams</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{stats['images']}</div>
            <div class="stat-label">Images</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(
        page_title="README to Word Converter",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Theme toggle and CSS
    theme = create_theme_toggle()
    load_custom_css(theme)

    # Header
    st.markdown(
        """
    <div class="app-header">
        <h1 class="app-title">📄 README to Word</h1>
        <p class="app-subtitle">Transform your Markdown documentation into professional Word documents</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Features
    create_feature_cards()

    # Initialize converter
    converter = ReadmeToWordConverter()

    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")

        include_toc = st.checkbox("📑 Table of Contents", value=True)
        diagram_style = st.selectbox(
            "🎨 Diagram Theme", ["default", "neutral", "dark", "forest"]
        )

        st.markdown("---")

        debug_mode = st.checkbox("🐛 Debug Mode", value=False)

        if st.button("🧪 Test Mermaid API"):
            test_converter = ReadmeToWordConverter()
            test_converter.set_debug_mode(True)
            with st.spinner("Testing..."):
                success = test_converter.test_mermaid_conversion()
                if success:
                    st.success("✅ API working!")
                else:
                    st.error("❌ API test failed")

        st.markdown("---")
        st.markdown(
            "**💡 Tips:**\n- Use proper Markdown syntax\n- Test diagrams on mermaid.live\n- Enable debug for troubleshooting"
        )

    # Main content
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown(
            '<div class="content-section"><div class="section-title">📝 Input Content</div></div>',
            unsafe_allow_html=True,
        )

        uploaded_file = st.file_uploader("Upload README file", type=["md", "txt"])

        st.markdown("**Or paste content:**")
        readme_content = st.text_area(
            "README Content",
            height=300,
            placeholder="""# My Project

## Features
- ✅ Feature 1
- ✅ Feature 2

```mermaid
graph TD
    A[Start] --> B[End]
```

Ready to convert!""",
        )

        output_filename = st.text_input("📄 Output filename", value="README_converted")

    with col2:
        st.markdown(
            '<div class="content-section"><div class="section-title">👀 Preview & Convert</div></div>',
            unsafe_allow_html=True,
        )

        if uploaded_file is not None:
            readme_content = uploaded_file.read().decode("utf-8")
            with st.expander("📖 File Preview", expanded=True):
                st.code(
                    (
                        readme_content[:500] + "..."
                        if len(readme_content) > 500
                        else readme_content
                    ),
                    language="markdown",
                )

        if readme_content.strip():
            with st.expander("🔍 Markdown Preview"):
                st.markdown(
                    readme_content[:800] + "..."
                    if len(readme_content) > 800
                    else readme_content
                )

        if readme_content.strip():
            st.markdown("### 🚀 Ready to Convert")

            if st.button(
                "🔄 Convert to Word", type="primary", use_container_width=True
            ):
                try:
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    status_text.text("🔄 Processing...")
                    progress_bar.progress(25)
                    time.sleep(0.3)

                    status_text.text("🎨 Converting diagrams...")
                    progress_bar.progress(50)

                    output_dir = Path("output")
                    output_dir.mkdir(exist_ok=True)

                    converter.set_debug_mode(debug_mode)
                    output_path = converter.convert(
                        readme_content, output_filename, include_toc, diagram_style
                    )

                    progress_bar.progress(75)
                    status_text.text("📄 Generating document...")
                    time.sleep(0.3)

                    progress_bar.progress(100)
                    status_text.text("✅ Complete!")

                    st.markdown(
                        """
                    <div class="status-success">
                        <h4>🎉 Conversion Successful!</h4>
                        <p>Your README has been converted to a Word document.</p>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="📥 Download Word Document",
                            data=file.read(),
                            file_name=f"{output_filename}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True,
                        )

                    stats = converter.get_conversion_stats()
                    st.markdown("### 📊 Statistics")
                    create_stats_display(stats)

                    progress_bar.empty()
                    status_text.empty()

                except Exception as e:
                    st.markdown(
                        f"""
                    <div class="status-error">
                        <h4>❌ Error</h4>
                        <p><strong>Error:</strong> {str(e)}</p>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
        else:
            st.markdown(
                """
            <div class="status-info">
                <h4>👆 Getting Started</h4>
                <p>Upload a file or paste content to begin.</p>
                <ul>
                    <li>✅ Markdown syntax support</li>
                    <li>✅ Mermaid diagram conversion</li>
                    <li>✅ Professional formatting</li>
                </ul>
            </div>
            """,
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
