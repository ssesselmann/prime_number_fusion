import dash
import dash_daq as daq
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
import logging

# Silence Dash/Werkzeug HTTP request logs in the terminal
logging.getLogger("werkzeug").setLevel(logging.ERROR)

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
cno_cycle_rules     = fission_rules[0:4] 
rad_decay_rules     = fission_rules[-11:]
rad_decay_scarcity  = 0.10
heavy_inventory_threshold = 0  # Minimum count for heavy primes before they can fission

# Global variables to store state
P1_STOCK = 100000  # Fundamental p1 reservoir; held constant throughout the run

prime_inventory     = {f"p{i+1}": 0 for i in range(rule_range)}
prime_inventory["p1"] = P1_STOCK
total_fusion_count  = 0
total_fission_count = 0

cno_cycle_event = threading.Event()
fission_decay_event = threading.Event()

# Default both optional processes to ON
cno_cycle_event.set()
fission_decay_event.set()

seen_primes = {"p1"}
csv_path = "prime_proof_of_work.csv"
stock_csv_path = "prime_final_stock.csv"

# ------------------------------------------------------- ALL FUNCTIONS --------------------

# Function to save settings (e.g., after slider changes)
def save_settings():
    settings["center_rule_index"] = center_rule_index
    settings["spread"] = spread
    with open(settings_path, 'w') as f:
        json.dump(settings, f)
        #print("settings saved")

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
    global seen_primes

    weights = compute_density_weights()
    rule_index = random.choices(range(len(fusion_rules)), weights=weights, k=1)[0]
    rule = fusion_rules[rule_index]
    (prime_a, prime_b), result, remainder = rule

    if prime_inventory.get(prime_a, 0) > 0 and prime_inventory.get(prime_b, 0) > 0:

        prime_inventory[prime_a] -= 1
        prime_inventory[prime_b] -= 1
        prime_inventory[result] = prime_inventory.get(result, 0) + 1

        total_fusion_count += 1

        # Log only the first-ever creation of this prime
        if result not in seen_primes:
            seen_primes.add(result)

            i = int(result[1:]) - 1

            log_new_prime(i, total_fusion_count)

            scatter_points['x'].append(result)
            scatter_points['y'].append(total_fusion_count)

            print(
                f"FIRST PRIME: {result} = {prime_list[i]}, "
                f"fusion count: {total_fusion_count}"
            )

            # Automatically stop as soon as p1000 is first reached
            if result == "p1000":
                print(
                    f"TARGET REACHED: p1000 = {prime_list[i]} "
                    f"at fusion count {total_fusion_count}"
                )

                # Save a snapshot of the complete inventory at completion
                save_final_stock()

                start_event.clear()
                stop_event.set()

        # p1 is fundamental: restore its reservoir to the fixed starting stock
        # rather than adding one p1 on every successful crank.
        prime_inventory["p1"] = P1_STOCK

        if remainder:
            prime_inventory[remainder] = prime_inventory.get(remainder, 0) + 1

        return True

    return False
    
# Function to apply heavy element fission based on scarcity of key primes
def attempt_heavy_fission(prime_inventory):
    global total_fission_count

    # Hard safety guard: never execute fission when the switch is OFF.
    if not fission_decay_event.is_set():
        return False
    # Calculate total inventory and the scarcity threshold as a percentage of total
    total_inventory = sum(prime_inventory.values())
    dynamic_scarcity_threshold = total_inventory * rad_decay_scarcity

    # Check if there is scarcity for small primes below the dynamic threshold
    scarce_primes = ["p3", "p4", "p5", "p6"]
    scarcity_detected = any(prime_inventory.get(p, 0) < dynamic_scarcity_threshold for p in scarce_primes)

    if scarcity_detected:
        # Iterate through heavy fission rules to find eligible prime to decay
        for rule in rad_decay_rules:
            (prime_a, fusion_partner), result, remainder = rule

            # Check if `prime_a` is available and its fusion partner is scarce
            if (prime_inventory.get(prime_a, 0) > 0 and
                (fusion_partner is None or prime_inventory.get(fusion_partner, 0) < dynamic_scarcity_threshold)):
                
                # Apply the fission rule
                prime_inventory[prime_a] -= 1
                prime_inventory[result] = prime_inventory.get(result, 0) + 1
                prime_inventory[remainder] = prime_inventory.get(remainder, 0) + 1
                print(f"Fission..: {prime_a} -> {result} + {remainder}")
                total_fission_count += 1
                return True  # Fission occurred
    else:
        pass
    return False  # No fission occurred



