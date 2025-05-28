import dash
from dash import html, dcc, Input, Output, State
import dash_ag_grid as dag
import pandas as pd
import json
import os
import uuid
from pathlib import Path

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the path for storing layouts
LAYOUTS_DIR = Path(r"C:\temp\grid_layouts")
LAYOUTS_DIR.mkdir(parents=True, exist_ok=True)
LAYOUTS_FILE = LAYOUTS_DIR / "layouts.json"

# Load or initialize saved layouts
def load_layouts():
    if LAYOUTS_FILE.exists():
        with open(LAYOUTS_FILE, "r") as f:
            return json.load(f)
    return {}

# Save layouts to file
def save_layouts(layouts):
    with open(LAYOUTS_FILE, "w") as f:
        json.dump(layouts, f, indent=2)

# Load sample CSV data (replace with your CSV file path)
# For demonstration, assuming a CSV with required columns
csv_path = "sample_data.csv"  # Update with actual path
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    # Create sample data if CSV not found
    df = pd.DataFrame({
        "PD Key": ["PD1", "PD1", "PD2", "PD2", "PD3"],
        "type": ["color", "comment", "discard", "color", "comment"],
        "Source": ["TI - JPM", "TI - BWIC", "TB", "Solve", "PDC123"],
        "OtherCol": ["A", "B", "C", "D", "E"]
    })

# Get unique PD Keys for coloring
pd_keys = df["PD Key"].unique()
color_map = {key: "#D3D3D3" if i % 2 == 0 else "#ADD8E6" for i, key in enumerate(pd_keys)}

# Define row style based on PD Key
row_style = {
    "styleConditions": [
        {
            "condition": f"params.data['PD Key'] === '{key}'",
            "style": {"backgroundColor": color}
        } for key, color in color_map.items()
    ]
}

# Define column definitions
column_defs = [
    {"field": "PD Key"},
    {"field": "type", "hide": True},  # Hidden but used for radio button default
    {"field": "Source"},
    {"field": "OtherCol"},  # Example additional column
    {
        "headerName": "Action",
        "cellRenderer": "RadioButtonGroup",
        "cellRendererParams": {
            "options": ["color", "comment", "discard"],
            "defaultColDef": {
                "valueGetter": "data.type"  # Pre-check based on 'type' column
            }
        },
        "width": 200
    }
]

# Custom RadioButtonGroup component for AG-Grid
radio_button_js = """
class RadioButtonGroup {
  init(params) {
    this.params = params;
    this.eGui = document.createElement('div');
    const options = params.options || ['color', 'comment', 'discard'];
    const defaultValue = params.data.type || 'color';
    this.eGui.innerHTML = options.map(option => `
      <label style="margin-right: 10px;">
        <input type="radio" name="radio-${params.rowIndex}" value="${option}" ${option === defaultValue ? 'checked' : ''}>
        ${option.charAt(0).toUpperCase() + option.slice(1)}
      </label>
    `).join('');
    this.eGui.querySelectorAll('input').forEach(input => {
      input.addEventListener('change', (e) => {
        params.setValue(e.target.value);
      });
    });
  }
  getGui() {
    return this.eGui;
  }
  refresh(params) {
    this.params = params;
    const defaultValue = params.data.type || 'color';
    this.eGui.querySelectorAll('input').forEach(input => {
      input.checked = input.value === defaultValue;
    });
    return true;
  }
}
"""

# Register custom component
dag_component_functions = f"""
var dag_component_functions = {{ RadioButtonGroup }};
{radio_button_js}
"""

# Define default checkbox states
checkbox_options = [
    {"label": "TI-JPM Trades", "value": "TI - JPM"},
    {"label": "TI-BWIC", "value": "TI - BWIC"},
    {"label": "TradeBlotter", "value": "TB"},
    {"label": "Solve Quotes", "value": "Solve"},
    {"label": "PD Color", "value": "PDC"}
]

