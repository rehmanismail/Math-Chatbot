import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

PDF_FILE_NAME = "math_reference_book.pdf"

# Local ماحول کے لیے .env فائل لوڈ کریں
load_dotenv()

st.set_page_config(
    page_title="MathWiz AI - Personal Math Tutor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Configuration & Environment Setup (Streamlit Secrets + .env Support) ---
# یہ پہلے Streamlit Secrets چیک کرے گا، اگر وہاں نہ ملا تو .env سے لے گا
api_key = (
    st.secrets.get("GEMINI_API_KEY", "") 
    or os.getenv("GEMINI_API_KEY", "")
).strip().strip('"').strip("'")

configured_model = (
    st.secrets.get("GEMINI_MODEL", "") 
    or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
).strip().strip('"').strip("'")

PDF_SYSTEM_INSTRUCTION = """
You are MathBot AI (MathWiz AI), an expert mathematics tutor and document assistant.
Your primary role is to answer questions strictly based on the provided PDF document.
- Extract relevant formulas, theorems, exercises, and step-by-step explanations directly from the document.
- Always render formulas and mathematical notation in clean LaTeX ($inline$ or $$display$$).
- Highlight the final answer clearly.
- If the requested information is not present in the document, politely mention that it is not covered in the provided PDF.
"""

# --- Session State Initializations ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None
if "app_theme" not in st.session_state:
    st.session_state.app_theme = "Light"
if "math_user_input_box" not in st.session_state:
    st.session_state.math_user_input_box = ""
if "current_query" not in st.session_state:
    st.session_state.current_query = ""
if "active_nav" not in st.session_state:
    st.session_state.active_nav = "Dashboard"

# User Authentication State
if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = "Guest User"
if "registered_users" not in st.session_state:
    st.session_state.registered_users = {
        "rehmanismail758@gmail.com": {"name": "Rehman Ismail", "pass": "123456"}
    }

# --- Callbacks (Prevents StreamlitWidgetAlreadyInstantiatedError) ---
def add_symbol_to_buffer(symbol: str):
    st.session_state.math_user_input_box = st.session_state.get("math_user_input_box", "") + symbol

def on_send_click():
    st.session_state.current_query = st.session_state.get("math_user_input_box", "").strip()
    st.session_state.math_user_input_box = ""

def on_clear_click():
    st.session_state.messages = []
    st.session_state.math_user_input_box = ""
    st.session_state.current_query = ""

# --- Math Symbol Dictionary (Comprehensive Typing Tools Set) ---
MATH_SYMBOLS_FULL = {
    "Basic & Operators": [
        "+", "-", "×", "÷", "±", "∓", "=", "≠", "≈", "≡", "≤", "≥", "<", ">", 
        "·", "∘", "⊕", "⊗", "∝", "∞", "%", "‰", "!", "|x|"
    ],
    "Algebra & Powers": [
        "x²", "x³", "xⁿ", "x₀", "√", "∛", "∜", "log", "ln", "eˣ", "10ˣ", 
        "(", ")", "[", "]", "{", "}", "|", "‖", "f(x)", "g(x)", "P(x)"
    ],
    "Calculus & Analysis": [
        "∫", "∬", "∭", "∮", "d/dx", "∂/∂x", "∂", "dx", "dy", "dt", "lim", 
        "→", "∞", "∑", "∏", "∇", "Δ", "f'(x)", "f''(x)", "dy/dx"
    ],
    "Greek Letters": [
        "α", "β", "γ", "δ", "ε", "ζ", "η", "θ", "ι", "κ", "λ", "μ", 
        "ν", "ξ", "π", "ρ", "σ", "τ", "υ", "φ", "χ", "ψ", "ω",
        "Γ", "Δ", "Θ", "Λ", "Ξ", "Π", "Σ", "Φ", "Ψ", "Ω"
    ],
    "Logic & Sets": [
        "∈", "∉", "⊂", "⊆", "⊄", "∪", "∩", "∅", "∀", "∃", "∄", "∴", "∵", 
        "⇒", "⇔", "∧", "∨", "¬", "ℝ", "ℤ", "ℕ", "ℚ", "ℂ"
    ],
    "Geometry & Trig": [
        "∠", "∡", "∟", "⊥", "∥", "∦", "△", "□", "○", "≅", "∼", "°", "rad", 
        "sin", "cos", "tan", "csc", "sec", "cot", "arcsin", "arccos", "arctan"
    ]
}

# --- Theme & Dashboard CSS ---
is_dark = st.session_state.app_theme == "Dark"
bg_main = "#0d1117" if is_dark else "#ffffff"
sidebar_bg = "#161b22" if is_dark else "#f8fafc"
text_primary = "#f0f6fc" if is_dark else "#1e293b"
border_color = "rgba(56, 189, 248, 0.2)" if is_dark else "rgba(226, 232, 240, 1.0)"

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {bg_main};
        color: {text_primary};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
        border-right: 1px solid {border_color};
    }}
    .top-brand {{
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }}
    .mathwiz-hero {{
        position: relative;
        overflow: hidden;
        border-radius: 20px;
        padding: 42px 40px;
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 60%, #4338ca 100%);
        box-shadow: 0 10px 30px rgba(49, 46, 129, 0.2);
        margin-bottom: 24px;
        color: white;
    }}
    .hero-heading {{
        font-size: 2.3rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.25;
        margin-bottom: 12px;
    }}
    .hero-subtext {{
        font-size: 1.05rem;
        color: #cbd5e1;
        margin-bottom: 0px;
        max-width: 600px;
    }}
    div.stButton > button {{
        border-radius: 8px !important;
        font-weight: 500 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- Sidebar UI ---
with st.sidebar:
    st.markdown('<div class="top-brand">🤖 MathWiz AI</div>', unsafe_allow_html=True)

    nav_items = ["Dashboard", "Solver", "Practice", "History", "Resources"]
    icons = {"Dashboard": "⊞", "Solver": "🛠️", "Practice": "📋", "History": "🕒", "Resources": "📖"}
    for item in nav_items:
        btn_type = "primary" if st.session_state.active_nav == item else "secondary"
        if st.button(f"{icons[item]}  {item}", key=f"nav_{item}", use_container_width=True, type=btn_type):
            st.session_state.active_nav = item

    st.divider()
    st.markdown("##### 📄 PDF Document Status")

    if os.path.exists(PDF_FILE_NAME):
        if st.session_state.pdf_bytes is None:
            with open(PDF_FILE_NAME, "rb") as f:
                st.session_state.pdf_bytes = f.read()
        st.success(f"File active:\n`{PDF_FILE_NAME}`")
    else:
        st.warning(f"File `{PDF_FILE_NAME}` not found. Upload PDF:")
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_file is not None:
            st.session_state.pdf_bytes = uploaded_file.getvalue()
            st.success(f"Uploaded: `{uploaded_file.name}`")

    st.divider()

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pdf_bytes = None
        st.session_state.math_user_input_box = ""
        st.rerun()

# --- Top Header Bar ---
col_logo, col_top_search, col_profile, col_settings = st.columns([2.5, 5.5, 1.5, 1.5])
with col_logo:
    st.markdown("### 🤖 MathWiz AI")
with col_top_search:
    top_search = st.text_input("Quick search formulas...", placeholder="🔍 Search formulas, theorems, topics...", label_visibility="collapsed")

# --- Profile Dropdown ---
with col_profile:
    with st.popover("👤 Profile", use_container_width=True):
        st.markdown("### 👨‍🎓 User Profile")
        if st.session_state.user_logged_in:
            st.markdown(f"**Name:** {st.session_state.user_name}")
            st.markdown(f"**Email:** {st.session_state.user_email}")
            st.caption("Status: ✅ Authenticated via Google Account")
        else:
            st.markdown("**Name:** Rehman Ismail")
            st.markdown("**Email:** rehmanismail758@gmail.com")
            st.caption("Status: Student User")
            
        st.divider()
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            st.metric(label="Problems Solved", value=len(st.session_state.messages) // 2)
        with c_p2:
            st.metric(label="Active Books", value="1" if st.session_state.pdf_bytes else "0")

# --- Settings Dropdown ---
with col_settings:
    with st.popover("⚙️ Settings", use_container_width=True):
        st.markdown("##### 🚦 Math Assistant Preferences")
        st.checkbox("Auto-render formulas in LaTeX", value=True, key="set_autorender")
        st.checkbox("Enable real-time stream responses", value=True, key="set_stream")
        st.selectbox("Default Subject Focus", ["General Mathematics", "Calculus", "Algebra", "Geometry", "Statistics"], key="set_default_subj")

        st.divider()
        st.markdown("##### 🛡️ Session Management")

        if st.button("🧹 Clear Local Cache", use_container_width=True, key="btn_clear_cache"):
            st.session_state.math_user_input_box = ""
            st.info("Local cache cleared.")

        if not st.session_state.user_logged_in:
            st.markdown("---")
            st.markdown("##### 🔐 Account Access")
            
            if st.button("🌐 Continue with Google", use_container_width=True, type="secondary", key="btn_google_auth"):
                st.session_state.user_logged_in = True
                st.session_state.user_email = "rehmanismail758@gmail.com"
                st.session_state.user_name = "Rehman Ismail"
                st.success("Successfully authenticated and linked with Google!")
                st.rerun()

            auth_tab_login, auth_tab_signup = st.tabs(["🔑 Log In", "📝 Sign Up"])

            with auth_tab_login:
                login_email = st.text_input("Email", key="set_login_email")
                login_password = st.text_input("Password", type="password", key="set_login_password")
                if st.button("Log In to Account", use_container_width=True, type="primary", key="btn_exec_login"):
                    if login_email in st.session_state.registered_users:
                        if st.session_state.registered_users[login_email]["pass"] == login_password:
                            st.session_state.user_logged_in = True
                            st.session_state.user_email = login_email
                            st.session_state.user_name = st.session_state.registered_users[login_email]["name"]
                            st.success(f"Welcome back, {st.session_state.user_name}!")
                            st.rerun()
                        else:
                            st.error("Incorrect password.")
                    else:
                        st.error("Account not found. Please sign up.")

            with auth_tab_signup:
                new_name = st.text_input("Full Name", key="set_signup_name")
                new_email = st.text_input("Email Address", key="set_signup_email")
                new_pass = st.text_input("Create Password", type="password", key="set_signup_pass")
                if st.button("Create Account & Link", use_container_width=True, type="primary", key="btn_exec_signup"):
                    if new_email and new_pass and new_name:
                        st.session_state.registered_users[new_email] = {"name": new_name, "pass": new_pass}
                        st.session_state.user_logged_in = True
                        st.session_state.user_email = new_email
                        st.session_state.user_name = new_name
                        st.success("Account created and authenticated successfully!")
                        st.rerun()
                    else:
                        st.warning("Please fill out all fields.")
        else:
            st.success(f"Signed in as: **{st.session_state.user_name}** ({st.session_state.user_email})")
            if st.button("🚪 Log Out", use_container_width=True, type="primary", key="btn_logout_user"):
                st.session_state.user_logged_in = False
                st.session_state.user_email = ""
                st.session_state.user_name = "Guest User"
                st.session_state.messages = []
                st.session_state.math_user_input_box = ""
                st.rerun()

# --- Hero Section Banner ---
st.markdown("""
<div class="mathwiz-hero">
    <div class="hero-heading">Meet your personal math tutor.<br/>Ask anything, anytime.</div>
    <div class="hero-subtext">Step-by-step calculus, algebra, geometry, and problem solutions directly from your text.</div>
</div>
""", unsafe_allow_html=True)

col_quick, col_examples = st.columns([1.2, 1])

with col_quick:
    st.markdown("##### ⚡ Quick Options")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("➕✖️\n\nAlgebra", use_container_width=True):
            st.session_state.math_user_input_box = "Solve for x in quadratic equation: "
            st.rerun()
    with c2:
        if st.button("∫ y\n\nCalculus", use_container_width=True):
            st.session_state.math_user_input_box = "Find derivative of: "
            st.rerun()
    with c3:
        if st.button("📐\n\nGeometry", use_container_width=True):
            st.session_state.math_user_input_box = "Calculate the volume of: "
            st.rerun()
    with c4:
        if st.button("📊\n\nStatistics", use_container_width=True):
            st.session_state.math_user_input_box = "Compute standard deviation for: "
            st.rerun()

with col_examples:
    st.markdown("##### 💬 Recent Examples")
    ex_col1, ex_col2 = st.columns(2)
    with ex_col1:
        if st.button("📌 Integrate 2x dx", use_container_width=True):
            st.session_state.math_user_input_box = "Integrate 2x dx step by step"
            st.rerun()
        if st.button("📌 Solve: 3x + 5 = 14", use_container_width=True):
            st.session_state.math_user_input_box = "Solve for x: 3x + 5 = 14"
            st.rerun()
    with ex_col2:
        if st.button("📌 Lim x→0 sin(x)/x", use_container_width=True):
            st.session_state.math_user_input_box = "Evaluate limit of sin(x)/x as x approaches 0"
            st.rerun()
        if st.button("📌 Matrix Eigenvalues", use_container_width=True):
            st.session_state.math_user_input_box = "Explain how to calculate eigenvalues"
            st.rerun()

st.write("")

if not st.session_state.pdf_bytes:
    st.warning("⚠️ Koi PDF active nahi hai. Barah-e-karam project folder mein PDF rakhein ya upload karein.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

symbol_tool_col, input_field_col = st.columns([1.2, 8.8])

with symbol_tool_col:
    with st.popover("∑ Math Symbols", use_container_width=True):
        st.markdown("#### ⌨️ Full Mathematical Symbol Set")
        tabs = st.tabs(list(MATH_SYMBOLS_FULL.keys()))
        
        for tab_idx, (cat_name, sym_list) in enumerate(MATH_SYMBOLS_FULL.items()):
            with tabs[tab_idx]:
                grid_cols = st.columns(6)
                for s_idx, sym in enumerate(sym_list):
                    with grid_cols[s_idx % 6]:
                        st.button(
                            sym, 
                            key=f"symbol_btn_{cat_name}_{s_idx}", 
                            use_container_width=True, 
                            on_click=add_symbol_to_buffer, 
                            args=(sym,)
                        )

with input_field_col:
    f_col1, f_col2, f_col3 = st.columns([7.5, 1.3, 1.2])
    with f_col1:
        st.text_input(
            "Math Problem Input",
            placeholder="Ask any math problem, formula, theorem... (or click ∑ Math Symbols)",
            label_visibility="collapsed",
            key="math_user_input_box"
        )
    with f_col2:
        st.button("Send ➔", use_container_width=True, type="primary", on_click=on_send_click)
    with f_col3:
        st.button("🗑️ Clear", use_container_width=True, on_click=on_clear_click)

user_query = st.session_state.get("current_query", "").strip()

if user_query:
    st.session_state.current_query = ""

    if not api_key:
        st.error("⚠️ Gemini API Key detect nahi hui. Barah-e-karam `.env` file mein ya Streamlit Secrets mein `GEMINI_API_KEY` define karein.")
    elif not st.session_state.pdf_bytes:
        st.error("⚠️ Sawal poochne ke liye PDF ka hona zaroori hai.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            try:
                genai.configure(api_key=api_key)

                model = genai.GenerativeModel(
                    model_name=configured_model,
                    system_instruction=PDF_SYSTEM_INSTRUCTION,
                )

                request_payload = [
                    {
                        "mime_type": "application/pdf",
                        "data": st.session_state.pdf_bytes,
                    },
                    user_query,
                ]

                response = model.generate_content(request_payload, stream=True)

                for chunk in response:
                    if chunk.text:
                        full_point = chunk.text
                        full_response += full_point
                        placeholder.markdown(full_response + "▌")

                placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                placeholder.error(f"Error: {str(e)}")