# Function to apply a random CNO cycle rule
def attempt_cno_cycle(prime_inventory):
    # Hard safety guard: never execute CNO when the switch is OFF.
    if not cno_cycle_event.is_set():
        return False

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
        return False

from dash import callback_context

def stochastic_prime_fusion():
    print(
        "Fusion thread started | "
        f"CNO: {'ON' if cno_cycle_event.is_set() else 'OFF'} | "
        f"Fission: {'ON' if fission_decay_event.is_set() else 'OFF'}"
    )
    fission_attempts = 0
    cno_cycle_frequency = 75    # Frequency to trigger the CNO cycle
    rad_decay_frequency = 50    # Frequency to trigger heavy element fission

    while not stop_event.is_set():
        if start_event.is_set():
            # Attempt fusion
            successful_fusion = attempt_weighted_random_fusion()

            if successful_fusion:
                fission_attempts += 1

                # Trigger CNO cycle if enabled
                if cno_cycle_event.is_set() and fission_attempts % cno_cycle_frequency == 0:
                    attempt_cno_cycle(prime_inventory)

                # Trigger heavy fission if enabled
                if fission_decay_event.is_set() and fission_attempts % rad_decay_frequency == 0:
                    attempt_heavy_fission(prime_inventory)

    print("Fusion loop stopped")

def compute_total_primes():
    return sum(prime_inventory.values())

def compute_total_mass():
    return sum(int(p[1:]) * count for p, count in prime_inventory.items())

def initialise_proof_of_work_csv():
    if not os.path.exists(csv_path):
        with open(csv_path, "w") as f:
            f.write("prime_index,prime_value,fusion_count\n")
            f.write(f"p1,{prime_list[0]},0\n")


def log_new_prime(prime_index, fusion_count):
    # prime_index is zero-based here
    label = f"p{prime_index + 1}"
    value = prime_list[prime_index]

    with open(csv_path, "a") as f:
        f.write(f"{label},{value},{fusion_count}\n")


def save_final_stock():
    """Save the complete prime inventory at the end of a run."""
    with open(stock_csv_path, "w") as f:
        f.write("prime_index,prime_value,stock\n")

        for i in range(rule_range):
            label = f"p{i+1}"
            value = prime_list[i]
            stock = prime_inventory.get(label, 0)
            f.write(f"{label},{value},{stock}\n")

    print(f"Final stock saved to {stock_csv_path}")


def record_first_prime(result):
    global scatter_points

    i = int(result[1:]) - 1

    # Freeze the crank count at this exact instant
    crank_count = total_fusion_count

    # Write CSV
    log_new_prime(i, crank_count)

    print(
        f"FIRST PRIME: {result} = {prime_list[i]}, "
        f"fusion count: {crank_count}"
    )



initialise_proof_of_work_csv()

# --------------------------------------- START HTML ------------------------------------------------------------------------------

