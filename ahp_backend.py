
import os
import json
import pandas as pd
import zipfile
from datetime import datetime

FORCES_FILE = "forces.json"
def load_forces():
    if os.path.exists(FORCES_FILE):
        with open(FORCES_FILE, "r") as f:
            return json.load(f)
    return ["blue", "red"]

PROJECTS_DIR = "projects"
ARCHIVE_DIR = "archive"

os.makedirs(PROJECTS_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

SIDES = load_forces()

DEFAULT_METADATA = {
    "name": "",
    "description": "",
    "status": "active",
    "created": "",
    "modified": ""
}

DEFAULT_STRUCTURE = {
    "metadata": DEFAULT_METADATA.copy(),
    "phases": [],
    "objectives": [],
    "dps": [],
    "tasks": [],
    "ko": {},
    "progress": {},
    "control": {}
}

def get_project_path(project_name, side):
    return os.path.join(PROJECTS_DIR, f"{project_name}_{side}.json")

def get_archive_path(project_name, side):
    return os.path.join(ARCHIVE_DIR, f"{project_name}_{side}.json")

def list_projects():
    files = os.listdir(PROJECTS_DIR)
    projects = set()
    for f in files:
        if f.endswith(".json"):
            name = f.split("_")[0]
            projects.add(name)
    return sorted(list(projects))

def load_project(project_name, side):
    path = get_project_path(project_name, side)
    if not os.path.exists(path):
        data = DEFAULT_STRUCTURE.copy()
        data["metadata"] = DEFAULT_METADATA.copy()
        data["metadata"]["name"] = project_name
        data["metadata"]["created"] = datetime.now().isoformat()
        save_project(project_name, side, data)
    with open(path, "r") as f:
        return json.load(f)

def save_project(project_name, side, data):
    data["metadata"]["modified"] = datetime.now().isoformat()
    path = get_project_path(project_name, side)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def archive_project(project_name):
    for side in SIDES:
        src = get_project_path(project_name, side)
        dst = get_archive_path(project_name, side)
        if os.path.exists(src):
            os.replace(src, dst)

def delete_project(project_name):
    """Move ALL project files to archive instead of deleting - dismounts from active projects"""
    # Move all files starting with project_name (handles control, pink, and any other variants)
    files = os.listdir(PROJECTS_DIR)
    for f in files:
        if f.startswith(f"{project_name}_") and f.endswith(".json"):
            src = os.path.join(PROJECTS_DIR, f)
            dst = os.path.join(ARCHIVE_DIR, f)
            if os.path.exists(src):
                os.replace(src, dst)

def export_project_json(project_name, side):
    data = load_project(project_name, side)
    path = f"{project_name}_{side}_export.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path

def export_project_excel(project_name, side):
    data = load_project(project_name, side)
    writer = pd.ExcelWriter(f"{project_name}_{side}_export.xlsx", engine="openpyxl")
    for key in ["phases", "objectives", "dps", "tasks"]:
        df = pd.DataFrame(data.get(key, []))
        df.to_excel(writer, sheet_name=key.capitalize(), index=False)
    writer.save()
    return writer.path

def export_project_zip(project_name):
    files = []
    for side in SIDES:
        json_path = export_project_json(project_name, side)
        excel_path = export_project_excel(project_name, side)
        files.extend([json_path, excel_path])
    zip_path = f"{project_name}_export.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for f in files:
            zipf.write(f)
    for f in files:
        os.remove(f)
    return zip_path

def import_from_single_sheet(data, df):
    """Import data from a single sheet containing all information"""
    # Extract unique phases
    if 'Phase' in df.columns:
        unique_phases = df['Phase'].dropna().unique()
        data['phases'] = [{"Name": str(phase).strip()} for phase in unique_phases if str(phase).strip()]
    
    # Extract unique objectives with their phases
    if 'Objective' in df.columns and 'Phase' in df.columns:
        objectives_data = df[['Objective', 'Phase']].drop_duplicates().dropna()
        data['objectives'] = []
        for _, row in objectives_data.iterrows():
            if pd.notna(row['Objective']) and str(row['Objective']).strip():
                data['objectives'].append({
                    "Name": str(row['Objective']).strip(),
                    "Phase": str(row['Phase']).strip() if pd.notna(row['Phase']) else ""
                })
    
    # Extract DPs - handle both old and new formats
    dp_description_cols = ['Description of DP', 'DP Description']
    force_group_cols = ['Force Group Asigned', 'Force Group Assigned', 'Force Group']
    weight_cols = ['Weightage Factor (1-5) (W)', 'Weightage Factor (1–5)', 'Weightage Factor', 'Weight']
    
    # Find which columns exist
    dp_desc_col = None
    force_col = None
    weight_col = None
    
    for col in dp_description_cols:
        if col in df.columns:
            dp_desc_col = col
            break
    
    for col in force_group_cols:
        if col in df.columns:
            force_col = col
            break
            
    for col in weight_cols:
        if col in df.columns:
            weight_col = col
            break
    
    if any(col in df.columns for col in ['DP No'] + dp_description_cols):
        # Build column list dynamically based on what exists
        dp_columns = ['DP No', 'Objective']
        # If Phase column exists in the combined sheet, include it so DPs carry phase info
        if 'Phase' in df.columns:
            dp_columns.append('Phase')
        if dp_desc_col:
            dp_columns.append(dp_desc_col)
        if force_col:
            dp_columns.append(force_col)
        if weight_col:
            dp_columns.append(weight_col)

        dp_data = df[dp_columns].drop_duplicates()
        data['dps'] = []
        for _, row in dp_data.iterrows():
            if pd.notna(row.get('DP No')) or (dp_desc_col and pd.notna(row.get(dp_desc_col))):
                dp_entry = {}
                if pd.notna(row.get('DP No')):
                    dp_entry['DP No'] = str(row['DP No']).strip()
                if dp_desc_col and pd.notna(row.get(dp_desc_col)):
                    dp_entry['Name'] = str(row[dp_desc_col]).strip()
                if pd.notna(row.get('Objective')):
                    dp_entry['Objective'] = str(row['Objective']).strip()
                # If Phase column is present in the sheet, attach it to the DP entry
                if 'Phase' in row.index and pd.notna(row.get('Phase')):
                    dp_entry['Phase'] = str(row['Phase']).strip()
                if force_col and pd.notna(row.get(force_col)):
                    dp_entry['Force Group'] = str(row[force_col]).strip()
                if weight_col and pd.notna(row.get(weight_col)):
                    dp_entry['Weight'] = str(row[weight_col]).strip()
                
                if dp_entry:  # Only add if we have some data
                    data['dps'].append(dp_entry)
    
    # Extract tasks - handle both old and new formats
    task_desc_cols = ['Task Description']
    type_cols = ['Task Tangible / Intangible (T/IN)', 'Type (Tangible/Intangible)', 'Type']
    weight_cols = ['Weightage Factor (1-5) (W)', 'Weightage Factor (1–5)', 'Weightage Factor']
    force_group_cols = ['Force Group Asigned', 'Force Group Assigned', 'Force Group']
    
    # Find which columns exist
    task_desc_col = None
    type_col = None
    weight_col = None
    force_col = None
    
    for col in task_desc_cols:
        if col in df.columns:
            task_desc_col = col
            break
            
    for col in type_cols:
        if col in df.columns:
            type_col = col
            break
            
    for col in weight_cols:
        if col in df.columns:
            weight_col = col
            break
            
    for col in force_group_cols:
        if col in df.columns:
            force_col = col
            break
    
    task_columns_needed = ['Task No', 'DP No', 'Criteria of Success']
    if task_desc_col:
        task_columns_needed.append(task_desc_col)
        
    if any(col in df.columns for col in task_columns_needed):
        data['tasks'] = []
        for _, row in df.iterrows():
            if pd.notna(row.get('Task No')) or (task_desc_col and pd.notna(row.get(task_desc_col))):
                task_entry = {}
                
                if pd.notna(row.get('Task No')):
                    task_entry['Task No'] = str(row['Task No']).strip()
                
                if task_desc_col and pd.notna(row.get(task_desc_col)):
                    task_name = str(row[task_desc_col]).strip()
                    task_entry['Name'] = task_name
                    task_entry['Desc'] = task_name
                    task_entry['description'] = task_name
                    task_entry['Task Name'] = task_name
                
                if pd.notna(row.get('DP No')):
                    dp_no = str(row['DP No']).strip()
                    task_entry['DP No'] = dp_no
                    task_entry['dp_no'] = dp_no
                
                if type_col and pd.notna(row.get(type_col)):
                    type_val = str(row[type_col]).strip().upper()
                    # Handle different type formats
                    if any(word in type_val for word in ['T', 'TANGIBLE', 'TAN']):
                        task_entry['Type'] = 'T'
                        task_entry['Intangible'] = 'nil'
                    elif any(word in type_val for word in ['I', 'INTANGIBLE', 'INT']):
                        task_entry['Type'] = 'I'
                        task_entry['Intangible'] = 'partial'
                    else:
                        task_entry['Type'] = type_val
                
                if weight_col and pd.notna(row.get(weight_col)):
                    weight_val = str(row[weight_col]).strip()
                    task_entry['Weight'] = weight_val
                    task_entry['stated'] = weight_val
                    task_entry['Stated %'] = weight_val
                
                if pd.notna(row.get('Criteria of Success')):
                    criteria_val = str(row['Criteria of Success']).strip()
                    task_entry['Criteria'] = criteria_val
                    task_entry['Criteria of Success'] = criteria_val
                
                # Add force group
                if force_col and pd.notna(row.get(force_col)):
                    task_entry['Force Group'] = str(row[force_col]).strip()
                
                if task_entry:  # Only add if we have some data
                    data['tasks'].append(task_entry)

def import_excel_to_project(project_name, side, excel_path):
    data = load_project(project_name, side)
    xls = None
    try:
        xls = pd.ExcelFile(excel_path)
        
        # Check if this is a single-sheet format with all data
        if len(xls.sheet_names) == 1 or 'Sheet1' in xls.sheet_names:
            # Try to import from single sheet first
            sheet_name = xls.sheet_names[0]
            df = pd.read_excel(xls, sheet_name)
            
            # Check if this sheet has the user's combined format (both old and new formats)
            user_columns_old = ['Phase', 'Objective', 'DP No', 'Description of DP', 'Force Group Asigned', 
                               'Task No', 'Task Description', 'Task Tangible / Intangible (T/IN)', 
                               'Weightage Factor (1-5) (W)', 'Criteria of Success']
            
            user_columns_new = ['Phase', 'Objective', 'DP No', 'DP Description', 'Task No', 'Task Description',
                               'Force Group', 'Type (Tangible/Intangible)', 'Criteria of Success', 'Weightage Factor (1–5)']
            
            # Check if we have key columns that indicate either user format
            has_user_format = (any(col in df.columns for col in ['Description of DP', 'Task Description', 'Weightage Factor (1-5) (W)']) or
                              any(col in df.columns for col in ['DP Description', 'Task Description', 'Weightage Factor (1–5)']))
            
            if has_user_format:
                # Process single-sheet format
                import_from_single_sheet(data, df)
                save_project(project_name, side, data)
                return
        
        # Otherwise, use multi-sheet format
        sheet_map = {
            "phases": ["Phases", "Phase", "phases", "phase"],
            "objectives": ["Objectives", "Objective", "objectives", "objective"],
            "dps": ["DPs", "DP", "dps", "dp"],
            "tasks": ["Tasks", "Task", "tasks", "task"]
        }
        for key, variants in sheet_map.items():
            found = None
            for sheet in xls.sheet_names:
                # Convert sheet name to string and handle case insensitive comparison
                sheet_str = str(sheet).lower()
                if sheet_str in [v.lower() for v in variants]:
                    found = sheet
                    break
            if found:
                df = pd.read_excel(xls, found)
                # Remove any empty rows
                df = df.dropna(how='all')
                
                # Normalize column names and handle common variations for all data types
                if key == "objectives":
                    # Common objective column name variations (including user's format)
                    name_columns = ['Name', 'Objective', 'Objective Name', 'objective', 'name', 'objective name']
                    phase_columns = ['Phase', 'phase', 'Phase Name', 'phase name']
                    
                    # Find the actual column names in the Excel file
                    actual_name_col = None
                    actual_phase_col = None
                    
                    for col in df.columns:
                        col_str = str(col).strip()
                        if col_str in name_columns or col_str.lower() in [nc.lower() for nc in name_columns]:
                            actual_name_col = col
                        if col_str in phase_columns or col_str.lower() in [pc.lower() for pc in phase_columns]:
                            actual_phase_col = col
                    
                    # Standardize the data structure
                    standardized_data = []
                    for _, row in df.iterrows():
                        obj_data = {}
                        if actual_name_col and pd.notna(row.get(actual_name_col)):
                            obj_data["Name"] = str(row[actual_name_col]).strip()
                        if actual_phase_col and pd.notna(row.get(actual_phase_col)):
                            obj_data["Phase"] = str(row[actual_phase_col]).strip()
                        
                        # Only add if we have at least a name
                        if obj_data.get("Name"):
                            standardized_data.append(obj_data)
                    
                    data[key] = standardized_data
                # If objectives are available, ensure each DP has its Phase populated
                if data.get('objectives'):
                    obj_phase_map = {obj.get('Name'): obj.get('Phase', '') for obj in data.get('objectives', [])}
                    for dp in data.get('dps', []):
                        if not dp.get('Phase') and dp.get('Objective'):
                            dp['Phase'] = obj_phase_map.get(dp.get('Objective'), '')
                
                elif key == "tasks":
                    # Common task column name variations (including user's specific format)
                    name_columns = ['Name', 'Task', 'Task Name', 'Desc', 'Description', 'Task Description', 'task', 'name', 'task name', 'desc', 'description', 'TASK', 'NAME', 'DESCRIPTION']
                    dp_columns = ['DP', 'DP No', 'Decisive Point', 'dp', 'dp no', 'decisive point', 'DP_No', 'dp_no', 'DPNo', 'dpno', 'DPNO', 'DP_NO']
                    weight_columns = ['Weight', 'weight', 'Wt', 'wt', 'Weightage', 'weightage', 'WEIGHT', 'Weight %', 'weight %', 'Weights', 'weights', 'WEIGHTS', 'Weightage %', 'Weightage Factor (1-5) (W)', 'Weightage Factor (1–5)', 'Weightage Factor']
                    progress_columns = ['Progress', 'Achieved %', 'Achieved', 'progress', 'achieved %', 'achieved', 'Progress %', 'progress %', 'ACHIEVED %', 'PROGRESS', 'Complete %', 'complete %', 'Completion', 'completion', 'Status', 'status', 'COMPLETION', 'STATUS']
                    task_no_columns = ['Task No', 'Task Number', 'task no', 'task number', 'TaskNo', 'Task_No', 'TASK NO']
                    type_columns = ['Type', 'type', 'T/I', 'Tangible / Intangible (T/IN)', 'Task Tangible / Intangible (T/IN)', 'Type (Tangible/Intangible)', 'Tangible/Intangible', 'T/IN']
                    criteria_columns = ['Criteria', 'criteria', 'Criteria of Success', 'Success Criteria', 'criterion']
                    force_columns = ['Force Group', 'Force TG Assigned', 'Task TG Assigned', 'force group', 'Force', 'Assigned Force']
                    
                    # Find the actual column names in the Excel file
                    actual_name_col = None
                    actual_dp_col = None
                    actual_weight_col = None
                    actual_progress_col = None
                    actual_task_no_col = None
                    actual_type_col = None
                    actual_criteria_col = None
                    actual_force_col = None
                    
                    for col in df.columns:
                        col_str = str(col).strip()
                        if col_str in name_columns or col_str.lower() in [nc.lower() for nc in name_columns]:
                            actual_name_col = col
                        if col_str in dp_columns or col_str.lower() in [dc.lower() for dc in dp_columns]:
                            actual_dp_col = col
                        if col_str in weight_columns or col_str.lower() in [wc.lower() for wc in weight_columns]:
                            actual_weight_col = col
                        if col_str in progress_columns or col_str.lower() in [pc.lower() for pc in progress_columns]:
                            actual_progress_col = col
                        if col_str in task_no_columns or col_str.lower() in [tnc.lower() for tnc in task_no_columns]:
                            actual_task_no_col = col
                        if col_str in type_columns or col_str.lower() in [tc.lower() for tc in type_columns]:
                            actual_type_col = col
                        if col_str in criteria_columns or col_str.lower() in [cc.lower() for cc in criteria_columns]:
                            actual_criteria_col = col
                        if col_str in force_columns or col_str.lower() in [fc.lower() for fc in force_columns]:
                            actual_force_col = col
                    
                    # Standardize the data structure
                    standardized_data = []
                    for _, row in df.iterrows():
                        task_data = {}
                        
                        # Store task name under multiple keys for compatibility
                        if actual_name_col and pd.notna(row.get(actual_name_col)):
                            task_name = str(row[actual_name_col]).strip()
                            task_data["Name"] = task_name
                            task_data["Desc"] = task_name  # For backward compatibility
                            task_data["description"] = task_name  # Match the user's Excel format
                        
                        if actual_dp_col and pd.notna(row.get(actual_dp_col)):
                            dp_val = str(row[actual_dp_col]).strip()
                            task_data["DP No"] = dp_val
                            task_data["dp_no"] = dp_val  # Match the user's Excel format
                        
                        if actual_weight_col and pd.notna(row.get(actual_weight_col)):
                            weight_val = str(row[actual_weight_col]).strip()
                            task_data["Weight"] = weight_val
                            task_data["stated"] = weight_val  # Match the user's Excel format
                        
                        if actual_progress_col and pd.notna(row.get(actual_progress_col)):
                            progress_val = str(row[actual_progress_col]).strip()
                            task_data["Achieved %"] = progress_val
                            task_data["progress"] = progress_val  # Alternative key
                            task_data["achieved"] = progress_val  # Match the user's Excel format
                        
                        # Handle user's specific columns
                        if actual_task_no_col and pd.notna(row.get(actual_task_no_col)):
                            task_no_val = str(row[actual_task_no_col]).strip()
                            task_data["Task No"] = task_no_val
                            task_data["task_no"] = task_no_val
                        
                        if actual_type_col and pd.notna(row.get(actual_type_col)):
                            type_val = str(row[actual_type_col]).strip().upper()
                            # Convert user's format to standard T/I
                            if type_val in ['T', 'TANGIBLE', 'TAN']:
                                task_data["Type"] = "T"
                            elif type_val in ['I', 'IN', 'INTANGIBLE', 'INT']:
                                task_data["Type"] = "I"
                            else:
                                task_data["Type"] = type_val
                            task_data["Intangible"] = "nil" if type_val == "T" else "partial"
                        
                        if actual_criteria_col and pd.notna(row.get(actual_criteria_col)):
                            criteria_val = str(row[actual_criteria_col]).strip()
                            task_data["Criteria"] = criteria_val
                            task_data["Criteria of Success"] = criteria_val
                        
                        if actual_force_col and pd.notna(row.get(actual_force_col)):
                            force_val = str(row[actual_force_col]).strip()
                            task_data["Force Group"] = force_val
                            task_data["Force TG Assigned"] = force_val
                        
                        # Add any other columns as-is
                        processed_cols = [actual_name_col, actual_dp_col, actual_weight_col, actual_progress_col, 
                                        actual_task_no_col, actual_type_col, actual_criteria_col, actual_force_col]
                        for col in df.columns:
                            if col not in processed_cols and pd.notna(row.get(col)):
                                col_value = str(row[col]).strip()
                                task_data[str(col)] = col_value
                                
                                # If we haven't found weight/progress yet, check if this column contains numeric data
                                if not task_data.get("Weight") and col_value.replace('.', '').replace('%', '').isdigit():
                                    col_lower = str(col).lower()
                                    if any(w in col_lower for w in ['weight', 'wt', 'importance']):
                                        task_data["Weight"] = col_value
                                
                                if not task_data.get("Achieved %") and col_value.replace('.', '').replace('%', '').isdigit():
                                    col_lower = str(col).lower()
                                    if any(p in col_lower for p in ['progress', 'achieve', 'complete', 'done', '%', 'status']):
                                        task_data["Achieved %"] = col_value
                                        task_data["progress"] = col_value
                        
                        # Only add if we have at least a name
                        if task_data.get("Name") or task_data.get("Desc"):
                            standardized_data.append(task_data)
                    
                    data[key] = standardized_data
                
                elif key == "phases":
                    # Common phase column name variations
                    name_columns = ['Name', 'Phase', 'Phase Name', 'phase', 'name', 'phase name']
                    
                    # Find the actual column names in the Excel file
                    actual_name_col = None
                    
                    for col in df.columns:
                        col_str = str(col).strip()
                        if col_str in name_columns or col_str.lower() in [nc.lower() for nc in name_columns]:
                            actual_name_col = col
                            break
                    
                    # Standardize the data structure
                    standardized_data = []
                    for _, row in df.iterrows():
                        phase_data = {}
                        if actual_name_col and pd.notna(row.get(actual_name_col)):
                            phase_data["Name"] = str(row[actual_name_col]).strip()
                        
                        # Add any other columns as-is
                        for col in df.columns:
                            if col != actual_name_col and pd.notna(row.get(col)):
                                phase_data[str(col)] = str(row[col]).strip()
                        
                        # Only add if we have at least a name
                        if phase_data.get("Name"):
                            standardized_data.append(phase_data)
                    
                    data[key] = standardized_data
                
                elif key == "dps":
                    # Common DP column name variations (including user's new format)
                    name_columns = ['Name', 'DP', 'Decisive Point', 'dp', 'name', 'decisive point', 'Description of DP', 'DP Description']
                    dp_no_columns = ['DP No', 'DP Number', 'dp no', 'dp number', 'DPNo', 'DP_No', 'dpno']
                    objective_columns = ['Objective', 'objective', 'Objective Name', 'objective name']
                    weight_columns = ['Weight', 'weight', 'Wt', 'wt', 'Weightage', 'weightage', 'WEIGHT', 'Weightage Factor (1-5) (W)', 'Weightage Factor (1–5)', 'Weightage Factor']
                    force_columns = ['Force Group', 'Force Group Assigned', 'Force Group Asigned', 'force group', 'Force', 'Assigned Force']
                    
                    # Find the actual column names in the Excel file
                    actual_name_col = None
                    actual_dp_no_col = None
                    actual_objective_col = None
                    actual_weight_col = None
                    actual_force_col = None
                    
                    for col in df.columns:
                        col_str = str(col).strip()
                        if col_str in name_columns or col_str.lower() in [nc.lower() for nc in name_columns]:
                            actual_name_col = col
                        if col_str in dp_no_columns or col_str.lower() in [dnc.lower() for dnc in dp_no_columns]:
                            actual_dp_no_col = col
                        if col_str in objective_columns or col_str.lower() in [oc.lower() for oc in objective_columns]:
                            actual_objective_col = col
                        if col_str in weight_columns or col_str.lower() in [wc.lower() for wc in weight_columns]:
                            actual_weight_col = col
                        if col_str in force_columns or col_str.lower() in [fc.lower() for fc in force_columns]:
                            actual_force_col = col
                    
                    # Standardize the data structure
                    standardized_data = []
                    for _, row in df.iterrows():
                        dp_data = {}
                        
                        if actual_name_col and pd.notna(row.get(actual_name_col)):
                            dp_name = str(row[actual_name_col]).strip()
                            dp_data["Name"] = dp_name
                            dp_data["Description of DP"] = dp_name
                        
                        if actual_dp_no_col and pd.notna(row.get(actual_dp_no_col)):
                            dp_no_val = str(row[actual_dp_no_col]).strip()
                            dp_data["DP No"] = dp_no_val
                            dp_data["dp_no"] = dp_no_val
                        
                        if actual_objective_col and pd.notna(row.get(actual_objective_col)):
                            obj_val = str(row[actual_objective_col]).strip()
                            dp_data["Objective"] = obj_val
                        
                        if actual_weight_col and pd.notna(row.get(actual_weight_col)):
                            weight_val = str(row[actual_weight_col]).strip()
                            dp_data["Weight"] = weight_val
                            dp_data["Weightage Factor"] = weight_val
                        
                        if actual_force_col and pd.notna(row.get(actual_force_col)):
                            force_val = str(row[actual_force_col]).strip()
                            dp_data["Force Group"] = force_val
                            dp_data["Force Group Assigned"] = force_val
                        
                        # Add any other columns as-is
                        processed_cols = [actual_name_col, actual_dp_no_col, actual_objective_col, actual_weight_col, actual_force_col]
                        for col in df.columns:
                            if col not in processed_cols and pd.notna(row.get(col)):
                                dp_data[str(col)] = str(row[col]).strip()
                        
                        # Only add if we have at least a name or DP number
                        if dp_data.get("Name") or dp_data.get("DP No"):
                            standardized_data.append(dp_data)
                    
                    data[key] = standardized_data
                else:
                    data[key] = df.to_dict(orient="records")
        save_project(project_name, side, data)
    finally:
        # Ensure Excel file handle is properly closed
        if xls is not None:
            xls.close()

def compute_progress(data):
    # Aggregates DP, Objective, and Phase progress using task achieved % and intangible values
    dp_progress = {}
    for dp in data.get("dps", []):
        dp_no = dp.get("DP No")
        dp_no_str = str(dp_no).strip() if dp_no is not None else None
        # Normalize DP No comparison to string to avoid int/str mismatches
        tasks = [t for t in data.get("tasks", []) if str(t.get("DP No", "")).strip() == dp_no_str]
        if not tasks:
            dp_progress[dp_no] = 0
            continue
        total = 0
        for t in tasks:
            achieved = t.get("Achieved %", 0)
            intangible = t.get("Intangible", "nil")
            if intangible == "complete":
                achieved = 100
            elif intangible == "partial":
                achieved = max(achieved, 50)
            total += achieved
        dp_progress[dp_no] = total / len(tasks)
    # Objective progress
    obj_progress = {}
    for obj in data.get("objectives", []):
        obj_name = obj.get("Name")
        obj_name_str = str(obj_name).strip() if obj_name is not None else None
        dps = [dp for dp in data.get("dps", []) if str(dp.get("Objective", "")).strip() == obj_name_str]
        if not dps:
            obj_progress[obj_name] = 0
            continue
        total = sum([dp_progress.get(dp.get("DP No"), 0) for dp in dps])
        obj_progress[obj_name] = total / len(dps)
    # Phase progress
    phase_progress = {}
    for phase in data.get("phases", []):
        phase_name = phase.get("Name")
        phase_name_str = str(phase_name).strip() if phase_name is not None else None
        objs = [obj for obj in data.get("objectives", []) if str(obj.get("Phase", "")).strip() == phase_name_str]
        if not objs:
            phase_progress[phase_name] = 0
            continue
        total = sum([obj_progress.get(obj.get("Name"), 0) for obj in objs])
        phase_progress[phase_name] = total / len(objs)
    return {
        "dp": dp_progress,
        "objective": obj_progress,
        "phase": phase_progress
    }

def get_progress_range(intangible_type):
    """
    Return (min_progress, max_progress, default_progress) based on Intangible type.
    Intangible type can be: "nil", "partial", "complete"
    """
    intangible_type = str(intangible_type).lower().strip()
    
    if intangible_type == "partial":
        return (34, 66, 34)
    elif intangible_type == "complete":
        return (67, 100, 67)
    else:  # "nil" or any other default
        return (0, 33, 0)
