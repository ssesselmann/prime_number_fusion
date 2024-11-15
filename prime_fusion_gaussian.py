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
fission_rules       = settings["fission_rules"]
center_rule_index   = settings["center_rule_index"]
spread              = settings["spread"]
center_rule_index   += 1
rule_range          = len(fusion_rules)+1
cno_cycle_rules     = fission_rules[0:3] 
rad_decay_rules     = fission_rules[-11:]
rad_decay_scarcity  = 0.10
heavy_inventory_threshold = 1  # Minimum count for heavy primes before they can fission

# Global variables to store state
prime_inventory     = {f"p{i+1}": 0 for i in range(rule_range)}
prime_inventory["p1"] = 100000  # Initial count for p1 to start fusion
total_fusion_count  = 0
total_fission_count = 0

# ------------------------------------------------------- ALL FUNCTIONS --------------------

# Function to save settings (e.g., after slider changes)
def save_settings():
    settings["center_rule_index"] = center_rule_index
    settings["spread"] = spread
    with open(settings_path, 'w') as f:
        json.dump(settings, f)
        #print("settings saved")

# def compute_gaussian_weights():
#     num_rules = len(fusion_rules)
#     weights = np.exp(-0.5 * ((np.arange(num_rules) - center_rule_index) / spread) ** 2)
#     return weights / np.sum(weights)  # Normalize weights

# def compute_density_weights():
#     # Calculate the total quantity of primes in inventory
#     total_inventory = sum(prime_inventory.values())
#     if total_inventory == 0:
#         # Avoid division by zero if inventory is empty
#         return [1 / len(fusion_rules)] * len(fusion_rules)

#     # Calculate weights with an inverse factor to favor low-inventory primes
#     weights = []
#     for (prime_a, prime_b), _, _ in fusion_rules:
#         quantity_a = prime_inventory.get(prime_a, 0)
#         quantity_b = prime_inventory.get(prime_b, 0)
        
#         # Inverse proportion factor for low-inventory primes
#         rule_weight = 1 / ((quantity_a + 1) * (quantity_b + 1))  # +1 to avoid division by zero
#         weights.append(rule_weight)

#     # Normalize the weights so they sum to 1
#     total_weight = sum(weights)
#     normalized_weights = [w / total_weight for w in weights]
#     return normalized_weights


def compute_density_weights(alpha=1, gamma=0.25, beta=0.9):
    # Calculate the total quantity of primes in inventory
    total_inventory = sum(prime_inventory.values())
    if total_inventory == 0:
        return [1 / len(fusion_rules)] * len(fusion_rules)  # Equal weights if inventory is empty

    weights = []
    for (prime_a, prime_b), _, _ in fusion_rules:
        quantity_a = prime_inventory.get(prime_a, 0)
        quantity_b = prime_inventory.get(prime_b, 0)

        # Calculate initial rule weight based on inventory
        rule_weight = ((quantity_a + alpha) * (quantity_b + alpha)) / total_inventory

        # Apply leveling factor to adjust the distribution of weights
        rule_weight = rule_weight ** (1 / beta)

        # Further dampen or amplify effect with gamma if needed
        weights.append(rule_weight ** gamma)

    # Normalize the weights so they sum to 1
    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]
    return normalized_weights


def attempt_weighted_random_fusion():
    global total_fusion_count
    # Call compute_density_weights to get updated weights based on the current inventory
    weights = compute_density_weights()
    rule_index = random.choices(range(len(fusion_rules)), weights=weights, k=1)[0]
    rule = fusion_rules[rule_index]
    (prime_a, prime_b), result, remainder = rule

    # Check if fusion can proceed with the selected primes
    if prime_inventory.get(prime_a, 0) > 0 and prime_inventory.get(prime_b, 0) > 0:
        # Perform fusion if both primes are available
        prime_inventory[prime_a] -= 1
        prime_inventory[prime_b] -= 1
        prime_inventory[result] = prime_inventory.get(result, 0) + 1
        total_fusion_count += 1
        prime_inventory["p1"] +=1
        if remainder:
            prime_inventory[remainder] = prime_inventory.get(remainder, 0) + 1
        return True  # Fusion success
    else:
        return False  # Fusion failed

# Function to apply heavy element fission based on scarcity of key primes
def attempt_heavy_fission(prime_inventory):
    global total_fission_count
    # Calculate total inventory and the scarcity threshold as a percentage of total
    total_inventory = sum(prime_inventory.values())
    dynamic_scarcity_threshold = total_inventory * rad_decay_scarcity

    # Check if there is a scarcity of small primes below the dynamic threshold
    scarce_primes = ["p2", "p3", "p4", "p5", "p6"]
    scarcity_detected = any(prime_inventory.get(p, 0) < dynamic_scarcity_threshold for p in scarce_primes)

    # Apply fission if there's scarcity
    if scarcity_detected:
        # Iterate through heavy fission rules to find eligible prime to decay
        for rule in rad_decay_rules:
            (prime_a, _), result, remainder = rule
            
            # Ensure that the heavy prime (prime_a) has enough inventory for fission
            if prime_inventory.get(prime_a, 0) >= heavy_inventory_threshold:
                # Apply the fission rule
                prime_inventory[prime_a] -= 1
                prime_inventory[result] = prime_inventory.get(result, 0) + 1
                prime_inventory[remainder] = prime_inventory.get(remainder, 0) + 1
                print(f"Heavy fission: {prime_a} -> {result} + {remainder}")
                total_fission_count += 1
                return True  # Fission occurred
    else:
        print("No fission: No scarcity detected.")
    return False  # No fission occurred