# App layout
app.layout = html.Div([
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # Update every second
        n_intervals=0
    ),

    # Header section
    html.Div([
        html.H1("Prime Number Nuclear Synthesis"),
        html.P('by Steven Sesselmann'),
    ], style={'text-align': 'center', 'margin-bottom': '20px'}),

    # Main content container
    html.Div([
        # Chart container
        html.Div([
            dcc.Graph(id='live-update-graph', style={'height': '600px', 'width': '100%'})
        ], style={'width': '100%', 'max-width': '1800px', 'margin': '0 auto'}),

        # Row for switches and buttons
        html.Div([
            # Switches for toggling
            html.Div([
                html.Label("CNO Cycle:", style={'margin-right': '10px'}),
                daq.BooleanSwitch(id='cno-cycle-switch', on=True, color='red', style={'margin-right': '20px'}),
                html.Label("Fission Decay:", style={'margin-right': '10px'}),
                daq.BooleanSwitch(id='fission-decay-switch', on=True, color='red', style={'margin-right': '20px'}),
                html.Label("Log Scale:", style={'margin-right': '10px'}),
                daq.BooleanSwitch(id='log-scale-switch', on=True, color='blue', style={'margin-right': '20px'}),
            ], style={'display': 'flex', 'align-items': 'center', 'margin-right': '20px'}),

            # Control buttons
            html.Div([
                html.Button('Start', id='start-button', n_clicks=0, style={'backgroundColor': 'green', 'color': 'white', 'margin': '10px'}),
                html.Button('Stop', id='stop-button', n_clicks=0, style={'backgroundColor': 'red', 'color': 'white', 'margin': '10px'}),
                html.Button('Reset', id='reset-button', n_clicks=0, style={'backgroundColor': 'orange', 'color': 'white', 'margin': '10px'}),
            ], style={'display': 'flex'}),
        ], style={
            'display': 'flex',
            'align-items': 'center',
            'justify-content': 'center',
            'margin-top': '20px',
            'width': '100%',
            'max-width': '1800px',
        }),

        # Dummy output for switches
        html.Div(id='switch-output', children="", style={'margin-top': '10px'}),

        # Explanation for users viewing the public simulator
        html.Div([
            html.H2("What you are seeing"),

            html.P([
                "This simulator explores a hypothesis in which prime numbers behave like "
                "discrete fusion states. The label p1 represents the first prime (2), p2 "
                "represents 3, p3 represents 5, and so on. In the nuclear analogy, the "
                "prime index is treated as a mass-number-like state: p16 corresponds to "
                "state 16, p62 to state 62, etc."
            ]),

            html.P([
                "The simulation begins with a fixed reservoir of p1, treated as the "
                "fundamental building block. Fusion can occur only between two prime "
                "states, according to the rules loaded from settings.json. A successful "
                "reaction moves material to a higher prime state and may return a lower "
                "prime as a remainder."
            ]),

            html.P([
                "Example: p4 + p3 → p5 + p2 corresponds numerically to "
                "[7 + 5] → [11 + 3]. The rule allows the system to cross the prime gap "
                "between 7 and 11 while conserving the ordinal index total."
            ]),

            html.P([
                "Each crank is one successful fusion event. The next reaction is selected "
                "stochastically, with the probability weighted by the current stock of the "
                "required reactants. This is intended to mimic the statistical nature of "
                "collisions in a large reaction network."
            ]),

            html.H3("Reading the plot"),

            html.Ul([
                html.Li([
                    html.B("Black bars: "),
                    "the current stock of each prime state. Large peaks are accumulation "
                    "points where material is produced faster than it can move onward."
                ]),
                html.Li([
                    html.B("Empty or very small bars: "),
                    "states that may be hard to reach or may be produced and consumed so "
                    "quickly that little stock accumulates."
                ]),
                html.Li([
                    html.B("Red dots: "),
                    "the total fusion count when that prime state first appeared during "
                    "the run. These provide a first-passage or proof-of-work measure for "
                    "reaching progressively higher states."
                ]),
                html.Li([
                    html.B("Log Scale: "),
                    "useful because the stock levels can differ by many orders of magnitude."
                ]),
            ]),

            html.P([
                "The program can optionally include CNO-inspired recycling rules and "
                "heavy-isotope fission/decay rules. Turning both switches off runs only "
                "the prime-fusion rule set, which is useful for studying the behaviour of "
                "the underlying algorithm by itself."
            ]),

            html.P([
                "A striking feature of long runs is the appearance of persistent abundance "
                "peaks and occasional very large bottlenecks. The simulator is intended as "
                "an exploratory mathematical model, not as a replacement for established "
                "nuclear reaction physics. Its purpose is to test whether simple prime-based "
                "rules can generate structures that are interesting to compare with nuclear "
                "synthesis and elemental abundance."
            ]),

            html.P([
                html.B("Prime fusion postulates: "),
                "p1 is treated as fundamental; fusion is binary; and a higher prime state "
                "can be produced only when the required partner state is available."
            ]),

        ], style={
            'width': '100%',
            'max-width': '1400px',
            'margin': '40px auto 20px auto',
            'padding': '25px 35px',
            'box-sizing': 'border-box',
            'line-height': '1.6',
            'font-size': '16px',
            'background-color': '#f7f7f7',
            'border-radius': '8px'
        }),
    ], style={
        'display': 'flex',
        'flex-direction': 'column',
        'align-items': 'center',
        'justify-content': 'center',
        'width': '100%',
        'max-width': '1800px',
        'margin': '0 auto',
        'padding': '20px',
        'box-sizing': 'border-box',
    }),
])



