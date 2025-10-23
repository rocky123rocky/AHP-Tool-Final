
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
import json
from ahp_backend import *

st.set_page_config(page_title="COPP AHP Military Planner", layout="wide")

FORCES_FILE = "forces.json"
AHP_TEAM_FILE = "ahp_team.json"

def load_forces():
    if os.path.exists(FORCES_FILE):
        with open(FORCES_FILE, "r") as f:
            return json.load(f)
    return []  # No default forces

def save_forces(sides):
    with open(FORCES_FILE, "w") as f:
        json.dump(sides, f)

def load_ahp_team():
    if os.path.exists(AHP_TEAM_FILE):
        try:
            with open(AHP_TEAM_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return [
        {"name": "Cdr A Kumar", "role": "Lead Architect"},
        {"name": "Lt B Singh", "role": "Backend Developer"},
        {"name": "Lt C Sharma", "role": "Frontend Developer"},
        {"name": "Lt D Patel", "role": "Testing & QA"}
    ]

def save_ahp_team(team_data):
    with open(AHP_TEAM_FILE, "w") as f:
        json.dump(team_data, f, indent=2)

SIDES = load_forces()
FORCE_COLORS = {
    "blue": "#1e3a8a",
    "red": "#7f1d1d",
    "yellow": "#facc15",
    "orange": "#fb923c",
    "pink": "#ec4899",
    "magenta": "#a21caf",
    "green": "#22c55e",
    "purple": "#8b5cf6",
    "teal": "#14b8a6",
    "cyan": "#06b6d4",
    "lime": "#84cc16",
    "amber": "#f59e42",
    "indigo": "#6366f1",
    "gray": "#64748b",
    "brown": "#a16207",
    "olive": "#a3e635",
    "maroon": "#be123c",
    "silver": "#e5e7eb",
    "gold": "#fbbf24",
    "navy": "#0f172a"
}

# --- Custom CSS Injection ---
def inject_css(role):
    accent = FORCE_COLORS.get(role, "#0f172a")
    # Indian Navy themed background with tricolor inspiration
    bg = "linear-gradient(135deg, #ff9933 0%, #ffffff 20%, #ffffff 80%, #138808 100%)"
    st.markdown(f"""
<style>
body {{ background: {bg}; }}
.tricolor-strip {{
    height: 6px;
    background: linear-gradient(to right, #ff9933 33.33%, #ffffff 33.33%, #ffffff 66.66%, #138808 66.66%);
    width: 100%;
    margin: 10px 0;
}}
.footer {{ 
    background: linear-gradient(45deg, #000080, #1e40af); 
    color: #fff; 
    text-align: center; 
    padding: 12px; 
    font-size: 18px; 
    font-weight: bold;
    border-top: 3px solid #fbbf24;
}}
.sidebar .sidebar-content {{ 
    background: linear-gradient(180deg, {accent} 0%, #001122 100%) !important; 
    border-right: 3px solid #fbbf24;
}}
.sidebar .sidebar-content .block-container {{
    padding-top: 2rem;
    padding-bottom: 2rem;
}}
.stRadio > div {{
    background: rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 8px 12px;
    margin: 4px 0;
    border: 1px solid rgba(251, 191, 36, 0.3);
    backdrop-filter: blur(10px);
    display: flex !important;
    align-items: center !important;
}}
.stRadio > div:hover {{
    background: rgba(251, 191, 36, 0.2);
    border-color: #fbbf24;
    transform: translateX(5px);
    transition: all 0.3s ease;
}}
.stRadio > div > label {{
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 4px 8px !important;
    display: flex !important;
    align-items: center !important;
    border-radius: 8px !important;
    width: 100% !important;
}}
.stRadio > div > label > span {{
    margin-left: 8px !important;
}}
.stRadio > div > label:hover {{
    background: rgba(255, 255, 255, 0.1) !important;
}}
.stRadio > div[data-checked="true"] {{
    background: linear-gradient(45deg, #fbbf24, #f59e42) !important;
    border-color: #fbbf24 !important;
    box-shadow: 0 4px 12px rgba(251, 191, 36, 0.4);
}}
.stRadio > div[data-checked="true"] > label {{
    color: #000080 !important;
    font-weight: 700 !important;
}}
.stRadio input[type="radio"] {{
    margin-right: 8px !important;
}}

.role-badge {{
    display: inline-block;
    background: linear-gradient(45deg, #fbbf24, #f59e42);
    color: #000080;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    margin: 8px auto;
    text-align: center;
    box-shadow: 0 2px 8px rgba(251, 191, 36, 0.4);
    border: 2px solid #ffffff;
}}
.stButton>button {{ 
    background: linear-gradient(90deg, #000080 0%, {accent} 50%, #fbbf24 100%); 
    color: white; 
    font-weight: 700; 
    border-radius: 12px; 
    box-shadow: 0 4px 16px rgba(0,0,0,0.3); 
    border: 2px solid #fbbf24;
    transition: all 0.3s ease;
}}
.stButton>button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.4);
}}
.stTable, .stDataFrame, .stTable th, .stTable td, .stDataFrame th, .stDataFrame td {{
    color: #ffffff !important;
    border-color: #000080 !important;
}}
.blue-force-table .stDataFrame, .blue-force-table .stTable {{
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%) !important;
}}
.blue-force-table .stDataFrame th, .blue-force-table .stDataFrame td, 
.blue-force-table .stTable th, .blue-force-table .stTable td {{
    background: rgba(30, 58, 138, 0.8) !important;
    color: #ffffff !important;
    border-color: #60a5fa !important;
}}
.red-force-table .stDataFrame, .red-force-table .stTable {{
    background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%) !important;
}}
.red-force-table .stDataFrame th, .red-force-table .stDataFrame td,
.red-force-table .stTable th, .red-force-table .stTable td {{
    background: rgba(220, 38, 38, 0.8) !important;
    color: #ffffff !important;
    border-color: #f87171 !important;
}}
.control-table .stDataFrame, .control-table .stTable {{
    background: #fffbf0 !important;
}}
.control-table .stDataFrame th, .control-table .stDataFrame td,
.control-table .stTable th, .control-table .stTable td {{
    background: #fffbf0 !important;
    color: #000080 !important;
    border-color: #000080 !important;
}}
.stTabs [data-baseweb="tab"] {{ 
    background: linear-gradient(45deg, #000080, {accent}); 
    color: #fff; 
    border-radius: 8px;
    margin: 2px;
}}
h1, h2, h3, h4 {{ 
    color: #ffffff; 
    text-shadow: 0 0 10px #fbbf24, 0 0 20px #f59e0b, 0 0 30px #d97706; 
    font-weight: bold;
    text-decoration: none;
}}
.main .block-container {{
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-height: 100vh;
    overflow-y: auto;
}}
body {{
    overflow: hidden;
}}
.stApp {{
    height: 100vh;
    max-height: 100vh;
}}
</style>
""", unsafe_allow_html=True)

# --- Force-specific table display ---
def display_force_table(df, use_container_width=True, force_type=None):
    """Display dataframe with force-specific background color using HTML tables"""
    current_role = st.session_state.get("role", "control")
    
    # If force_type is specified (for control view), use that; otherwise use current role
    display_force = force_type if force_type else current_role
    
    if df.empty:
        st.info("No data available")
        return
    
    # Define color schemes for each force
    force_colors = {
        "blue": {
            "gradient": "linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%)",
            "header_bg": "#1e3a8a",
            "th_bg": "#1e40af",
            "border": "#60a5fa",
            "row_bg": "rgba(59, 130, 246, 0.8)",
            "cell_bg": "rgba(30, 64, 175, 0.7)"
        },
        "red": {
            "gradient": "linear-gradient(135deg, #dc2626 0%, #ef4444 50%, #f87171 100%)",
            "header_bg": "#b91c1c", 
            "th_bg": "#dc2626",
            "border": "#f87171",
            "row_bg": "rgba(239, 68, 68, 0.8)",
            "cell_bg": "rgba(220, 38, 38, 0.7)"
        },
        "yellow": {
            "gradient": "linear-gradient(135deg, #d97706 0%, #f59e0b 50%, #fbbf24 100%)",
            "header_bg": "#92400e",
            "th_bg": "#d97706", 
            "border": "#fbbf24",
            "row_bg": "rgba(245, 158, 11, 0.9)",
            "cell_bg": "rgba(217, 119, 6, 0.8)"
        },
        "green": {
            "gradient": "linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%)",
            "header_bg": "#047857",
            "th_bg": "#059669",
            "border": "#34d399", 
            "row_bg": "rgba(16, 185, 129, 0.8)",
            "cell_bg": "rgba(5, 150, 105, 0.7)"
        },
        "orange": {
            "gradient": "linear-gradient(135deg, #ea580c 0%, #f97316 50%, #fb923c 100%)",
            "header_bg": "#c2410c",
            "th_bg": "#ea580c",
            "border": "#fb923c",
            "row_bg": "rgba(249, 115, 22, 0.8)", 
            "cell_bg": "rgba(234, 88, 12, 0.7)"
        },
        "purple": {
            "gradient": "linear-gradient(135deg, #7c3aed 0%, #8b5cf6 50%, #a78bfa 100%)",
            "header_bg": "#6d28d9",
            "th_bg": "#7c3aed",
            "border": "#a78bfa",
            "row_bg": "rgba(139, 92, 246, 0.8)",
            "cell_bg": "rgba(124, 58, 237, 0.7)"
        }
    }
    
    # Get colors for the display force (default to green if not found)
    colors = force_colors.get(display_force, force_colors["green"])
    
    # Generate HTML table with force-specific colors
    html_table = f"""
    <div style="width: 100%; overflow-x: auto; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
        <table style="width: 100%; border-collapse: collapse; background: {colors['gradient']}; font-family: Arial, sans-serif;">
            <thead>
                <tr style="background: {colors['header_bg']};">
                    {"".join([f'<th style="padding: 12px; text-align: left; color: white; font-weight: bold; border: 2px solid {colors["border"]}; background: {colors["th_bg"]};">{col}</th>' for col in df.columns])}
                </tr>
            </thead>
            <tbody>
    """
    
    for _, row in df.iterrows():
        html_table += f'<tr style="background: {colors["row_bg"]};">'
        for col in df.columns:
            value = str(row[col]) if pd.notna(row[col]) else ""
            html_table += f'<td style="padding: 10px; color: white; font-weight: 500; border: 1px solid {colors["border"]}; background: {colors["cell_bg"]};">{value}</td>'
        html_table += '</tr>'
        
    html_table += """
            </tbody>
        </table>
    </div>
    <br>
    """
    st.markdown(html_table, unsafe_allow_html=True)

# --- Banner & Footer ---
def show_banner():
    st.markdown('''
    <div style="background: linear-gradient(45deg, #000080, #1e40af); color: white; padding: 20px; text-align: center; border-bottom: 4px solid #fbbf24;">
        <div style="display: flex; justify-content: center; align-items: center; max-width: 1200px; margin: 0 auto;">
            <div style="text-align: center;">
                <h1 style="margin: 0; color: white; font-size: 2.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">COPP AHP Military Planner</h1>
                <p style="margin: 0; color: #fbbf24; font-weight: bold; font-size: 1.2rem;">Advanced Planning System</p>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

def show_footer():
    st.markdown('''
    <div class="footer">
        <div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: center; align-items: center;">
            <div>🏛️ DSSC Wellington • Naval Wing 🏛️</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

# --- Session State ---
def clear_session():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# --- Login System ---
def login():
    # Initialize modal state to False if not set
    if "show_team_view_modal" not in st.session_state:
        st.session_state["show_team_view_modal"] = False
    
    # Compact AHP login with tricolor theme
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a, #1e293b);
    }
    
    .login-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 10px 15px 15px 15px;
    }
    
    .tricolor-header {
        background: linear-gradient(to bottom, #ff6600 33.33%, #ffffff 33.33%, #ffffff 66.66%, #138808 66.66%);
        padding: 4px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        margin-top: 0px;
    }
    
    .header-content {
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(10px);
        padding: 25px;
        border-radius: 8px;
        text-align: center;
        margin: 5px;
    }
    
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 12px;
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.9);
        line-height: 1.1;
    }
    
    .subtitle {
        font-size: 1.4rem;
        color: #ffffff;
        margin-bottom: 8px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
    }
    
    .organization {
        font-size: 1.6rem;
        color: #ffffff;
        font-weight: 600;
        margin-bottom: 10px;
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.9);
    }
    
    .motto {
        font-size: 1.3rem;
        color: #fbbf24;
        font-style: italic;
        font-weight: 600;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9);
    }
    
    .roles-container {
        display: flex;
        flex-direction: row;
        flex-wrap: nowrap;
        gap: 8px;
        justify-content: center;
        align-items: center;
        margin: 0 auto 20px auto;
        width: fit-content;
        padding: 0 10px;
        overflow-x: auto;
    }
    
    .role-card {
        border-radius: 8px;
        padding: 8px 6px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 2px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        width: 60px;
        height: 60px;
        min-width: 60px;
        flex-shrink: 0;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .role-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 50%, rgba(255,255,255,0.1) 100%);
        border-radius: 15px;
        pointer-events: none;
    }
    
    .role-card:hover {
        transform: translateY(-4px) scale(1.05);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
        border-color: rgba(255, 255, 255, 0.4);
    }
    
    .role-card.selected {
        border-color: #fbbf24;
        box-shadow: 0 0 15px rgba(251, 191, 36, 0.8), 0 4px 16px rgba(0, 0, 0, 0.3);
        transform: translateY(-2px);
    }
    
    .role-title {
        font-size: 0.7rem;
        font-weight: 800;
        color: white;
        margin-bottom: 2px;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
        position: relative;
        z-index: 1;
        line-height: 1;
    }
    
    .role-desc {
        font-size: 0.5rem;
        color: rgba(255, 255, 255, 0.95);
        margin: 0;
        font-weight: 600;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6);
        position: relative;
        z-index: 1;
        line-height: 1;
    }
    
    .auth-panel {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding: 15px;
        border: 2px solid #000080;
        margin-bottom: 10px;
    }
    
    .auth-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #000080;
        text-align: center;
        margin-bottom: 12px;
    }
    
    .team-btn {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .team-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main login container
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Tricolor AHP Header with Owls
    st.markdown("""
    <div class="tricolor-header">
        <div class="header-content">
            <h1 class="main-title">🦉 ANALYTICAL HIERARCHY PROCESS (AHP) FRAMEWORK 🦉</h1>
            <p class="subtitle">Common Operational Planning Process</p>
            <p class="subtitle">(Assessment of progress in Decisive Points, Objectives & Phases)</p>
            <p class="motto">"To War With Wisdom"</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Role selection buttons (horizontal layout)
    st.markdown("### 🎯 Select Your Role:")
    
    # Prepare all roles
    all_roles = [("control", "CONTROL")]
    
    for side in SIDES:
        base_color = FORCE_COLORS.get(side, "#8b5cf6")
        # Create bright gradients for each color
        color_gradients = {
            "#3b82f6": "linear-gradient(135deg, #3b82f6, #2563eb, #1d4ed8)",  # Blue
            "#ef4444": "linear-gradient(135deg, #ef4444, #dc2626, #b91c1c)",  # Red
            "#eab308": "linear-gradient(135deg, #eab308, #ca8a04, #a16207)",  # Yellow
            "#22c55e": "linear-gradient(135deg, #22c55e, #16a34a, #15803d)",  # Green
            "#f97316": "linear-gradient(135deg, #f97316, #ea580c, #c2410c)",  # Orange
            "#a855f7": "linear-gradient(135deg, #a855f7, #9333ea, #7c3aed)",  # Purple
            "#8b5cf6": "linear-gradient(135deg, #8b5cf6, #7c3aed, #6d28d9)"   # Violet
        }
        gradient = color_gradients.get(base_color, f"linear-gradient(135deg, {base_color}, #6b7280, #4b5563)")
        dark_color = base_color
        
        emoji_map = {"blue": "🔵", "red": "🔴", "yellow": "🟡", "green": "�", 
                    "orange": "�", "purple": "🟣", "brown": "🟤", "black": "⚫"}
        emoji = emoji_map.get(side, "�")
        
        all_roles.append((side, f"{side.upper()}"))
    
    # If no forces, add info
    if not SIDES:
        all_roles.append(("info", "NO FORCES"))
    
    # Create columns for horizontal button layout
    if len(all_roles) > 0:
        cols = st.columns(len(all_roles))
        
        for idx, (role_id, title) in enumerate(all_roles):
            with cols[idx]:
                # Button styling based on selection and role
                selected_role = st.session_state.get("login_role", "")
                is_selected = (selected_role == role_id)
                
                button_type = "primary" if is_selected else "secondary"
                button_label = f"{'✅ ' if is_selected else ''}{title}"
                
                if role_id != "info":
                    if st.button(button_label, key=f"role_btn_{role_id}", 
                               type=button_type, use_container_width=True,
                               help=f"Select {title} role"):
                        st.session_state["login_role"] = role_id
                        st.rerun()
                else:
                    st.button("⚠️ NO FORCES", disabled=True, use_container_width=True,
                            help="Add forces in Force Manager first")
    
    # Color-coordinate buttons with force colors - override all states
    st.markdown("""
    <style>
    /* Control button - multi-colored gradient (all states) */
    .stButton > button[data-testid="role_btn_control"],
    .stButton > button[data-testid="role_btn_control"]:focus,
    .stButton > button[data-testid="role_btn_control"]:active,
    .stButton > button[data-testid="role_btn_control"]:focus:not(:active) {
        background: linear-gradient(135deg, #22c55e, #16a34a, #15803d) !important;
        color: white !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        font-weight: 600 !important;
        box-shadow: 0 0 10px rgba(34, 197, 94, 0.5) !important;
    }
    
    .stButton > button[data-testid="role_btn_control"]:hover {
        background: linear-gradient(135deg, #16a34a, #15803d, #166534) !important;
        border-color: rgba(255, 255, 255, 0.5) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(34, 197, 94, 0.6) !important;
    }""", unsafe_allow_html=True)
    
    # Add force-specific button colors
    for side in SIDES:
        force_color = FORCE_COLORS.get(side, "#8b5cf6")
        
        # Create darker shade for hover
        color_variants = {
            "#3b82f6": "#2563eb",  # Blue -> darker blue
            "#ef4444": "#dc2626",  # Red -> darker red  
            "#eab308": "#ca8a04",  # Yellow -> darker yellow
            "#22c55e": "#16a34a",  # Green -> darker green
            "#f97316": "#ea580c",  # Orange -> darker orange
            "#a855f7": "#9333ea",  # Purple -> darker purple
            "#8b5cf6": "#7c3aed"   # Violet -> darker violet
        }
        hover_color = color_variants.get(force_color, "#6b7280")
        
        st.markdown(f"""
        <style>
        /* {side.upper()} force button - all states */
        .stButton > button[data-testid="role_btn_{side}"],
        .stButton > button[data-testid="role_btn_{side}"]:focus,
        .stButton > button[data-testid="role_btn_{side}"]:active,
        .stButton > button[data-testid="role_btn_{side}"]:focus:not(:active) {{
            background: {force_color} !important;
            color: white !important;
            border: 2px solid rgba(255, 255, 255, 0.3) !important;
            font-weight: 600 !important;
            box-shadow: 0 0 10px {force_color}80 !important;
        }}
        
        .stButton > button[data-testid="role_btn_{side}"]:hover {{
            background: {hover_color} !important;
            border-color: rgba(255, 255, 255, 0.5) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 15px {force_color}99 !important;
        }}
        </style>
        """, unsafe_allow_html=True)
    
    # Simple PIN authentication (center-aligned)
    role = st.session_state.get("login_role")
    if role and role != "info":
        # Center the PIN input section
        _, center_col, _ = st.columns([1, 2, 1])
        with center_col:
            col1, col2 = st.columns([2, 1])
            with col1:
                pin = st.text_input("Enter PIN:", type="password", placeholder="Security PIN", 
                                   help="Default: Control=9999, Forces=0000", label_visibility="collapsed")
            with col2:
                if st.button("🚀 LOGIN", key="login_btn", help="Authenticate"):
                    valid = False
                    if role == "control":
                        valid = (pin == st.session_state.get("pin_control", "9999"))
                    elif role in SIDES:
                        default_pin = "0000"
                        valid = (pin == st.session_state.get(f"pin_{role}", default_pin))
                    
                    if valid:
                        st.session_state["role"] = role
                        st.session_state["side"] = role if role != "control" else "blue"
                        st.success(f"✅ Welcome to {role.capitalize()} Operations!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Invalid PIN")
    

    
    # Close main container
    st.markdown('</div>', unsafe_allow_html=True)  # Close login-container
    
    # Team credits (bottom left)
    if st.button("👥 Team Credits", key="ahp_team_view_btn", help="View development team"):
        st.session_state["show_team_view_modal"] = not st.session_state.get("show_team_view_modal", False)
    
    # Simple team info display
    if st.session_state.get("show_team_view_modal"):
        with st.expander("👥 AHP Development Team", expanded=True):
            st.write("**Capt Swaminathan** - Conceptualized by")
            st.write("**Cdr Kaki Rohit Raju** - Software Designed by")
    
    # Style the team credits button
    st.markdown("""
    <style>
    .stButton > button[data-testid="ahp_team_view_btn"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 6px 12px !important;
        font-size: 0.8rem !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        width: auto !important;
        height: auto !important;
    }
    
    .stButton > button[data-testid="ahp_team_view_btn"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Footer banner
    show_footer()

# --- Sidebar Navigation ---
def sidebar():
    role = st.session_state.get("role", "")
    project = st.session_state.get("project", "Demo")
    inject_css(role)
    

    # Role Badge
    role_colors = {
        "control": "🟢 CONTROL",
        "blue": "🔵 BLUE FORCE", 
        "red": "🔴 RED FORCE"
    }
    role_display = role_colors.get(role, f"⚡ {role.upper()}" if role else "🔐 GUEST")
    
    st.sidebar.markdown(f"""
    <div class="role-badge">
        {role_display}
    </div>
    """, unsafe_allow_html=True)
    
    # Project Info
    st.sidebar.markdown(f"""
    <div style="text-align:center; color:#fbbf24; font-weight:600; margin:1rem 0; padding:0.5rem; background:rgba(0,0,0,0.3); border-radius:8px; border:1px solid rgba(251,191,36,0.3);">
        📁 Project: {project}
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Navigation Menu with Icons
    if role == "control":
        tab_options = {
            "📋 Phases": "Phases",
            "🎯 Objectives": "Objectives", 
            "📍 Decisive Points": "Decisive Points",
            "✅ Tasks": "Tasks",
            "📊 Progress Entry": "Progress Entry",
            "📈 Dashboard": "Dashboard",
            "⚙️ Control Panel": "Control Panel",
            "👥 Force Manager": "Force Manager",
            "🗂️ Project Management": "Project Management",
            "🚪 Logout": "Logout"
        }
    else:
        tab_options = {
            "📋 Phases": "Phases",
            "🎯 Objectives": "Objectives",
            "📍 Decisive Points": "Decisive Points", 
            "✅ Tasks": "Tasks",
            "⚖️ KO Method": "KO Method",
            "🗂️ Project Management": "Project Management",
            "🚪 Logout": "Logout"
        }
    
    # Enhanced radio selection
    st.sidebar.markdown("""
    <div style="color:#fbbf24; font-weight:600; font-size:1.1rem; text-align:center; margin-bottom:1rem;">
        🧭 NAVIGATION MENU
    </div>
    """, unsafe_allow_html=True)
    
    selected_display = st.sidebar.radio(
        "Navigate to:", 
        list(tab_options.keys()),
        label_visibility="collapsed"
    )
    
    # Status indicators
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="text-align:center; color:#94a3b8; font-size:0.8rem; margin-top:1rem;">
        🛡️ Secure Military Planning<br>
        ⚓ DSSC Wellington
    </div>
    """, unsafe_allow_html=True)
    
    return tab_options[selected_display]

# --- Project Management ---
def project_management():
    st.header("Project Management")
    projects = list_projects()
    selected = st.selectbox("Select Project", projects)
    if st.button("Switch Project"):
        st.session_state["project"] = selected
        st.success(f"Switched to {selected}")
        st.rerun()
    new_name = st.text_input("New Project Name")
    new_desc = st.text_area("Description")
    if st.button("Create Project") and new_name:
        for side in SIDES:
            save_project(new_name, side, DEFAULT_STRUCTURE)
        st.success(f"Project {new_name} created.")
        st.rerun()
    if st.button("Archive Project"):
        archive_project(selected)
        st.success(f"Project {selected} archived.")
        st.rerun()
    if st.button("Delete Project"):
        delete_project(selected)
        st.success(f"Project {selected} deleted.")
        st.rerun()
    st.write("Export:")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Export Blue JSON"):
            path = export_project_json(selected, "blue")
            st.download_button("Download Blue JSON", open(path, "rb"), file_name=path)
    with col2:
        if st.button("Export Red JSON"):
            path = export_project_json(selected, "red")
            st.download_button("Download Red JSON", open(path, "rb"), file_name=path)
    with col3:
        if st.button("Export ZIP"):
            path = export_project_zip(selected)
            st.download_button("Download ZIP", open(path, "rb"), file_name=path)
    st.write("Upload Excel Sheets (Control Only):")
    if st.session_state.get("role") == "control":
        for side in SIDES:
            uploaded = st.file_uploader(f"Upload {side.capitalize()} Excel", type=["xlsx"], key=f"upload_{side}_excel")
            if uploaded:
                tmp_path = f"tmp_{side}.xlsx"
                try:
                    with open(tmp_path, "wb") as f:
                        f.write(uploaded.read())
                    import_excel_to_project(selected, side, tmp_path)
                    st.success(f"Imported {side} Excel.")
                except Exception as e:
                    st.error(f"Error importing {side} Excel: {str(e)}")
                finally:
                    # Safe file cleanup with retry mechanism
                    import time
                    for attempt in range(3):
                        try:
                            if os.path.exists(tmp_path):
                                os.remove(tmp_path)
                            break
                        except PermissionError:
                            if attempt < 2:  # Only wait if we have more attempts
                                time.sleep(0.5)  # Wait 500ms before retry
                            else:
                                st.warning(f"Could not delete temporary file {tmp_path}. Please delete it manually if it persists.")
        # Show summary of uploaded data for each force
        st.markdown("### Project Data Summary")
        for side in SIDES:
            data = load_project(selected, side)
            st.subheader(f"{side.capitalize()} Data")
            st.write("Phases:")
            st.table(data.get("phases", []))
            st.write("Objectives:")
            st.table(data.get("objectives", []))
            st.write("DPs:")
            st.table(data.get("dps", []))
            st.write("Tasks:")
            st.table(data.get("tasks", []))
    # Removed stray/incorrectly indented lines from summary display loop
    role = st.session_state.get("role")
    project = st.session_state.get("project")
    if role in ["control"] + SIDES:
        name = st.text_input("Phase Name")
        if st.button("Add Phase") and name:
            # Add to all forces if control, else just current side
            if role == "control":
                for force in SIDES:
                    data = load_project(project, force)
                    data["phases"].append({"Name": name})
                    save_project(project, force, data)
                st.success(f"Phase '{name}' added to all forces.")
            else:
                side = role
                data = load_project(project, side)
                data["phases"].append({"Name": name})
                save_project(project, side, data)
                st.success(f"Phase '{name}' added.")
            st.rerun()

# --- Objectives Tab ---
def objectives_tab():
    st.header("🎯 Objectives")
    project = st.session_state.get("project")
    role = st.session_state.get("role")
    side = st.session_state.get("side")
    
    if role == "control":
        # Create tabs for each force
        force_tabs = st.tabs([f"{get_force_emoji(force)} {force.capitalize()}" for force in SIDES])
        
        for idx, force in enumerate(SIDES):
            with force_tabs[idx]:
                data = load_project(project, force)
                objectives = data.get("objectives", [])
                
                # Display current objectives
                st.subheader(f"{force.capitalize()} Force Objectives")
                objective_data = []
                for obj_idx, obj in enumerate(objectives):
                    name = obj.get("Name") or obj.get("Objective") or f"Objective {obj_idx+1}"
                    phase = obj.get("Phase") or obj.get("phase") or ""
                    
                    objective_data.append({
                        "No": obj_idx + 1,
                        "Objective": str(name).strip(),
                        "Phase": str(phase).strip()
                    })
                
                df = pd.DataFrame(objective_data)
                display_force_table(df, use_container_width=True, force_type=force)
                
                # Manage objectives
                st.markdown("---")
                col_add, col_delete = st.columns(2)
                
                with col_add:
                    st.markdown("**➕ Add New Objective**")
                    new_name = st.text_input("Objective Name", key=f"obj_name_{force}")
                    # Get phases for this force
                    phases = [p.get("Name") for p in data.get("phases", [])]
                    if phases:
                        new_phase = st.selectbox("Select Phase", phases, key=f"obj_phase_{force}")
                    else:
                        st.warning("No phases available. Add phases first.")
                        new_phase = None
                    
                    if st.button(f"➕ Add to {force.capitalize()}", type="primary", key=f"add_obj_{force}") and new_name and new_phase:
                        if "objectives" not in data:
                            data["objectives"] = []
                        data["objectives"].append({"Name": new_name, "Phase": new_phase})
                        save_project(project, force, data)
                        st.success(f"✅ Objective '{new_name}' added to {force} force")
                        st.rerun()
                
                with col_delete:
                    st.markdown("**🗑️ Delete Objective**")
                    if objectives:
                        obj_options = [f"{i+1}. {obj.get('Name', 'Unnamed')}" for i, obj in enumerate(objectives)]
                        selected_obj_idx = st.selectbox("Select Objective", range(len(objectives)), 
                                                       format_func=lambda x: obj_options[x], key=f"del_obj_{force}")
                        
                        if st.button(f"🗑️ Delete from {force.capitalize()}", type="secondary", key=f"delete_obj_{force}"):
                            obj_name = objectives[selected_obj_idx].get("Name")
                            del objectives[selected_obj_idx]
                            data["objectives"] = objectives
                            # Remove associated DPs
                            data["dps"] = [dp for dp in data.get("dps", []) if dp.get("Objective") != obj_name]
                            save_project(project, force, data)
                            st.success(f"✅ Objective '{obj_name}' deleted from {force} force")
                            st.rerun()
                    else:
                        st.info("No objectives to delete")
    else:
        # Single force view for specific side
        data = load_project(project, side)
        objectives = data.get("objectives", [])
        
        # Display current objectives
        st.subheader(f"{side.capitalize()} Force Objectives")
        objective_data = []
        for idx, obj in enumerate(objectives):
            name = obj.get("Name") or obj.get("Objective") or f"Objective {idx+1}"
            phase = obj.get("Phase") or obj.get("phase") or ""
            
            objective_data.append({
                "No": idx + 1,
                "Objective": str(name).strip(),
                "Phase": str(phase).strip()
            })
        
        df = pd.DataFrame(objective_data)
        display_force_table(df, use_container_width=True)
        
        # Manage objectives
        st.markdown("---")
        col_add, col_delete = st.columns(2)
        
        with col_add:
            st.markdown("**➕ Add New Objective**")
            name = st.text_input("Objective Name")
            # Get phases for this force
            phases = [p.get("Name") for p in data.get("phases", [])]
            if phases:
                phase = st.selectbox("Select Phase", phases)
            else:
                st.warning("No phases available. Add phases first.")
                phase = None
            
            if st.button("➕ Add Objective", type="primary") and name and phase:
                if "objectives" not in data:
                    data["objectives"] = []
                data["objectives"].append({"Name": name, "Phase": phase})
                save_project(project, side, data)
                st.success(f"✅ Objective '{name}' added")
                st.rerun()
        
        with col_delete:
            st.markdown("**🗑️ Delete Objective**")
            if objectives:
                obj_options = [f"{i+1}. {obj.get('Name', 'Unnamed')}" for i, obj in enumerate(objectives)]
                selected_obj_idx = st.selectbox("Select Objective", range(len(objectives)), 
                                               format_func=lambda x: obj_options[x])
                
                if st.button("🗑️ Delete Objective", type="secondary"):
                    obj_name = objectives[selected_obj_idx].get("Name")
                    del objectives[selected_obj_idx]
                    data["objectives"] = objectives
                    # Remove associated DPs
                    data["dps"] = [dp for dp in data.get("dps", []) if dp.get("Objective") != obj_name]
                    save_project(project, side, data)
                    st.success(f"✅ Objective '{obj_name}' deleted")
                    st.rerun()
            else:
                st.info("No objectives to delete")

def phases_tab():
    st.header("⏱️ Phases")
    project = st.session_state.get("project")
    role = st.session_state.get("role")
    side = st.session_state.get("side")
    
    if role == "control":
        # Create tabs for each force
        force_tabs = st.tabs([f"{get_force_emoji(force)} {force.capitalize()}" for force in SIDES])
        
        for idx, force in enumerate(SIDES):
            with force_tabs[idx]:
                data = load_project(project, force)
                phases = data.get("phases", [])
                
                # Display current phases
                st.subheader(f"{force.capitalize()} Force Phases")
                df = pd.DataFrame({
                    "No": [phase_idx + 1 for phase_idx in range(len(phases))],
                    "Phase Name": [p.get("Name") or p.get("Phase") for p in phases]
                })
                
                display_force_table(df, use_container_width=True, force_type=force)
                
                # Manage phases
                st.markdown("---")
                col_add, col_delete = st.columns(2)
                
                with col_add:
                    st.markdown("**➕ Add New Phase**")
                    new_name = st.text_input("Phase Name", key=f"phase_name_{force}")
                    
                    if st.button(f"➕ Add to {force.capitalize()}", type="primary", key=f"add_phase_{force}") and new_name:
                        if "phases" not in data:
                            data["phases"] = []
                        data["phases"].append({"Name": new_name})
                        save_project(project, force, data)
                        st.success(f"✅ Phase '{new_name}' added to {force} force")
                        st.rerun()
                
                with col_delete:
                    st.markdown("**🗑️ Delete Phase**")
                    if phases:
                        phase_options = [f"{i+1}. {phase.get('Name', 'Unnamed')}" for i, phase in enumerate(phases)]
                        selected_phase_idx = st.selectbox("Select Phase", range(len(phases)), 
                                                         format_func=lambda x: phase_options[x], key=f"del_phase_{force}")
                        
                        if st.button(f"🗑️ Delete from {force.capitalize()}", type="secondary", key=f"delete_phase_{force}"):
                            phase_name = phases[selected_phase_idx].get("Name")
                            del phases[selected_phase_idx]
                            data["phases"] = phases
                            # Remove objectives associated with this phase
                            data["objectives"] = [obj for obj in data.get("objectives", []) if obj.get("Phase") != phase_name]
                            save_project(project, force, data)
                            st.success(f"✅ Phase '{phase_name}' deleted from {force} force")
                            st.rerun()
                    else:
                        st.info("No phases to delete")
    else:
        # Single force view for specific side
        data = load_project(project, side)
        phases = data.get("phases", [])
        
        # Display current phases
        st.subheader(f"{side.capitalize()} Force Phases")
        df = pd.DataFrame({
            "No": [idx + 1 for idx in range(len(phases))],
            "Phase Name": [p.get("Name") or p.get("Phase") for p in phases]
        })
        
        display_force_table(df, use_container_width=True)
        
        # Manage phases
        st.markdown("---")
        col_add, col_delete = st.columns(2)
        
        with col_add:
            st.markdown("**➕ Add New Phase**")
            name = st.text_input("Phase Name")
            
            if st.button("➕ Add Phase", type="primary") and name:
                if "phases" not in data:
                    data["phases"] = []
                data["phases"].append({"Name": name})
                save_project(project, side, data)
                st.success(f"✅ Phase '{name}' added")
                st.rerun()
        
        with col_delete:
            st.markdown("**🗑️ Delete Phase**")
            if phases:
                phase_options = [f"{i+1}. {phase.get('Name', 'Unnamed')}" for i, phase in enumerate(phases)]
                selected_phase_idx = st.selectbox("Select Phase", range(len(phases)), 
                                                 format_func=lambda x: phase_options[x])
                
                if st.button("🗑️ Delete Phase", type="secondary"):
                    phase_name = phases[selected_phase_idx].get("Name")
                    del phases[selected_phase_idx]
                    data["phases"] = phases
                    # Remove objectives associated with this phase
                    data["objectives"] = [obj for obj in data.get("objectives", []) if obj.get("Phase") != phase_name]
                    save_project(project, side, data)
                    st.success(f"✅ Phase '{phase_name}' deleted")
                    st.rerun()
            else:
                st.info("No phases to delete")
def dps_tab():
    st.header("🎯 Decisive Points (DPs)")
    project = st.session_state.get("project")
    role = st.session_state.get("role")
    side = st.session_state.get("side")
    
    if role == "control":
        # Create tabs for each force
        force_tabs = st.tabs([f"{get_force_emoji(force)} {force.capitalize()}" for force in SIDES])
        
        for idx, force in enumerate(SIDES):
            with force_tabs[idx]:
                data = load_project(project, force)
                dps = data.get("dps", [])
                objectives = data.get("objectives", [])
                phases = data.get("phases", [])
                
                # Display current DPs
                st.subheader(f"{force.capitalize()} Force DPs")
                if dps:
                    dp_data = []
                    for dp in dps:
                        dp_data.append({
                            "DP No": dp.get("DP No", ""),
                            "DP Name": dp.get("Name", ""),
                            "Objective": dp.get("Objective", ""),
                            "Phase": dp.get("Phase", ""),
                            "Weight": dp.get("Weight", ""),
                            "Force Group": dp.get("Force Group", "")
                        })
                    df = pd.DataFrame(dp_data)
                else:
                    df = pd.DataFrame(columns=["DP No", "DP Name", "Objective", "Phase", "Weight", "Force Group"])
                
                display_force_table(df, use_container_width=True, force_type=force)
                
                # Manage DPs
                st.markdown("---")
                col_add, col_delete = st.columns(2)
                
                with col_add:
                    st.markdown("**➕ Add New DP**")
                    
                    # Auto-generate unique DP number
                    existing_dp_nos = {int(dp.get("DP No", 0)) for dp in dps if str(dp.get("DP No", "")).isdigit()}
                    suggested_dp_no = 1
                    while suggested_dp_no in existing_dp_nos:
                        suggested_dp_no += 1
                    
                    new_dp_no = st.number_input("DP Number", min_value=1, value=suggested_dp_no, key=f"dp_no_{force}")
                    new_dp_name = st.text_input("DP Name", key=f"dp_name_{force}")
                    
                    # Get objectives and phases for this force
                    obj_names = [obj.get("Name") for obj in objectives if obj.get("Name")]
                    phase_names = [phase.get("Name") for phase in phases if phase.get("Name")]
                    
                    if obj_names:
                        new_objective = st.selectbox("Select Objective", obj_names, key=f"dp_obj_{force}")
                    else:
                        st.warning("No objectives available. Add objectives first.")
                        new_objective = None
                    
                    if phase_names:
                        new_phase = st.selectbox("Select Phase", phase_names, key=f"dp_phase_{force}")
                    else:
                        new_phase = st.text_input("Phase (manual)", key=f"dp_phase_manual_{force}")
                    
                    new_weight = st.slider("Weight/Priority", 1, 5, 3, key=f"dp_weight_{force}")
                    new_force_group = st.text_input("Force Group", key=f"dp_force_group_{force}")
                    
                    # Check DP number uniqueness
                    dp_no_exists = new_dp_no in existing_dp_nos
                    if dp_no_exists:
                        st.error(f"DP Number {new_dp_no} already exists!")
                    
                    if st.button(f"➕ Add to {force.capitalize()}", type="primary", key=f"add_dp_{force}") and new_dp_name and new_objective and not dp_no_exists:
                        if "dps" not in data:
                            data["dps"] = []
                        data["dps"].append({
                            "DP No": new_dp_no,
                            "Name": new_dp_name,
                            "Objective": new_objective,
                            "Phase": new_phase,
                            "Weight": new_weight,
                            "Force Group": new_force_group
                        })
                        save_project(project, force, data)
                        st.success(f"✅ DP '{new_dp_name}' added to {force} force")
                        st.rerun()
                
                with col_delete:
                    st.markdown("**🗑️ Delete DP**")
                    if dps:
                        dp_options = [f"DP {dp.get('DP No', 'N/A')}: {dp.get('Name', 'Unnamed')}" for dp in dps]
                        selected_dp_idx = st.selectbox("Select DP", range(len(dps)), 
                                                      format_func=lambda x: dp_options[x], key=f"del_dp_{force}")
                        
                        if st.button(f"🗑️ Delete from {force.capitalize()}", type="secondary", key=f"delete_dp_{force}"):
                            dp_to_delete = dps[selected_dp_idx]
                            dp_no = dp_to_delete.get("DP No")
                            dp_name = dp_to_delete.get("Name")
                            
                            del dps[selected_dp_idx]
                            data["dps"] = dps
                            # Remove associated tasks
                            data["tasks"] = [task for task in data.get("tasks", []) 
                                           if str(task.get("DP No", "")) != str(dp_no) and 
                                              str(task.get("dp_no", "")) != str(dp_no)]
                            save_project(project, force, data)
                            st.success(f"✅ DP '{dp_name}' deleted from {force} force")
                            st.rerun()
                    else:
                        st.info("No DPs to delete")
    else:
        # Single force view
        data = load_project(project, side)
        dps = data.get("dps", [])
        objectives = data.get("objectives", [])
        phases = data.get("phases", [])
        
        # Display current DPs
        st.subheader(f"{side.capitalize()} Force DPs")
        if dps:
            dp_data = []
            for dp in dps:
                dp_data.append({
                    "DP No": dp.get("DP No", ""),
                    "DP Name": dp.get("Name", ""),
                    "Objective": dp.get("Objective", ""),
                    "Phase": dp.get("Phase", ""),
                    "Weight": dp.get("Weight", ""),
                    "Force Group": dp.get("Force Group", "")
                })
            df = pd.DataFrame(dp_data)
        else:
            df = pd.DataFrame(columns=["DP No", "DP Name", "Objective", "Phase", "Weight", "Force Group"])
        
        display_force_table(df, use_container_width=True)
        
        # Manage DPs
        st.markdown("---")
        col_add, col_delete = st.columns(2)
        
        with col_add:
            st.markdown("**➕ Add New DP**")
            
            # Auto-generate unique DP number
            existing_dp_nos = {int(dp.get("DP No", 0)) for dp in dps if str(dp.get("DP No", "")).isdigit()}
            suggested_dp_no = 1
            while suggested_dp_no in existing_dp_nos:
                suggested_dp_no += 1
            
            dp_no = st.number_input("DP Number", min_value=1, value=suggested_dp_no)
            dp_name = st.text_input("DP Name")
            
            # Get objectives and phases for this force
            obj_names = [obj.get("Name") for obj in objectives if obj.get("Name")]
            phase_names = [phase.get("Name") for phase in phases if phase.get("Name")]
            
            if obj_names:
                objective = st.selectbox("Select Objective", obj_names)
            else:
                st.warning("No objectives available. Add objectives first.")
                objective = None
            
            if phase_names:
                phase = st.selectbox("Select Phase", phase_names)
            else:
                phase = st.text_input("Phase (manual)")
            
            weight = st.slider("Weight/Priority", 1, 5, 3)
            force_group = st.text_input("Force Group")
            
            # Check DP number uniqueness
            dp_no_exists = dp_no in existing_dp_nos
            if dp_no_exists:
                st.error(f"DP Number {dp_no} already exists!")
            
            if st.button("➕ Add DP", type="primary") and dp_name and objective and not dp_no_exists:
                if "dps" not in data:
                    data["dps"] = []
                data["dps"].append({
                    "DP No": dp_no,
                    "Name": dp_name,
                    "Objective": objective,
                    "Phase": phase,
                    "Weight": weight,
                    "Force Group": force_group
                })
                save_project(project, side, data)
                st.success(f"✅ DP '{dp_name}' added")
                st.rerun()
        
        with col_delete:
            st.markdown("**🗑️ Delete DP**")
            if dps:
                dp_options = [f"DP {dp.get('DP No', 'N/A')}: {dp.get('Name', 'Unnamed')}" for dp in dps]
                selected_dp_idx = st.selectbox("Select DP", range(len(dps)), 
                                              format_func=lambda x: dp_options[x])
                
                if st.button("🗑️ Delete DP", type="secondary"):
                    dp_to_delete = dps[selected_dp_idx]
                    dp_no = dp_to_delete.get("DP No")
                    dp_name = dp_to_delete.get("Name")
                    
                    del dps[selected_dp_idx]
                    data["dps"] = dps
                    # Remove associated tasks
                    data["tasks"] = [task for task in data.get("tasks", []) 
                                   if str(task.get("DP No", "")) != str(dp_no) and 
                                      str(task.get("dp_no", "")) != str(dp_no)]
                    save_project(project, side, data)
                    st.success(f"✅ DP '{dp_name}' deleted")
                    st.rerun()
            else:
                st.info("No DPs to delete")

def tasks_tab():
    st.header("📋 Tasks")
    project = st.session_state.get("project")
    role = st.session_state.get("role")
    side = st.session_state.get("side")
    
    def display_tasks_hierarchically(force_name, data):
        """Display tasks grouped by DP in hierarchical format"""
        tasks = data.get("tasks", [])
        dps = data.get("dps", [])
        
        if not tasks:
            st.info(f"No tasks found for {force_name}.")
            return
        
        # Group tasks by DP
        tasks_by_dp = {}
        for task in tasks:
            # Get task name - handle different column names from Excel
            task_name = (task.get("description") or task.get("Desc") or task.get("Name") or 
                        task.get("Task Name") or task.get("desc") or task.get("name") or 
                        task.get("task name") or task.get("Task") or task.get("task") or
                        task.get("Description") or f"Task {task.get('Task No', '')}")
            
            dp_no = task.get("dp_no") or task.get("DP No") or task.get("dp no") or task.get("DP") or task.get("dp") or "Unassigned"
            
            if str(dp_no) not in tasks_by_dp:
                tasks_by_dp[str(dp_no)] = []
            
            # Prepare task data with proper column handling
            weight_val = task.get("stated") or task.get("Weight") or task.get("weight") or task.get("Wt") or task.get("wt")
            progress_val = task.get("achieved") or task.get("Achieved %") or task.get("progress") or task.get("Progress") or task.get("achieved %") or task.get("Progress %")
            
            task_data = {
                "Task Name": str(task_name).strip() if task_name else "Unknown Task",
                "Weight": str(weight_val).strip() if weight_val and str(weight_val).lower() != 'nan' else "Not Set",
                "Progress (%)": str(progress_val).strip() if progress_val and str(progress_val).lower() != 'nan' else "0",
                "Type": task.get("Type", ""),
                "Force Group": task.get("Force Group", ""),
                "Criteria": task.get("Criteria", "")
            }
            tasks_by_dp[str(dp_no)].append(task_data)
        
        # Display tasks grouped by DP
        for dp_no, dp_tasks in tasks_by_dp.items():
            # Find DP details
            dp_name = "Unknown DP"
            dp_objective = "Unknown Objective"
            for dp in dps:
                if str(dp.get("DP No", "") or dp.get("dp_no", "")) == str(dp_no):
                    dp_name = dp.get("Name", f"DP {dp_no}")
                    dp_objective = dp.get("Objective", "Unknown Objective")
                    break
            
            with st.expander(f"📋 DP {dp_no}: {dp_name} (Objective: {dp_objective}) - {len(dp_tasks)} Tasks", expanded=True):
                if dp_tasks:
                    df = pd.DataFrame(dp_tasks)
                    display_force_table(df, use_container_width=True, force_type=force_name)
                else:
                    st.info(f"No tasks assigned to DP {dp_no}")
    
    if role == "control":
        # Create tabs for each force
        force_tabs = st.tabs([f"{get_force_emoji(force)} {force.capitalize()}" for force in SIDES])
        
        for idx, force in enumerate(SIDES):
            with force_tabs[idx]:
                data = load_project(project, force)
                tasks = data.get("tasks", [])
                dps = data.get("dps", [])
                
                # Display current tasks hierarchically
                st.subheader(f"{force.capitalize()} Force Tasks")
                display_tasks_hierarchically(force, data)
                
                # Manage tasks
                st.markdown("---")
                col_add, col_delete = st.columns(2)
                
                with col_add:
                    st.markdown("**➕ Add New Task**")
                    
                    # Get available DPs for this force
                    force_dps = []
                    for dp in dps:
                        dp_no = dp.get("DP No", dp.get("dp_no", ""))
                        dp_name = dp.get("Name", f"DP {dp_no}")
                        dp_objective = dp.get("Objective", "")
                        force_dps.append({
                            "display": f"DP {dp_no}: {dp_name} (Objective: {dp_objective})", 
                            "dp_no": dp_no
                        })
                    
                    if force_dps:
                        selected_dp = st.selectbox("Select DP", force_dps, 
                                                  format_func=lambda x: x["display"], key=f"task_dp_{force}")
                        
                        task_name = st.text_input("Task Name", key=f"task_name_{force}")
                        task_weight = st.number_input("Weight", min_value=0.0, max_value=100.0, value=0.0, key=f"task_weight_{force}")
                        task_progress = st.number_input("Progress (%)", min_value=0.0, max_value=100.0, value=0.0, key=f"task_progress_{force}")
                        task_type = st.selectbox("Type", ["Planning", "Execution", "Assessment", "Support"], key=f"task_type_{force}")
                        task_force_group = st.text_input("Force Group", key=f"task_force_group_{force}")
                        task_criteria = st.text_area("Criteria", key=f"task_criteria_{force}")
                        
                        if st.button(f"➕ Add to {force.capitalize()}", type="primary", key=f"add_task_{force}") and task_name:
                            if "tasks" not in data:
                                data["tasks"] = []
                            data["tasks"].append({
                                "Name": task_name,
                                "description": task_name,
                                "DP No": selected_dp["dp_no"],
                                "dp_no": selected_dp["dp_no"],
                                "Weight": task_weight,
                                "stated": task_weight,
                                "Progress": task_progress,
                                "achieved": task_progress,
                                "Type": task_type,
                                "Force Group": task_force_group,
                                "Criteria": task_criteria
                            })
                            save_project(project, force, data)
                            st.success(f"✅ Task '{task_name}' added to {force} force")
                            st.rerun()
                    else:
                        st.warning("No DPs available. Add DPs first.")
                
                with col_delete:
                    st.markdown("**🗑️ Delete Task**")
                    if tasks:
                        task_options = []
                        for i, task in enumerate(tasks):
                            task_name = (task.get("description") or task.get("Name") or 
                                       task.get("Task Name") or f"Task {i+1}")
                            dp_no = task.get("dp_no") or task.get("DP No") or "No DP"
                            task_options.append(f"{i+1}. {task_name} (DP: {dp_no})")
                        
                        selected_task_idx = st.selectbox("Select Task", range(len(tasks)), 
                                                        format_func=lambda x: task_options[x], key=f"del_task_{force}")
                        
                        if st.button(f"🗑️ Delete from {force.capitalize()}", type="secondary", key=f"delete_task_{force}"):
                            task_to_delete = tasks[selected_task_idx]
                            task_name = (task_to_delete.get("description") or task_to_delete.get("Name") or 
                                       task_to_delete.get("Task Name") or "Unknown Task")
                            
                            del tasks[selected_task_idx]
                            data["tasks"] = tasks
                            save_project(project, force, data)
                            st.success(f"✅ Task '{task_name}' deleted from {force} force")
                            st.rerun()
                    else:
                        st.info("No tasks to delete")
    else:
        # Single force view
        data = load_project(project, side)
        tasks = data.get("tasks", [])
        dps = data.get("dps", [])
        
        # Display current tasks hierarchically
        st.subheader(f"{side.capitalize()} Force Tasks")
        display_tasks_hierarchically(side, data)
        
        # Manage tasks
        st.markdown("---")
        col_add, col_delete = st.columns(2)
        
        with col_add:
            st.markdown("**➕ Add New Task**")
            
            # Get available DPs for this force
            force_dps = []
            for dp in dps:
                dp_no = dp.get("DP No", dp.get("dp_no", ""))
                dp_name = dp.get("Name", f"DP {dp_no}")
                dp_objective = dp.get("Objective", "")
                force_dps.append({
                    "display": f"DP {dp_no}: {dp_name} (Objective: {dp_objective})", 
                    "dp_no": dp_no
                })
            
            if force_dps:
                selected_dp = st.selectbox("Select DP", force_dps, 
                                          format_func=lambda x: x["display"])
                
                task_name = st.text_input("Task Name")
                task_weight = st.number_input("Weight", min_value=0.0, max_value=100.0, value=0.0)
                task_progress = st.number_input("Progress (%)", min_value=0.0, max_value=100.0, value=0.0)
                task_type = st.selectbox("Type", ["Planning", "Execution", "Assessment", "Support"])
                task_force_group = st.text_input("Force Group")
                task_criteria = st.text_area("Criteria")
                
                if st.button("➕ Add Task", type="primary") and task_name:
                    if "tasks" not in data:
                        data["tasks"] = []
                    data["tasks"].append({
                        "Name": task_name,
                        "description": task_name,
                        "DP No": selected_dp["dp_no"],
                        "dp_no": selected_dp["dp_no"],
                        "Weight": task_weight,
                        "stated": task_weight,
                        "Progress": task_progress,
                        "achieved": task_progress,
                        "Type": task_type,
                        "Force Group": task_force_group,
                        "Criteria": task_criteria
                    })
                    save_project(project, side, data)
                    st.success(f"✅ Task '{task_name}' added")
                    st.rerun()
            else:
                st.warning("No DPs available. Add DPs first.")
        
        with col_delete:
            st.markdown("**🗑️ Delete Task**")
            if tasks:
                task_options = []
                for i, task in enumerate(tasks):
                    task_name = (task.get("description") or task.get("Name") or 
                               task.get("Task Name") or f"Task {i+1}")
                    dp_no = task.get("dp_no") or task.get("DP No") or "No DP"
                    task_options.append(f"{i+1}. {task_name} (DP: {dp_no})")
                
                selected_task_idx = st.selectbox("Select Task", range(len(tasks)), 
                                                format_func=lambda x: task_options[x])
                
                if st.button("🗑️ Delete Task", type="secondary"):
                    task_to_delete = tasks[selected_task_idx]
                    task_name = (task_to_delete.get("description") or task_to_delete.get("Name") or 
                               task_to_delete.get("Task Name") or "Unknown Task")
                    
                    del tasks[selected_task_idx]
                    data["tasks"] = tasks
                    save_project(project, side, data)
                    st.success(f"✅ Task '{task_name}' deleted")
                    st.rerun()
            else:
                st.info("No tasks to delete")
def ko_tab():
    import itertools
    st.header("⚖️ KO Method (Task Weightage within DP)")
    st.markdown("*Pairwise comparison method to determine task weights within a selected Decision Point*")
    
    s = st.session_state
    project = s.get("project")
    side = s.get("side")
    data = load_project(project, side)
    dps = data.get("dps", [])
    tasks = data.get("tasks", [])
    
    # Support both 'DP No' and 'dp_no' keys
    def get_dp_no(dp):
        return dp.get("DP No") or dp.get("dp_no")
    
    def get_task_dp(task):
        return task.get("DP No") or task.get("dp_no")
    
    if not dps:
        st.warning("⚠️ No DPs found. Please create DPs first in the DPs tab.")
        return
    
    if not tasks:
        st.warning("⚠️ No tasks found. Please create tasks first in the Tasks tab.")
        return
    
    # Step 1: DP Selection
    st.subheader("🎯 Step 1: Select Decision Point")
    
    # Create DP options with names and numbers
    dp_options = {}
    for dp in dps:
        dp_no = get_dp_no(dp)
        dp_name = dp.get("Name", dp.get("name", f"DP {dp_no}"))
        if dp_no is not None:
            dp_options[f"DP {dp_no}: {dp_name}"] = dp_no
    
    if not dp_options:
        st.error("❌ No valid DPs found. Please ensure DPs have proper DP No assigned.")
        return
    
    selected_dp_display = st.selectbox(
        "Select DP for task weightage calculation:",
        list(dp_options.keys()),
        help="Choose the Decision Point whose tasks you want to compare for weight calculation"
    )
    
    selected_dp_no = dp_options[selected_dp_display]
    
    # Find tasks for selected DP
    dp_tasks = [task for task in tasks if str(get_task_dp(task)) == str(selected_dp_no)]
    
    if len(dp_tasks) < 2:
        st.info(f"📝 Need at least 2 tasks in DP {selected_dp_no} for KO comparison. Found {len(dp_tasks)} task(s).")
        if len(dp_tasks) == 1:
            st.info("💡 Single task automatically gets 100% weight.")
            # Automatically assign 100% weight to single task
            dp_tasks[0]["Weight"] = 100.0
            dp_tasks[0]["weight"] = 100.0
            dp_tasks[0]["stated"] = 100.0
            # Update in main tasks list
            for i, task in enumerate(tasks):
                if str(get_task_dp(task)) == str(selected_dp_no):
                    tasks[i] = dp_tasks[0]
                    break
            data["tasks"] = tasks
            save_project(project, side, data)
            st.success("✅ Single task weight set to 100%")
        return
    
    # Step 2: Display DP and Task Information & Pairwise Comparison
    st.subheader(f"📋 Step 2: DP Overview & Pairwise Comparison")
    
    # Find DP details
    selected_dp_info = next((dp for dp in dps if str(get_dp_no(dp)) == str(selected_dp_no)), {})
    dp_name = selected_dp_info.get("Name", selected_dp_info.get("name", f"DP {selected_dp_no}"))
    dp_objective = selected_dp_info.get("Objective", "Not specified")
    
    st.markdown(f"""
    **DP Name:** {dp_name}  
    **Objective:** {dp_objective}  
    **Tasks to Compare:** {len(dp_tasks)}
    """)
    
    # Display tasks in this DP
    with st.expander("📝 Tasks in this DP", expanded=False):
        for i, task in enumerate(dp_tasks):
            task_name = (task.get("description") or task.get("Desc") or task.get("Name") or 
                        task.get("Task Name") or task.get("desc") or task.get("name") or 
                        f"Task {i+1}")
            current_weight = task.get("Weight", task.get("weight", task.get("stated", 0)))
            st.write(f"**{i+1}.** {task_name} (Current Weight: {current_weight}%)")
    
    # KO Method Implementation
    st.markdown("### ⚖️ Pairwise Comparison")
    
    pairs = list(itertools.combinations(range(len(dp_tasks)), 2))
    key_prefix = f"ko_tasks_{project}_{side}_{selected_dp_no}"
    
    # Initialize KO session state for this DP's tasks
    if f"{key_prefix}_idx" not in s:
        s[f"{key_prefix}_idx"] = 0
        s[f"{key_prefix}_scores"] = {i: 1 for i in range(len(dp_tasks))}
    
    # Reset if DP changed
    current_dp_key = f"{key_prefix}_current_dp"
    if s.get(current_dp_key) != selected_dp_no:
        s[f"{key_prefix}_idx"] = 0
        s[f"{key_prefix}_scores"] = {i: 1 for i in range(len(dp_tasks))}
        s[current_dp_key] = selected_dp_no
    
    idx = s[f"{key_prefix}_idx"]
    scores = s[f"{key_prefix}_scores"]
    
    # KO Voting UI
    if idx < len(pairs):
        a_idx, b_idx = pairs[idx]
        task_a = dp_tasks[a_idx]
        task_b = dp_tasks[b_idx]
        
        # Get task names
        task_a_name = (task_a.get("description") or task_a.get("Desc") or task_a.get("Name") or 
                      task_a.get("Task Name") or task_a.get("desc") or task_a.get("name") or 
                      f"Task {a_idx+1}")
        task_b_name = (task_b.get("description") or task_b.get("Desc") or task_b.get("Name") or 
                      task_b.get("Task Name") or task_b.get("desc") or task_b.get("name") or 
                      f"Task {b_idx+1}")
        
        st.markdown(f"**Comparison {idx+1} of {len(pairs)}**")
        st.markdown("*Which task is more important/critical for achieving the DP objective?*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div style="background: #1e40af; color: white; padding: 15px; border-radius: 10px; text-align: center;">
                <h4 style="color: white; margin: 0;">Option A</h4>
                <p style="color: white; margin: 10px 0;">{task_a_name}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🅰️ Choose Task A", key=f"task_a_{idx}", type="primary"):
                scores[a_idx] += 1
                s[f"{key_prefix}_idx"] += 1
                st.rerun()
        
        with col2:
            st.markdown(f"""
            <div style="background: #dc2626; color: white; padding: 15px; border-radius: 10px; text-align: center;">
                <h4 style="color: white; margin: 0;">Option B</h4>
                <p style="color: white; margin: 10px 0;">{task_b_name}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🅱️ Choose Task B", key=f"task_b_{idx}", type="primary"):
                scores[b_idx] += 1
                s[f"{key_prefix}_idx"] += 1
                st.rerun()
        
        # Progress indicator
        progress = (idx + 1) / len(pairs)
        st.progress(progress)
        st.caption(f"Progress: {idx+1}/{len(pairs)} comparisons completed")
        
    else:
        # All pairs compared, compute weights
        st.subheader("🎉 Comparison Complete!")
        
        # Calculate weights based on scores
        total_score = sum(scores.values()) if scores else 1
        
        # Update task weights
        updated_tasks = []
        for i, task in enumerate(dp_tasks):
            if i in scores:
                # Calculate percentage weight
                weight_percentage = (scores[i] / total_score) * 100
                
                # Update task with new weight
                task["Weight"] = round(weight_percentage, 2)
                task["weight"] = round(weight_percentage, 2)
                task["stated"] = round(weight_percentage, 2)
                task["Stated %"] = round(weight_percentage, 2)
                
                updated_tasks.append({
                    "name": (task.get("description") or task.get("Desc") or task.get("Name") or 
                            task.get("Task Name") or task.get("desc") or task.get("name") or 
                            f"Task {i+1}"),
                    "score": scores[i],
                    "weight": round(weight_percentage, 2)
                })
        
        # Update main tasks list
        for i, task in enumerate(tasks):
            if str(get_task_dp(task)) == str(selected_dp_no):
                # Find corresponding updated task
                for j, dp_task in enumerate(dp_tasks):
                    if task is dp_task or (
                        task.get("description") == dp_task.get("description") and
                        task.get("Name") == dp_task.get("Name")
                    ):
                        tasks[i] = dp_task
                        break
        
        # Save updated data
        data["tasks"] = tasks
        save_project(project, side, data)
        
        st.success(f"✅ KO Method completed! Task weights updated for DP {selected_dp_no}")
        
        # Display results
        st.subheader("📊 Calculated Task Weights")
        
        # Results table
        col1, col2, col3 = st.columns(3)
        col1.markdown("**Task Name**")
        col2.markdown("**Score**") 
        col3.markdown("**Weight (%)**")
        
        for task_result in updated_tasks:
            col1.write(task_result["name"])
            col2.write(task_result["score"])
            col3.write(f"{task_result['weight']}%")
        
        st.divider()
        
        # Control buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Restart KO for this DP", type="secondary"):
                s[f"{key_prefix}_idx"] = 0
                s[f"{key_prefix}_scores"] = {i: 1 for i in range(len(dp_tasks))}
                st.rerun()
        
        with col2:
            if st.button("🎯 Select Different DP", type="secondary"):
                # Clear current session state to allow new DP selection
                keys_to_clear = [k for k in s.keys() if k.startswith(f"ko_tasks_{project}_{side}_")]
                for key in keys_to_clear:
                    del s[key]
                st.rerun()

# --- Progress Entry Tab (Control Only) ---
def progress_entry_tab():
    st.header("📊 Progress Entry (Control Only)")
    st.markdown("*Update task progress and weights for all forces*")
    
    project = st.session_state.get("project")
    
    if not SIDES:
        st.warning("⚠️ No forces configured. Please use Force Manager to add forces first.")
        return
    
    # Force-based tabs for progress entry
    if len(SIDES) == 1:
        # Single force - show directly
        force = SIDES[0]
        show_force_progress_entry(project, force)
    else:
        # Multiple forces - create tabs
        tab_names = [f"{get_force_emoji(force)} {force.capitalize()}" for force in SIDES]
        tabs = st.tabs(tab_names)
        
        for i, force in enumerate(SIDES):
            with tabs[i]:
                show_force_progress_entry(project, force)

def show_force_progress_entry(project, force):
    """Show progress entry interface for a specific force"""
    
    data = load_project(project, force)
    tasks = data.get("tasks", [])
    dps = data.get("dps", [])
    
    color = FORCE_COLORS.get(force, "#0f172a")
    
    # Force header
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, {color}, {color}88); 
         padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid {color};">
        <h3 style="color: white; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);">
            {get_force_emoji(force)} {force.capitalize()} Force - Progress Update
        </h3>
        <p style="color: white; margin: 5px 0 0 0; opacity: 0.9;">
            Update task weights and progress for strategic planning
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if not tasks:
        st.info(f"📝 No tasks found for {force} force. Please add tasks in the Tasks tab first.")
        return
    
    # Group tasks by DP for organized display
    tasks_by_dp = {}
    for i, task in enumerate(tasks):
        dp_no = task.get("DP No") or task.get("dp_no") or "Unassigned"
        if str(dp_no) not in tasks_by_dp:
            tasks_by_dp[str(dp_no)] = []
        tasks_by_dp[str(dp_no)].append((i, task))
    
    # Summary statistics
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if (task.get("Progress", task.get("progress", task.get("achieved", 0))) or 0) >= 100)
    avg_progress = sum(task.get("Progress", task.get("progress", task.get("achieved", 0))) or 0 for task in tasks) / total_tasks if total_tasks > 0 else 0
    
    # Summary cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📋 Total Tasks", total_tasks)
    with col2:
        st.metric("✅ Completed Tasks", completed_tasks)
    with col3:
        st.metric("📈 Average Progress", f"{avg_progress:.1f}%")
    
    st.divider()
    
    # Display tasks by DP with progress update interface
    for dp_no, dp_tasks in sorted(tasks_by_dp.items()):
        # Find DP details
        dp_name = "Unknown DP"
        dp_objective = "Unknown Objective"
        for dp in dps:
            if str(dp.get("DP No", "") or dp.get("dp_no", "")) == str(dp_no):
                dp_name = dp.get("Name", f"DP {dp_no}")
                dp_objective = dp.get("Objective", "Unknown Objective")
                break
        
        with st.expander(f"🎯 DP {dp_no}: {dp_name} │ {dp_objective} │ {len(dp_tasks)} Tasks", expanded=True):
            if not dp_tasks:
                st.info(f"No tasks found for DP {dp_no}")
                continue
                
            for task_idx, (original_idx, task) in enumerate(dp_tasks):
                # Get task name with fallback
                task_name = (task.get("description") or task.get("Desc") or task.get("Name") or 
                           task.get("Task Name") or task.get("desc") or task.get("name") or 
                           task.get("task name") or task.get("Task") or task.get("task") or
                           task.get("Description") or f"Task {task.get('Task No', task_idx+1)}")
                
                # Task progress card
                current_progress = task.get("Progress", task.get("progress", task.get("achieved", 0))) or 0
                try:
                    current_progress = float(str(current_progress).replace('%', '')) if current_progress else 0
                except:
                    current_progress = 0
                    
                task_color = "#38a169" if current_progress >= 75 else "#e53e3e" if current_progress < 25 else "#d69e2e"
                
                st.markdown(f"""
                <div style="background: {task_color}; color: white; padding: 12px; border-radius: 8px; margin-bottom: 15px;">
                    <h4 style="color: white; margin: 0;">🔹 Task {task_idx+1}: {task_name}</h4>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">Current Progress: {current_progress:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Two-column layout for progress interface
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("**📊 Progress Controls**")
                    
                    # Current values with proper handling
                    current_weight = task.get("stated") or task.get("Weight") or task.get("weight") or task.get("Wt") or task.get("wt") or 0
                    
                    # Handle string percentages
                    try:
                        current_weight = float(str(current_weight).replace('%', '')) if current_weight else 0
                    except:
                        current_weight = 0
                    
                    # Progress update controls
                    unique_key = f"progress_{force}_{dp_no}_{original_idx}"
                    
                    new_weight = st.slider(
                        "Task Weight (%)", 
                        0.0, 100.0, 
                        float(current_weight), 
                        step=0.1,
                        key=f"weight_{unique_key}",
                        help="Strategic importance and priority of this task"
                    )
                    
                    new_progress = st.slider(
                        "Progress Achieved (%)", 
                        0.0, 100.0, 
                        float(current_progress), 
                        step=0.1,
                        key=f"progress_{unique_key}",
                        help="Actual completion percentage"
                    )
                    
                    # Additional intangible assessment
                    intangible = st.selectbox(
                        "Intangible Assessment",
                        ["nil", "partial", "complete"],
                        index=["nil", "partial", "complete"].index(task.get("Intangible", "nil")),
                        key=f"intangible_{unique_key}",
                        help="Qualitative assessment beyond measurable progress"
                    )
                
                with col2:
                    st.markdown("**📝 Task Information**")
                    
                    # Task details in organized format
                    st.markdown(f"""
                    **Current Metrics:**
                    - Weight: {current_weight}%
                    - Progress: {current_progress}%
                    - Assessment: {task.get('Intangible', 'nil').capitalize()}
                    
                    **Task Details:**
                    - Force Group: {task.get('Force Group', 'Not specified')}
                    - Type: {task.get('Type', 'Not specified')}
                    - Criteria: {task.get('Criteria', 'Not specified')}
                    """)
                    
                    # Update button
                    if st.button(f"💾 Update Progress", key=f"save_{unique_key}", type="primary"):
                        # Update task with new values
                        updated_task = tasks[original_idx].copy()
                        
                        # Update multiple key formats for compatibility
                        updated_task["Weight"] = new_weight
                        updated_task["weight"] = new_weight
                        updated_task["stated"] = new_weight
                        updated_task["Stated %"] = new_weight
                        
                        updated_task["Progress"] = new_progress
                        updated_task["progress"] = new_progress
                        updated_task["achieved"] = new_progress
                        updated_task["Achieved %"] = new_progress
                        updated_task["Progress %"] = new_progress
                        
                        updated_task["Intangible"] = intangible
                        
                        # Save updated task
                        tasks[original_idx] = updated_task
                        data["tasks"] = tasks
                        save_project(project, force, data)
                        
                        st.success(f"✅ Task '{task_name}' progress updated successfully!")
                        st.balloons()
                        st.rerun()
                
                st.divider()

# --- Dashboard Tab (Control Only) ---
def dashboard_tab():
    st.header("📊 Control Dashboard")
    st.markdown("*Real-time operational status and progress monitoring for all forces*")
    
    project = st.session_state.get("project")
    rag = st.session_state.get("rag", {"red": 40, "amber": 70})
    
    if not SIDES:
        st.warning("⚠️ No forces configured yet. Please use Force Manager to add forces first.")
        return
    
    # Create tabs for different views
    if len(SIDES) == 1:
        # If only one force, show detailed view directly
        force = SIDES[0]
        show_force_dashboard(force, project, rag)
    else:
        # Multiple forces - create tabs
        tab_names = ["📈 Overview"] + [f"{get_force_emoji(side)} {side.capitalize()}" for side in SIDES]
        tabs = st.tabs(tab_names)
        
        # Overview tab
        with tabs[0]:
            show_overview_dashboard(project, rag)
        
        # Individual force tabs
        for i, side in enumerate(SIDES):
            with tabs[i + 1]:
                show_force_dashboard(side, project, rag)

def get_force_emoji(force_name):
    """Get appropriate emoji for force"""
    emoji_map = {
        "blue": "🔵", "red": "🔴", "yellow": "🟡", "green": "🟢", 
        "orange": "🟠", "purple": "🟣", "brown": "🟤", "black": "⚫"
    }
    return emoji_map.get(force_name.lower(), "🔶")

def show_overview_dashboard(project, rag):
    """Show high-level overview of all forces"""
    
    # Create tabs for different progress types
    dp_tab, phase_tab, obj_tab = st.tabs(["🎯 DP Progress", "⏱️ Phase Progress", "🎖️ Objective Progress"])
    
    # DP Progress Tab
    with dp_tab:
        st.subheader("🎯 All Forces DP Summary")
        st.markdown("*Quick overview of Decision Point status across all forces*")
        
        # Force status cards for DP
        cols = st.columns(min(len(SIDES), 4))  # Max 4 columns
        overall_dp_stats = {"total_items": 0, "red_count": 0, "amber_count": 0, "green_count": 0}
        
        for idx, side in enumerate(SIDES):
            data = load_project(project, side)
            progress = compute_progress(data)
            
            with cols[idx % len(cols)]:
                color = FORCE_COLORS.get(side, "#8b5cf6")
                
                # Calculate DP summary
                dp_progress = list(progress["dp"].values()) if progress["dp"] else [0]
                avg_progress = sum(dp_progress) / len(dp_progress) if dp_progress else 0
                total_items = len(dp_progress)
                
                # Count RAG status
                red_count = sum(1 for v in dp_progress if v < rag["red"])
                amber_count = sum(1 for v in dp_progress if rag["red"] <= v < rag["amber"])
                green_count = sum(1 for v in dp_progress if v >= rag["amber"])
                
                # Update overall stats
                overall_dp_stats["total_items"] += total_items
                overall_dp_stats["red_count"] += red_count
                overall_dp_stats["amber_count"] += amber_count
                overall_dp_stats["green_count"] += green_count
                
                # Force status card
                st.markdown(f"""
                <div style="background: {color}; color: white; padding: 16px; border-radius: 10px; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: white;">{get_force_emoji(side)} {side.capitalize()}</h4>
                    <h2 style="margin: 5px 0; color: white;">{avg_progress:.1f}%</h2>
                    <p style="margin: 0; color: white; opacity: 0.9;">Average DP Progress</p>
                </div>
                """, unsafe_allow_html=True)
                
                # RAG status breakdown
                st.markdown("**Status Breakdown:**")
                if green_count > 0:
                    st.markdown(f"🟢 {green_count} Green")
                if amber_count > 0:
                    st.markdown(f"🟡 {amber_count} Amber") 
                if red_count > 0:
                    st.markdown(f"🔴 {red_count} Red")
    
    # Phase Progress Tab
    with phase_tab:
        st.subheader("⏱️ All Forces Phase Summary")
        st.markdown("*Quick overview of Phase execution status across all forces*")
        
        # Force status cards for Phase
        cols = st.columns(min(len(SIDES), 4))  # Max 4 columns
        overall_phase_stats = {"total_items": 0, "red_count": 0, "amber_count": 0, "green_count": 0}
        
        for idx, side in enumerate(SIDES):
            data = load_project(project, side)
            progress = compute_progress(data)
            
            with cols[idx % len(cols)]:
                color = FORCE_COLORS.get(side, "#8b5cf6")
                
                # Calculate Phase summary
                phase_progress = list(progress["phase"].values()) if progress["phase"] else [0]
                avg_progress = sum(phase_progress) / len(phase_progress) if phase_progress else 0
                total_items = len(phase_progress)
                
                # Count RAG status
                red_count = sum(1 for v in phase_progress if v < rag["red"])
                amber_count = sum(1 for v in phase_progress if rag["red"] <= v < rag["amber"])
                green_count = sum(1 for v in phase_progress if v >= rag["amber"])
                
                # Update overall stats
                overall_phase_stats["total_items"] += total_items
                overall_phase_stats["red_count"] += red_count
                overall_phase_stats["amber_count"] += amber_count
                overall_phase_stats["green_count"] += green_count
                
                # Force status card
                st.markdown(f"""
                <div style="background: {color}; color: white; padding: 16px; border-radius: 10px; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: white;">{get_force_emoji(side)} {side.capitalize()}</h4>
                    <h2 style="margin: 5px 0; color: white;">{avg_progress:.1f}%</h2>
                    <p style="margin: 0; color: white; opacity: 0.9;">Average Phase Progress</p>
                </div>
                """, unsafe_allow_html=True)
                
                # RAG status breakdown
                st.markdown("**Status Breakdown:**")
                if green_count > 0:
                    st.markdown(f"🟢 {green_count} Green")
                if amber_count > 0:
                    st.markdown(f"🟡 {amber_count} Amber") 
                if red_count > 0:
                    st.markdown(f"🔴 {red_count} Red")
    
    # Objective Progress Tab
    with obj_tab:
        st.subheader("🎖️ All Forces Objective Summary")
        st.markdown("*Quick overview of Objective achievement status across all forces*")
        
        # Force status cards for Objectives
        cols = st.columns(min(len(SIDES), 4))  # Max 4 columns
        overall_obj_stats = {"total_items": 0, "red_count": 0, "amber_count": 0, "green_count": 0}
        
        for idx, side in enumerate(SIDES):
            data = load_project(project, side)
            progress = compute_progress(data)
            
            with cols[idx % len(cols)]:
                color = FORCE_COLORS.get(side, "#8b5cf6")
                
                # Calculate Objective summary
                obj_progress = list(progress["objective"].values()) if progress["objective"] else [0]
                avg_progress = sum(obj_progress) / len(obj_progress) if obj_progress else 0
                total_items = len(obj_progress)
                
                # Count RAG status
                red_count = sum(1 for v in obj_progress if v < rag["red"])
                amber_count = sum(1 for v in obj_progress if rag["red"] <= v < rag["amber"])
                green_count = sum(1 for v in obj_progress if v >= rag["amber"])
                
                # Update overall stats
                overall_obj_stats["total_items"] += total_items
                overall_obj_stats["red_count"] += red_count
                overall_obj_stats["amber_count"] += amber_count
                overall_obj_stats["green_count"] += green_count
                
                # Force status card
                st.markdown(f"""
                <div style="background: {color}; color: white; padding: 16px; border-radius: 10px; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: white;">{get_force_emoji(side)} {side.capitalize()}</h4>
                    <h2 style="margin: 5px 0; color: white;">{avg_progress:.1f}%</h2>
                    <p style="margin: 0; color: white; opacity: 0.9;">Average Objective Progress</p>
                </div>
                """, unsafe_allow_html=True)
                
                # RAG status breakdown
                st.markdown("**Status Breakdown:**")
                if green_count > 0:
                    st.markdown(f"🟢 {green_count} Green")
                if amber_count > 0:
                    st.markdown(f"🟡 {amber_count} Amber") 
                if red_count > 0:
                    st.markdown(f"🔴 {red_count} Red")
    


def show_force_dashboard(side, project, rag):
    """Show detailed dashboard for a specific force"""
    st.subheader(f"{get_force_emoji(side)} {side.capitalize()} Force - Detailed Analysis")
    
    data = load_project(project, side)
    progress = compute_progress(data)
    
    if not any([progress.get("dp"), progress.get("objective"), progress.get("phase")]):
        st.info(f"No data available for {side.capitalize()} force. Please configure objectives, phases, and DPs first.")
        return
    
    # Create sub-tabs for different chart types
    chart_tab1, chart_tab2, chart_tab3, chart_tab4 = st.tabs(["🎯 Decisive Points", "🎖️ Objectives", "⏱️ Phases", "📋 Summary"])
    
    with chart_tab1:
        show_dp_analysis(progress, data, rag, side)
    
    with chart_tab2:
        show_objective_analysis(progress, side)
    
    with chart_tab3:
        show_phase_analysis(progress, side)
    
    with chart_tab4:
        show_force_summary(progress, data, side)

def show_dp_analysis(progress, data, rag, side):
    """Show DP analysis charts"""
    if not progress.get("dp"):
        st.info("No Decisive Points configured for this force.")
        return
    
    dp_vals = list(progress["dp"].values())
    dp_numbers = list(progress["dp"].keys())
    
    # Get DP names from the data and create clean labels
    dps_data = data.get("dps", [])
    dp_labels = []
    for dp_no in dp_numbers:
        dp_name = "Unknown DP"
        for dp in dps_data:
            if str(dp.get("DP No", "") or dp.get("dp_no", "")) == str(dp_no):
                dp_name = dp.get("Name", f"DP {dp_no}")
                break
        clean_name = dp_name[:40] + "..." if len(dp_name) > 40 else dp_name
        dp_labels.append(f"DP {dp_no}: {clean_name}")
    
    # Enhanced RAG coloring
    rag_colors = []
    for v in dp_vals:
        if v < rag["red"]:
            rag_colors.append("#dc2626")  # Red
        elif v < rag["amber"]:
            rag_colors.append("#f59e0b")  # Amber
        else:
            rag_colors.append("#16a34a")  # Green
    
    fig = go.Figure([go.Bar(
        y=dp_labels, 
        x=dp_vals, 
        orientation='h',
        marker_color=rag_colors,
        text=[f"{v:.1f}%" for v in dp_vals],
        textposition='inside',
        textfont=dict(color='white', size=11, family='Arial Black')
    )])
    fig.update_layout(
        title=f"DP Progress - RAG Status (🔴 <{rag['red']}% | 🟡 <{rag['amber']}% | 🟢 ≥{rag['amber']}%)", 
        xaxis_title="Progress (%)", 
        yaxis_title="Decisive Points",
        height=max(400, len(dp_labels) * 50),
        margin=dict(l=200, r=50, t=70, b=50),
        yaxis=dict(automargin=True),
        font=dict(size=11)
    )
    st.plotly_chart(fig, use_container_width=True, key=f"dp_chart_{side}")
    
    # DP Status Summary
    red_count = sum(1 for v in dp_vals if v < rag["red"])
    amber_count = sum(1 for v in dp_vals if rag["red"] <= v < rag["amber"])
    green_count = sum(1 for v in dp_vals if v >= rag["amber"])
    avg_dp_progress = sum(dp_vals) / len(dp_vals) if dp_vals else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔴 Critical DPs", red_count)
    with col2:
        st.metric("🟡 Caution DPs", amber_count)
    with col3:
        st.metric("🟢 On-Track DPs", green_count)
    with col4:
        st.metric("📊 Average DP Progress", f"{avg_dp_progress:.1f}%")

def show_objective_analysis(progress, side):
    """Show objective analysis charts"""
    if not progress.get("objective"):
        st.info("No Objectives configured for this force.")
        return
        
    obj_vals = list(progress["objective"].values())
    obj_names = list(progress["objective"].keys())
    
    # Colorful bars for objectives
    obj_colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#84cc16", "#f97316", "#ec4899", "#6366f1"]
    obj_colors = [obj_colors[i % len(obj_colors)] for i in range(len(obj_vals))]
    
    fig2 = go.Figure([go.Bar(
        y=obj_names, 
        x=obj_vals, 
        orientation='h',
        marker_color=obj_colors,
        text=[f"{v:.1f}%" for v in obj_vals],
        textposition='inside',
        textfont=dict(color='white', size=11, family='Arial Black')
    )])
    fig2.update_layout(
        title="Objective Progress Analysis",
        xaxis_title="Progress (%)",
        yaxis_title="Objectives",
        height=max(350, len(obj_names) * 60),
        margin=dict(l=150, r=50, t=50, b=50)
    )
    st.plotly_chart(fig2, use_container_width=True, key=f"obj_chart_{side}")
    
    # Objective metrics
    avg_obj_progress = sum(obj_vals) / len(obj_vals) if obj_vals else 0
    st.metric("Average Objective Progress", f"{avg_obj_progress:.1f}%")

def show_phase_analysis(progress, side):
    """Show phase analysis charts"""
    if not progress.get("phase"):
        st.info("No Phases configured for this force.")
        return
        
    phase_vals = list(progress["phase"].values())
    phase_names = list(progress["phase"].keys())
    
    # Colorful gradient bars for phases
    phase_colors = ["#059669", "#7c3aed", "#dc2626", "#2563eb", "#d97706", "#0891b2", "#be185d", "#4338ca", "#65a30d", "#c2410c"]
    phase_colors = [phase_colors[i % len(phase_colors)] for i in range(len(phase_vals))]
    
    fig3 = go.Figure([go.Bar(
        y=phase_names, 
        x=phase_vals, 
        orientation='h',
        marker_color=phase_colors,
        text=[f"{v:.1f}%" for v in phase_vals],
        textposition='inside',
        textfont=dict(color='white', size=12, family='Arial Black')
    )])
    fig3.update_layout(
        title="Phase Progress Timeline", 
        xaxis_title="Progress (%)", 
        yaxis_title="Phases",
        height=max(300, len(phase_names) * 70),
        margin=dict(l=120, r=50, t=50, b=50),
        yaxis=dict(automargin=True),
        font=dict(size=11)
    )
    st.plotly_chart(fig3, use_container_width=True, key=f"phase_chart_{side}")
    
    # Phase metrics
    avg_phase_progress = sum(phase_vals) / len(phase_vals) if phase_vals else 0
    st.metric("Average Phase Progress", f"{avg_phase_progress:.1f}%")

def show_force_summary(progress, data, side):
    """Show comprehensive force summary"""
    st.markdown("### 📋 Force Summary Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Progress Metrics**")
        
        # Calculate averages
        dp_vals = list(progress["dp"].values()) if progress.get("dp") else []
        obj_vals = list(progress["objective"].values()) if progress.get("objective") else []
        phase_vals = list(progress["phase"].values()) if progress.get("phase") else []
        
        avg_dp = sum(dp_vals) / len(dp_vals) if dp_vals else 0
        avg_obj = sum(obj_vals) / len(obj_vals) if obj_vals else 0
        avg_phase = sum(phase_vals) / len(phase_vals) if phase_vals else 0
        
        st.metric("Decisive Points", f"{avg_dp:.1f}%", f"{len(dp_vals)} total")
        st.metric("Objectives", f"{avg_obj:.1f}%", f"{len(obj_vals)} total")
        st.metric("Phases", f"{avg_phase:.1f}%", f"{len(phase_vals)} total")
    
    with col2:
        st.markdown("**📈 Quick Stats**")
        
        # Count elements
        total_tasks = len(data.get("tasks", []))
        total_dps = len(data.get("dps", []))
        total_objectives = len(data.get("objectives", []))
        
        st.info(f"**Tasks:** {total_tasks}")
        st.info(f"**Decision Points:** {total_dps}") 
        st.info(f"**Objectives:** {total_objectives}")
        
        # Display individual progress metrics instead of overall readiness
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🎯 DP Progress", f"{avg_dp:.1f}%")
        with col2:
            st.metric("⏱️ Phase Progress", f"{avg_phase:.1f}%")
        with col3:
            st.metric("🎖️ Objective Progress", f"{avg_obj:.1f}%")

def show_quick_progress_preview(project):
    """Show quick progress preview for all forces across DP, Phases, and Objectives"""
    
    # Create three columns for DP, Phase, and Objective overview
    col_dp, col_phase, col_obj = st.columns(3)
    
    with col_dp:
        st.markdown("### 🎯 DP Progress Overview")
        show_progress_comparison_chart(project, "dp", "Decisive Points")
    
    with col_phase:
        st.markdown("### ⏱️ Phase Progress Overview")
        show_progress_comparison_chart(project, "phase", "Phases")
    
    with col_obj:
        st.markdown("### 🎖️ Objective Progress Overview")
        show_progress_comparison_chart(project, "objective", "Objectives")

def show_progress_comparison_chart(project, progress_type, title):
    """Show comparison chart for specific progress type across all forces"""
    import plotly.graph_objects as go
    
    force_names = []
    progress_values = []
    colors = []
    
    for side in SIDES:
        data = load_project(project, side)
        progress = compute_progress(data)
        
        if progress.get(progress_type):
            # Calculate average progress for this force
            values = list(progress[progress_type].values())
            avg_progress = sum(values) / len(values) if values else 0
            
            force_names.append(f"{get_force_emoji(side)} {side.capitalize()}")
            progress_values.append(avg_progress)
            colors.append(FORCE_COLORS.get(side, "#8b5cf6"))
        else:
            force_names.append(f"{get_force_emoji(side)} {side.capitalize()}")
            progress_values.append(0)
            colors.append("#cccccc")  # Gray for no data
    
    if not progress_values or all(v == 0 for v in progress_values):
        st.info(f"No {title.lower()} data available")
        return
    
    # Create horizontal bar chart
    fig = go.Figure([go.Bar(
        y=force_names,
        x=progress_values,
        orientation='h',
        marker_color=colors,
        text=[f"{v:.1f}%" for v in progress_values],
        textposition='inside',
        textfont=dict(color='white', size=10, family='Arial Black')
    )])
    
    fig.update_layout(
        title=f"Average {title} Progress",
        xaxis_title="Progress (%)",
        height=max(200, len(force_names) * 60),
        margin=dict(l=120, r=30, t=50, b=30),
        font=dict(size=9),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True, key=f"preview_{progress_type}")
    
    # Show summary statistics
    if progress_values:
        avg_all = sum(progress_values) / len(progress_values)
        max_progress = max(progress_values)
        min_progress = min(progress_values)
        
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 8px; border-radius: 6px; margin-top: 10px;">
            <small>
                <b>Avg:</b> {avg_all:.1f}% | 
                <b>Max:</b> {max_progress:.1f}% | 
                <b>Min:</b> {min_progress:.1f}%
            </small>
        </div>
        """, unsafe_allow_html=True)

def show_compact_progress_overview(project):
    """Show compact table view of all progress types for all forces"""
    
    # Collect data for all forces
    progress_data = []
    
    for side in SIDES:
        data = load_project(project, side)
        progress = compute_progress(data)
        
        # Calculate averages for each progress type
        dp_avg = 0
        if progress.get("dp"):
            dp_values = list(progress["dp"].values())
            dp_avg = sum(dp_values) / len(dp_values) if dp_values else 0
        
        phase_avg = 0
        if progress.get("phase"):
            phase_values = list(progress["phase"].values())
            phase_avg = sum(phase_values) / len(phase_values) if phase_values else 0
        
        obj_avg = 0
        if progress.get("objective"):
            obj_values = list(progress["objective"].values())
            obj_avg = sum(obj_values) / len(obj_values) if obj_values else 0
        
        progress_data.append({
            "Force": f"{get_force_emoji(side)} {side.capitalize()}",
            "DP Progress": f"{dp_avg:.1f}%",
            "Phase Progress": f"{phase_avg:.1f}%",
            "Objective Progress": f"{obj_avg:.1f}%",
            "Force Color": FORCE_COLORS.get(side, "#8b5cf6"),
            "DP_Raw": dp_avg,
            "Phase_Raw": phase_avg,
            "Obj_Raw": obj_avg
        })
    
    if not progress_data:
        st.info("No force data available.")
        return
    
    # Create DataFrame for display
    summary_df = pd.DataFrame([
        {
            "Force": row["Force"],
            "🎯 DP Progress": row["DP Progress"],
            "⏱️ Phase Progress": row["Phase Progress"], 
            "🎖️ Objective Progress": row["Objective Progress"]
        }
        for row in progress_data
    ])
    
    # Display as colored table using force-specific styling
    st.markdown("### 📊 All Forces Progress Summary")
    
    # Use our existing display_force_table function with control styling
    display_force_table(summary_df, use_container_width=True, force_type="control")
    
    # Summary statistics below the table
    st.markdown("---")
    col_summary1, col_summary2, col_summary3 = st.columns(3)
    
    avg_dp = sum(row["DP_Raw"] for row in progress_data) / len(progress_data)
    avg_phase = sum(row["Phase_Raw"] for row in progress_data) / len(progress_data)
    avg_obj = sum(row["Obj_Raw"] for row in progress_data) / len(progress_data)
    
    with col_summary1:
        st.metric("🎯 Avg DP Progress", f"{avg_dp:.1f}%")
    with col_summary2:
        st.metric("⏱️ Avg Phase Progress", f"{avg_phase:.1f}%")
    with col_summary3:
        st.metric("🎖️ Avg Objective Progress", f"{avg_obj:.1f}%")

# --- Control Panel Tab ---
def control_panel_tab():
    st.header("⚙️ Control Panel")
    st.markdown("*Centralized command and control interface for all force operations*")
    
    # Create organized tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["🎛️ System Settings", "🔐 Security Management", "👥 Team Management", "📊 System Status"])
    
    with tab1:
        st.subheader("📊 RAG Threshold Configuration")
        st.markdown("*Set performance thresholds for Red-Amber-Green status indicators*")
        
        col1, col2 = st.columns(2)
        rag = st.session_state.get("rag", {"red": 40, "amber": 70})
        
        with col1:
            red = st.slider("🔴 Red Threshold (%)", 0, 100, int(rag["red"]), 
                           help="Below this percentage shows as RED status")
        with col2:
            amber = st.slider("🟡 Amber Threshold (%)", 0, 100, int(rag["amber"]), 
                             help="Below this percentage shows as AMBER status")
        
        st.session_state["rag"] = {"red": red, "amber": amber}
        
        # Show current settings in a nice display
        st.markdown("**Current Thresholds:**")
        col_display1, col_display2, col_display3 = st.columns(3)
        with col_display1:
            st.markdown(f"🔴 **Red:** 0-{red}%")
        with col_display2:
            st.markdown(f"🟡 **Amber:** {red+1}-{amber}%")
        with col_display3:
            st.markdown(f"🟢 **Green:** {amber+1}-100%")
    
    with tab2:
        st.subheader("🔐 PIN & Access Management")
        st.markdown("*Configure security credentials for all force access*")
        
        project = st.session_state.get("project")
        
        # Control PIN section
        with st.expander("🎯 Control Access", expanded=True):
            pwd_control = st.text_input("Control PIN", 
                                      value=st.session_state.get("pin_control", "9999"), 
                                      type="password", 
                                      key="pin_control_panel_cp",
                                      help="Master control access PIN")
        
        # Forces PIN section
        if SIDES:
            with st.expander(f"⚔️ Force Access ({len(SIDES)} forces configured)", expanded=True):
                force_pins = {}
                for force in SIDES:
                    st.session_state.setdefault(f"pin_{force}", "0000")
                    force_pins[force] = st.text_input(
                        f"{force.capitalize()} Force PIN", 
                        value=st.session_state.get(f"pin_{force}", "0000"), 
                        type="password", 
                        key=f"pin_{force}_panel_cp",
                        help=f"Access PIN for {force.capitalize()} force operations"
                    )
                
                # Save all PINs button
                if st.button("💾 Save All PINs", key="save_all_pins_panel_cp", type="primary"):
                    st.session_state["pin_control"] = pwd_control
                    for force, pin_val in force_pins.items():
                        st.session_state[f"pin_{force}"] = pin_val
                    st.success("✅ All PINs updated successfully!")
        else:
            st.info("ℹ️ No forces configured. Use Force Manager to add forces first.")
    
    with tab3:
        st.subheader("👥 AHP Team Management")
        st.markdown("*Manage team members and their roles for project credits and documentation*")
        
        # Load team data from persistent file
        if "ahp_team" not in st.session_state:
            st.session_state["ahp_team"] = load_ahp_team()
        
        team = st.session_state["ahp_team"]
        
        # Team overview
        with st.expander(f"📋 Team Overview ({len([m for m in team if m['name'].strip()])} active members)", expanded=True):
            if team:
                # Display current team members in a clean format
                for i, member in enumerate(team):
                    col1, col2, col3 = st.columns([3, 3, 1])
                    with col1:
                        new_name = st.text_input("Name", value=member["name"], key=f"cp_team_name_{i}", placeholder="Enter member name")
                    with col2:
                        new_role = st.text_input("Role/Position", value=member["role"], key=f"cp_team_role_{i}", placeholder="Enter role or position")
                    with col3:
                        st.markdown("<br>", unsafe_allow_html=True)  # Align with inputs
                        if st.button("🗑️", key=f"delete_member_{i}", help="Remove this member"):
                            team.pop(i)
                            st.session_state["ahp_team"] = team
                            save_ahp_team(team)
                            st.success("Team member removed!")
                            st.rerun()
                    
                    # Update team member data and auto-save if changed
                    if team[i]["name"] != new_name or team[i]["role"] != new_role:
                        team[i]["name"] = new_name
                        team[i]["role"] = new_role
                        st.session_state["ahp_team"] = team
                        save_ahp_team(team)
            else:
                st.info("No team members added yet. Click 'Add Team Member' to start.")
        
        # Team management actions
        col_add, col_save, col_export = st.columns(3)
        
        with col_add:
            if st.button("➕ Add Team Member", key="add_team_member_cp", type="secondary"):
                team.append({"name": "", "role": ""})
                st.session_state["ahp_team"] = team
                save_ahp_team(team)
                st.success("New team member slot added!")
                st.rerun()
        
        with col_save:
            if st.button("💾 Save Changes", key="save_team_credits_cp", type="primary"):
                # Filter out empty entries
                filtered_team = [member for member in team if member["name"].strip() or member["role"].strip()]
                st.session_state["ahp_team"] = filtered_team
                save_ahp_team(filtered_team)
                st.success("Team data saved successfully!")
                st.balloons()
        
        with col_export:
            if st.button("📥 Export Data", key="export_team_data"):
                current_team = load_ahp_team()
                team_json = json.dumps(current_team, indent=2)
                st.download_button(
                    label="Download Team Data (JSON)",
                    data=team_json,
                    file_name="ahp_team_credits.json",
                    mime="application/json",
                    key="download_team_json"
                )
    
    with tab4:
        st.subheader("📊 System Status & Information")
        st.markdown("*Current system configuration and operational status*")
        
        # System configuration overview
        col_sys1, col_sys2 = st.columns(2)
        
        with col_sys1:
            st.markdown("**🎯 Current Project**")
            current_project = st.session_state.get("project", "None")
            st.info(f"Active Project: **{current_project}**")
            
            st.markdown("**⚔️ Configured Forces**")
            if SIDES:
                for force in SIDES:
                    color = FORCE_COLORS.get(force, "#8b5cf6")
                    st.markdown(f"<div style='background:{color};color:white;padding:4px 8px;border-radius:4px;margin:2px 0;display:inline-block;'>{force.capitalize()}</div>", unsafe_allow_html=True)
            else:
                st.warning("No forces configured")
        
        with col_sys2:
            st.markdown("**📈 Team Status**")
            team = st.session_state.get("ahp_team", [])
            active_members = len([m for m in team if m['name'].strip()])
            st.metric("Active Team Members", active_members)
            
            st.markdown("**💾 Data Status**")
            if os.path.exists(AHP_TEAM_FILE):
                st.success("✅ Team data saved")
            else:
                st.info("💾 Team data not saved")
        
        # RAG settings display
        st.markdown("**� Current RAG Thresholds**")
        rag = st.session_state.get("rag", {"red": 40, "amber": 70})
        col_rag1, col_rag2, col_rag3 = st.columns(3)
        with col_rag1:
            st.metric("🔴 Red Zone", f"0-{rag['red']}%")
        with col_rag2:
            st.metric("🟡 Amber Zone", f"{rag['red']+1}-{rag['amber']}%")
        with col_rag3:
            st.metric("🟢 Green Zone", f"{rag['amber']+1}-100%")

# --- Force Manager Tab ---
def force_manager_tab():
    st.header("Force Manager")
    global SIDES
    st.write("Current Forces:")
    if SIDES:
        cols = st.columns(len(SIDES))
        for idx, side in enumerate(SIDES):
            color = FORCE_COLORS.get(side, "#0f172a")
            with cols[idx]:
                st.markdown(f"<div style='background:{color};color:#fff;padding:8px;border-radius:8px;text-align:center;'>{side.capitalize()}</div>", unsafe_allow_html=True)
                # Allow deletion of any force (including blue and red)
                if st.button(f"Remove {side.capitalize()}", key=f"remove_{side}"):
                    SIDES.remove(side)
                    save_forces(SIDES)
                    st.success(f"Removed {side.capitalize()} force.")
                    st.rerun()
    else:
        st.info("No forces configured yet. Add forces using the form below.")
    st.markdown("---")
    st.subheader("Add New Force")
    new_force = st.text_input("Force Name (lowercase, e.g. yellow)")
    color = st.color_picker("Force Color", FORCE_COLORS.get(new_force, "#0f172a"))
    if st.button("Add Force") and new_force and new_force not in SIDES:
        SIDES.append(new_force)
        save_forces(SIDES)
        FORCE_COLORS[new_force] = color
        # Create project structure for new force in all projects
        for proj in list_projects():
            save_project(proj, new_force, DEFAULT_STRUCTURE)
        st.success(f"Added {new_force.capitalize()} force.")
        st.rerun()

# --- Main Routing ---
def main():
    global SIDES
    # Reload forces in case they were modified
    SIDES = load_forces()
    
    if "role" not in st.session_state:
        login()
        return
    if "project" not in st.session_state:
        projects = list_projects()
        if projects:
            st.session_state["project"] = projects[0]
        else:
            st.session_state["project"] = "Demo"
            for side in SIDES:
                save_project("Demo", side, DEFAULT_STRUCTURE)
    selected = sidebar()
    if selected == "Phases":
        phases_tab()
    elif selected == "Objectives":
        objectives_tab()
    elif selected == "Decisive Points":
        dps_tab()
    elif selected == "Tasks":
        tasks_tab()
    elif selected == "KO Method":
        ko_tab()
    elif selected == "Progress Entry":
        progress_entry_tab()
    elif selected == "Dashboard":
        dashboard_tab()
    elif selected == "Control Panel":
        control_panel_tab()
    elif selected == "Force Manager":
        force_manager_tab()
    elif selected == "Project Management":
        project_management()
    elif selected == "Logout":
        clear_session()
    show_footer()

if __name__ == "__main__":
    main()