# Function to apply a random CNO cycle rule
def attempt_cno_cycle(prime_inventory):
    # Randomly select one of the first three CNO cycle rules from fission_rules
    rule = random.choice(cno_cycle_rules)
    (prime_a, fusion_partner), result, remainder = rule

    # Check if the larger prime and partner are available in inventory
    if prime_inventory.get(prime_a, 0) > 0 and prime_inventory.get(fusion_partner, 0) > 0:
        # Apply the fission rule for the selected CNO cycle
        prime_inventory[prime_a] -= 1
        prime_inventory[fusion_partner] -= 1
        prime_inventory[result] = prime_inventory.get(result, 0) + 1
        prime_inventory[remainder] = prime_inventory.get(remainder, 0) + 1
        print(f"CNO cycle: {prime_a} + {fusion_partner} -> {result} + {remainder}")
        return True
    else:
        # Insufficient primes to apply the rule
        # print(f"Unable to apply CNO cycle: insufficient {prime_a} or {fusion_partner}")
        return False

def stochastic_prime_fusion():
    print("Fusion thread started")
    fission_attempts    = 0
    cno_cycle_frequency = 100    # Frequency to trigger the CNO cycle
    rad_decay_frequency = 30  # Frequency to trigger heavy element fission

    while not stop_event.is_set():
        if start_event.is_set():
            # Attempt fusion
            successful_fusion = attempt_weighted_random_fusion()

            # Increment fission attempts if fusion was successful
            if successful_fusion:
                fission_attempts += 1
                
                # Trigger CNO cycle after every 'cno_cycle_frequency' fusions
                if fission_attempts % cno_cycle_frequency == 0:
                    attempt_cno_cycle(prime_inventory)

                # Apply heavy element fission at 'heavy_fission_frequency' intervals
                if fission_attempts % rad_decay_frequency == 0:
                    attempt_heavy_fission(prime_inventory)

    print("Fusion loop stopped")



# --------------------------------------- START HTML ------------------------------------------------------------------------------

# App layout
app.layout = html.Div([
    html.Div(id='header', children=[
        html.H1("Prime Number Nuclear Synthesis"),
        html.P('by Steven Sesselmann'),
    ], style={'text-align':'center'}),

    # Center the chart using flexbox
    html.Div(id="graph", children=[
        dcc.Graph(id='live-update-graph'),
    ], style={
        'display': 'flex',
        'justify-content': 'center',
        'width': '100%',
        'margin-left':'30px'
    }),

    # html.Div(id='sliders', children=[
    #     dcc.Slider(
    #         id='center-slider',
    #         min=0,
    #         max=rule_range,
    #         step=1,
    #         value=center_rule_index,
    #         marks={i: str(i) for i in range(0, rule_range, 10)},
    #         tooltip={"placement": "bottom", "always_visible": True},
    #     ),
    #     html.Div(id='center-slider-value', style={'margin-top': 10, 'margin-bottom':50, 'textAlign':'center'}),
    #     dcc.Slider(
    #         id='spread-slider',
    #         min=1,
    #         max=rule_range,
    #         step=1,
    #         value=spread,
    #         marks={i: str(i) for i in range(0, rule_range, 10)},
    #         tooltip={"placement": "bottom", "always_visible": True},
    #     ),
    #     html.Div(id='spread-slider-value', style={'margin-top': 10, 'textAlign':'center'}),
    # ], style={'width':'90%', 'margin':'auto'}),

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


# --------------------------------------- END HTML ------------------------------------------------------------------------------

@app.callback(
    Output('live-update-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph_live(n):
    global center_rule_index, spread, total_fusion_count, total_fission_count

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
    #fig.add_trace(go.Scatter(x=[f"p{i+1}" for i in range(rule_range)], y=gaussian_curve, mode='lines', line=dict(color='red'), name="Gaussian Curve"))

    fig.update_layout(
        xaxis_title=f"Prime Elements (p1 to p{rule_range})",
        yaxis_title="Counts",
        yaxis_type="log",
        showlegend=False,
        height=600,
        width=1250,
        annotations=[
            dict(
                x=0.5,
                y=1.1,
                xref="paper",
                yref="paper",
                text=f"Total fusion count {total_fusion_count}, fission Count: {total_fission_count}",
                showarrow=False,
                font=dict(size=16)
            )
        ]
    )

    return fig


@app.callback(
    [Output('start-button', 'disabled'), 
     Output('stop-button', 'disabled')],
    [Input('start-button', 'n_clicks'),
     Input('stop-button', 'n_clicks'),
     Input('reset-button', 'n_clicks')]
)
def control_simulation(start_clicks, stop_clicks, reset_clicks):
    global fusion_thread
    global prime_inventory

    # Check if reset button was clicked
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-button' in changed_id:
        print("Resetting counts")
        prime_inventory = {f"p{i+1}": 0 for i in range(rule_range)}
        prime_inventory["p1"] = 1000000  # Initial count for p1 to start fusion
        total_fusion_count = 0
        # Reset button behavior: enables start and disables stop
        start_event.clear()
        stop_event.set()
        return False, True  # Enables start and disables stop

    # Start simulation
    elif 'start-button' in changed_id and start_clicks and not start_event.is_set():
        print("Starting fusion")
        stop_event.clear()
        start_event.set()
        if not fusion_thread or not fusion_thread.is_alive():
            fusion_thread = threading.Thread(target=stochastic_prime_fusion, daemon=True)
            fusion_thread.start()
        return True, False  # Disables start and enables stop

    # Stop simulation
    elif 'stop-button' in changed_id and stop_clicks and start_event.is_set():
        print("Stopping fusion")
        start_event.clear()
        stop_event.set()
        return False, True  # Enables start and disables stop

    # Default state (no clicks or re-run of callback)
    return False, True



if __name__ == '__main__':
    webbrowser.open_new("http://127.0.0.1:8050")
    app.run_server(debug=True)