# --------------------------------------- END HTML ------------------------------------------------------------------------------

# Global variable to track last prime inventory state for scatter points
last_prime_inventory = {f"p{i+1}": 0 for i in range(rule_range)}
scatter_points = {'x': [], 'y': []}  # Stores the x and y coordinates of the red dots

# Global variable to track last prime inventory state for scatter points
last_prime_inventory = {f"p{i+1}": 0 for i in range(rule_range)}
scatter_points = {'x': [], 'y': []}  # Stores the x and y coordinates of the red dots

# Global variable to track last prime inventory state and red dot points
last_prime_inventory = {f"p{i+1}": 0 for i in range(rule_range)}
scatter_points = {'x': [], 'y': []}  # Stores the x and y coordinates of the red dots

@app.callback(
    Output('live-update-graph', 'figure'),
    [Input('interval-component', 'n_intervals'),
     Input('log-scale-switch', 'on')],
    [State('live-update-graph', 'relayoutData')]
)
def update_graph_live(n, log_scale, relayout_data):
    global center_rule_index, spread, total_fusion_count, total_fission_count
    global last_prime_inventory, scatter_points

    # Retrieve current counts from global prime inventory
    y_counts = [
        prime_inventory.get(f"p{i+1}", 0)
        for i in range(rule_range)
    ]

    # Determine the y-axis type
    yaxis_type = 'log' if log_scale else 'linear'

    total_primes = compute_total_primes()
    total_mass = compute_total_mass()

    # Create bar chart
    fig = go.Figure([
        go.Bar(
            x=[f"p{i+1}" for i in range(rule_range)],
            y=y_counts,
            name="Prime Counts",
            marker=dict(color='black')
        )
    ])

    # Add first-appearance points
    fig.add_trace(go.Scatter(
        x=scatter_points['x'],
        y=scatter_points['y'],
        mode='markers',
        marker=dict(size=2, color='red'),
        name="Fusion Points"
    ))

    fig.update_layout(
        uirevision="prime-spectrum",
        xaxis_title=f"Prime Elements (p1 to p{rule_range})",
        yaxis_title="Counts",
        yaxis_type=yaxis_type,
        showlegend=True,
        height=600,
        width=1875,
        annotations=[
            dict(
                x=0.5,
                y=1.1,
                xref="paper",
                yref="paper",
                text=(
                    f"Total fusion count {total_fusion_count}, "
                    f"fission Count: {total_fission_count}, "
                    f"total primes: {total_primes}, "
                    f"total mass: {total_mass}"
                ),
                showarrow=False,
                font=dict(size=16)
            )
        ]
    )

    # Explicitly preserve the user's current zoom/pan ranges.
    # Plotly sends the current axis ranges in relayoutData whenever the user zooms or pans.
    if relayout_data:
        if 'xaxis.range[0]' in relayout_data and 'xaxis.range[1]' in relayout_data:
            fig.update_xaxes(
                range=[
                    relayout_data['xaxis.range[0]'],
                    relayout_data['xaxis.range[1]']
                ],
                autorange=False
            )

        if 'yaxis.range[0]' in relayout_data and 'yaxis.range[1]' in relayout_data:
            fig.update_yaxes(
                range=[
                    relayout_data['yaxis.range[0]'],
                    relayout_data['yaxis.range[1]']
                ],
                autorange=False
            )

        # Respect Plotly's "Reset axes" / autoscale action.
        if relayout_data.get('xaxis.autorange'):
            fig.update_xaxes(autorange=True)

        if relayout_data.get('yaxis.autorange'):
            fig.update_yaxes(autorange=True)

    return fig


