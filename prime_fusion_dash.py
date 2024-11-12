import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash import callback_context
import plotly.graph_objs as go
import numpy as np
import random
import threading
import time
import os
import webbrowser
import json

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=False)

# Thread control events
start_event = threading.Event()
stop_event = threading.Event()
fusion_thread = None

# Path to settings file
settings_path = 'settings.json'

# Load settings from JSON at the start of the script
if os.path.exists(settings_path):
    with open(settings_path, 'r') as f:
        settings = json.load(f)


# Access settings data
prime_list          = settings["primes"]
fusion_rules        = settings["fusion_rules"]
center_rule_index   = settings["center_rule_index"]
spread              = settings["spread"]
rule_range        = len(fusion_rules)+1



# Global variables to store state
prime_inventory     = {f"p{i+1}": 0 for i in range(rule_range)}
prime_inventory["p1"] = 10000  # Initial count for p1 to start fusion
total_fusion_count  = 0

# Function to save settings (e.g., after slider changes)
def save_settings():
    settings["center_rule_index"] = center_rule_index
    settings["spread"] = spread
    with open(settings_path, 'w') as f:
        json.dump(settings, f)
        print("settings saved")

def compute_weights():
    num_rules = len(fusion_rules)
    weights = np.exp(-0.5 * ((np.arange(num_rules) - center_rule_index) / spread) ** 2)
    return weights / np.sum(weights)  # Normalize weights

def attempt_weighted_random_fusion():
    global total_fusion_count
    weights = compute_weights()  # Update weights based on slider values
    rule_index = random.choices(range(len(fusion_rules)), weights=weights, k=1)[0]
    rule = fusion_rules[rule_index]
    (prime_a, prime_b), result, remainder = rule

    # Debugging statements to trace execution
    #print(f"Attempting fusion with rule: {rule}")    
    # Check if fusion is possible with available inventory
    if prime_inventory.get(prime_a, 0) > 0 and prime_inventory.get(prime_b, 0) > 0:
        # Perform fusion if both primes are available
        prime_inventory[prime_a] -= 1
        prime_inventory[prime_b] -= 1
        prime_inventory[result] = prime_inventory.get(result, 0) + 1
        if remainder:
            prime_inventory[remainder] = prime_inventory.get(remainder, 0) + 1
        total_fusion_count += 1
        prime_inventory["p1"] +=1

        # Debugging statements to confirm fusion was successful
        #print(f"Fusion successful: {prime_a} + {prime_b} -> {result} (+ {remainder})")
        #print(f"Total fusion count: {total_fusion_count}")
        return True  # Fusion was successful
    else:
        # Fusion was not possible due to insufficient inventory
        #print(f"Fusion failed: insufficient inventory for {prime_a} or {prime_b}")
        return False  # Fusion was not possible

def stochastic_prime_fusion():
    print("Fusion thread started")
    while not stop_event.is_set():
        if start_event.is_set():  # Only run fusion when start_event is set
            attempt_weighted_random_fusion()
            #time.sleep(0.001)  # Prevent overloading the CPU
    print("Fusion thread stopped")

# App layout
app.layout = html.Div([
    html.Div(id='header', children=[
        html.H1("Prime Number Nuclear Synthesis"),
        html.P('by Steven Sesselmann'),
        html.Div(id="total-fusion-count")
    ], style={'text-align':'center'}),

    dcc.Graph(id='live-update-graph'),

    html.Div(id='sliders', children=[
        dcc.Slider(
            id='center-slider',
            min=0,
            max=rule_range,
            step=1,
            value=center_rule_index,
            marks={i: str(i) for i in range(0, rule_range, 10)},
            tooltip={"placement": "bottom", "always_visible": True},
        ),
        html.Div(id='center-slider-value', style={'margin-top': 10, 'margin-bottom':50, 'textAlign':'center'}),
        dcc.Slider(
            id='spread-slider',
            min=1,
            max=rule_range,
            step=1,
            value=spread,
            marks={i: str(i) for i in range(0, rule_range, 10)},
            tooltip={"placement": "bottom", "always_visible": True},
        ),
        html.Div(id='spread-slider-value', style={'margin-top': 10, 'textAlign':'center'}),
    ], style={'width':'90%', 'margin':'auto'}),

    html.Div(id='controls', children=[
        html.Button('Start', id='start-button', n_clicks=0, style={'backgroundColor':'green', 'color':'white', 'margin':'10px'}),
        html.Button('Stop', id='stop-button', n_clicks=0, style={'backgroundColor':'red', 'color':'white', 'margin':'10px'}),
        html.Button('Reset', id='reset-button', n_clicks=0, style={'backgroundColor':'orange', 'color':'white', 'margin':'10px'})
    ], style={'text-align': 'center', 'margin-top': '20px'}),

    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # Update every 1 second
        n_intervals=0
    ),

    html.Div(id='footer', children=[html.Img(id='footer', src='assets/abundance.jpg')], style={'text-align':'center'}),
])

