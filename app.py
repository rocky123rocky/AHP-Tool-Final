
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
import json
from datetime import datetime
from ahp_backend import *

st.set_page_config(
    page_title="COPP AHP Military Planner", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit default elements with CSS immediately after page config
st.markdown("""
<style>
/* Hide the Deploy button, hamburger menu, and header */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}
button[kind="header"] {display: none;}
[data-testid="stToolbar"] {display: none;}
.css-14xtw13.e8zbici0 {display: none;}
section[data-testid="stSidebar"] > div:first-child {padding-top: 0rem;}
</style>
""", unsafe_allow_html=True)

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

def load_independent_project(project, force):
    """Load independent force data (completely separate from control data)"""
    try:
        independent_file = f"{project}_{force}_independent.json"
        
        if os.path.exists(independent_file):
            # Load the complete independent data
            with open(independent_file, "r") as f:
                independent_data = json.load(f)
            
            # Ensure we have the complete structure by merging with base data if needed
            base_data = load_project(project, force)
            
            # Preserve independent progress but ensure we have all structural data
            merged_data = base_data.copy()
            
            # Update with independent task progress
            if "tasks" in independent_data and "tasks" in merged_data:
                for i, base_task in enumerate(merged_data["tasks"]):
                    # Find matching task in independent data
                    for ind_task in independent_data.get("tasks", []):
                        if (base_task.get("description") == ind_task.get("description") and
                            base_task.get("Name") == ind_task.get("Name")):
                            # Update with independent progress values
                            base_task.update({
                                "progress": ind_task.get("progress", 0),
                                "Progress": ind_task.get("Progress", 0),
                                "Actual Progress": ind_task.get("Actual Progress", 0),
                                "achieved": ind_task.get("achieved", 0),
                                "Achieved %": ind_task.get("Achieved %", 0),
                                "Progress %": ind_task.get("Progress %", 0),
                                "Intangible": ind_task.get("Intangible", "nil")
                            })
                            break
            
            return merged_data
        else:
            # First time - create independent copy from base structure
            base_data = load_project(project, force)
            independent_data = base_data.copy()
            
            # Reset only progress-related fields to start fresh, keep all structure
            if "tasks" in independent_data:
                for task in independent_data["tasks"]:
                    # Reset progress fields to 0 for independent tracking
                    task["progress"] = 0
                    task["Progress"] = 0
                    task["Actual Progress"] = 0
                    task["achieved"] = 0
                    task["Achieved %"] = 0
                    task["Progress %"] = 0
                    task["Intangible"] = "nil"
                    # Keep all other fields including weights, descriptions, DPs, etc.
            
            # Save this initial independent version
            save_independent_project(project, force, independent_data)
            return independent_data
            
    except Exception as e:
        st.error(f"Error loading independent data: {str(e)}")
        # Fallback to base data but reset progress
        base_data = load_project(project, force)
        if "tasks" in base_data:
            for task in base_data["tasks"]:
                task["progress"] = 0
                task["Progress"] = 0
                task["Actual Progress"] = 0
                task["achieved"] = 0
                task["Achieved %"] = 0
                task["Progress %"] = 0
                task["Intangible"] = "nil"
        return base_data

def save_independent_project(project, force, data):
    """Save complete independent force data (completely separate from control data)"""
    try:
        independent_file = f"{project}_{force}_independent.json"
        
        # Save the complete data structure for full independence
        with open(independent_file, "w") as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        st.error(f"Error saving independent data: {str(e)}")

def load_theater_config(project):
    """Load theater configurations for the project"""
    try:
        theater_file = f"{project}_theaters.json"
        if os.path.exists(theater_file):
            with open(theater_file, "r") as f:
                config = json.load(f)
                
                # Ensure all available forces are either in theaters or unassigned
                available_forces = get_available_forces(project)
                assigned_forces = [force for theater in config["theaters"].values() for force in theater["forces"]]
                
                # Add any new forces to unassigned list
                for force in available_forces:
                    if force not in assigned_forces and force not in config.get("unassigned_forces", []):
                        config.setdefault("unassigned_forces", []).append(force)
                
                # Remove forces that no longer exist
                config["unassigned_forces"] = [f for f in config.get("unassigned_forces", []) if f in available_forces]
                
                return config
        else:
            # Default theater structure with all available forces as unassigned
            available_forces = get_available_forces(project)
            return {
                "theaters": {},
                "unassigned_forces": available_forces
            }
    except Exception as e:
        st.error(f"Error loading theater config: {str(e)}")
        return {"theaters": {}, "unassigned_forces": []}

def save_theater_config(project, theater_config):
    """Save theater configurations for the project"""
    try:
        theater_file = f"{project}_theaters.json"
        with open(theater_file, "w") as f:
            json.dump(theater_config, f, indent=2)
    except Exception as e:
        st.error(f"Error saving theater config: {str(e)}")

def get_available_forces(project):
    """Get list of available forces from the global SIDES list"""
    global SIDES
    if not SIDES:
        SIDES = load_forces()  # Reload if needed
    return SIDES.copy()  # Return a copy of the forces list

def calculate_theater_progress(project, theater_forces):
    """Calculate average objective progress for forces in the theater from Control's perspective"""
    if not theater_forces:
        return 0
    
    total_progress = 0
    valid_forces = 0
    
    for force in theater_forces:
        try:
            # Load the Control's data for this specific force (not independent data)
            force_data = load_project(project, force)
            
            if not force_data:
                continue
                
            # Use compute_progress to get calculated progress values (same as Control dashboard)
            progress = compute_progress(force_data)
            
            if progress and "objective" in progress:
                obj_progress_dict = progress["objective"]
                if obj_progress_dict:
                    # Calculate average objective progress for this force
                    obj_progress_values = list(obj_progress_dict.values())
                    if obj_progress_values:
                        force_obj_progress = sum(obj_progress_values) / len(obj_progress_values)
                        total_progress += force_obj_progress
                        valid_forces += 1
                    
        except Exception as e:
            st.error(f"Error calculating progress for force {force}: {str(e)}")
            continue
    
    # Return average objective progress across all forces in the theater
    return total_progress / valid_forces if valid_forces > 0 else 0

def sort_dps_numerically(dps):
    """Sort DPs numerically by DP No"""
    return sorted(dps, key=lambda dp: int(dp.get('DP No', 0)) if str(dp.get('DP No', '')).isdigit() else float('inf'))

def sort_phases_numerically(phases):
    """Sort phases numerically by Phase No"""
    return sorted(phases, key=lambda phase: int(phase.get('Phase No', 0)) if str(phase.get('Phase No', '')).isdigit() else float('inf'))

def sort_objectives_numerically(objectives):
    """Sort objectives numerically by Objective No"""
    return sorted(objectives, key=lambda obj: int(obj.get('Objective No', 0)) if str(obj.get('Objective No', '')).isdigit() else float('inf'))

def sort_tasks_numerically(tasks):
    """Sort tasks numerically by Task No"""
    return sorted(tasks, key=lambda task: int(task.get('Task No', 0)) if str(task.get('Task No', '')).isdigit() else float('inf'))

def get_numeric_sort_key(item, field_name):
    """Generic function to get numeric sort key for any field"""
    value = item.get(field_name, 0)
    try:
        return int(value) if str(value).isdigit() else float('inf')
    except:
        return float('inf')

# ==================== CHAT SYSTEM FUNCTIONS ====================
def load_messages(project):
    """Load all messages for a project"""
    try:
        messages_file = f"{project}_messages.json"
        if os.path.exists(messages_file):
            with open(messages_file, "r") as f:
                return json.load(f)
        else:
            # Default structure
            return {
                "conversations": {},  # Format: {"control_to_blue": [...], "blue_to_control": [...]}
                "last_updated": ""
            }
    except Exception as e:
        st.error(f"Error loading messages: {str(e)}")
        return {"conversations": {}, "last_updated": ""}

def save_message(project, sender, recipient, message_text):
    """Save a new message to the chat system"""
    try:
        # Load existing messages
        messages_data = load_messages(project)
        
        # Create conversation key
        conversation_key = f"{sender}_to_{recipient}"
        
        # Initialize conversation if it doesn't exist
        if conversation_key not in messages_data["conversations"]:
            messages_data["conversations"][conversation_key] = []
        
        # Create new message
        new_message = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sender": sender,
            "recipient": recipient,
            "message": message_text,
            "message_id": len(messages_data["conversations"][conversation_key]) + 1
        }
        
        # Add message to conversation
        messages_data["conversations"][conversation_key].append(new_message)
        messages_data["last_updated"] = new_message["timestamp"]
        
        # Save to file
        messages_file = f"{project}_messages.json"
        with open(messages_file, "w") as f:
            json.dump(messages_data, f, indent=2)
        
        return True
        
    except Exception as e:
        st.error(f"Error saving message: {str(e)}")
        return False

def get_conversation(project, participant1, participant2):
    """Get all messages between two participants (bidirectional)"""
    try:
        messages_data = load_messages(project)
        
        # Get messages from both directions
        conv1_key = f"{participant1}_to_{participant2}"
        conv2_key = f"{participant2}_to_{participant1}"
        
        messages = []
        
        if conv1_key in messages_data["conversations"]:
            messages.extend(messages_data["conversations"][conv1_key])
        
        if conv2_key in messages_data["conversations"]:
            messages.extend(messages_data["conversations"][conv2_key])
        
        # Sort by timestamp
        messages.sort(key=lambda x: x["timestamp"])
        
        return messages
        
    except Exception as e:
        st.error(f"Error loading conversation: {str(e)}")
        return []

