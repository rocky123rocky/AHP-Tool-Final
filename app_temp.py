
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
    return ["blue", "red"]

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

.footer {{ 
    background: linear-gradient(45deg, #000080, #1e40af); 
    color: #fff; 
    text-align: center; 
    padding: 12px; 
    font-size: 18px; 
    font-weight: bold;
    border-top: 3px solid #fbbf24;
}}
.sidebar .sidebar-content {{ background: {accent}; }}
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
    color: #000080 !important;
    background: #fffbf0 !important;
    border-color: #000080 !important;
}}
.stTabs [data-baseweb="tab"] {{ 
    background: linear-gradient(45deg, #000080, {accent}); 
    color: #fff; 
    border-radius: 8px;
    margin: 2px;
}}
h1, h2, h3, h4 {{ 
    color: #000080; 
    text-shadow: 0 2px 8px #fbbf24; 
    font-weight: bold;
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
    
    # Indian Navy themed main page with tricolor elements
    st.markdown("""
    <style>
    .main-container {
        padding: 20px;
        margin: 10px auto;
        max-width: 1200px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .title-section {
        background: linear-gradient(45deg, #000080, #1e40af);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 15px;
        border: 2px solid #fbbf24;
        flex-shrink: 0;
    }
    .navy-emblem {
        font-size: 3rem;
        margin-bottom: 10px;
        display: none;
    }
    .force-selection {
        background: rgba(255,255,255,0.95);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border: 2px solid #000080;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .big-button {
        width: 100%;
        height: 80px;
        font-size: 1.3rem;
        font-weight: bold;
        border-radius: 10px;
        margin: 8px 0;
        border: 2px solid;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .control-btn {
        background: linear-gradient(45deg, #22c55e, #16a34a);
        color: white;
        border-color: #15803d;
    }
    .control-btn:hover {
        background: linear-gradient(45deg, #16a34a, #15803d);
        transform: scale(1.05);
    }
    .blue-btn {
        background: linear-gradient(45deg, #3b82f6, #1d4ed8);
        color: white;
        border-color: #1e40af;
    }
    .blue-btn:hover {
        background: linear-gradient(45deg, #1d4ed8, #1e40af);
        transform: scale(1.05);
    }
    .red-btn {
        background: linear-gradient(45deg, #ef4444, #dc2626);
        color: white;
        border-color: #b91c1c;
    }
    .red-btn:hover {
        background: linear-gradient(45deg, #dc2626, #b91c1c);
        transform: scale(1.05);
    }
    .login-section {
        background: rgba(255,255,255,0.9);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border: 2px solid #000080;
        flex-shrink: 0;
    }
    .team-credits {
        text-align: center;
        margin-top: 10px;
        flex-shrink: 0;
    }
    .tricolor-line {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main container with tricolor theme
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Title section with Navy theme
    st.markdown("""
    <div class="title-section">
        <div class="navy-emblem">�</div>
        <h1 style='font-size:2.5rem;margin:8px 0;text-shadow:2px 2px 4px rgba(0,0,0,0.5);'>COPP AHP Military Planner</h1>
        <h3 style='font-size:1.2rem;margin:4px 0;'>🏛️ NAVAL WING, DSSC Wellington 🏛️</h3>
        <p style='font-size:1.2rem;margin:10px 0;font-style:italic;'>&quot;To War With Wisdom&quot;</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Force selection section
    st.markdown('<div class="force-selection">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#000080;margin-bottom:20px;font-size:1.6rem;'>🎯 Select Your Role 🎯</h2>", unsafe_allow_html=True)
    
    # Create columns for force selection
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🟢 CONTROL", key="big_control_btn_login", help="Access control panel and manage all forces"):
            st.session_state["login_role"] = "control"
    
    with col2:
        if st.button("🔵 BLUE FORCE", key="big_blue_btn_login", help="Access blue force planning"):
            st.session_state["login_role"] = "blue"
    
    with col3:
        if st.button("🔴 RED FORCE", key="big_red_btn_login", help="Access red force planning"):
            st.session_state["login_role"] = "red"

    st.markdown('</div>', unsafe_allow_html=True)  # Close force-selection
    
    # Additional forces (if any)
    additional_forces = [side for side in SIDES if side not in ["blue", "red"]]
    if additional_forces:
        st.markdown('<div class="force-selection">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center;color:#000080;margin-bottom:20px;'>⚡ Additional Forces ⚡</h3>", unsafe_allow_html=True)
        
        add_cols = st.columns(len(additional_forces))
        for idx, side in enumerate(additional_forces):
            with add_cols[idx]:
                color = FORCE_COLORS.get(side, "#8b5cf6")
                if st.button(f"⚡ {side.upper()}\n🌟 SPECIAL OPERATIONS 🌟", key=f"big_{side}_btn_login"):
                    st.session_state["login_role"] = side
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Login section
    role = st.session_state.get("login_role")
    if role:
        st.markdown('<div class="login-section">', unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center;color:#000080;margin-bottom:20px;'>🔐 Authentication for {role.upper()} 🔐</h3>", unsafe_allow_html=True)
        
        col_pin, col_btn = st.columns([2, 1])
        with col_pin:
            pin = st.text_input(f"Enter PIN for {role.capitalize()}:", type="password", placeholder="Enter your secure PIN")
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)  # Align with input
            if st.button("🚀 LOGIN", key="login_btn", help="Click to authenticate"):
                valid = False
                if role == "control":
                    valid = (pin == st.session_state.get("pin_control", "9999"))
                elif role in SIDES:
                    valid = (pin == st.session_state.get(f"pin_{role}", "0000" if role not in ["blue", "red"] else ("2222" if role == "blue" else "1111")))
                if valid:
                    st.session_state["role"] = role
                    st.session_state["side"] = role if role != "control" else "blue"
                    st.success(f"✅ Successfully logged in as {role.capitalize()}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Invalid PIN - Access Denied")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Team credits section
    st.markdown('<div class="team-credits">', unsafe_allow_html=True)

    if st.button("👥 View AHP Development Team", key="ahp_team_view_btn", help="View team credits"):
        st.session_state["show_team_view_modal"] = True
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close main-container
    
    # Team View Modal (Read-only)
    if st.session_state.get("show_team_view_modal"):
        st.markdown("<div style='background:#fff;border-radius:12px;padding:24px;box-shadow:0 2px 12px #0003;position:relative;z-index:100;'>", unsafe_allow_html=True)
        st.subheader("AHP Team Credits")
        # Load team data from file
        team = load_ahp_team()
        st.markdown("### Team Members:")
        for i, member in enumerate(team, 1):
            st.write(f"{i}. **{member['name']}** — {member['role']}")
        if st.button("Close", key="close_team_view_modal"):
            st.session_state["show_team_view_modal"] = False
        st.markdown("</div>", unsafe_allow_html=True)

# --- Sidebar Navigation ---
def sidebar():
    role = st.session_state.get("role", "")
    inject_css(role)
    st.sidebar.title("Navigation")
    if role == "control":
        tabs = ["Phases", "Objectives", "Decisive Points", "Tasks", "Progress Entry", "Dashboard", "Control Panel", "Force Manager", "Project Management", "Logout"]
    else:
        tabs = ["Phases", "Objectives", "Decisive Points", "Tasks", "KO Method", "Project Management", "Logout"]
    selected = st.sidebar.radio("Go to:", tabs)
    return selected

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
    st.header("Objectives")
    project = st.session_state.get("project")
    role = st.session_state.get("role")
    if role == "control":
        st.subheader("All Forces - Objectives Comparison")
        for force in SIDES:
            data = load_project(project, force)
            objectives = data.get("objectives", [])
            
            if objectives:
                # Handle different possible column names from Excel
                objective_data = []
                for idx, obj in enumerate(objectives):
                    # Try multiple possible column names for objective name
                    name = (obj.get("Name") or obj.get("Objective") or 
                           obj.get("name") or obj.get("objective") or 
                           obj.get("Objective Name") or obj.get("objective name"))
                    
                    # If no standard name found, try to get the first non-empty value
                    if not name and obj:
                        for key, value in obj.items():
                            if value and str(value).strip():
                                name = str(value).strip()
                                break
                    
                    # Try multiple possible column names for phase
                    phase = (obj.get("Phase") or obj.get("phase") or 
                            obj.get("Phase Name") or obj.get("phase name") or "")
                    
                    # Ensure we have at least some name
                    if not name:
                        name = f"Objective {idx+1}"
                    
                    objective_data.append({
                        "Objective No": idx + 1,
                        "Objective Name": str(name).strip(),
                        "Phase": str(phase).strip() if phase else ""
                    })
                
                df = pd.DataFrame(objective_data)
            else:
                df = pd.DataFrame({
                    "Objective No": [],
                    "Objective Name": [],
                    "Phase": []
                })
            
            st.write(f"{force.capitalize()} Objectives:")
            st.dataframe(df, use_container_width=True)
    else:
        side = st.session_state.get("side")
        data = load_project(project, side)
        objectives = data.get("objectives", [])
        
        if objectives:
            # Handle different possible column names from Excel
            objective_data = []
            for idx, obj in enumerate(objectives):
                # Try multiple possible column names for objective name
                name = (obj.get("Name") or obj.get("Objective") or 
                       obj.get("name") or obj.get("objective") or 
                       obj.get("Objective Name") or obj.get("objective name"))
                
                # If no standard name found, try to get the first non-empty value
                if not name and obj:
                    for key, value in obj.items():
                        if value and str(value).strip():
                            name = str(value).strip()
                            break
                
                # Try multiple possible column names for phase
                phase = (obj.get("Phase") or obj.get("phase") or 
                        obj.get("Phase Name") or obj.get("phase name") or "")
                
                # Ensure we have at least some name
                if not name:
                    name = f"Objective {idx+1}"
                
                objective_data.append({
                    "Objective No": idx + 1,
                    "Objective Name": str(name).strip(),
                    "Phase": str(phase).strip() if phase else ""
                })
            
            df = pd.DataFrame(objective_data)
        else:
            df = pd.DataFrame({
                "Objective No": [],
                "Objective Name": [],
                "Phase": []
            })
        
        st.dataframe(df, use_container_width=True)
    # Show hierarchical view of Phases → Objectives
    st.subheader("Phase-Objective Hierarchy")
    if role == "control":
        # Show all forces
        for force in SIDES:
            data = load_project(project, force)
            phases = data.get("phases", [])
            objectives = data.get("objectives", [])
            
            if phases:
                st.write(f"**{force.capitalize()} Force:**")
                for phase in phases:
                    phase_name = phase.get("Name") or phase.get("Phase", "Unknown Phase")
                    phase_objectives = [obj for obj in objectives if obj.get("Phase") == phase_name]
                    
                    with st.expander(f"📋 Phase: {phase_name} ({len(phase_objectives)} objectives)"):
                        if phase_objectives:
                            for i, obj in enumerate(phase_objectives, 1):
                                st.write(f"{i}. {obj.get('Name', 'Unnamed Objective')}")
                        else:
                            st.info("No objectives in this phase yet")
    else:
        # Show current side only
        if side:
            data = load_project(project, side)
            phases = data.get("phases", [])
            objectives = data.get("objectives", [])
            
            if phases:
                st.write(f"**{side.capitalize()} Force:**")
                for phase in phases:
                    phase_name = phase.get("Name") or phase.get("Phase", "Unknown Phase")
                    phase_objectives = [obj for obj in objectives if obj.get("Phase") == phase_name]
                    
                    with st.expander(f"📋 Phase: {phase_name} ({len(phase_objectives)} objectives)"):
                        if phase_objectives:
                            for i, obj in enumerate(phase_objectives, 1):
                                st.write(f"{i}. {obj.get('Name', 'Unnamed Objective')}")
                        else:
                            st.info("No objectives in this phase yet")

    # Add objective (for control or current side)
    st.subheader("Add New Objective")
    if role in ["control"] + SIDES:
        name = st.text_input("Objective Name", key="new_obj_name")
        # Collect all phases for selectbox
        all_phases = []
        for force in SIDES:
            data = load_project(project, force)
            all_phases.extend([p.get("Name") or p.get("Phase") for p in data.get("phases", [])])
        all_phases = list(set([p for p in all_phases if p]))
        
        if all_phases:
            phase = st.selectbox("Select Phase", all_phases, key="new_obj_phase")
            if st.button("Add Objective") and name and phase:
                # Add to all forces if control, else just current side
                if role == "control":
                    for force in SIDES:
                        data = load_project(project, force)
                        if "objectives" not in data:
                            data["objectives"] = []
                        data["objectives"].append({"Name": name, "Phase": phase})
                        save_project(project, force, data)
                    st.success(f"Objective '{name}' added to phase '{phase}' for all forces.")
                else:
                    data = load_project(project, side)
                    if "objectives" not in data:
                        data["objectives"] = []
                    data["objectives"].append({"Name": name, "Phase": phase})
                    save_project(project, side, data)
                    st.success(f"Objective '{name}' added to phase '{phase}'.")
                st.rerun()
        else:
            st.warning("No phases available. Please add phases first in the Phases tab.")
    
    st.divider()
    
    # Edit and Delete Objectives Section
    st.subheader("✏️ Edit & Delete Objectives")
    if role == "control":
        # Control can edit objectives for all forces
        selected_force_edit = st.selectbox("Select Force to Edit", SIDES, key="obj_edit_force")
        data = load_project(project, selected_force_edit)
    else:
        selected_force_edit = side
        data = load_project(project, side)
    
    objectives = data.get("objectives", [])
    
    if objectives:
        obj_options = [f"{i+1}. {obj.get('Name', 'Unnamed Objective')} (Phase: {obj.get('Phase', 'No Phase')})" for i, obj in enumerate(objectives)]
        selected_obj_idx = st.selectbox("Select Objective to Edit/Delete", range(len(objectives)), format_func=lambda x: obj_options[x], key="obj_edit_select")
        
        if selected_obj_idx is not None:
            selected_obj = objectives[selected_obj_idx]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Edit Objective**")
                new_obj_name = st.text_input("Objective Name", value=selected_obj.get("Name", ""), key="edit_obj_name")
                
                # Get available phases for dropdown
                all_phases = []
                for force in SIDES:
                    force_data = load_project(project, force)
                    all_phases.extend([p.get("Name") or p.get("Phase") for p in force_data.get("phases", [])])
                all_phases = list(set([p for p in all_phases if p]))
                
                current_phase = selected_obj.get("Phase", "")
                if all_phases:
                    try:
                        phase_index = all_phases.index(current_phase) if current_phase in all_phases else 0
                    except:
                        phase_index = 0
                    new_phase = st.selectbox("Phase", all_phases, index=phase_index, key="edit_obj_phase")
                else:
                    new_phase = st.text_input("Phase (manual)", value=current_phase, key="edit_obj_phase_manual")
                
                if st.button("💾 Save Changes", key="save_obj_changes"):
                    if new_obj_name:
                        old_obj_name = selected_obj.get("Name")
                        objectives[selected_obj_idx]["Name"] = new_obj_name
                        objectives[selected_obj_idx]["Phase"] = new_phase
                        
                        if role == "control":
                            # Update for all forces
                            for force in SIDES:
                                force_data = load_project(project, force)
                                if selected_obj_idx < len(force_data.get("objectives", [])):
                                    force_data["objectives"][selected_obj_idx]["Name"] = new_obj_name
                                    force_data["objectives"][selected_obj_idx]["Phase"] = new_phase
                                    # Update references in DPs
                                    for dp in force_data.get("dps", []):
                                        if dp.get("Objective") == old_obj_name:
                                            dp["Objective"] = new_obj_name
                                    save_project(project, force, force_data)
                            st.success(f"Objective updated to '{new_obj_name}' for all forces!")
                        else:
                            data["objectives"] = objectives
                            # Update references in DPs
                            for dp in data.get("dps", []):
                                if dp.get("Objective") == old_obj_name:
                                    dp["Objective"] = new_obj_name
                            save_project(project, selected_force_edit, data)
                            st.success(f"Objective updated to '{new_obj_name}'!")
                        st.rerun()
                    else:
                        st.error("Objective name cannot be empty")
            
            with col2:
                st.markdown("**Delete Objective**")
                st.warning(f"⚠️ This will delete objective: {selected_obj.get('Name')}")
                st.write("This action will also remove all DPs and tasks associated with this objective.")
                
                if st.button("🗑️ Delete Objective", key="delete_obj_btn", type="secondary"):
                    obj_name_to_delete = selected_obj.get("Name")
                    
                    if role == "control":
                        # Delete from all forces
                        for force in SIDES:
                            force_data = load_project(project, force)
                            if selected_obj_idx < len(force_data.get("objectives", [])):
                                del force_data["objectives"][selected_obj_idx]
                                # Remove DPs associated with this objective
                                dp_nos_to_remove = [dp.get("DP No") for dp in force_data.get("dps", []) if dp.get("Objective") == obj_name_to_delete]
                                force_data["dps"] = [dp for dp in force_data.get("dps", []) if dp.get("Objective") != obj_name_to_delete]
                                # Remove tasks associated with DPs of this objective
                                force_data["tasks"] = [task for task in force_data.get("tasks", []) if task.get("DP No") not in dp_nos_to_remove]
                                save_project(project, force, force_data)
                        st.success(f"Objective '{obj_name_to_delete}' deleted from all forces!")
                    else:
                        del objectives[selected_obj_idx]
                        data["objectives"] = objectives
                        # Remove DPs associated with this objective
                        dp_nos_to_remove = [dp.get("DP No") for dp in data.get("dps", []) if dp.get("Objective") == obj_name_to_delete]
                        data["dps"] = [dp for dp in data.get("dps", []) if dp.get("Objective") != obj_name_to_delete]
                        # Remove tasks associated with DPs of this objective
                        data["tasks"] = [task for task in data.get("tasks", []) if task.get("DP No") not in dp_nos_to_remove]
                        save_project(project, selected_force_edit, data)
                        st.success(f"Objective '{obj_name_to_delete}' deleted!")
                    st.rerun()
    else:
        st.info("No objectives available to edit or delete.")
    # --- Phases Tab ---
# Move phases_tab to top-level scope
def phases_tab():
    st.header("Phases")
    project = st.session_state.get("project")
    role = st.session_state.get("role")
    if role == "control":
        st.subheader("All Forces - Phases Comparison")
        for force in SIDES:
            color = FORCE_COLORS.get(force, "#0f172a")
            data = load_project(project, force)
            phases = data.get("phases", [])
            df = pd.DataFrame({
                "Phase No": [idx + 1 for idx in range(len(phases))],
                "Phase Name": [p.get("Name") or p.get("Phase") for p in phases]
            })
            st.markdown(f"<div style='color:{color};font-weight:bold'>{force.capitalize()} Phases:</div>", unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)
    else:
        side = st.session_state.get("side")
        color = FORCE_COLORS.get(side, "#0f172a")
        data = load_project(project, side)
        phases = data.get("phases", [])
        df = pd.DataFrame({
            "Phase No": [idx + 1 for idx in range(len(phases))],
            "Phase Name": [p.get("Name") or p.get("Phase") for p in phases]
        })
        st.markdown(f"<div style='color:{color};font-weight:bold'>{side.capitalize()} Phases:</div>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
    # Add phase (for control or current side)
    if role == "control" or role in SIDES:
        name = st.text_input("Phase Name")
        if st.button("Add Phase") and name:
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
    
    st.divider()
    
    # Edit and Delete Phases Section
    st.subheader("✏️ Edit & Delete Phases")
    if role == "control":
        # Control can edit phases for all forces
        selected_force_edit = st.selectbox("Select Force to Edit", SIDES, key="phase_edit_force")
        data = load_project(project, selected_force_edit)
    else:
        selected_force_edit = side
        data = load_project(project, side)
    
    phases = data.get("phases", [])
    
    if phases:
        phase_options = [f"{i+1}. {phase.get('Name', 'Unnamed Phase')}" for i, phase in enumerate(phases)]
        selected_phase_idx = st.selectbox("Select Phase to Edit/Delete", range(len(phases)), format_func=lambda x: phase_options[x], key="phase_edit_select")
        
        if selected_phase_idx is not None:
            selected_phase = phases[selected_phase_idx]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Edit Phase**")
                new_name = st.text_input("Phase Name", value=selected_phase.get("Name", ""), key="edit_phase_name")
                
                if st.button("💾 Save Changes", key="save_phase_changes"):
                    if new_name:
                        old_name = selected_phase.get("Name")
                        phases[selected_phase_idx]["Name"] = new_name
                        
                        if role == "control":
                            # Update for all forces
                            for force in SIDES:
                                force_data = load_project(project, force)
                                if selected_phase_idx < len(force_data.get("phases", [])):
                                    force_data["phases"][selected_phase_idx]["Name"] = new_name
                                    # Also update references in objectives
                                    for obj in force_data.get("objectives", []):
                                        if obj.get("Phase") == old_name:
                                            obj["Phase"] = new_name
                                    save_project(project, force, force_data)
                            st.success(f"Phase updated to '{new_name}' for all forces!")
                        else:
                            data["phases"] = phases
                            # Update references in objectives
                            for obj in data.get("objectives", []):
                                if obj.get("Phase") == old_name:
                                    obj["Phase"] = new_name
                            save_project(project, selected_force_edit, data)
                            st.success(f"Phase updated to '{new_name}'!")
                        st.rerun()
                    else:
                        st.error("Phase name cannot be empty")
            
            with col2:
                st.markdown("**Delete Phase**")
                st.warning(f"⚠️ This will delete phase: {selected_phase.get('Name')}")
                st.write("This action will also remove all objectives associated with this phase.")
                
                if st.button("🗑️ Delete Phase", key="delete_phase_btn", type="secondary"):
                    phase_name_to_delete = selected_phase.get("Name")
                    
                    if role == "control":
                        # Delete from all forces
                        for force in SIDES:
                            force_data = load_project(project, force)
                            if selected_phase_idx < len(force_data.get("phases", [])):
                                del force_data["phases"][selected_phase_idx]
                                # Remove objectives associated with this phase
                                force_data["objectives"] = [obj for obj in force_data.get("objectives", []) if obj.get("Phase") != phase_name_to_delete]
                                save_project(project, force, force_data)
                        st.success(f"Phase '{phase_name_to_delete}' deleted from all forces!")
                    else:
                        del phases[selected_phase_idx]
                        data["phases"] = phases
                        # Remove objectives associated with this phase
                        data["objectives"] = [obj for obj in data.get("objectives", []) if obj.get("Phase") != phase_name_to_delete]
                        save_project(project, selected_force_edit, data)
                        st.success(f"Phase '{phase_name_to_delete}' deleted!")
                    st.rerun()
    else:
        st.info("No phases available to edit or delete.")

# --- Decisive Points Tab ---
def dps_tab():
    st.header("Decisive Points (DPs)")
    project = st.session_state.get("project")
    role = st.session_state.get("role")
    side = st.session_state.get("side")
    
    # Show DP table first
    st.subheader("DP Summary Table")
    if role == "control":
        for force in SIDES:
            data = load_project(project, force)
            dps = data.get("dps", [])
            color = FORCE_COLORS.get(force, "#0f172a")
            
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
            
            st.markdown(f"<div style='color:{color};font-weight:bold'>{force.capitalize()} DPs:</div>", unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)
    else:
        if side:
            data = load_project(project, side)
            dps = data.get("dps", [])
            color = FORCE_COLORS.get(side, "#0f172a")
            
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
            
            st.markdown(f"<div style='color:{color};font-weight:bold'>{side.capitalize()} DPs:</div>", unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)
    
    st.divider()
    
    # Show hierarchical view of Objectives → DPs
    st.subheader("Objective-DP Hierarchy")
    if role == "control":
        # Show all forces
        for force in SIDES:
            data = load_project(project, force)
            objectives = data.get("objectives", [])
            dps = data.get("dps", [])
            
            if objectives:
                st.write(f"**{force.capitalize()} Force:**")
                for objective in objectives:
                    obj_name = objective.get("Name", "Unknown Objective")
                    obj_phase = objective.get("Phase", "")
                    obj_dps = [dp for dp in dps if dp.get("Objective") == obj_name]
                    
                    with st.expander(f"🎯 Objective: {obj_name} (Phase: {obj_phase}) - {len(obj_dps)} DPs"):
                        if obj_dps:
                            for i, dp in enumerate(obj_dps, 1):
                                dp_name = dp.get("Name", "Unnamed DP")
                                dp_no = dp.get("DP No", i)
                                weight = dp.get("Weight", "")
                                st.write(f"{i}. **DP {dp_no}**: {dp_name} (Weight: {weight})")
                        else:
                            st.info("No DPs assigned to this objective yet")
            else:
                st.info(f"No objectives found for {force} force")
    else:
        # Show current side only
        if side:
            data = load_project(project, side)
            objectives = data.get("objectives", [])
            dps = data.get("dps", [])
            
            if objectives:
                st.write(f"**{side.capitalize()} Force:**")
                for objective in objectives:
                    obj_name = objective.get("Name", "Unknown Objective")
                    obj_phase = objective.get("Phase", "")
                    obj_dps = [dp for dp in dps if dp.get("Objective") == obj_name]
                    
                    with st.expander(f"🎯 Objective: {obj_name} (Phase: {obj_phase}) - {len(obj_dps)} DPs"):
                        if obj_dps:
                            for i, dp in enumerate(obj_dps, 1):
                                dp_name = dp.get("Name", "Unnamed DP")
                                dp_no = dp.get("DP No", i)
                                weight = dp.get("Weight", "")
                                st.write(f"{i}. **DP {dp_no}**: {dp_name} (Weight: {weight})")
                        else:
                            st.info("No DPs assigned to this objective yet")
            else:
                st.info("No objectives found. Please add objectives first in the Objectives tab.")
    # Add DP (for control or current side)
    st.subheader("Add New DP")
    if role in ["control"] + SIDES:
        # Collect all objectives and phases for selectbox
        all_objectives = []
        all_phases = []
        for force in SIDES:
            data = load_project(project, force)
            all_objectives.extend([o.get("Name") for o in data.get("objectives", []) if o.get("Name")])
            all_phases.extend([p.get("Name") or p.get("Phase") for p in data.get("phases", [])])
        all_objectives = list(set(all_objectives))
        all_phases = list(set([p for p in all_phases if p]))
        
        if all_objectives:
            objective = st.selectbox("Select Objective", all_objectives, key="new_dp_objective", help="Choose the objective this DP belongs to")
            
            # Auto-generate unique DP number across entire system
            all_existing_dp_nos = set()
            for force in SIDES:
                data = load_project(project, force)
                for dp in data.get("dps", []):
                    dp_no_val = dp.get("DP No")
                    if dp_no_val is not None:
                        all_existing_dp_nos.add(int(dp_no_val) if str(dp_no_val).isdigit() else 0)
            
            # Find next available unique DP number
            suggested_dp_no = 1
            while suggested_dp_no in all_existing_dp_nos:
                suggested_dp_no += 1
                
            dp_no = st.number_input("DP Number (Unique)", min_value=1, value=suggested_dp_no, key="new_dp_no", help=f"Suggested: {suggested_dp_no} (next unique DP number across all forces)")
            
            # Validate uniqueness
            if dp_no in all_existing_dp_nos:
                st.error(f"DP Number {dp_no} already exists! Please choose a different number.")
                st.stop()
            name = st.text_input("DP Name", key="new_dp_name", help="Descriptive name for this decisive point")
            
            if all_phases:
                phase = st.selectbox("Select Phase", all_phases, key="new_dp_phase")
            else:
                phase = st.text_input("Phase (manual)", key="new_dp_phase_manual")
                
            weight = st.slider("Weight/Priority", 1, 5, 3, key="new_dp_weight", help="1=Low priority, 5=High priority")
            force_group = st.text_input("Force Group", key="new_dp_force_group", help="Which force group is responsible")
            
            if st.button("Add DP") and name and objective:
                if role == "control":
                    for force in SIDES:
                        data = load_project(project, force)
                        if "dps" not in data:
                            data["dps"] = []
                        data["dps"].append({
                            "DP No": dp_no, 
                            "Name": name, 
                            "Objective": objective, 
                            "Phase": phase, 
                            "Weight": weight, 
                            "Force Group": force_group
                        })
                        save_project(project, force, data)
                    st.success(f"DP '{name}' added to objective '{objective}' for all forces.")
                else:
                    data = load_project(project, side)
                    if "dps" not in data:
                        data["dps"] = []
                    data["dps"].append({
                        "DP No": dp_no, 
                        "Name": name, 
                        "Objective": objective, 
                        "Phase": phase, 
                        "Weight": weight, 
                        "Force Group": force_group
                    })
                    save_project(project, side, data)
                    st.success(f"DP '{name}' added to objective '{objective}'.")
                st.rerun()
        else:
            st.warning("No objectives available. Please add objectives first in the Objectives tab.")
    
    st.divider()
    
    # Edit and Delete DPs Section
    st.subheader("✏️ Edit & Delete DPs")
    if role == "control":
        # Control can edit DPs for all forces
        selected_force_edit = st.selectbox("Select Force to Edit", SIDES, key="dp_edit_force")
        data = load_project(project, selected_force_edit)
    else:
        selected_force_edit = side
        data = load_project(project, side)
    
    dps = data.get("dps", [])
    
    if dps:
        dp_options = [f"DP {dp.get('DP No', 'N/A')}: {dp.get('Name', 'Unnamed DP')} (Objective: {dp.get('Objective', 'No Objective')})" for dp in dps]
        selected_dp_idx = st.selectbox("Select DP to Edit/Delete", range(len(dps)), format_func=lambda x: dp_options[x], key="dp_edit_select")
        
        if selected_dp_idx is not None:
            selected_dp = dps[selected_dp_idx]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Edit DP**")
                
                # Get all existing DP numbers for uniqueness check
                all_existing_dp_nos = set()
                for force in SIDES:
                    force_data = load_project(project, force)
                    for dp in force_data.get("dps", []):
                        dp_no_val = dp.get("DP No")
                        if dp_no_val is not None and dp != selected_dp:  # Exclude current DP
                            all_existing_dp_nos.add(int(dp_no_val) if str(dp_no_val).isdigit() else 0)
                
                current_dp_no = selected_dp.get("DP No", 1)
                new_dp_no = st.number_input("DP Number (Unique)", min_value=1, value=int(current_dp_no) if str(current_dp_no).isdigit() else 1, key="edit_dp_no")
                
                # Check uniqueness
                dp_no_valid = new_dp_no not in all_existing_dp_nos or new_dp_no == current_dp_no
                if not dp_no_valid:
                    st.error(f"DP Number {new_dp_no} already exists! Please choose a different number.")
                
                new_dp_name = st.text_input("DP Name", value=selected_dp.get("Name", ""), key="edit_dp_name")
                
                # Get available objectives
                all_objectives = []
                for force in SIDES:
                    force_data = load_project(project, force)
                    all_objectives.extend([o.get("Name") for o in force_data.get("objectives", []) if o.get("Name")])
                all_objectives = list(set(all_objectives))
                
                current_objective = selected_dp.get("Objective", "")
                if all_objectives:
                    try:
                        obj_index = all_objectives.index(current_objective) if current_objective in all_objectives else 0
                    except:
                        obj_index = 0
                    new_objective = st.selectbox("Objective", all_objectives, index=obj_index, key="edit_dp_objective")
                else:
                    new_objective = st.text_input("Objective (manual)", value=current_objective, key="edit_dp_objective_manual")
                
                new_weight = st.slider("Weight/Priority", 1, 5, int(selected_dp.get("Weight", 3)), key="edit_dp_weight")
                new_force_group = st.text_input("Force Group", value=selected_dp.get("Force Group", ""), key="edit_dp_force_group")
                
                if st.button("💾 Save Changes", key="save_dp_changes") and dp_no_valid:
                    if new_dp_name and new_objective:
                        old_dp_no = selected_dp.get("DP No")
                        dps[selected_dp_idx].update({
                            "DP No": new_dp_no,
                            "Name": new_dp_name,
                            "Objective": new_objective,
                            "Weight": new_weight,
                            "Force Group": new_force_group
                        })
                        
                        if role == "control":
                            # Update for all forces
                            for force in SIDES:
                                force_data = load_project(project, force)
                                if selected_dp_idx < len(force_data.get("dps", [])):
                                    force_data["dps"][selected_dp_idx].update({
                                        "DP No": new_dp_no,
                                        "Name": new_dp_name,
                                        "Objective": new_objective,
                                        "Weight": new_weight,
                                        "Force Group": new_force_group
                                    })
                                    # Update references in tasks
                                    for task in force_data.get("tasks", []):
                                        if str(task.get("DP No", "")) == str(old_dp_no) or str(task.get("dp_no", "")) == str(old_dp_no):
                                            task["DP No"] = new_dp_no
                                            task["dp_no"] = new_dp_no
                                    save_project(project, force, force_data)
                            st.success(f"DP updated for all forces!")
                        else:
                            data["dps"] = dps
                            # Update references in tasks
                            for task in data.get("tasks", []):
                                if str(task.get("DP No", "")) == str(old_dp_no) or str(task.get("dp_no", "")) == str(old_dp_no):
                                    task["DP No"] = new_dp_no
                                    task["dp_no"] = new_dp_no
                            save_project(project, selected_force_edit, data)
                            st.success(f"DP updated!")
                        st.rerun()
                    else:
                        st.error("DP name and objective are required")
            
            with col2:
                st.markdown("**Delete DP**")
                st.warning(f"⚠️ This will delete DP {selected_dp.get('DP No')}: {selected_dp.get('Name')}")
                st.write("This action will also remove all tasks associated with this DP.")
                
                if st.button("🗑️ Delete DP", key="delete_dp_btn", type="secondary"):
                    dp_no_to_delete = selected_dp.get("DP No")
                    
                    if role == "control":
                        # Delete from all forces
                        for force in SIDES:
                            force_data = load_project(project, force)
                            if selected_dp_idx < len(force_data.get("dps", [])):
                                del force_data["dps"][selected_dp_idx]
                                # Remove tasks associated with this DP
                                force_data["tasks"] = [task for task in force_data.get("tasks", []) 
                                                      if str(task.get("DP No", "")) != str(dp_no_to_delete) and 
                                                         str(task.get("dp_no", "")) != str(dp_no_to_delete)]
                                save_project(project, force, force_data)
                        st.success(f"DP {dp_no_to_delete} deleted from all forces!")
                    else:
                        del dps[selected_dp_idx]
                        data["dps"] = dps
                        # Remove tasks associated with this DP
                        data["tasks"] = [task for task in data.get("tasks", []) 
                                        if str(task.get("DP No", "")) != str(dp_no_to_delete) and 
                                           str(task.get("dp_no", "")) != str(dp_no_to_delete)]
                        save_project(project, selected_force_edit, data)
                        st.success(f"DP {dp_no_to_delete} deleted!")
                    st.rerun()
    else:
        st.info("No DPs available to edit or delete.")

# --- Tasks Tab ---
def tasks_tab():
    st.header("Tasks")
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
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info(f"No tasks assigned to DP {dp_no}")
    
    if role == "control":
        st.subheader("All Forces - Tasks by DP")
        for force in SIDES:
            color = FORCE_COLORS.get(force, "#0f172a")
            st.markdown(f"<div style='color:{color};font-weight:bold;font-size:18px'>{force.capitalize()} Force:</div>", unsafe_allow_html=True)
            data = load_project(project, force)
            display_tasks_hierarchically(force, data)
            st.divider()
    else:
        if side:
            color = FORCE_COLORS.get(side, "#0f172a")
            st.markdown(f"<div style='color:{color};font-weight:bold;font-size:18px'>{side.capitalize()} Tasks by DP:</div>", unsafe_allow_html=True)
            data = load_project(project, side)
            display_tasks_hierarchically(side, data)
    
    # Add New Task Section
    st.subheader("Add New Task")
    if role in ["control"] + SIDES:
        # Get available DPs for selection
        if role == "control":
            all_dps = []
            for force in SIDES:
                force_data = load_project(project, force)
                for dp in force_data.get("dps", []):
                    dp_no = dp.get("DP No", dp.get("dp_no", ""))
                    dp_name = dp.get("Name", f"DP {dp_no}")
                    dp_objective = dp.get("Objective", "")
                    all_dps.append({
                        "display": f"DP {dp_no}: {dp_name} (Objective: {dp_objective}, Force: {force})", 
                        "dp_no": dp_no,
                        "force": force
                    })
        else:
            data = load_project(project, side)
            all_dps = []
            for dp in data.get("dps", []):
                dp_no = dp.get("DP No", dp.get("dp_no", ""))
                dp_name = dp.get("Name", f"DP {dp_no}")
                dp_objective = dp.get("Objective", "")
                all_dps.append({
                    "display": f"DP {dp_no}: {dp_name} (Objective: {dp_objective})", 
                    "dp_no": dp_no
                })
        
        if all_dps:
            selected_dp = st.selectbox(
                "Select DP", 
                all_dps, 
                format_func=lambda x: x["display"],
                key="new_task_dp",
                help="Choose which DP this task belongs to"
            )
            
            task_name = st.text_input("Task Name", key="new_task_name", help="Descriptive name for this task")
            description = st.text_area("Description", key="new_task_description", help="Detailed description of the task")
            force_group = st.text_input("Force Group", key="new_task_force_group", help="Which force group is responsible")
            type_ = st.selectbox("Type", ["T", "I"], key="new_task_type", help="Task type: T=Tactical, I=Intelligence")
            criteria = st.text_input("Criteria", key="new_task_criteria", help="Success criteria for this task")
            weight = st.slider("Weight/Priority", 0.0, 1.0, 0.1, step=0.1, key="new_task_weight", help="Task importance (0.1=Low, 1.0=High)")
            progress = st.slider("Progress (%)", 0, 100, 0, key="new_task_progress", help="Current completion percentage")
            
            if st.button("Add Task") and task_name and selected_dp:
                new_task = {
                    "Task Name": task_name,
                    "Desc": description,
                    "DP No": selected_dp["dp_no"],
                    "Force Group": force_group,
                    "Type": type_,
                    "Criteria": criteria,
                    "Weight": weight,
                    "Stated %": weight * 100,  # Convert to percentage
                    "Progress": progress,
                    "Achieved %": progress
                }
                
                if role == "control":
                    # Add to all forces or specific force
                    if "force" in selected_dp:
                        # Add to specific force
                        force_data = load_project(project, selected_dp["force"])
                        if "tasks" not in force_data:
                            force_data["tasks"] = []
                        force_data["tasks"].append(new_task)
                        save_project(project, selected_dp["force"], force_data)
                        st.success(f"Task '{task_name}' added to {selected_dp['force']} force.")
                    else:
                        # Add to all forces
                        for force in SIDES:
                            force_data = load_project(project, force)
                            if "tasks" not in force_data:
                                force_data["tasks"] = []
                            force_data["tasks"].append(new_task)
                            save_project(project, force, force_data)
                        st.success(f"Task '{task_name}' added to all forces.")
                else:
                    data = load_project(project, side)
                    if "tasks" not in data:
                        data["tasks"] = []
                    data["tasks"].append(new_task)
                    save_project(project, side, data)
                    st.success(f"Task '{task_name}' added to DP {selected_dp['dp_no']}.")
                st.rerun()
        else:
            st.warning("No DPs available. Please add DPs first in the DPs tab.")
    
    st.divider()
    
    # Edit and Delete Tasks Section
    st.subheader("✏️ Edit & Delete Tasks")
    if role == "control":
        # Control can edit tasks for all forces
        selected_force_edit = st.selectbox("Select Force to Edit", SIDES, key="task_edit_force")
        data = load_project(project, selected_force_edit)
    else:
        selected_force_edit = side
        data = load_project(project, side)
    
    tasks = data.get("tasks", [])
    
    if tasks:
        # Create task options with better descriptions
        task_options = []
        for i, task in enumerate(tasks):
            task_name = (task.get("description") or task.get("Desc") or task.get("Name") or 
                        task.get("Task Name") or task.get("desc") or task.get("name") or 
                        task.get("task name") or task.get("Task") or task.get("task") or
                        task.get("Description") or f"Task {i+1}")
            dp_no = task.get("DP No") or task.get("dp_no") or "No DP"
            task_options.append(f"{i+1}. {task_name} (DP: {dp_no})")
        
        selected_task_idx = st.selectbox("Select Task to Edit/Delete", range(len(tasks)), format_func=lambda x: task_options[x], key="task_edit_select")
        
        if selected_task_idx is not None:
            selected_task = tasks[selected_task_idx]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Edit Task**")
                
                # Task name
                current_task_name = (selected_task.get("description") or selected_task.get("Desc") or selected_task.get("Name") or 
                                    selected_task.get("Task Name") or selected_task.get("desc") or selected_task.get("name") or 
                                    selected_task.get("task name") or selected_task.get("Task") or selected_task.get("task") or
                                    selected_task.get("Description") or "")
                new_task_name = st.text_input("Task Name", value=current_task_name, key="edit_task_name")
                
                # Description
                new_description = st.text_area("Description", value=selected_task.get("Desc", ""), key="edit_task_description")
                
                # Get available DPs for selection
                available_dps = []
                for dp in data.get("dps", []):
                    dp_no = dp.get("DP No", dp.get("dp_no", ""))
                    dp_name = dp.get("Name", f"DP {dp_no}")
                    dp_objective = dp.get("Objective", "")
                    available_dps.append({
                        "display": f"DP {dp_no}: {dp_name} (Objective: {dp_objective})", 
                        "dp_no": dp_no
                    })
                
                current_dp_no = selected_task.get("DP No") or selected_task.get("dp_no")
                if available_dps:
                    try:
                        dp_index = next(i for i, dp in enumerate(available_dps) if str(dp["dp_no"]) == str(current_dp_no))
                    except:
                        dp_index = 0
                    selected_dp = st.selectbox("Select DP", available_dps, index=dp_index, format_func=lambda x: x["display"], key="edit_task_dp")
                else:
                    selected_dp = {"dp_no": current_dp_no}
                    st.text_input("DP No (manual)", value=str(current_dp_no), key="edit_task_dp_manual")
                
                # Other fields
                new_force_group = st.text_input("Force Group", value=selected_task.get("Force Group", ""), key="edit_task_force_group")
                current_type = selected_task.get("Type", "T")
                type_index = 0 if current_type == "T" else 1
                new_type = st.selectbox("Type", ["T", "I"], index=type_index, key="edit_task_type")
                new_criteria = st.text_input("Criteria", value=selected_task.get("Criteria", ""), key="edit_task_criteria")
                
                # Progress fields
                current_weight = selected_task.get("stated") or selected_task.get("Weight") or selected_task.get("weight") or 0
                try:
                    current_weight = float(str(current_weight).replace('%', '')) if current_weight else 0
                except:
                    current_weight = 0
                    
                current_progress = selected_task.get("achieved") or selected_task.get("Achieved %") or selected_task.get("progress") or 0
                try:
                    current_progress = float(str(current_progress).replace('%', '')) if current_progress else 0
                except:
                    current_progress = 0
                
                new_weight = st.slider("Weight/Priority", 0.0, 100.0, current_weight, step=0.1, key="edit_task_weight")
                new_progress = st.slider("Progress (%)", 0.0, 100.0, current_progress, step=0.1, key="edit_task_progress")
                
                current_intangible = selected_task.get("Intangible", "nil")
                intangible_index = ["nil", "partial", "complete"].index(current_intangible) if current_intangible in ["nil", "partial", "complete"] else 0
                new_intangible = st.selectbox("Intangible Assessment", ["nil", "partial", "complete"], index=intangible_index, key="edit_task_intangible")
                
                if st.button("💾 Save Changes", key="save_task_changes"):
                    if new_task_name:
                        # Update task with all fields
                        updated_task = {
                            "Task Name": new_task_name,
                            "Name": new_task_name,
                            "Desc": new_description,
                            "description": new_task_name,
                            "DP No": selected_dp["dp_no"] if available_dps else current_dp_no,
                            "dp_no": selected_dp["dp_no"] if available_dps else current_dp_no,
                            "Force Group": new_force_group,
                            "Type": new_type,
                            "Criteria": new_criteria,
                            "Weight": new_weight,
                            "weight": new_weight,
                            "stated": new_weight,
                            "Stated %": new_weight,
                            "Progress": new_progress,
                            "progress": new_progress,
                            "achieved": new_progress,
                            "Achieved %": new_progress,
                            "Progress %": new_progress,
                            "Intangible": new_intangible
                        }
                        
                        # Preserve any additional fields from the original task
                        for key, value in selected_task.items():
                            if key not in updated_task:
                                updated_task[key] = value
                        
                        tasks[selected_task_idx] = updated_task
                        
                        if role == "control":
                            # Update for all forces
                            for force in SIDES:
                                force_data = load_project(project, force)
                                if selected_task_idx < len(force_data.get("tasks", [])):
                                    force_data["tasks"][selected_task_idx] = updated_task.copy()
                                    save_project(project, force, force_data)
                            st.success(f"Task '{new_task_name}' updated for all forces!")
                        else:
                            data["tasks"] = tasks
                            save_project(project, selected_force_edit, data)
                            st.success(f"Task '{new_task_name}' updated!")
                        st.rerun()
                    else:
                        st.error("Task name cannot be empty")
            
            with col2:
                st.markdown("**Delete Task**")
                task_name_display = (selected_task.get("description") or selected_task.get("Desc") or 
                                   selected_task.get("Name") or selected_task.get("Task Name") or "Unnamed Task")
                st.warning(f"⚠️ This will delete task: {task_name_display}")
                
                if st.button("🗑️ Delete Task", key="delete_task_btn", type="secondary"):
                    if role == "control":
                        # Delete from all forces
                        for force in SIDES:
                            force_data = load_project(project, force)
                            if selected_task_idx < len(force_data.get("tasks", [])):
                                del force_data["tasks"][selected_task_idx]
                                save_project(project, force, force_data)
                        st.success(f"Task '{task_name_display}' deleted from all forces!")
                    else:
                        del tasks[selected_task_idx]
                        data["tasks"] = tasks
                        save_project(project, selected_force_edit, data)
                        st.success(f"Task '{task_name_display}' deleted!")
                    st.rerun()
    else:
        st.info("No tasks available to edit or delete.")

# --- KO Method Tab ---
def ko_tab():
    import itertools
    st.header("KO Method (Pairwise DP Weightage)")
    s = st.session_state
    project = s.get("project")
    side = s.get("side")
    data = load_project(project, side)
    dps = data.get("dps", [])
    # Support both 'DP No' and 'dp_no' keys
    def get_dp_no(dp):
        return dp.get("DP No") or dp.get("dp_no")
    if len(dps) < 2:
        st.info("Need at least 2 DPs for KO comparison. KO is optional.")
        return
    pairs = list(itertools.combinations(dps, 2))
    key_prefix = f"ko_{project}_{side}"
    # Initialize KO session state
    if f"{key_prefix}_idx" not in s:
        s[f"{key_prefix}_idx"] = 0
        s[f"{key_prefix}_scores"] = {get_dp_no(d): 1 for d in dps if get_dp_no(d) is not None}
    idx = s[f"{key_prefix}_idx"]
    scores = s[f"{key_prefix}_scores"]
    # KO Voting UI
    if idx < len(pairs):
        a, b = pairs[idx]
        st.write(f"Comparison {idx+1} of {len(pairs)}")
        colA, colB = st.columns(2)
        if colA.button(f"A: {a.get('Name', a.get('name', ''))}"):
            scores[get_dp_no(a)] += 1
            s[f"{key_prefix}_idx"] += 1
            st.rerun()
        if colB.button(f"B: {b.get('Name', b.get('name', ''))}"):
            scores[get_dp_no(b)] += 1
            s[f"{key_prefix}_idx"] += 1
            st.rerun()
    else:
        # All pairs compared, compute weights
        mx = max(scores.values()) if scores else 1
        for d in dps:
            dp_no = get_dp_no(d)
            if dp_no in scores:
                d["Weight"] = round((scores[dp_no] / mx) * 5, 2)
        save_project(project, side, data)
        st.success("KO complete! DP Weights updated (scaled to max 5).")
        st.write("DP Weights:", {d.get("Name", d.get("name", "")): d["Weight"] for d in dps if "Weight" in d})
        if st.button("Restart KO"):
            s[f"{key_prefix}_idx"] = 0
            s[f"{key_prefix}_scores"] = {get_dp_no(d): 1 for d in dps if get_dp_no(d) is not None}
            st.rerun()

# --- Progress Entry Tab (Control Only) ---
def progress_entry_tab():
    st.header("Progress Entry (Control Only)")
    project = st.session_state.get("project")
    
    # Force selection for easier navigation
    selected_force = st.selectbox("Select Force to Update", SIDES, key="progress_force_select")
    
    data = load_project(project, selected_force)
    tasks = data.get("tasks", [])
    dps = data.get("dps", [])
    
    color = FORCE_COLORS.get(selected_force, "#0f172a")
    st.markdown(f"<h3 style='color:{color}'>{selected_force.capitalize()} Force - Progress Update</h3>", unsafe_allow_html=True)
    
    if not tasks:
        st.info(f"No tasks found for {selected_force}. Please add tasks in the Tasks tab.")
        return
    
    # Group tasks by DP for organized display
    tasks_by_dp = {}
    for i, task in enumerate(tasks):
        dp_no = task.get("DP No") or task.get("dp_no") or "Unassigned"
        if str(dp_no) not in tasks_by_dp:
            tasks_by_dp[str(dp_no)] = []
        tasks_by_dp[str(dp_no)].append((i, task))
    
    # Display tasks by DP with progress update interface
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
            if not dp_tasks:
                st.info(f"No tasks found for DP {dp_no}")
                continue
                
            for task_idx, (original_idx, task) in enumerate(dp_tasks):
                # Get task name with fallback
                task_name = (task.get("description") or task.get("Desc") or task.get("Name") or 
                           task.get("Task Name") or task.get("desc") or task.get("name") or 
                           task.get("task name") or task.get("Task") or task.get("task") or
                           task.get("Description") or f"Task {task.get('Task No', task_idx+1)}")
                
                st.markdown(f"**Task {task_idx+1}: {task_name}**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Current progress display
                    current_weight = task.get("stated") or task.get("Weight") or task.get("weight") or task.get("Wt") or task.get("wt") or 0
                    current_progress = task.get("achieved") or task.get("Achieved %") or task.get("progress") or task.get("Progress") or task.get("achieved %") or task.get("Progress %") or 0
                    
                    # Handle string percentages
                    try:
                        current_weight = float(str(current_weight).replace('%', '')) if current_weight else 0
                    except:
                        current_weight = 0
                    try:
                        current_progress = float(str(current_progress).replace('%', '')) if current_progress else 0
                    except:
                        current_progress = 0
                    
                    st.info(f"Current Weight: {current_weight}%")
                    st.info(f"Current Progress: {current_progress}%")
                    
                    # Task details
                    st.write(f"**Force Group:** {task.get('Force Group', 'Not specified')}")
                    st.write(f"**Type:** {task.get('Type', 'Not specified')}")
                    st.write(f"**Criteria:** {task.get('Criteria', 'Not specified')}")
                
                with col2:
                    # Progress update controls
                    unique_key = f"progress_{selected_force}_{dp_no}_{original_idx}"
                    
                    new_weight = st.slider(
                        "Update Weight %", 
                        0.0, 100.0, 
                        float(current_weight), 
                        step=0.1,
                        key=f"weight_{unique_key}",
                        help="Task importance/weightage percentage"
                    )
                    
                    new_progress = st.slider(
                        "Update Progress %", 
                        0.0, 100.0, 
                        float(current_progress), 
                        step=0.1,
                        key=f"progress_{unique_key}",
                        help="Task completion percentage"
                    )
                    
                    # Additional intangible assessment
                    intangible = st.selectbox(
                        "Intangible Assessment",
                        ["nil", "partial", "complete"],
                        index=["nil", "partial", "complete"].index(task.get("Intangible", "nil")),
                        key=f"intangible_{unique_key}",
                        help="Qualitative assessment beyond measurable progress"
                    )
                    
                    if st.button(f"💾 Update Task Progress", key=f"save_{unique_key}"):
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
                        save_project(project, selected_force, data)
                        
                        st.success(f"✅ Task '{task_name}' progress updated!")
                        st.balloons()
                        st.rerun()
                
                st.divider()

# --- Dashboard Tab (Control Only) ---
def dashboard_tab():
    st.header("Dashboard (Control Only)")
    project = st.session_state.get("project")
    rag = st.session_state.get("rag", {"red": 40, "amber": 70})
    col1, col2 = st.columns(2)
    for idx, side in enumerate(SIDES):
        data = load_project(project, side)
        progress = compute_progress(data)
        with [col1, col2][idx % 2]:
            st.subheader(f"{side.capitalize()} Force")
            # DP Bar Chart
            dp_vals = list(progress["dp"].values())
            dp_names = list(progress["dp"].keys())
            colors = ["#7f1d1d" if v < rag["red"] else "#f59e42" if v < rag["amber"] else "#1e3a8a" for v in dp_vals]
            fig = go.Figure([go.Bar(x=dp_names, y=dp_vals, marker_color=colors)])
            fig.update_layout(title="DP Progress", yaxis_title="%", xaxis_title="DP No")
            st.plotly_chart(fig, use_container_width=True, key=f"dp_chart_{side}")
            # Objective Pie Chart
            obj_vals = list(progress["objective"].values())
            obj_names = list(progress["objective"].keys())
            fig2 = go.Figure([go.Pie(labels=obj_names, values=obj_vals)])
            fig2.update_layout(title="Objective Progress")
            st.plotly_chart(fig2, use_container_width=True, key=f"obj_chart_{side}")
            # Phase Line Chart
            phase_vals = list(progress["phase"].values())
            phase_names = list(progress["phase"].keys())
            fig3 = go.Figure([go.Scatter(x=phase_names, y=phase_vals, mode="lines+markers")])
            fig3.update_layout(title="Phase Progress", yaxis_title="%", xaxis_title="Phase")
            st.plotly_chart(fig3, use_container_width=True, key=f"phase_chart_{side}")
            # Mini Gauges for Objectives
            for obj, val in progress["objective"].items():
                st.metric(label=f"Objective: {obj}", value=f"{val:.1f}%")

# --- Control Panel Tab ---
def control_panel_tab():
    st.header("Control Panel")
    
    # RAG Threshold Settings
    st.subheader("📊 RAG Threshold Settings")
    rag = st.session_state.get("rag", {"red": 40, "amber": 70})
    red = st.slider("Red Threshold", 0, 100, rag["red"])
    amber = st.slider("Amber Threshold", 0, 100, rag["amber"])
    st.session_state["rag"] = {"red": red, "amber": amber}
    
    st.divider()
    
    # Force Password Management
    st.subheader("🔐 Force Password Management")
    project = st.session_state.get("project")
    pwd_control = st.text_input("Control PIN", value=st.session_state.get("pin_control", "9999"), type="password", key="pin_control_panel_cp")
    pwd_blue = st.text_input("Blue Force PIN", value=st.session_state.get("pin_blue", "2222"), type="password", key="pin_blue_panel_cp")
    pwd_red = st.text_input("Red Force PIN", value=st.session_state.get("pin_red", "1111"), type="password", key="pin_red_panel_cp")
    for force in SIDES:
        if force not in ["control", "blue", "red"]:
            st.session_state.setdefault(f"pin_{force}", "0000")
            pin_val = st.text_input(f"{force.capitalize()} PIN", value=st.session_state.get(f"pin_{force}", "0000"), type="password", key=f"pin_{force}_panel_cp")
            if st.button(f"Save {force.capitalize()} PIN", key=f"save_pin_{force}_panel_cp"):
                st.session_state[f"pin_{force}"] = pin_val
                st.success(f"{force.capitalize()} PIN updated.")
    if st.button("Save All PINs", key="save_all_pins_panel_cp"):
        st.session_state["pin_control"] = pwd_control
        st.session_state["pin_blue"] = pwd_blue
        st.session_state["pin_red"] = pwd_red
        st.success("All PINs updated.")
    
    st.divider()
    
    # AHP Team Management (Control Only)
    st.subheader("👥 AHP Team Management")
    # Load team data from persistent file
    if "ahp_team" not in st.session_state:
        st.session_state["ahp_team"] = load_ahp_team()
    
    team = st.session_state["ahp_team"]
    
    # Display current team members
    st.markdown("**Current Team Members:**")
    for i, member in enumerate(team):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            new_name = st.text_input(f"Name", value=member["name"], key=f"cp_team_name_{i}")
        with col2:
            new_role = st.text_input(f"Role", value=member["role"], key=f"cp_team_role_{i}")
        with col3:
            if st.button("🗑️", key=f"delete_member_{i}", help="Delete this member"):
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
            # Auto-save on every change
            save_ahp_team(team)
    
    col_add, col_save = st.columns(2)
    with col_add:
        if st.button("➕ Add Team Member", key="add_team_member_cp"):
            team.append({"name": "", "role": ""})
            st.session_state["ahp_team"] = team
            save_ahp_team(team)
            st.success("New team member slot added!")
            st.rerun()
    
    with col_save:
        if st.button("💾 Save Team Changes", key="save_team_credits_cp"):
            # Filter out empty entries
            filtered_team = [member for member in team if member["name"].strip() or member["role"].strip()]
            st.session_state["ahp_team"] = filtered_team
            save_ahp_team(filtered_team)
            st.success("Team credits saved successfully!")
            st.balloons()
    
    # Team Statistics and Status
    st.markdown("---")
    col_stats, col_status = st.columns([2, 1])
    with col_stats:
        st.markdown(f"**📈 Team Statistics:** {len([m for m in team if m['name'].strip()])} active members")
    with col_status:
        if os.path.exists(AHP_TEAM_FILE):
            st.success("✅ Data saved to file")
        else:
            st.info("💾 Click save to persist changes")
    
    # Export team data option
    if st.button("📥 Export Team Data", key="export_team_data"):
        current_team = load_ahp_team()  # Load fresh data from file
        team_json = json.dumps(current_team, indent=2)
        st.download_button(
            label="Download Team Data (JSON)",
            data=team_json,
            file_name="ahp_team_credits.json",
            mime="application/json",
            key="download_team_json"
        )

# --- Force Manager Tab ---
def force_manager_tab():
    st.header("Force Manager")
    global SIDES
    st.write("Current Forces:")
    cols = st.columns(len(SIDES))
    for idx, side in enumerate(SIDES):
        color = FORCE_COLORS.get(side, "#0f172a")
        with cols[idx]:
            st.markdown(f"<div style='background:{color};color:#fff;padding:8px;border-radius:8px;text-align:center;'>{side.capitalize()}</div>", unsafe_allow_html=True)
            if side not in ["blue", "red"]:
                if st.button(f"Remove {side.capitalize()}", key=f"remove_{side}"):
                    SIDES.remove(side)
                    save_forces(SIDES)
                    st.success(f"Removed {side.capitalize()} force.")
                    st.rerun()
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