@app.callback(
    [Output('live-update-graph', 'figure'),
     Output('total-fusion-count', 'children'),
     Output('center-slider-value', 'children'),
     Output('spread-slider-value', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('center-slider', 'value'),
     Input('spread-slider', 'value')]
)
def update_graph_live(n, center_value, spread_value):
    global center_rule_index, spread, total_fusion_count
    center_rule_index = center_value-1
    spread = spread_value

    # Retrieve current counts from global prime inventory
    y_counts = [prime_inventory.get(f"p{i+1}", 0) for i in range(rule_range)]
    
    # Create bar chart figure
    fig = go.Figure([go.Bar(x=[f"p{i+1}" for i in range(rule_range)], y=y_counts, name="Prime Counts")])
    
    # Define x-values across the original range (0 to 199)
    x_values = np.arange(0, rule_range)
    
    # Calculate Gaussian curve centered on `center_rule_index`
    gaussian_curve = np.exp(-0.5 * ((x_values - center_rule_index) / spread) ** 2)
    gaussian_curve = gaussian_curve * max(y_counts)  # Scale Gaussian to match the bar height
    
    # Add Gaussian curve as a red line overlay
    fig.add_trace(go.Scatter(x=[f"p{i+1}" for i in range(rule_range)], y=gaussian_curve, mode='lines', line=dict(color='red'), name="Gaussian Curve"))

    fig.update_layout(
        xaxis_title=f"Prime Elements (p1 to p{rule_range})",
        yaxis_title="Counts",
        #yaxis_type="linear",
        yaxis_type="log",
        showlegend=False
    )
    
    # Display total fusion count
    total_fusion_text = f"Total Fusion Count: {total_fusion_count}"
    center_text = f"Center Rule Index: {center_value}"
    spread_text = f"Gaussian Spread: {spread_value}"

    # Save settings only if sliders triggered the callback
    triggered = callback_context.triggered[0]['prop_id']
    if 'center-slider' in triggered or 'spread-slider' in triggered:
        save_settings()

    return fig, total_fusion_text, center_text, spread_text

@app.callback(
    [Output('start-button'  , 'disabled'), Output('stop-button', 'disabled')],
    [Input('start-button'   , 'n_clicks'),
     Input('stop-button'    , 'n_clicks'),
     Input('reset-button'   , 'n_clicks')]
)
def control_simulation(start_clicks, stop_clicks, reset_clicks):
    global fusion_thread
    global prime_inventory

    # Start simulation
    if start_clicks > 0 and not start_event.is_set():
        #print("Starting fusion")
        stop_event.clear()
        start_event.set()
        if not fusion_thread or not fusion_thread.is_alive():
            fusion_thread = threading.Thread(target=stochastic_prime_fusion, daemon=True)
            fusion_thread.start()
        return True, False

    # Stop simulation
    elif stop_clicks > 0:
        #print("Stopping fusion")
        start_event.clear()
        return False, True

    elif reset_clicks >0:
        #print("Resetting counts")
        prime_inventory = {f"p{i+1}": 0 for i in range(rule_range)}
        prime_inventory["p1"] = 10000  # Initial count for p1 to start fusion
        total_fusion_count = 0    

    return False, True

if __name__ == '__main__':
    webbrowser.open_new("http://127.0.0.1:8050")
    app.run_server(debug=True)