def get_force_conversations(project, force):
    """Get all conversations for a specific force"""
    try:
        messages_data = load_messages(project)
        force_messages = []
        
        for conv_key, messages in messages_data["conversations"].items():
            if force in conv_key:
                force_messages.extend(messages)
        
        # Sort by timestamp
        force_messages.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return force_messages
        
    except Exception as e:
        st.error(f"Error loading force conversations: {str(e)}")
        return []

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
/* Hide the Deploy button and main menu */
#MainMenu {{visibility: hidden !important;}}
header {{visibility: hidden !important;}}
footer {{visibility: hidden !important;}}
.stDeployButton {{display: none !important;}}
button[kind="header"] {{display: none !important;}}
[data-testid="stToolbar"] {{display: none !important;}}
.viewerBadge_container__1QSob {{display: none !important;}}
.styles_viewerBadge__1yB5_ {{display: none !important;}}
.viewerBadge_link__1S137 {{display: none !important;}}
.viewerBadge_text__1JaDK {{display: none !important;}}
header[data-testid="stHeader"] {{display: none !important;}}
div[data-testid="stToolbar"] {{display: none !important;}}
div[data-testid="stDecoration"] {{display: none !important;}}
div[data-testid="stStatusWidget"] {{display: none !important;}}
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
            "💬 Chat": "Chat",
            "⚙️ Control Panel": "Control Panel",
            "👥 Force Manager": "Force Manager",
            "🏛️ Theater Command": "Theater Command",
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
            "� Force Progress Entry": "Force Progress Entry",
            "📈 Force Dashboard": "Force Dashboard",
            "💬 Chat": "Chat",
            "�🗂️ Project Management": "Project Management",
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
            st.table(sort_phases_numerically(data.get("phases", [])))
            st.write("Objectives:")
            st.table(sort_objectives_numerically(data.get("objectives", [])))
            st.write("DPs:")
            st.table(sort_dps_numerically(data.get("dps", [])))
            st.write("Tasks:")
            st.table(data.get("tasks", []))

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
                
                # Display current objectives in sequential order
                st.subheader(f"{force.capitalize()} Force Objectives")
                
                # Sort objectives numerically
                sorted_objectives = sort_objectives_numerically(objectives)
                
                objective_data = []
                for obj_idx, obj in enumerate(sorted_objectives):
                    name = obj.get("Name") or obj.get("Objective") or f"Objective {obj_idx+1}"
                    phase = obj.get("Phase") or obj.get("phase") or ""
                    obj_no = obj.get("Objective No", obj_idx + 1)
                    
                    objective_data.append({
                        "No": obj_no,
                        "Objective": str(name).strip(),
                        "Phase": str(phase).strip()
                    })
                
                df = pd.DataFrame(objective_data)
                display_force_table(df, use_container_width=True, force_type=force)
                
                # Manage objectives
                st.markdown("---")
                col_add, col_edit, col_delete = st.columns(3)
                
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
                        # Sort objectives after adding to maintain sequential order
                        data["objectives"] = sort_objectives_numerically(data["objectives"])
                        save_project(project, force, data)
                        st.success(f"✅ Objective '{new_name}' added to {force} force")
                        st.rerun()
                
                with col_edit:
                    st.markdown("**✏️ Edit Objective**")
                    if objectives:
                        sorted_objectives = sort_objectives_numerically(objectives)
                        obj_to_original_idx = {id(obj): objectives.index(obj) for obj in objectives}
                        obj_options = [f"{obj.get('Objective No', i+1)}. {obj.get('Name', 'Unnamed')}" for i, obj in enumerate(sorted_objectives)]
                        selected_sorted_idx = st.selectbox("Select Objective to Edit", range(len(sorted_objectives)), 
                                                       format_func=lambda x: obj_options[x], key=f"edit_obj_sel_{force}")
                        selected_obj = sorted_objectives[selected_sorted_idx]
                        selected_obj_idx = obj_to_original_idx[id(selected_obj)]
                        current_obj = objectives[selected_obj_idx]
                        
                        edit_obj_name = st.text_input("Objective Name", value=current_obj.get("Name", ""), key=f"edit_obj_name_{force}")
                        phases = [p.get("Name") for p in data.get("phases", [])]
                        if phases:
                            current_phase_idx = phases.index(current_obj.get("Phase")) if current_obj.get("Phase") in phases else 0
                            edit_phase = st.selectbox("Phase", phases, index=current_phase_idx, key=f"edit_obj_phase_{force}")
                        else:
                            edit_phase = current_obj.get("Phase", "")
                        
                        if st.button("💾 Save Changes", type="primary", key=f"save_edit_obj_{force}"):
                            objectives[selected_obj_idx]["Name"] = edit_obj_name
                            objectives[selected_obj_idx]["Phase"] = edit_phase
                            data["objectives"] = objectives
                            save_project(project, force, data)
                            st.success("✅ Objective updated")
                            st.rerun()
                    else:
                        st.info("No objectives to edit")
                
                with col_delete:
                    st.markdown("**🗑️ Delete Objective**")
                    if objectives:
                        # Sort objectives and create mapping for deletion
                        sorted_objectives = sort_objectives_numerically(objectives)
                        obj_to_original_idx = {id(obj): objectives.index(obj) for obj in objectives}
                        
                        obj_options = [f"{obj.get('Objective No', i+1)}. {obj.get('Name', 'Unnamed')}" for i, obj in enumerate(sorted_objectives)]
                        selected_sorted_idx = st.selectbox("Select Objective", range(len(sorted_objectives)), 
                                                       format_func=lambda x: obj_options[x], key=f"del_obj_{force}")
                        selected_obj = sorted_objectives[selected_sorted_idx]
                        selected_obj_idx = obj_to_original_idx[id(selected_obj)]
                        
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
        col_add, col_edit, col_delete = st.columns(3)
        
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
                # Sort objectives after adding to maintain sequential order
                data["objectives"] = sort_objectives_numerically(data["objectives"])
                save_project(project, side, data)
                st.success(f"✅ Objective '{name}' added")
                st.rerun()
        
        with col_edit:
            st.markdown("**✏️ Edit Objective**")
            if objectives:
                obj_options = [f"{i+1}. {obj.get('Name', 'Unnamed')}" for i, obj in enumerate(objectives)]
                selected_obj_idx = st.selectbox("Select Objective to Edit", range(len(objectives)), 
                                               format_func=lambda x: obj_options[x], key="edit_obj_sel_single")
                current_obj = objectives[selected_obj_idx]
                
                edit_obj_name = st.text_input("Objective Name", value=current_obj.get("Name", ""), key="edit_obj_name_single")
                phases = [p.get("Name") for p in data.get("phases", [])]
                if phases:
                    current_phase_idx = phases.index(current_obj.get("Phase")) if current_obj.get("Phase") in phases else 0
                    edit_phase = st.selectbox("Phase", phases, index=current_phase_idx, key="edit_obj_phase_single")
                else:
                    edit_phase = current_obj.get("Phase", "")
                
                if st.button("💾 Save Changes", type="primary", key="save_edit_obj_single"):
                    objectives[selected_obj_idx]["Name"] = edit_obj_name
                    objectives[selected_obj_idx]["Phase"] = edit_phase
                    data["objectives"] = objectives
                    save_project(project, side, data)
                    st.success("✅ Objective updated")
                    st.rerun()
            else:
                st.info("No objectives to edit")
        
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
                
                # Display current phases in sequential order
                st.subheader(f"{force.capitalize()} Force Phases")
                
                # Sort phases appropriately
                sorted_phases = sort_phases_numerically(phases)
                
                df = pd.DataFrame({
                    "No": [phase.get("Phase No", idx + 1) for idx, phase in enumerate(sorted_phases)],
                    "Phase Name": [p.get("Name") or p.get("Phase") for p in sorted_phases]
                })
                
                display_force_table(df, use_container_width=True, force_type=force)
                
                # Manage phases
                st.markdown("---")
                col_add, col_edit, col_delete = st.columns(3)
                
                with col_add:
                    st.markdown("**➕ Add New Phase**")
                    new_name = st.text_input("Phase Name", key=f"phase_name_{force}")
                    
                    if st.button(f"➕ Add to {force.capitalize()}", type="primary", key=f"add_phase_{force}") and new_name:
                        if "phases" not in data:
                            data["phases"] = []
                        data["phases"].append({"Name": new_name})
                        # Sort phases after adding to maintain sequential order
                        data["phases"] = sort_phases_numerically(data["phases"])
                        save_project(project, force, data)
                        st.success(f"✅ Phase '{new_name}' added to {force} force")
                        st.rerun()
                
                with col_edit:
                    st.markdown("**✏️ Edit Phase**")
                    if phases:
                        sorted_phases = sort_phases_numerically(phases)
                        phase_to_original_idx = {id(phase): phases.index(phase) for phase in phases}
                        phase_options = [f"{phase.get('Phase No', i+1)}. {phase.get('Name', 'Unnamed')}" for i, phase in enumerate(sorted_phases)]
                        selected_sorted_idx = st.selectbox("Select Phase to Edit", range(len(sorted_phases)), 
                                                         format_func=lambda x: phase_options[x], key=f"edit_phase_sel_{force}")
                        selected_phase = sorted_phases[selected_sorted_idx]
                        selected_phase_idx = phase_to_original_idx[id(selected_phase)]
                        current_phase = phases[selected_phase_idx]
                        
                        edit_phase_name = st.text_input("Phase Name", value=current_phase.get("Name", ""), key=f"edit_phase_name_{force}")
                        
                        if st.button(f"💾 Save Changes", type="primary", key=f"save_edit_phase_{force}"):
                            phases[selected_phase_idx]["Name"] = edit_phase_name
                            data["phases"] = phases
                            save_project(project, force, data)
                            st.success("✅ Phase updated")
                            st.rerun()
                    else:
                        st.info("No phases to edit")
                
                with col_delete:
                    st.markdown("**🗑️ Delete Phase**")
                    if phases:
                        # Sort phases and create mapping for deletion
                        sorted_phases = sort_phases_numerically(phases)
                        phase_to_original_idx = {id(phase): phases.index(phase) for phase in phases}
                        
                        phase_options = [f"{phase.get('Phase No', i+1)}. {phase.get('Name', 'Unnamed')}" for i, phase in enumerate(sorted_phases)]
                        selected_sorted_idx = st.selectbox("Select Phase", range(len(sorted_phases)), 
                                                         format_func=lambda x: phase_options[x], key=f"del_phase_{force}")
                        selected_phase = sorted_phases[selected_sorted_idx]
                        selected_phase_idx = phase_to_original_idx[id(selected_phase)]
                        
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
        col_add, col_edit, col_delete = st.columns(3)
        
        with col_add:
            st.markdown("**➕ Add New Phase**")
            name = st.text_input("Phase Name")
            
            if st.button("➕ Add Phase", type="primary") and name:
                if "phases" not in data:
                    data["phases"] = []
                data["phases"].append({"Name": name})
                # Sort phases after adding to maintain sequential order
                data["phases"] = sort_phases_numerically(data["phases"])
                save_project(project, side, data)
                st.success(f"✅ Phase '{name}' added")
                st.rerun()
        
        with col_edit:
            st.markdown("**✏️ Edit Phase**")
            if phases:
                phase_options = [f"{i+1}. {phase.get('Name', 'Unnamed')}" for i, phase in enumerate(phases)]
                selected_phase_idx = st.selectbox("Select Phase to Edit", range(len(phases)), 
                                                 format_func=lambda x: phase_options[x], key="edit_phase_sel_single")
                current_phase = phases[selected_phase_idx]
                edit_phase_name = st.text_input("Phase Name", value=current_phase.get("Name", ""), key="edit_phase_name_single")
                
                if st.button("💾 Save Changes", type="primary", key="save_edit_phase_single"):
                    phases[selected_phase_idx]["Name"] = edit_phase_name
                    data["phases"] = phases
                    save_project(project, side, data)
                    st.success("✅ Phase updated")
                    st.rerun()
            else:
                st.info("No phases to edit")
        
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
                
                # Display current DPs (already sorted in data)
                st.subheader(f"{force.capitalize()} Force DPs")
                if dps:
                    dp_data = []
                    for dp in dps:
                        dp_data.append({
                            "DP No": dp.get("DP No", ""),
                            "DP Name": dp.get("Name", ""),
                            "DP weightage": dp.get("Weight", ""),
                            "Objective": dp.get("Objective", ""),
                            "Phase": dp.get("Phase", ""),
                            "Force Group": dp.get("Force Group", "")
                        })
                    df = pd.DataFrame(dp_data)
                else:
                    df = pd.DataFrame(columns=["DP No", "DP Name", "DP weightage", "Objective", "Phase", "Force Group"])
                
                display_force_table(df, use_container_width=True, force_type=force)
                
                # Manage DPs
                st.markdown("---")
                col_add, col_edit, col_delete = st.columns(3)
                
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
                        # Sort DPs after adding to maintain sequential order
                        data["dps"] = sort_dps_numerically(data["dps"])
                        save_project(project, force, data)
                        st.success(f"✅ DP '{new_dp_name}' added to {force} force")
                        st.rerun()
                
                with col_edit:
                    st.markdown("**✏️ Edit DP**")
                    if dps:
                        sorted_dps = sorted(enumerate(dps), key=lambda x: int(x[1].get('DP No', 0)) if str(x[1].get('DP No', '')).isdigit() else float('inf'))
                        dp_options = [f"DP {dps[original_idx].get('DP No', 'N/A')}: {dps[original_idx].get('Name', 'Unnamed')}" for original_idx, dp in sorted_dps]
                        sorted_indices = [original_idx for original_idx, dp in sorted_dps]
                        
                        selected_sorted_idx = st.selectbox("Select DP to Edit", range(len(sorted_dps)), 
                                                      format_func=lambda x: dp_options[x], key=f"edit_dp_sel_{force}")
                        selected_dp_idx = sorted_indices[selected_sorted_idx]
                        current_dp = dps[selected_dp_idx]
                        
                        edit_dp_name = st.text_input("DP Name", value=current_dp.get("Name", ""), key=f"edit_dp_name_{force}")
                        
                        obj_names = [obj.get("Name") for obj in objectives if obj.get("Name")]
                        if obj_names:
                            current_obj_idx = obj_names.index(current_dp.get("Objective")) if current_dp.get("Objective") in obj_names else 0
                            edit_objective = st.selectbox("Objective", obj_names, index=current_obj_idx, key=f"edit_dp_obj_{force}")
                        else:
                            edit_objective = current_dp.get("Objective", "")
                        
                        phase_names = [phase.get("Name") for phase in phases if phase.get("Name")]
                        if phase_names and current_dp.get("Phase") in phase_names:
                            current_phase_idx = phase_names.index(current_dp.get("Phase"))
                            edit_phase = st.selectbox("Phase", phase_names, index=current_phase_idx, key=f"edit_dp_phase_{force}")
                        else:
                            edit_phase = st.text_input("Phase", value=current_dp.get("Phase", ""), key=f"edit_dp_phase_manual_{force}")
                        
                        edit_weight = st.slider("Weight", 1, 5, int(float(str(current_dp.get("Weight", 3)))), key=f"edit_dp_weight_{force}")
                        edit_force_group = st.text_input("Force Group", value=current_dp.get("Force Group", ""), key=f"edit_dp_fg_{force}")
                        
                        if st.button(f"💾 Save Changes", type="primary", key=f"save_edit_dp_{force}"):
                            dps[selected_dp_idx]["Name"] = edit_dp_name
                            dps[selected_dp_idx]["Objective"] = edit_objective
                            dps[selected_dp_idx]["Phase"] = edit_phase
                            dps[selected_dp_idx]["Weight"] = edit_weight
                            dps[selected_dp_idx]["Force Group"] = edit_force_group
                            data["dps"] = dps
                            save_project(project, force, data)
                            st.success(f"✅ DP updated")
                            st.rerun()
                    else:
                        st.info("No DPs to edit")
                
                with col_delete:
                    st.markdown("**🗑️ Delete DP**")
                    if dps:
                        # Sort DPs numerically by DP No for display
                        sorted_dps = sorted(enumerate(dps), key=lambda x: int(x[1].get('DP No', 0)) if str(x[1].get('DP No', '')).isdigit() else float('inf'))
                        dp_options = [f"DP {dps[original_idx].get('DP No', 'N/A')}: {dps[original_idx].get('Name', 'Unnamed')}" for original_idx, dp in sorted_dps]
                        sorted_indices = [original_idx for original_idx, dp in sorted_dps]
                        
                        selected_sorted_idx = st.selectbox("Select DP", range(len(sorted_dps)), 
                                                      format_func=lambda x: dp_options[x], key=f"del_dp_{force}")
                        selected_dp_idx = sorted_indices[selected_sorted_idx]
                        
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
                    "DP weightage": dp.get("Weight", ""),
                    "Objective": dp.get("Objective", ""),
                    "Phase": dp.get("Phase", ""),
                    "Force Group": dp.get("Force Group", "")
                })
            df = pd.DataFrame(dp_data)
        else:
            df = pd.DataFrame(columns=["DP No", "DP Name", "DP weightage", "Objective", "Phase", "Force Group"])
        
        display_force_table(df, use_container_width=True)
        
        # Manage DPs
        st.markdown("---")
        col_add, col_edit, col_delete = st.columns(3)
        
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
                # Sort DPs after adding to maintain sequential order
                data["dps"] = sort_dps_numerically(data["dps"])
                save_project(project, side, data)
                st.success(f"✅ DP '{dp_name}' added")
                st.rerun()
        
        with col_edit:
            st.markdown("**✏️ Edit DP**")
            if dps:
                sorted_dps = sorted(enumerate(dps), key=lambda x: int(x[1].get('DP No', 0)) if str(x[1].get('DP No', '')).isdigit() else float('inf'))
                dp_options = [f"DP {dps[original_idx].get('DP No', 'N/A')}: {dps[original_idx].get('Name', 'Unnamed')}" for original_idx, dp in sorted_dps]
                sorted_indices = [original_idx for original_idx, dp in sorted_dps]
                
                selected_sorted_idx = st.selectbox("Select DP to Edit", range(len(sorted_dps)), 
                                              format_func=lambda x: dp_options[x], key="edit_dp_sel_single")
                selected_dp_idx = sorted_indices[selected_sorted_idx]
                current_dp = dps[selected_dp_idx]
                
                edit_dp_name = st.text_input("DP Name", value=current_dp.get("Name", ""), key="edit_dp_name_single")
                
                obj_names = [obj.get("Name") for obj in objectives if obj.get("Name")]
                if obj_names:
                    current_obj_idx = obj_names.index(current_dp.get("Objective")) if current_dp.get("Objective") in obj_names else 0
                    edit_objective = st.selectbox("Objective", obj_names, index=current_obj_idx, key="edit_dp_obj_single")
                else:
                    edit_objective = current_dp.get("Objective", "")
                
                phase_names = [phase.get("Name") for phase in phases if phase.get("Name")]
                if phase_names and current_dp.get("Phase") in phase_names:
                    current_phase_idx = phase_names.index(current_dp.get("Phase"))
                    edit_phase = st.selectbox("Phase", phase_names, index=current_phase_idx, key="edit_dp_phase_single")
                else:
                    edit_phase = st.text_input("Phase", value=current_dp.get("Phase", ""), key="edit_dp_phase_manual_single")
                
                edit_weight = st.slider("Weight", 1, 5, int(float(str(current_dp.get("Weight", 3)))), key="edit_dp_weight_single")
                edit_force_group = st.text_input("Force Group", value=current_dp.get("Force Group", ""), key="edit_dp_fg_single")
                
                if st.button("💾 Save Changes", type="primary", key="save_edit_dp_single"):
                    dps[selected_dp_idx]["Name"] = edit_dp_name
                    dps[selected_dp_idx]["Objective"] = edit_objective
                    dps[selected_dp_idx]["Phase"] = edit_phase
                    dps[selected_dp_idx]["Weight"] = edit_weight
                    dps[selected_dp_idx]["Force Group"] = edit_force_group
                    data["dps"] = dps
                    save_project(project, side, data)
                    st.success("✅ DP updated")
                    st.rerun()
            else:
                st.info("No DPs to edit")
        
        with col_delete:
            st.markdown("**🗑️ Delete DP**")
            if dps:
                # Sort DPs numerically by DP No for display
                sorted_dps = sorted(enumerate(dps), key=lambda x: int(x[1].get('DP No', 0)) if str(x[1].get('DP No', '')).isdigit() else float('inf'))
                dp_options = [f"DP {dps[original_idx].get('DP No', 'N/A')}: {dps[original_idx].get('Name', 'Unnamed')}" for original_idx, dp in sorted_dps]
                sorted_indices = [original_idx for original_idx, dp in sorted_dps]
                
                selected_sorted_idx = st.selectbox("Select DP", range(len(sorted_dps)), 
                                              format_func=lambda x: dp_options[x])
                selected_dp_idx = sorted_indices[selected_sorted_idx]
                
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
        
        # Display tasks grouped by DP - sort numerically by DP number
        def sort_dp_key(item):
            dp_no = item[0]
            try:
                return int(dp_no) if dp_no.isdigit() else float('inf')
            except:
                return float('inf')
        
        for dp_no, dp_tasks in sorted(tasks_by_dp.items(), key=sort_dp_key):
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
                    # Get original tasks for sorting by Task No
                    dp_original_tasks = [task for task in tasks if str(task.get("dp_no") or task.get("DP No") or task.get("dp no") or task.get("DP") or task.get("dp") or "Unassigned") == str(dp_no)]
                    
                    # Sort tasks by Task No
                    sorted_original_tasks = sort_tasks_numerically(dp_original_tasks)
                    
                    # Rebuild dp_tasks in sorted order
                    sorted_dp_tasks = []
                    for task in sorted_original_tasks:
                        task_name = (task.get("description") or task.get("Desc") or task.get("Name") or 
                                   task.get("Task Name") or task.get("desc") or task.get("name") or 
                                   task.get("task name") or task.get("Task") or task.get("task") or
                                   task.get("Description") or f"Task {task.get('Task No', '')}")
                        
                        weight_val = task.get("stated") or task.get("Weight") or task.get("weight") or task.get("Wt") or task.get("wt")
                        progress_val = task.get("achieved") or task.get("Achieved %") or task.get("progress") or task.get("Progress") or task.get("achieved %") or task.get("Progress %")
                        
                        task_data = {
                            "Task No": task.get("Task No", ""),
                            "Task Name": str(task_name).strip() if task_name else "Unknown Task",
                            "Weight": str(weight_val).strip() if weight_val and str(weight_val).lower() != 'nan' else "Not Set",
                            "Progress (%)": str(progress_val).strip() if progress_val and str(progress_val).lower() != 'nan' else "0",
                            "Type": task.get("Type", ""),
                            "Force Group": task.get("Force Group", ""),
                            "Criteria": task.get("Criteria", "")
                        }
                        sorted_dp_tasks.append(task_data)
                    
                    df = pd.DataFrame(sorted_dp_tasks)
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
                            
                            # Generate next task number
                            existing_task_nos = {int(task.get("Task No", 0)) for task in data["tasks"] if str(task.get("Task No", "")).isdigit()}
                            next_task_no = max(existing_task_nos) + 1 if existing_task_nos else 1
                            
                            data["tasks"].append({
                                "Task No": next_task_no,
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
                            # Sort tasks after adding to maintain sequential order
                            data["tasks"] = sort_tasks_numerically(data["tasks"])
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
    st.header("⚖️ KO Method (Pairwise Comparison)")
    st.markdown("*Advanced analytical hierarchy process for priority weightage calculation*")
    
    # Create tabs for different comparison types
    tab1, tab2 = st.tabs(["🎯 DP Comparison", "✅ Task Comparison"])
    
    s = st.session_state
    project = s.get("project")
    side = s.get("side")
    data = load_project(project, side)
    
    with tab1:
        dp_comparison_tab(s, project, side, data)
    
    with tab2:
        task_comparison_tab(s, project, side, data)

def dp_comparison_tab(s, project, side, data):
    """Tab for comparing DPs within an objective"""
    st.subheader("🎯 DP Comparison within Objective")
    st.markdown("*Compare Decision Points within a selected Objective to determine their priority weights*")
    
    objectives = data.get("objectives", [])
    dps = data.get("dps", [])
    
    if not objectives:
        st.warning("⚠️ No objectives found. Please create objectives first.")
        return
    
    if not dps:
        st.warning("⚠️ No DPs found. Please create DPs first.")
        return
    
    # Step 1: Objective Selection
    st.markdown("#### 📋 Step 1: Select Objective")
    
    # Sort objectives numerically and create mapping
    sorted_objectives = sort_objectives_numerically(objectives)
    obj_to_original_idx = {id(obj): objectives.index(obj) for obj in objectives}
    
    obj_options = {}
    for i, obj in enumerate(sorted_objectives):
        obj_no = obj.get("Objective No", i+1)
        obj_name = obj.get("Name", obj.get("name", f"Objective {obj_no}"))
        obj_options[f"Obj {obj_no}: {obj_name}"] = obj
    
    selected_obj_display = st.selectbox(
        "Select objective for DP comparison:",
        list(obj_options.keys()),
        help="Choose the objective whose DPs you want to compare"
    )
    
    selected_objective = obj_options[selected_obj_display]
    
    # Get the index of the selected objective
    selected_obj_idx = obj_to_original_idx[id(selected_objective)]
    
    # Find DPs for selected objective
    objective_name = selected_objective.get("Name", selected_objective.get("name", ""))
    obj_dps = [dp for dp in dps if dp.get("Objective", "") == objective_name]
    
    if len(obj_dps) < 2:
        st.info(f"📝 Need at least 2 DPs in objective '{objective_name}' for comparison. Found {len(obj_dps)} DP(s).")
        if len(obj_dps) == 1:
            st.info("💡 Single DP automatically gets 100% weight.")
            obj_dps[0]["Weight"] = 100.0
            obj_dps[0]["weight"] = 100.0
            # Update in main DPs list
            for i, dp in enumerate(dps):
                if dp.get("Objective") == objective_name:
                    dps[i] = obj_dps[0]
                    break
            data["dps"] = dps
            save_project(project, side, data)
            st.success("✅ Single DP weight set to 100%")
        return
    
    # Step 2: Display objective info and comparison
    st.markdown("#### ⚖️ Step 2: Objective Overview & Pairwise Comparison")
    
    st.markdown(f"""
    **Objective:** {objective_name}  
    **DPs to Compare:** {len(obj_dps)}
    """)
    
    # Display DPs in this objective
    with st.expander("📝 DPs in this Objective", expanded=False):
        for i, dp in enumerate(obj_dps):
            dp_name = dp.get("Name", dp.get("name", f"DP {i+1}"))
            current_weight = dp.get("Weight", dp.get("weight", 0))
            st.write(f"**{i+1}.** {dp_name} (Current Weight: {current_weight}%)")
    
    # KO Method for DPs
    perform_ko_comparison(s, project, side, data, obj_dps, "dp", f"obj_{selected_obj_idx}", "DP", objective_name)

def task_comparison_tab(s, project, side, data):
    """Tab for comparing tasks within a DP"""
    st.subheader("✅ Task Comparison within DP")
    st.markdown("*Compare tasks within a selected Decision Point to determine their priority weights*")
    
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
    st.markdown("#### 🎯 Step 1: Select Decision Point")
    
    # Create DP options with names and numbers - sort numerically
    dp_list = []
    for dp in dps:
        dp_no = get_dp_no(dp)
        dp_name = dp.get("Name", dp.get("name", f"DP {dp_no}"))
        if dp_no is not None:
            dp_list.append((dp_no, f"DP {dp_no}: {dp_name}"))
    
    if not dp_list:
        st.error("❌ No valid DPs found. Please ensure DPs have proper DP No assigned.")
        return
    
    # Sort numerically by DP number
    dp_list.sort(key=lambda x: int(x[0]) if str(x[0]).isdigit() else float('inf'))
    
    # Create options dictionary in sorted order
    dp_options = {display: dp_no for dp_no, display in dp_list}
    
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
    st.markdown("#### 📋 Step 2: DP Overview & Pairwise Comparison")
    
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
    
    # KO Method for tasks
    perform_ko_comparison(s, project, side, data, dp_tasks, "task", selected_dp_no, "Task", dp_name)

def perform_ko_comparison(s, project, side, data, items, item_type, identifier, item_label, parent_name):
    """
    Generic KO comparison function for both DPs and tasks
    """
    import itertools
    
    if len(items) < 2:
        return
    
    pairs = list(itertools.combinations(range(len(items)), 2))
    key_prefix = f"ko_{item_type}_{project}_{side}_{identifier}"
    
    # Initialize KO session state
    if f"{key_prefix}_idx" not in s:
        s[f"{key_prefix}_idx"] = 0
        s[f"{key_prefix}_scores"] = {i: 1 for i in range(len(items))}
    
    # Reset if identifier changed
    current_key = f"{key_prefix}_current"
    if s.get(current_key) != identifier:
        s[f"{key_prefix}_idx"] = 0
        s[f"{key_prefix}_scores"] = {i: 1 for i in range(len(items))}
        s[current_key] = identifier
    
    idx = s[f"{key_prefix}_idx"]
    scores = s[f"{key_prefix}_scores"]
    
    st.markdown("#### ⚖️ Pairwise Comparison")
    
    # KO Voting UI
    if idx < len(pairs):
        a_idx, b_idx = pairs[idx]
        item_a = items[a_idx]
        item_b = items[b_idx]
        
        # Get item names based on type
        def get_item_name(item, idx, item_type):
            if item_type == "task":
                return (item.get("description") or item.get("Desc") or item.get("Name") or 
                       item.get("Task Name") or item.get("desc") or item.get("name") or 
                       f"Task {idx+1}")
            else:  # DP
                return (item.get("Name") or item.get("name") or f"DP {idx+1}")
        
        item_a_name = get_item_name(item_a, a_idx, item_type)
        item_b_name = get_item_name(item_b, b_idx, item_type)
        
        st.markdown(f"**Comparison {idx+1} of {len(pairs)}**")
        comparison_question = f"*Which {item_type} is more important/critical for achieving the {parent_name} objective?*" if item_type == "task" else f"*Which DP has higher priority within the {parent_name} objective?*"
        st.markdown(comparison_question)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div style="background: #1e40af; color: white; padding: 15px; border-radius: 10px; text-align: center;">
                <h4 style="color: white; margin: 0;">Option A</h4>
                <p style="color: white; margin: 10px 0;">{item_a_name}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🅰️ Choose {item_label} A", key=f"{item_type}_a_{idx}_{identifier}", type="primary"):
                scores[a_idx] += 1
                s[f"{key_prefix}_idx"] += 1
                st.rerun()
        
        with col2:
            st.markdown(f"""
            <div style="background: #dc2626; color: white; padding: 15px; border-radius: 10px; text-align: center;">
                <h4 style="color: white; margin: 0;">Option B</h4>
                <p style="color: white; margin: 10px 0;">{item_b_name}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🅱️ Choose {item_label} B", key=f"{item_type}_b_{idx}_{identifier}", type="primary"):
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
        
        # Update item weights
        updated_items = []
        for i, item in enumerate(items):
            if i in scores:
                # Calculate percentage weight
                weight_percentage = (scores[i] / total_score) * 100
                
                # Update item with new weight
                item["Weight"] = round(weight_percentage, 2)
                item["weight"] = round(weight_percentage, 2)
                
                if item_type == "task":
                    item["stated"] = round(weight_percentage, 2)
                    item["Stated %"] = round(weight_percentage, 2)
                
                # Get item name for display
                if item_type == "task":
                    item_name = (item.get("description") or item.get("Desc") or item.get("Name") or 
                               item.get("Task Name") or item.get("desc") or item.get("name") or 
                               f"Task {i+1}")
                else:  # DP
                    item_name = (item.get("Name") or item.get("name") or f"DP {i+1}")
                
                updated_items.append({
                    "name": item_name,
                    "score": scores[i],
                    "weight": round(weight_percentage, 2)
                })
        
        # Update main data list based on item type
        if item_type == "task":
            # Update main tasks list
            tasks = data.get("tasks", [])
            def get_task_dp(task):
                return task.get("DP No") or task.get("dp_no")
            
            for i, task in enumerate(tasks):
                if str(get_task_dp(task)) == str(identifier):
                    # Find corresponding updated task
                    for j, updated_task in enumerate(items):
                        if task is updated_task or (
                            task.get("description") == updated_task.get("description") and
                            task.get("Name") == updated_task.get("Name")
                        ):
                            tasks[i] = updated_task
                            break
            data["tasks"] = tasks
            
        else:  # DP
            # Update main DPs list
            dps = data.get("dps", [])
            objectives = data.get("objectives", [])
            
            # Find objective name
            objective_name = parent_name if item_type == "dp" else ""
            
            for i, dp in enumerate(dps):
                if dp.get("Objective") == objective_name:
                    # Find corresponding updated DP
                    for j, updated_dp in enumerate(items):
                        if dp is updated_dp or dp.get("Name") == updated_dp.get("Name"):
                            dps[i] = updated_dp
                            break
            data["dps"] = dps
        
        # Save updated data
        save_project(project, side, data)
        
        success_msg = f"✅ KO Method completed! {item_label} weights updated"
        if item_type == "task":
            success_msg += f" for DP {identifier}"
        else:
            success_msg += f" for objective '{parent_name}'"
        st.success(success_msg)
        
        # Display results
        st.subheader(f"📊 Calculated {item_label} Weights")
        
        # Results table
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"**{item_label} Name**")
        col2.markdown("**Score**") 
        col3.markdown("**Weight (%)**")
        
        for item_result in updated_items:
            col1.write(item_result["name"])
            col2.write(item_result["score"])
            col3.write(f"{item_result['weight']}%")
        
        st.divider()
        
        # Control buttons
        col1, col2 = st.columns(2)
        
        with col1:
            restart_key = f"restart_ko_{item_type}_{identifier}"
            if st.button(f"🔄 Restart KO for this {item_label}", key=restart_key, type="secondary"):
                s[f"{key_prefix}_idx"] = 0
                s[f"{key_prefix}_scores"] = {i: 1 for i in range(len(items))}
                st.rerun()
        
        with col2:
            select_diff_key = f"select_diff_{item_type}_{identifier}"
            select_label = "Objective" if item_type == "dp" else "DP"
            if st.button(f"🎯 Select Different {select_label}", key=select_diff_key, type="secondary"):
                # Clear current session state to allow new selection
                keys_to_clear = [k for k in s.keys() if k.startswith(f"ko_{item_type}_{project}_{side}_")]
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

def show_force_progress_entry(project, force, independent=False):
    """Show progress entry interface for a specific force"""
    
    # Load data using appropriate method based on mode
    if independent:
        data = load_independent_project(project, force)
    else:
        data = load_project(project, force)
        
    tasks = data.get("tasks", [])
    dps = data.get("dps", [])
    
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
    
    # Sort tasks within each DP by Task No
    for dp_no in tasks_by_dp:
        tasks_by_dp[dp_no].sort(key=lambda x: get_numeric_sort_key(x[1], "Task No"))
    
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
    
    # DP Selection - Card-based interface
    def sort_dp_key(item):
        dp_no = item[0]
        try:
            return int(dp_no) if dp_no.isdigit() else float('inf')
        except:
            return float('inf')
    
    sorted_dps = sorted(tasks_by_dp.items(), key=sort_dp_key)
    
    if not sorted_dps:
        st.info("No tasks available for progress entry")
        return
    
    # Initialize selected DP in session state
    if f"selected_dp_{force}" not in st.session_state:
        st.session_state[f"selected_dp_{force}"] = sorted_dps[0][0]
    
    # Display DP cards for selection
    st.markdown("### 🎯 Select Decisive Point")
    
    # Calculate number of columns based on number of DPs
    num_dps = len(sorted_dps)
    cols_per_row = min(3, num_dps)
    
    # Create DP selection cards
    for row_start in range(0, num_dps, cols_per_row):
        cols = st.columns(cols_per_row)
        for idx, (dp_no, dp_tasks) in enumerate(sorted_dps[row_start:row_start+cols_per_row]):
            # Find DP details
            dp_name = "Unknown DP"
            dp_objective = "Unknown Objective"
            for dp in dps:
                if str(dp.get("DP No", "") or dp.get("dp_no", "")) == str(dp_no):
                    dp_name = dp.get("Name", f"DP {dp_no}")
                    dp_objective = dp.get("Objective", "Unknown Objective")
                    break
            
            # Calculate DP progress
            dp_progress = sum(task.get("Progress", task.get("progress", 0)) or 0 for _, task in dp_tasks) / len(dp_tasks) if dp_tasks else 0
            
            # Check if this DP is selected
            is_selected = st.session_state[f"selected_dp_{force}"] == dp_no
            
            with cols[idx]:
                # Card styling based on selection
                if is_selected:
                    card_color = "#667eea"
                    border_style = "border: 3px solid #4c51bf;"
                else:
                    card_color = "#6b7280"
                    border_style = "border: 1px solid #d1d5db;"
                
                # DP Card - show full name with text wrapping
                st.markdown(f"""
                <div style="background: {card_color}; {border_style}
                     padding: 15px; border-radius: 10px; margin-bottom: 10px; cursor: pointer;
                     box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: all 0.3s; min-height: 120px;">
                    <h4 style="color: white; margin: 0; font-size: 16px;">🎯 DP {dp_no}</h4>
                    <p style="color: white; opacity: 0.9; margin: 8px 0; font-size: 13px; 
                       word-wrap: break-word; overflow-wrap: break-word;">{dp_name}</p>
                    <p style="color: white; opacity: 0.8; margin: 5px 0 0 0; font-size: 12px;">
                        📋 {len(dp_tasks)} tasks | 📈 {int(dp_progress)}%
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Select DP {dp_no}", key=f"select_dp_{dp_no}_{force}", use_container_width=True):
                    st.session_state[f"selected_dp_{force}"] = dp_no
                    st.rerun()
    
    st.divider()
    
    # Display selected DP with all tasks
    selected_dp_no = st.session_state[f"selected_dp_{force}"]
    dp_tasks = tasks_by_dp[selected_dp_no]
    
    # Find DP details
    dp_name = "Unknown DP"
    dp_objective = "Unknown Objective"
    for dp in dps:
        if str(dp.get("DP No", "") or dp.get("dp_no", "")) == str(selected_dp_no):
            dp_name = dp.get("Name", f"DP {selected_dp_no}")
            dp_objective = dp.get("Objective", "Unknown Objective")
            break
    
    # DP Header
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
         padding: 20px; border-radius: 10px; margin: 20px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h3 style="color: white; margin: 0;">🎯 DP {selected_dp_no}: {dp_name}</h3>
        <p style="color: white; opacity: 0.9; margin: 8px 0 0 0;">📌 {dp_objective}</p>
        <p style="color: white; opacity: 0.8; margin: 8px 0 0 0; font-size: 14px;">Tasks: {len(dp_tasks)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display all tasks for this DP
    for task_idx, (original_idx, task) in enumerate(dp_tasks):
        # Get task name and details
        task_name = (task.get("description") or task.get("Desc") or task.get("Name") or 
                   task.get("Task Name") or task.get("desc") or task.get("name") or 
                   task.get("task name") or task.get("Task") or task.get("task") or
                   task.get("Description") or f"Task {task.get('Task No', task_idx+1)}")
        
        # Get current progress
        current_progress = task.get("Progress", task.get("progress", task.get("achieved", 0))) or 0
        try:
            current_progress = float(str(current_progress).replace('%', ''))
        except:
            current_progress = 0
        
        task_no = task.get("Task No", task_idx+1)
        
        # Current values with proper handling
        current_weight = task.get("stated") or task.get("Weight") or task.get("weight") or task.get("Wt") or task.get("wt") or 0
        
        # Handle string percentages
        try:
            current_weight = float(str(current_weight).replace('%', ''))
        except:
            current_weight = 0
        
        # Progress update controls
        unique_key = f"progress_{force}_{selected_dp_no}_{original_idx}"
        
        # Check for sync flags from previous render and update widget states BEFORE creating widgets
        if f"sync_weight_{unique_key}" in st.session_state:
            sync_val = st.session_state[f"sync_weight_{unique_key}"]
            st.session_state[f"weight_slider_{unique_key}"] = sync_val
            st.session_state[f"weight_input_{unique_key}"] = sync_val
            del st.session_state[f"sync_weight_{unique_key}"]
        
        if f"sync_progress_{unique_key}" in st.session_state:
            sync_val = st.session_state[f"sync_progress_{unique_key}"]
            st.session_state[f"progress_slider_{unique_key}"] = sync_val
            st.session_state[f"progress_input_{unique_key}"] = sync_val
            del st.session_state[f"sync_progress_{unique_key}"]
        
        # Initialize session state for synchronized inputs if not exists
        if f"weight_val_{unique_key}" not in st.session_state:
            st.session_state[f"weight_val_{unique_key}"] = int(round(current_weight))
        if f"progress_val_{unique_key}" not in st.session_state:
            st.session_state[f"progress_val_{unique_key}"] = int(round(current_progress))
        
        # Always sync from saved values on first load to ensure consistency
        saved_weight_val = int(round(float(str(task.get("Weight", task.get("weight", 0))).replace('%', ''))))
        saved_progress_val = int(round(float(str(task.get("Progress", task.get("progress", 0))).replace('%', ''))))
        
        # Update session state if it doesn't match saved value (e.g., after page reload)
        if f"synced_{unique_key}" not in st.session_state:
            st.session_state[f"weight_val_{unique_key}"] = saved_weight_val
            st.session_state[f"progress_val_{unique_key}"] = saved_progress_val
            st.session_state[f"synced_{unique_key}"] = True
        
        # Get live progress value from session state
        live_progress = st.session_state[f"progress_val_{unique_key}"]
        
        # Task header with LIVE progress value
        task_color = "#38a169" if live_progress >= 75 else "#e53e3e" if live_progress < 25 else "#d69e2e"
        st.markdown(f"""
        <div style="background: {task_color}; color: white; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <h4 style="color: white; margin: 0;">🔹 Task {task_no}: {task_name}</h4>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Current Progress: {live_progress}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Two-column layout for task editing
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**📊 Progress Controls**")
            
            # Weight input with slider and number input (synchronized)
            st.markdown("**Task Weight (%)**")
            
            # Initialize widget keys if not present
            if f"weight_slider_{unique_key}" not in st.session_state:
                st.session_state[f"weight_slider_{unique_key}"] = st.session_state[f"weight_val_{unique_key}"]
            if f"weight_input_{unique_key}" not in st.session_state:
                st.session_state[f"weight_input_{unique_key}"] = st.session_state[f"weight_val_{unique_key}"]
            
            weight_col1, weight_col2 = st.columns([3, 1])
            
            with weight_col1:
                weight_slider = st.slider(
                    "Weight Slider", 
                    0, 
                    100, 
                    key=f"weight_slider_{unique_key}",
                    label_visibility="collapsed",
                    help="Strategic importance of this task (doesn't need to sum to 100% - relative proportions matter)"
                )
                    
            with weight_col2:
                weight_input = st.number_input(
                    "Weight Value",
                    min_value=0,
                    max_value=100,
                    key=f"weight_input_{unique_key}",
                    label_visibility="collapsed",
                    help="Enter exact value"
                )
            
            # Get values and detect changes
            new_weight = weight_slider if weight_slider == weight_input else (weight_slider if weight_slider != st.session_state[f"weight_val_{unique_key}"] else weight_input)
            
            # If they differ, set sync flag for next render
            if weight_slider != weight_input:
                st.session_state[f"sync_weight_{unique_key}"] = new_weight
                st.session_state[f"weight_val_{unique_key}"] = new_weight
                st.rerun()
            else:
                st.session_state[f"weight_val_{unique_key}"] = new_weight
            
            # Progress input with slider and number input (synchronized)
            st.markdown("**Progress Achieved (%)**")
            
            # Get progress range based on task type
            task_type_check = str(task.get('Type', 'T')).upper()
            if task_type_check == 'T':
                # Tangible tasks: full range 0-100%
                min_progress, max_progress, default_progress = 0, 100, 0
            else:
                # Intangible tasks: range based on intangible assessment
                current_intangible = st.session_state.get(f"intangible_{unique_key}", task.get("Intangible", "nil"))
                min_progress, max_progress, default_progress = get_progress_range(current_intangible)

            # Initialize widget keys if not present, ensure they're within range
            current_progress_val = st.session_state[f"progress_val_{unique_key}"]
            clamped_progress = max(min_progress, min(current_progress_val, max_progress))
            
            if f"progress_slider_{unique_key}" not in st.session_state:
                st.session_state[f"progress_slider_{unique_key}"] = clamped_progress
            if f"progress_input_{unique_key}" not in st.session_state:
                st.session_state[f"progress_input_{unique_key}"] = clamped_progress
            
            progress_col1, progress_col2 = st.columns([3, 1])
            with progress_col1:
                progress_slider = st.slider(
                    "Progress Slider", 
                    min_progress, 
                    max_progress,
                    key=f"progress_slider_{unique_key}",
                    label_visibility="collapsed",
                    help=f"Adjust progress within range {min_progress}–{max_progress}% (Tangible: 0–100%, Intangible Nil: 0–33%, Partial: 34–66%, Complete: 67–100%)"
                )
                    
            with progress_col2:
                progress_input = st.number_input(
                    "Progress Value",
                    min_value=min_progress,
                    max_value=max_progress,
                    key=f"progress_input_{unique_key}",
                    label_visibility="collapsed",
                    help=f"Enter value in range {min_progress}–{max_progress}%"
                )
            
            # Get values and detect changes
            new_progress = progress_slider if progress_slider == progress_input else (progress_slider if progress_slider != st.session_state[f"progress_val_{unique_key}"] else progress_input)
            
            # If they differ, set sync flag for next render
            if progress_slider != progress_input:
                st.session_state[f"sync_progress_{unique_key}"] = new_progress
                st.session_state[f"progress_val_{unique_key}"] = new_progress
                st.rerun()
            else:
                st.session_state[f"progress_val_{unique_key}"] = new_progress
            
            # Progress comment/notes
            current_comment = task.get("Progress Comment", task.get("progress_comment", ""))
            progress_comment = st.text_area(
                "Progress Notes (Optional)",
                value=current_comment,
                key=f"comment_{unique_key}",
                height=80,
                help="Add notes explaining the progress update for future reference",
                placeholder="e.g., 'Completed initial planning phase, waiting for resources...'"
            )
            
            # Additional intangible assessment
            task_type_for_intangible = str(task.get('Type', 'T')).upper()
            if task_type_for_intangible == 'T':
                # Tangible tasks: force intangible to nil and hide options
                intangible = 'nil'
            else:
                intangible = st.selectbox(
                    "Intangible Assessment",
                    ["nil", "partial", "complete"],
                    index=["nil", "partial", "complete"].index(task.get("Intangible", "nil")),
                    key=f"intangible_{unique_key}",
                    help="Qualitative assessment beyond measurable progress"
                )
            
            # AUTO-SAVE: Check if values have changed from saved values
            saved_weight = int(round(float(str(task.get("Weight", task.get("weight", 0))).replace('%', ''))))
            saved_progress = int(round(float(str(task.get("Progress", task.get("progress", 0))).replace('%', ''))))
            saved_intangible = task.get("Intangible", "nil")
            saved_comment = task.get("Progress Comment", task.get("progress_comment", ""))
            
            # If any value changed, auto-save
            if (new_weight != saved_weight or new_progress != saved_progress or 
                intangible != saved_intangible or progress_comment != saved_comment):
                
                # Update task with new values (as whole numbers)
                tasks[original_idx]["Weight"] = new_weight
                tasks[original_idx]["weight"] = new_weight
                tasks[original_idx]["stated"] = new_weight
                tasks[original_idx]["Stated %"] = new_weight
                
                tasks[original_idx]["Progress"] = new_progress
                tasks[original_idx]["progress"] = new_progress
                tasks[original_idx]["achieved"] = new_progress
                tasks[original_idx]["Achieved %"] = new_progress
                tasks[original_idx]["Progress %"] = new_progress
                
                # Force intangible to nil for tangible tasks
                if task_type_for_intangible == 'T':
                    tasks[original_idx]["Intangible"] = 'nil'
                else:
                    tasks[original_idx]["Intangible"] = intangible
                
                # Save progress comment
                tasks[original_idx]["Progress Comment"] = progress_comment
                tasks[original_idx]["progress_comment"] = progress_comment
                
                # Save to file
                data["tasks"] = tasks
                if independent:
                    save_independent_project(project, force, data)
                else:
                    save_project(project, force, data)
        
        with col2:
            st.markdown("**📝 Task Information**")
            
            # Get task type and display full name
            task_type = task.get('Type', 'Not specified')
            if task_type == 'T':
                task_type_display = 'Tangible'
            elif task_type == 'I':
                task_type_display = 'Intangible'
            else:
                task_type_display = task_type
            
            # Task details in organized format - using LIVE values from session state
            st.markdown(f"""
            **Current Metrics:**
            - Weight: {new_weight}%
            - Progress: {new_progress}%
            - Assessment: {intangible.capitalize()}
            
            **Task Details:**
            - Force Group: {task.get('Force Group', 'Not specified')}
            - Type: {task_type_display}
            - Criteria: {task.get('Criteria', 'Not specified')}
            """)
            
            # Show current progress comment if exists
            if progress_comment:
                st.markdown(f"**Progress Notes:**")
                st.info(progress_comment)
            
            # Auto-save indicator
            if (new_weight != saved_weight or new_progress != saved_progress or 
                intangible != saved_intangible or progress_comment != saved_comment):
                st.success("✅ Auto-saved")
        
        st.divider()
    
    # Calculate REAL-TIME total weightage for this DP using session state values
    dp_total_weight = 0
    for task_idx, (original_idx, task_data) in enumerate(dp_tasks):
        unique_key = f"progress_{force}_{selected_dp_no}_{original_idx}"
        # Use session state value if exists, otherwise use saved value
        if f"weight_val_{unique_key}" in st.session_state:
            dp_total_weight += st.session_state[f"weight_val_{unique_key}"]
        else:
            saved_weight = float(str(task_data.get("Weight", task_data.get("weight", 0))).replace('%', ''))
            dp_total_weight += saved_weight
    
    dp_total_weight = int(round(dp_total_weight))
    
    st.markdown("### 📊 Total Task Weightage Summary")
    
    # Visual progress bar for total weight
    col1, col2 = st.columns([3, 1])
    with col1:
        if dp_total_weight < 100:
            st.progress(dp_total_weight / 100.0, text=f"Total Weightage: {dp_total_weight}%")
            st.info("ℹ️ Note: Weightage doesn't need to equal 100% - relative proportions are what matter mathematically")
        elif dp_total_weight > 100:
            st.progress(1.0, text=f"Total Weightage: {dp_total_weight}%")
            st.warning(f"⚠️ Total weightage is {dp_total_weight}% (more than 100%)")
        else:
            st.progress(1.0, text=f"Total Weightage: {dp_total_weight}%")
            st.success("✅ Total weightage equals 100%")
    with col2:
        st.metric("Total", f"{dp_total_weight}%")

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
        tab_names = [" Control Overview", " Force Monitoring"] + [f"{get_force_emoji(side)} {side.capitalize()}" for side in SIDES]
        tabs = st.tabs(tab_names)
        
        # Overview tab
        with tabs[0]:
            show_overview_dashboard(project, rag)

        # Force Independent Monitoring tab (Forces' independent progress)
        with tabs[1]:
            show_force_monitoring_dashboard(project, rag)
        
        
        
                # Individual force tabs
        for i, side in enumerate(SIDES):
            with tabs[i + 2]:
                show_force_dashboard(side, project, rag)

# --- Chat Tab ---
def chat_tab():
    """Dedicated chat interface in navigation panel"""
    project = st.session_state.get("project")
    role = st.session_state.get("role", "control")
    
    if not project:
        st.warning("⚠️ Please select a project first from Project Management")
        return
    
    st.header("💬 Chat")
    
    if role == "control":
        # Control Chat Interface
        st.markdown("*Command Control - Force Chat Center*")
        st.markdown("---")
        
        # Select force to communicate with
        selected_force = st.selectbox("Select Force to Communicate With:", SIDES, key="comm_force_select")
        
        if selected_force:
            # Display conversation with selected force
            st.markdown(f"### 📨 Conversation with {selected_force.capitalize()}")
            
            # Get conversation history
            conversation = get_conversation(project, "control", selected_force)
            
            # Display messages in a chat-like interface
            if conversation:
                chat_container = st.container()
                with chat_container:
                    for message in conversation[-15:]:  # Show last 15 messages
                        is_control = message["sender"] == "control"
                        alignment = "flex-end" if is_control else "flex-start"
                        bg_color = "#e3f2fd" if is_control else "#f5f5f5"
                        sender_icon = "🎯" if is_control else get_force_emoji(message["sender"])
                        
                        st.markdown(f"""
                        <div style="display: flex; justify-content: {alignment}; margin: 10px 0;">
                            <div style="background: {bg_color}; padding: 10px 15px; border-radius: 15px; 
                                        max-width: 70%; border: 1px solid #ddd; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <div style="font-size: 0.8em; color: #666; margin-bottom: 5px;">
                                    {sender_icon} {message["sender"].title()} - {message["timestamp"]}
                                </div>
                                <div style="color: #333;">
                                    {message["message"]}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info(f"No messages yet with {selected_force.capitalize()}")
            
            # Send new message
            st.markdown("### ✍️ Send Message")
            with st.form(f"send_message_comm_tab_{selected_force}"):
                message_text = st.text_area("Type your message:", key=f"comm_control_message_{selected_force}", height=100)
                col1, col2 = st.columns([4, 1])
                with col2:
                    send_button = st.form_submit_button("📤 Send", use_container_width=True)
                
                if send_button and message_text.strip():
                    if save_message(project, "control", selected_force, message_text.strip()):
                        st.success(f"✅ Message sent to {selected_force.capitalize()}!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to send message. Please try again.")
        
        # Show recent queries from all forces
        st.markdown("---")
        st.markdown("### 📥 Recent Force Queries")
        all_messages = []
        for force in SIDES:
            force_messages = get_conversation(project, force, "control")
            all_messages.extend([msg for msg in force_messages if msg["sender"] != "control"])
        
        # Sort by timestamp (most recent first)
        all_messages.sort(key=lambda x: x["timestamp"], reverse=True)
        
        if all_messages:
            for message in all_messages[:8]:  # Show last 8 queries
                force_color = FORCE_COLORS.get(message["sender"], "#64748b")
                st.markdown(f"""
                <div style="background: {force_color}10; border-left: 4px solid {force_color}; 
                            padding: 12px; margin: 10px 0; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-weight: bold; color: {force_color}; font-size: 1.05em;">
                        {get_force_emoji(message["sender"])} {message["sender"].capitalize()} - {message["timestamp"]}
                    </div>
                    <div style="margin-top: 6px; color: #333;">
                        {message["message"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📭 No recent queries from forces")
    
    else:
        # Force Chat Interface
        force = st.session_state.get("role")  # Force name is stored in role
        if not force or force == "control":
            st.error("❌ Unable to determine force identity")
            return
            
        st.markdown(f"*{get_force_emoji(force)} {force.capitalize()} Force - Communication with Control*")
        st.markdown("---")
        
        # Display conversation with Control
        st.markdown("### 📨 Conversation with Command Control")
        conversation = get_conversation(project, force, "control")
        
        if conversation:
            chat_container = st.container()
            with chat_container:
                for message in conversation[-15:]:  # Show last 15 messages
                    is_control = message["sender"] == "control"
                    alignment = "flex-start" if is_control else "flex-end"
                    bg_color = "#e3f2fd" if is_control else "#f5f5f5"
                    sender_icon = "🎯" if is_control else get_force_emoji(force)
                    
                    st.markdown(f"""
                    <div style="display: flex; justify-content: {alignment}; margin: 10px 0;">
                        <div style="background: {bg_color}; padding: 10px 15px; border-radius: 15px; 
                                    max-width: 80%; border: 1px solid #ddd; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <div style="font-size: 0.8em; color: #666; margin-bottom: 5px;">
                                {sender_icon} {message["sender"].title()} - {message["timestamp"]}
                            </div>
                            <div style="color: #333;">
                                {message["message"]}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("📭 No messages yet with Control")
        
        # Send message to Control
        st.markdown("### ✍️ Send Query to Control")
        with st.form(f"send_query_comm_tab_{force}"):
            message_text = st.text_area("Type your query or message:", key=f"comm_force_message_{force}", height=100)
            col1, col2 = st.columns([4, 1])
            with col2:
                send_button = st.form_submit_button("📤 Send", use_container_width=True)
            
            if send_button and message_text.strip():
                if save_message(project, force, "control", message_text.strip()):
                    st.success("✅ Message sent to Control!")
                    st.rerun()
                else:
                    st.error("❌ Failed to send message. Please try again.")

def get_force_emoji(force_name):
    """Get appropriate emoji for force"""
    emoji_map = {
        "blue": "🔵", "red": "🔴", "yellow": "🟡", "green": "🟢", 
        "orange": "🟠", "purple": "🟣", "brown": "🟤", "black": "⚫"
    }
    return emoji_map.get(force_name.lower(), "🔶")

def show_overview_dashboard(project, rag):
    """Show high-level overview of all forces"""

    dp_tab, phase_tab, obj_tab, theater_tab = st.tabs(["🎯 DP Progress", "⏱️ Phase Progress", "🎖️ Objective Progress", "🏛️ Theater Progress"])

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
        st.markdown("*Quick overview of Objective execution status across all forces*")
        
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
    
    # Theater Progress Tab
    with theater_tab:
        # Show the same data as Theater Command tab
        st.subheader("🏛️ Theater Command Progress")
        st.markdown("*Theater commands and combined force progress (same as Theater Command tab)*")
        
        if not project:
            st.error("Please select a project first")
        else:
            # Load theater configuration
            theater_config = load_theater_config(project)
            
            if theater_config["theaters"]:
                # Display theater status (same as Theater Command tab)
                theater_names = list(theater_config["theaters"].keys())
                if theater_names:
                    cols = st.columns(len(theater_names))
                    for idx, (theater_name, theater_data) in enumerate(theater_config["theaters"].items()):
                        with cols[idx]:
                            # Calculate theater progress
                            theater_progress = calculate_theater_progress(project, theater_data["forces"])
                            
                            # Progress color coding
                            progress_color = "#ef4444" if theater_progress < 30 else "#f59e0b" if theater_progress < 70 else "#10b981"
                            
                            st.markdown(f"""
                            <div style="background:linear-gradient(135deg, {progress_color}15, {progress_color}05); 
                                        border:1px solid {progress_color}40; border-radius:12px; padding:1rem; margin-bottom:1rem;">
                                <h4 style="color:{progress_color}; margin:0; text-align:center; font-weight:600;">🏛️ {theater_name}</h4>
                                <div style="text-align:center; margin:0.5rem 0;">
                                    <span style="font-size:2rem; font-weight:bold; color:{progress_color};">{theater_progress:.1f}%</span><br>
                                    <span style="color:#666; font-size:0.9rem;">Average Progress</span>
                                </div>
                                <div style="color:#666; font-size:0.85rem; text-align:center;">
                                    Forces: {len(theater_data["forces"])}<br>
                                    {", ".join([f.capitalize() for f in theater_data["forces"]])}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("ℹ️ No theaters configured yet. Go to Theater Command tab to create theaters.")
                
            # Show unassigned forces if any
            if theater_config.get("unassigned_forces"):
                st.markdown("### 🔄 Unassigned Forces")
                unassigned_cols = st.columns(len(theater_config["unassigned_forces"]))
                for idx, force in enumerate(theater_config["unassigned_forces"]):
                    with unassigned_cols[idx]:
                        color = FORCE_COLORS.get(force, "#64748b")
                        st.markdown(f"""
                        <div style="background:{color}20; border:1px solid {color}60; 
                                    border-radius:8px; padding:0.5rem; text-align:center; color:{color};">
                            <strong>{force.capitalize()}</strong>
                        </div>
                        """, unsafe_allow_html=True)


                
                # RAG status breakdown
                st.markdown("**Status Breakdown:**")
                if green_count > 0:
                    st.markdown(f"� {green_count} Green")
                if amber_count > 0:
                    st.markdown(f"🟡 {amber_count} Amber") 
                if red_count > 0:
                    st.markdown(f"🔴 {red_count} Red")


def show_force_monitoring_dashboard(project, rag):
    """Show Control's monitoring view of forces' independent progress assessments"""
    st.subheader(" Force Independent Progress Monitoring")
    st.markdown("*Monitor progress assessments as reported by individual forces (independent tracking)*")
    
    # Create tabs for different progress types
    dp_tab, phase_tab, obj_tab = st.tabs([" DP Progress (Forces)", " Phase Progress (Forces)", " Objective Progress (Forces)"])
    
    # DP Progress Tab - Force Independent View
    with dp_tab:
        st.subheader(" Forces' DP Assessment Summary")
        st.markdown("*Decision Point progress as assessed by each force*")
        
        # Force status cards for DP (using independent data)
        cols = st.columns(min(len(SIDES), 4))  # Max 4 columns
        
        for idx, side in enumerate(SIDES):
            # Load independent force data (what forces are reporting)
            independent_data = load_independent_project(project, side)
            if not independent_data:
                independent_data = load_project(project, side)  # Fallback to base data
            
            progress = compute_progress(independent_data)
            
            with cols[idx % len(cols)]:
                color = FORCE_COLORS.get(side, "#8b5cf6")
                
                # Calculate DP summary from force's independent assessment
                dp_progress = list(progress["dp"].values()) if progress["dp"] else [0]
                avg_progress = sum(dp_progress) / len(dp_progress) if dp_progress else 0
                
                # Count RAG status
                red_count = sum(1 for v in dp_progress if v < rag["red"])
                amber_count = sum(1 for v in dp_progress if rag["red"] <= v < rag["amber"])
                green_count = sum(1 for v in dp_progress if v >= rag["amber"])
                
                # Force status card with indicator of independent assessment
                st.markdown(f"""
                <div style="background: {color}; color: white; padding: 16px; border-radius: 10px; margin-bottom: 10px; border: 2px solid #fbbf24;">
                    <h4 style="margin: 0; color: white;">{get_force_emoji(side)} {side.capitalize()}</h4>
                    <h2 style="margin: 5px 0; color: white;">{avg_progress:.1f}%</h2>
                    <p style="margin: 0; color: white; opacity: 0.9;">DP Progress</p>
                </div>
                """, unsafe_allow_html=True)
                
                # RAG status breakdown
                st.markdown("**Force''s Assessment:**")
                if green_count > 0:
                    st.markdown(f" {green_count} Good Progress")
                if amber_count > 0:
                    st.markdown(f" {amber_count} Moderate Progress") 
                if red_count > 0:
                    st.markdown(f" {red_count} Low Progress")
        
        # DP Comparison Section
        st.markdown("---")
        st.subheader("🔍 Control vs Force DP Assessment Comparison")
        st.markdown("*Compare Control's master data with Force's independent DP assessments*")
        
        cols = st.columns(min(len(SIDES), 2))  # Max 2 columns for better comparison view
        
        for idx, side in enumerate(SIDES):
            # Load Control's master data
            control_data = load_project(project, side)
            control_progress = compute_progress(control_data)
            
            # Load Force's independent assessment
            force_data = load_independent_project(project, side)
            if not force_data:
                force_data = load_project(project, side)
            force_progress = compute_progress(force_data)
            
            with cols[idx % len(cols)]:
                # Calculate Control's DP average
                if control_progress.get("dp"):
                    control_dp_avg = sum(control_progress["dp"].values()) / len(control_progress["dp"].values())
                else:
                    control_dp_avg = 0
                
                # Calculate Force's DP average
                if force_progress.get("dp"):
                    force_dp_avg = sum(force_progress["dp"].values()) / len(force_progress["dp"].values())
                else:
                    force_dp_avg = 0
                
                # Comparison indicator
                diff = force_dp_avg - control_dp_avg
                if abs(diff) <= 1:
                    status_color = "#10b981"
                    status_text = "🔄 Aligned"
                elif diff > 1:
                    status_color = "#f59e0b"
                    status_text = "📈 Force Higher"
                else:
                    status_color = "#ef4444"
                    status_text = "📉 Force Lower"
                
                st.markdown(f"""
                <div style="background: {status_color}20; border: 1px solid {status_color}40; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                    <h5 style="margin: 0; color: {status_color};">{get_force_emoji(side)} {side.capitalize()}</h5>
                    <p style="margin: 2px 0; font-size: 0.9rem;">Control View: {control_dp_avg:.1f}%</p>
                    <p style="margin: 2px 0; font-size: 0.9rem;">Force Assessment: {force_dp_avg:.1f}%</p>
                    <p style="margin: 2px 0; font-weight: bold; color: {status_color};">{status_text}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Phase Progress Tab - Force Independent View
    with phase_tab:
        st.subheader("⏱️ Forces' Phase Assessment Summary")
        st.markdown("*Phase progress as assessed by each force*")
        
        # Force status cards for Phase (using independent data)
        cols = st.columns(min(len(SIDES), 4))  # Max 4 columns
        
        for idx, side in enumerate(SIDES):
            # Load independent force data (what forces are reporting)
            independent_data = load_independent_project(project, side)
            if not independent_data:
                independent_data = load_project(project, side)  # Fallback to base data
            
            progress = compute_progress(independent_data)
            
            with cols[idx % len(cols)]:
                color = FORCE_COLORS.get(side, "#8b5cf6")
                
                # Calculate Phase summary from force's independent assessment
                phase_progress = list(progress["phase"].values()) if progress["phase"] else [0]
                avg_progress = sum(phase_progress) / len(phase_progress) if phase_progress else 0
                
                # Count RAG status
                red_count = sum(1 for v in phase_progress if v < rag["red"])
                amber_count = sum(1 for v in phase_progress if rag["red"] <= v < rag["amber"])
                green_count = sum(1 for v in phase_progress if v >= rag["amber"])
                
                # Force status card with indicator of independent assessment
                st.markdown(f"""
                <div style="background: {color}; color: white; padding: 16px; border-radius: 10px; margin-bottom: 10px; border: 2px solid #fbbf24;">
                    <h4 style="margin: 0; color: white;">{get_force_emoji(side)} {side.capitalize()}</h4>
                    <h2 style="margin: 5px 0; color: white;">{avg_progress:.1f}%</h2>
                    <p style="margin: 0; color: white; opacity: 0.9;">Phase Progress</p>
                </div>
                """, unsafe_allow_html=True)
                
                # RAG status breakdown
                st.markdown("**Force's Assessment:**")
                if green_count > 0:
                    st.markdown(f" {green_count} Good Progress")
                if amber_count > 0:
                    st.markdown(f" {amber_count} Moderate Progress") 
                if red_count > 0:
                    st.markdown(f" {red_count} Low Progress")
        
        # Phase Comparison Section
        st.markdown("---")
        st.subheader("🔍 Control vs Force Phase Assessment Comparison")
        st.markdown("*Compare Control's master data with Force's independent Phase assessments*")
        
        cols = st.columns(min(len(SIDES), 2))  # Max 2 columns for better comparison view
        
        for idx, side in enumerate(SIDES):
            # Load Control's master data
            control_data = load_project(project, side)
            control_progress = compute_progress(control_data)
            
            # Load Force's independent assessment
            force_data = load_independent_project(project, side)
            if not force_data:
                force_data = load_project(project, side)
            force_progress = compute_progress(force_data)
            
            with cols[idx % len(cols)]:
                # Calculate Control's Phase average
                if control_progress.get("phase"):
                    control_phase_avg = sum(control_progress["phase"].values()) / len(control_progress["phase"].values())
                else:
                    control_phase_avg = 0
                
                # Calculate Force's Phase average
                if force_progress.get("phase"):
                    force_phase_avg = sum(force_progress["phase"].values()) / len(force_progress["phase"].values())
                else:
                    force_phase_avg = 0
                
                # Comparison indicator
                diff = force_phase_avg - control_phase_avg
                if abs(diff) <= 1:
                    status_color = "#10b981"
                    status_text = "🔄 Aligned"
                elif diff > 1:
                    status_color = "#f59e0b"
                    status_text = "📈 Force Higher"
                else:
                    status_color = "#ef4444"
                    status_text = "📉 Force Lower"
                
                st.markdown(f"""
                <div style="background: {status_color}20; border: 1px solid {status_color}40; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                    <h5 style="margin: 0; color: {status_color};">{get_force_emoji(side)} {side.capitalize()}</h5>
                    <p style="margin: 2px 0; font-size: 0.9rem;">Control View: {control_phase_avg:.1f}%</p>
                    <p style="margin: 2px 0; font-size: 0.9rem;">Force Assessment: {force_phase_avg:.1f}%</p>
                    <p style="margin: 2px 0; font-weight: bold; color: {status_color};">{status_text}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Objective Progress Tab - Force Independent View
    with obj_tab:
        st.subheader("🎖️ Forces' Objective Assessment Summary")
        st.markdown("*Objective progress as assessed by each force*")
        
        # Force status cards for Objectives (using independent data)
        cols = st.columns(min(len(SIDES), 4))  # Max 4 columns
        
        for idx, side in enumerate(SIDES):
            # Load independent force data (what forces are reporting)
            independent_data = load_independent_project(project, side)
            if not independent_data:
                independent_data = load_project(project, side)  # Fallback to base data
            
            progress = compute_progress(independent_data)
            
            with cols[idx % len(cols)]:
                color = FORCE_COLORS.get(side, "#8b5cf6")
                
                # Calculate Objective summary from force's independent assessment
                obj_progress = list(progress["objective"].values()) if progress["objective"] else [0]
                avg_progress = sum(obj_progress) / len(obj_progress) if obj_progress else 0
                
                # Count RAG status
                red_count = sum(1 for v in obj_progress if v < rag["red"])
                amber_count = sum(1 for v in obj_progress if rag["red"] <= v < rag["amber"])
                green_count = sum(1 for v in obj_progress if v >= rag["amber"])
                
                # Force status card with indicator of independent assessment
                st.markdown(f"""
                <div style="background: {color}; color: white; padding: 16px; border-radius: 10px; margin-bottom: 10px; border: 2px solid #fbbf24;">
                    <h4 style="margin: 0; color: white;">{get_force_emoji(side)} {side.capitalize()}</h4>
                    <h2 style="margin: 5px 0; color: white;">{avg_progress:.1f}%</h2>
                    <p style="margin: 0; color: white; opacity: 0.9;">Objective Progress</p>
                </div>
                """, unsafe_allow_html=True)
                
                # RAG status breakdown
                st.markdown("**Force's Assessment:**")
                if green_count > 0:
                    st.markdown(f" {green_count} Good Progress")
                if amber_count > 0:
                    st.markdown(f" {amber_count} Moderate Progress") 
                if red_count > 0:
                    st.markdown(f" {red_count} Low Progress")
        
        # Objective Comparison Section
        st.markdown("---")
        st.subheader("🔍 Control vs Force Objective Assessment Comparison")
        st.markdown("*Compare Control's master data with Force's independent Objective assessments*")
        
        # Force comparison cards for Objectives
        cols = st.columns(min(len(SIDES), 2))  # Max 2 columns for better comparison view
        
        for idx, side in enumerate(SIDES):
            # Load Control's master data
            control_data = load_project(project, side)
            control_progress = compute_progress(control_data)
            
            # Load Force's independent assessment
            force_data = load_independent_project(project, side)
            if not force_data:
                force_data = load_project(project, side)  # Fallback to base data
            force_progress = compute_progress(force_data)
            
            with cols[idx % len(cols)]:
                color = FORCE_COLORS.get(side, "#8b5cf6")
                
                # Calculate Control's objective average
                if control_progress.get("objective"):
                    control_obj_avg = sum(control_progress["objective"].values()) / len(control_progress["objective"].values()) if control_progress.get("objective") else 0
                else:
                    control_obj_avg = 0
                
                # Calculate Force's objective average
                if force_progress.get("objective"):
                    force_obj_avg = sum(force_progress["objective"].values()) / len(force_progress["objective"].values()) if force_progress.get("objective") else 0
                else:
                    force_obj_avg = 0
                
                # Comparison indicator
                diff = force_obj_avg - control_obj_avg
                if abs(diff) <= 1:  # Very strict alignment threshold (within 1%)
                    status_color = "#10b981"
                    status_text = "🔄 Aligned"
                elif diff > 1:
                    status_color = "#f59e0b"
                    status_text = "📈 Force Higher"
                else:
                    status_color = "#ef4444"
                    status_text = "📉 Force Lower"
                
                st.markdown(f"""
                <div style="background: {status_color}20; border: 1px solid {status_color}40; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                    <h5 style="margin: 0; color: {status_color};">{get_force_emoji(side)} {side.capitalize()}</h5>
                    <p style="margin: 2px 0; font-size: 0.9rem;">Control View: {control_obj_avg:.1f}%</p>
                    <p style="margin: 2px 0; font-size: 0.9rem;">Force Assessment: {force_obj_avg:.1f}%</p>
                    <p style="margin: 2px 0; font-weight: bold; color: {status_color};">{status_text}</p>
                </div>
                """, unsafe_allow_html=True)

def show_force_dashboard(side, project, rag, independent=False):
    """Show detailed dashboard for a specific force"""
    if independent:
        st.subheader(f"📊 My Force Dashboard - Real-time Status")
        st.markdown(f"*{get_force_emoji(side)} {side.capitalize()} Force operational progress and analytics*")
    else:
        st.subheader(f"{get_force_emoji(side)} {side.capitalize()} Force - Detailed Analysis")
    
    # Load data using appropriate method based on mode
    if independent:
        data = load_independent_project(project, side)
    else:
        data = load_project(project, side)
    progress = compute_progress(data)
    
    if not any([progress.get("dp"), progress.get("objective"), progress.get("phase")]):
        if independent:
            st.warning(f"⚠️ No progress data available for {side.capitalize()} force dashboard.")
            st.info("""
            **Possible solutions:**
            1. 📊 Use **Force Progress Entry** to set some task progress first
            2. 🔄 Click **Reset Independent Data** button above to regenerate from base structure  
            3. 🔧 Ensure tasks, DPs, objectives, and phases are configured by Control
            """)
        else:
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
    
    # Sort DP data numerically by DP number for display
    dp_items = list(progress["dp"].items())
    dp_items.sort(key=lambda x: int(x[0]) if str(x[0]).isdigit() else float('inf'))
    
    dp_numbers = [item[0] for item in dp_items]
    dp_vals = [item[1] for item in dp_items]
    
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
        st.metric("🔴 Low Progress", red_count)
    with col2:
        st.metric("🟡 Moderate Progress", amber_count)
    with col3:
        st.metric("🟢 Good Progress", green_count)
    with col4:
        st.metric("📊 Average DP Progress", f"{avg_dp_progress:.1f}%")

def show_objective_analysis(progress, side):
    """Show objective analysis charts"""
    if not progress.get("objective"):
        st.info("No Objectives configured for this force.")
        return
        
    # Sort objectives numerically by objective name/number for display
    obj_items = list(progress["objective"].items())
    obj_items.sort(key=lambda x: get_numeric_sort_key({"Objective No": x[0]}, "Objective No"))
    
    obj_names = [item[0] for item in obj_items]
    obj_vals = [item[1] for item in obj_items]
    
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
        
    # Sort phases numerically by phase name/number for display
    phase_items = list(progress["phase"].items())
    phase_items.sort(key=lambda x: get_numeric_sort_key({"Phase No": x[0]}, "Phase No"))
    
    phase_names = [item[0] for item in phase_items]
    phase_vals = [item[1] for item in phase_items]
    
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

# --- Force Dashboard Tab ---
def force_dashboard_tab():
    """Independent dashboard for individual forces to view their own progress"""
    role = st.session_state.get("role")
    project = st.session_state.get("project")
    rag = st.session_state.get("rag", {"red": 40, "amber": 70})
    
    if role == "control":
        st.warning("⚠️ This is the Force Dashboard. Use the main Dashboard for control operations.")
        return
    
    # Get force emoji and display name
    force_emoji = get_force_emoji(role)
    force_display = role.upper() if role else "UNKNOWN"
    
    st.header(f"{force_emoji} {force_display} Force Dashboard")
    st.markdown(f"*Independent progress monitoring and operational status for {force_display} Force*")
    
    if not role or role not in SIDES:
        st.error("❌ Invalid force role. Please contact your administrator.")
        return
    
    # Option to reset independent data if needed
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Reset Independent Data", help="Regenerate independent data from base structure"):
            independent_file = f"{project}_{role}_independent.json"
            if os.path.exists(independent_file):
                os.remove(independent_file)
            st.success("Independent data reset. Please refresh the page.")
            st.rerun()
    
    # Show only this force's dashboard
    show_force_dashboard(role, project, rag, independent=True)

def force_progress_entry_tab():
    """Independent progress entry for individual forces"""
    role = st.session_state.get("role")
    project = st.session_state.get("project")
    
    if role == "control":
        st.warning("⚠️ This is the Force Progress Entry. Use the main Progress Entry for control operations.")
        return
    
    # Get force emoji and display name  
    force_emoji = get_force_emoji(role)
    force_display = role.upper() if role else "UNKNOWN"
    
    st.header(f"{force_emoji} {force_display} Force Progress Entry")
    st.markdown(f"*Independent progress tracking and task management for {force_display} Force*")
    
    if not role or role not in SIDES:
        st.error("❌ Invalid force role. Please contact your administrator.")
        return
    
    # Show force-specific progress entry interface
    show_force_progress_entry(project, role, independent=True)

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

# --- Theater Command Tab ---
def theater_command_tab():
    st.header("🏛️ Theater Command")
    st.write("Manage theater groupings and view combined progress.")
    
    if not st.session_state.get("project"):
        st.error("Please select a project first")
        return
        
    project = st.session_state["project"]
    
    # Load theater configuration
    theater_config = load_theater_config(project)
    available_forces = get_available_forces(project)
    
    if not available_forces:
        st.warning("⚠️ No forces found. Please add forces in Force Manager first.")
        return
    
    # Display current theaters
    st.subheader("📊 Current Theater Status")
    
    if theater_config["theaters"]:
        # Create columns for theater overview
        theater_names = list(theater_config["theaters"].keys())
        if theater_names:
            cols = st.columns(len(theater_names))
            for idx, (theater_name, theater_data) in enumerate(theater_config["theaters"].items()):
                with cols[idx]:
                    # Calculate theater progress
                    theater_progress = calculate_theater_progress(project, theater_data["forces"])
                    
                    # Progress color coding
                    progress_color = "#ef4444" if theater_progress < 30 else "#f59e0b" if theater_progress < 70 else "#10b981"
                    
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg, {progress_color}15, {progress_color}05); 
                                border:1px solid {progress_color}40; border-radius:12px; padding:1rem; margin-bottom:1rem;">
                        <h4 style="color:white; margin:0; text-align:center; text-shadow:none; font-weight:600;">🏛️ {theater_name}</h4>
                        <div style="text-align:center; margin:0.5rem 0;">
                            <span style="font-size:2rem; font-weight:bold; color:{progress_color}; text-shadow:none;">{theater_progress:.1f}%</span><br>
                            <span style="color:#e5e7eb; font-size:0.9rem; text-shadow:none;">Average Progress</span>
                        </div>
                        <div style="color:#e5e7eb; font-size:0.85rem; text-align:center; text-shadow:none;">
                            Forces: {len(theater_data["forces"])}<br>
                            {", ".join([f.capitalize() for f in theater_data["forces"]])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Theater management buttons
                    if st.button(f"Manage {theater_name}", key=f"manage_{theater_name}"):
                        st.session_state[f"managing_theater"] = theater_name
                    if st.button(f"Delete {theater_name}", key=f"delete_{theater_name}", type="secondary"):
                        # Move forces back to unassigned
                        theater_config["unassigned_forces"].extend(theater_data["forces"])
                        del theater_config["theaters"][theater_name]
                        save_theater_config(project, theater_config)
                        st.success(f"Deleted theater {theater_name}")
                        st.rerun()
    else:
        st.info("No theaters configured yet. Create your first theater below.")
    
    # Show unassigned forces
    if theater_config["unassigned_forces"]:
        st.subheader("🔄 Unassigned Forces")
        unassigned_cols = st.columns(len(theater_config["unassigned_forces"]))
        for idx, force in enumerate(theater_config["unassigned_forces"]):
            with unassigned_cols[idx]:
                color = FORCE_COLORS.get(force, "#64748b")
                st.markdown(f"""
                <div style="background:{color}20; border:1px solid {color}60; 
                            border-radius:8px; padding:0.5rem; text-align:center; color:{color};">
                    <strong>{force.capitalize()}</strong>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Create new theater
    st.subheader("➕ Create New Theater")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        new_theater_name = st.text_input("Theater Name", placeholder="e.g., Northern Theater")
    
    with col2:
        # Get unassigned forces for selection
        unassigned = [f for f in available_forces if f not in [force for theater in theater_config["theaters"].values() for force in theater["forces"]]]
        if unassigned:
            selected_forces = st.multiselect("Select Forces for Theater", unassigned)
        else:
            st.info("All forces are already assigned to theaters")
            selected_forces = []
    
    if st.button("Create Theater", type="primary") and new_theater_name and selected_forces:
        if new_theater_name not in theater_config["theaters"]:
            theater_config["theaters"][new_theater_name] = {
                "forces": selected_forces,
                "created_date": str(datetime.now().date())
            }
            # Remove forces from unassigned list
            theater_config["unassigned_forces"] = [f for f in theater_config["unassigned_forces"] if f not in selected_forces]
            save_theater_config(project, theater_config)
            st.success(f"Created theater '{new_theater_name}' with forces: {', '.join([f.capitalize() for f in selected_forces])}")
            st.rerun()
        else:
            st.error("Theater name already exists")
    
    # Theater management section
    if st.session_state.get("managing_theater"):
        managing = st.session_state["managing_theater"]
        if managing in theater_config["theaters"]:
            st.markdown("---")
            st.subheader(f"🔧 Managing Theater: {managing}")
            
            theater_data = theater_config["theaters"][managing]
            current_forces = theater_data["forces"]
            
            # Show current forces in theater
            st.write(f"**Current Forces in {managing}:**")
            if current_forces:
                force_cols = st.columns(len(current_forces))
                for idx, force in enumerate(current_forces):
                    with force_cols[idx]:
                        color = FORCE_COLORS.get(force, "#64748b")
                        st.markdown(f"""
                        <div style="background:{color}; color:#fff; padding:0.5rem; 
                                    border-radius:8px; text-align:center;">
                            {force.capitalize()}
                        </div>
                        """, unsafe_allow_html=True)
            
            # Add/Remove forces
            col_add, col_remove = st.columns(2)
            
            with col_add:
                # Forces available to add
                available_to_add = [f for f in available_forces if f not in current_forces]
                if available_to_add:
                    forces_to_add = st.multiselect("Add Forces", available_to_add, key=f"add_forces_{managing}")
                    if st.button("Add Selected Forces", key=f"add_btn_{managing}") and forces_to_add:
                        theater_config["theaters"][managing]["forces"].extend(forces_to_add)
                        theater_config["unassigned_forces"] = [f for f in theater_config["unassigned_forces"] if f not in forces_to_add]
                        save_theater_config(project, theater_config)
                        st.success(f"Added forces to {managing}")
                        st.rerun()
            
            with col_remove:
                if current_forces:
                    forces_to_remove = st.multiselect("Remove Forces", current_forces, key=f"remove_forces_{managing}")
                    if st.button("Remove Selected Forces", key=f"remove_btn_{managing}") and forces_to_remove:
                        theater_config["theaters"][managing]["forces"] = [f for f in current_forces if f not in forces_to_remove]
                        theater_config["unassigned_forces"].extend(forces_to_remove)
                        save_theater_config(project, theater_config)
                        st.success(f"Removed forces from {managing}")
                        st.rerun()
            
            if st.button("Done Managing", key=f"done_{managing}"):
                del st.session_state["managing_theater"]
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
    elif selected == "Chat":
        chat_tab()
    elif selected == "Force Progress Entry":
        force_progress_entry_tab()
    elif selected == "Force Dashboard":
        force_dashboard_tab()
    elif selected == "Control Panel":
        control_panel_tab()
    elif selected == "Force Manager":
        force_manager_tab()
    elif selected == "Theater Command":
        theater_command_tab()
    elif selected == "Project Management":
        project_management()
    elif selected == "Logout":
        clear_session()
    show_footer()

if __name__ == "__main__":
    main()