# App layout
app.layout = html.Div([
    html.Div([
        # Checkbox group (top-left)
        html.Div([
            html.Label("Color Source", style={"fontWeight": "bold"}),
            dcc.Checklist(
                id="source-filter",
                options=checkbox_options,
                value=[opt["value"] for opt in checkbox_options],  # All checked by default
                style={"display": "flex", "flexDirection": "column"}
            )
        ], style={
            "border": "2px dashed grey",
            "padding": "10px",
            "margin": "10px",
            "width": "200px"
        }),
        # Layout controls (top-right)
        html.Div([
            dcc.Input(id="layout-name", placeholder="Enter layout name", style={"marginRight": "10px"}),
            html.Button("Save Layout", id="save-layout", n_clicks=0, style={"marginRight": "10px"}),
            dcc.Dropdown(
                id="layout-dropdown",
                options=[{"label": k, "value": k} for k in load_layouts().keys()],
                placeholder="Select saved layout",
                style={"width": "200px", "marginRight": "10px"}
            ),
            html.Button("Delete Layout", id="delete-layout", n_clicks=0)
        ], style={"display": "flex", "alignItems": "center", "margin": "10px"})
    ], style={"display": "flex", "justifyContent": "space-between"}),
    # AG-Grid
    dag.AgGrid(
        id="grid",
        columnDefs=column_defs,
        rowData=df.to_dict("records"),
        defaultColDef={"sortable": True, "filter": True, "resizable": True},
        rowStyle=row_style,
        style={"height": "50vh"},  # Half the viewport height
        dashGridOptions={"rowSelection": "multiple", "animateRows": True},
        licenseKey="YOUR_AG_GRID_ENTERPRISE_LICENSE_KEY"  # Replace with actual license key
    ),
    # Store for layouts
    dcc.Store(id="layout-store", data=load_layouts()),
    # JavaScript for custom radio buttons
    html.Script(dag_component_functions, type="text/javascript")
])

# Callback to filter grid based on checkbox selection
@app.callback(
    Output("grid", "rowData"),
    Input("source-filter", "value")
)
def update_grid_filter(selected_sources):
    filtered_df = df[
        df["Source"].apply(
            lambda x: any(
                x == source or (source == "PDC" and x.startswith("PDC"))
                for source in selected_sources
            )
        )
    ]
    return filtered_df.to_dict("records")

# Callback to save layout
@app.callback(
    Output("layout-store", "data"),
    Output("layout-dropdown", "options"),
    Input("save-layout", "n_clicks"),
    State("layout-name", "value"),
    State("grid", "columnState"),
    State("grid", "filterModel"),
    State("layout-store", "data")
)
def save_layout(n_clicks, layout_name, column_state, filter_model, layouts):
    if n_clicks > 0 and layout_name:
        layouts = layouts.copy() if layouts else {}
        layouts[layout_name] = {
            "columnState": column_state,
            "filterModel": filter_model
        }
        save_layouts(layouts)
        options = [{"label": k, "value": k} for k in layouts.keys()]
        return layouts, options
    return layouts, [{"label": k, "value": k} for k in layouts.keys()]

# Callback to load layout
@app.callback(
    Output("grid", "columnState"),
    Output("grid", "filterModel"),
    Input("layout-dropdown", "value"),
    State("layout-store", "data")
)
def load_layout(selected_layout, layouts):
    if selected_layout and selected_layout in layouts:
        return layouts[selected_layout]["columnState"], layouts[selected_layout]["filterModel"]
    return dash.no_update, dash.no_update

# Callback to delete layout
@app.callback(
    Output("layout-store", "data", allow_duplicate=True),
    Output("layout-dropdown", "options", allow_duplicate=True),
    Output("layout-dropdown", "value"),
    Input("delete-layout", "n_clicks"),
    State("layout-dropdown", "value"),
    State("layout-store", "data"),
    prevent_initial_call=True
)
def delete_layout(n_clicks, selected_layout, layouts):
    if n_clicks > 0 and selected_layout:
        layouts = layouts.copy() if layouts else {}
        layouts.pop(selected_layout, None)
        save_layouts(layouts)
        options = [{"label": k, "value": k} for k in layouts.keys()]
        return layouts, options, None
    return layouts, [{"label": k, "value": k} for k in layouts.keys()], dash.no_update

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)