@app.callback(
    [Output('start-button'  , 'disabled'), 
     Output('stop-button'   , 'disabled'),
     Output('interval-component', 'disabled')],
    [Input('start-button'   , 'n_clicks'),
     Input('stop-button'    , 'n_clicks'),
     Input('reset-button'   , 'n_clicks')],
    [State('cno-cycle-switch', 'on'),
     State('fission-decay-switch', 'on')]
)
def control_simulation(start_clicks, stop_clicks, reset_clicks,
                       cno_switch_state, fission_switch_state):
    global fusion_thread
    global prime_inventory
    global seen_primes
    global total_fusion_count
    # Check if reset button was clicked
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-button' in changed_id:
        print("Resetting counts")

        prime_inventory = {f"p{i+1}": 0 for i in range(rule_range)}
        prime_inventory["p1"] = P1_STOCK

        total_fusion_count = 0
        seen_primes = {"p1"}

        start_event.clear()
        stop_event.set()

        if os.path.exists(csv_path):
            os.remove(csv_path)

        initialise_proof_of_work_csv()

        return False, True, True

    # Start simulation
    elif 'start-button' in changed_id and start_clicks and not start_event.is_set():

        # Synchronize the worker flags with the ACTUAL browser switch positions
        # immediately before the fusion thread starts.
        if cno_switch_state:
            cno_cycle_event.set()
        else:
            cno_cycle_event.clear()

        if fission_switch_state:
            fission_decay_event.set()
        else:
            fission_decay_event.clear()

        print(
            "Starting fusion | "
            f"CNO: {'ON' if cno_cycle_event.is_set() else 'OFF'} | "
            f"Fission: {'ON' if fission_decay_event.is_set() else 'OFF'}"
        )

        stop_event.clear()
        start_event.set()

        if not fusion_thread or not fusion_thread.is_alive():
            fusion_thread = threading.Thread(
                target=stochastic_prime_fusion,
                daemon=True
            )
            fusion_thread.start()

        return True, False, False  # Start disabled, Stop enabled, graph refresh enabled

    # Stop simulation
    elif 'stop-button' in changed_id and stop_clicks and start_event.is_set():
        print("Stopping fusion")

        # Save a snapshot of the complete inventory whenever Stop is pressed
        save_final_stock()

        start_event.clear()
        stop_event.set()
        return False, True, True  # Start enabled, Stop disabled, graph refresh disabled

    # Default state (no clicks or re-run of callback)
    return False, True, True

@app.callback(
    Output('switch-output', 'children'),
    [Input('cno-cycle-switch', 'on'),
     Input('fission-decay-switch', 'on')]
)
def update_switch_states(cno_cycle_state, fission_decay_state):

    if cno_cycle_state:
        cno_cycle_event.set()
    else:
        cno_cycle_event.clear()

    if fission_decay_state:
        fission_decay_event.set()
    else:
        fission_decay_event.clear()

    cno_text = "ON" if cno_cycle_event.is_set() else "OFF"
    fission_text = "ON" if fission_decay_event.is_set() else "OFF"

    print(f"CNO Cycle: {cno_text}, Fission Decay: {fission_text}")

    return f"CNO: {cno_text} | Fission: {fission_text}"



if __name__ == '__main__':
    webbrowser.open_new("http://127.0.0.1:8050")
    app.run(debug=False, use_reloader=False)
