import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import numpy as np
import random
import threading
import time
import webbrowser

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=False)

# Global variables to store state
prime_inventory = {f"p{i+1}": 0 for i in range(200)}
prime_inventory["p1"] = 10000  # Initial count for p1 to start fusion
total_fusion_count = 0
center_rule_index = 2
spread = 5

# Thread control events
start_event = threading.Event()
stop_event = threading.Event()
fusion_thread = None

# Define primes up to p200
primes = {"p" + str(i): prime for i, prime in enumerate(
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 
     73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 
     157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 
     239, 241, 251, 257, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 
     337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 
     431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 
     521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 
     617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 
     719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 
     823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 
     929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013, 1019, 
     1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 
     1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 
     1193, 1201, 1213, 1217, 1223, 1229], 1)}


# Define fusion rules with target primes up to p82
fusion_rules = [
        (('p1', 'p1'), 'p2', None),         # 1-H
        (('p2', 'p1'), 'p3', None),         # 2-H, 2-He
        (('p3', 'p1'), 'p4', None),         # 3-H, 3-He
        (('p4', 'p3'), 'p5', 'p2'),         # 4-H, 4-He, 4-Li
        (('p5', 'p1'), 'p6', None),         # 5-H, 5-He, 5-Li, 5-Be
        (('p6', 'p3'), 'p7', 'p2'),         # 6-H, 6-He, 6-Li, 6-Be
        (('p7', 'p1'), 'p8', None),         # 7-He, 7-Li, 7-Be, 7-B
        (('p8', 'p3'), 'p9', 'p2'),         # 8-He, 8-Li, 8-Be, 8-B, 8-C 
        (('p9', 'p4'), 'p10', 'p3'),        # 9-He, 9-Li, 9-Be, 9-B, 9-C
        (('p10', 'p1'), 'p11', None),       # 10-He, 10-Li, 10-Be, 10-B, 10-C, 10-N
        (('p11', 'p4'), 'p12', 'p3'),       # 11-Li, 11-Be, 11-B, 11-C, 11-N, 
        (('p12', 'p3'), 'p13', 'p2'),       # 12-Li, 12-Be, 12-B, 12-C, 12-N, 12-O
        (('p13', 'p1'), 'p14', None),       # 13-Be, 13-B, 13-C, 13-N, 13-O
        (('p14', 'p3'), 'p15', 'p2'),       # 14-Be, 14-B, 14-C, 14-N, 14-O, 14-F
        (('p15', 'p4'), 'p16', 'p3'),       # 15-B, 15-C, 15-N, 15-O, 15-F
        (('p16', 'p4'), 'p17', 'p3'),       # 16-B, 16-C, 16-N, 16-O, 16-F, 16-Ne
        (('p17', 'p1'), 'p18', None),       # 17-B, 17-C, 17-N, 17-O, 17-F, 17-Ne
        (('p18', 'p4'), 'p19', 'p3'),       # 18-B, 18-C, 18-O, 18-F, 18-Ne, 18-Na
        (('p19', 'p3'), 'p20', 'p2'),       # 19-B, 19-C, 19-N, 19-O, 19-F, 19-Ne, 19-Na
        (('p20', 'p1'), 'p21', None),       # 20-C, 20-N, 20-O, 20-F, 20-Ne, 20-Na, 20-Mg
        (('p21', 'p4'), 'p22', 'p3'),       # 21-C, 21-N, 21-O, 21-F, 21-Ne, 21-Na, 21-Mg, 21-Al
        (('p22', 'p3'), 'p23', 'p2'),       # 22-C, 22-N, 22-O, 22-F, 22-Ne, 22-Na, 22-Mg, 22-Al, 22-Si
        (('p23', 'p4'), 'p24', 'p3'),       # 23-N, 23-O, 23-F, 23-Ne, 23-Na, 23-Mg, 23-Al, 23-Si
        (('p24', 'p5'), 'p25', 'p4'),
        (('p25', 'p3'), 'p26', 'p2'),
        (('p26', 'p1'), 'p27', None),
        (('p27', 'p3'), 'p28', 'p2'),
        (('p28', 'p1'), 'p29', None),
        (('p29', 'p3'), 'p30', 'p2'),
        (('p30', 'p7'), 'p31', 'p6'),
        (('p31', 'p3'), 'p32', 'p2'),
        (('p32', 'p4'), 'p33', 'p3'),
        (('p33', 'p1'), 'p34', None),
        (('p34', 'p5'), 'p35', 'p4'),
        (('p35', 'p1'), 'p36', None),
        (('p36', 'p4'), 'p37', 'p3'),
        (('p37', 'p4'), 'p38', 'p3'),
        (('p38', 'p3'), 'p39', 'p2'),
        (('p39', 'p4'), 'p40', 'p3'),
        (('p40', 'p4'), 'p41', 'p3'),
        (('p41', 'p1'), 'p42', None),
        (('p42', 'p5'), 'p43', 'p4'),
        (('p43', 'p1'), 'p44', None),
        (('p44', 'p3'), 'p45', 'p2'),
        (('p45', 'p1'), 'p46', None),
        (('p46', 'p6'), 'p47', 'p5'),
        (('p47', 'p6'), 'p48', 'p5'),
        (('p48', 'p3'), 'p49', 'p2'),
        (('p49', 'p1'), 'p50', None),
        (('p50', 'p3'), 'p51', 'p2'),
        (('p51', 'p4'), 'p52', 'p3'),
        (('p52', 'p1'), 'p53', None),
        (('p53', 'p5'), 'p54', 'p4'),
        (('p54', 'p4'), 'p55', 'p3'),
        (('p55', 'p6'), 'p56', 'p5'),
        (('p56', 'p1'), 'p57', None),
        (('p57', 'p4'), 'p58', 'p3'),
        (('p58', 'p3'), 'p59', 'p2'),
        (('p59', 'p1'), 'p60', None),
        (('p60', 'p5'), 'p61', 'p4'),
        (('p61', 'p7'), 'p62', 'p6'),
        (('p62', 'p3'), 'p63', 'p2'),
        (('p63', 'p1'), 'p64', None),
        (('p64', 'p3'), 'p65', 'p2'),
        (('p65', 'p7'), 'p66', 'p6'),
        (('p66', 'p4'), 'p67', 'p3'),
        (('p67', 'p5'), 'p68', 'p4'),
        (('p68', 'p1'), 'p69', None),
        (('p69', 'p3'), 'p70', 'p2'),
        (('p70', 'p4'), 'p71', 'p3'),
        (('p71', 'p5'), 'p72', 'p4'),
        (('p72', 'p4'), 'p73', 'p3'),
        (('p73', 'p4'), 'p74', 'p3'),
        (('p74', 'p3'), 'p75', 'p2'),
        (('p75', 'p4'), 'p76', 'p3'),
        (('p76', 'p5'), 'p77', 'p4'),
        (('p77', 'p3'), 'p78', 'p2'),
        (('p78', 'p5'), 'p79', 'p4'),
        (('p79', 'p5'), 'p80', 'p4'),
        (('p80', 'p1'), 'p81', None),
        (('p81', 'p5'), 'p82', 'p4'),
        (('p82', 'p1'), 'p83', None),
        (('p83', 'p4'), 'p84', 'p3'),
        (('p84', 'p3'), 'p85', 'p2'),
        (('p85', 'p4'), 'p86', 'p3'),
        (('p86', 'p5'), 'p87', 'p4'),
        (('p87', 'p3'), 'p88', 'p2'),
        (('p88', 'p1'), 'p89', None),
        (('p89', 'p3'), 'p90', 'p2'),
        (('p90', 'p6'), 'p91', 'p5'),
        (('p91', 'p5'), 'p92', 'p4'),
        (('p92', 'p3'), 'p93', 'p2'),
        (('p93', 'p5'), 'p94', 'p4'),
        (('p94', 'p3'), 'p95', 'p2'),
        (('p95', 'p4'), 'p96', 'p3'),
        (('p96', 'p6'), 'p97', 'p5'),
        (('p97', 'p1'), 'p98', None),
        (('p98', 'p8'), 'p99', 'p7'),
        (('p99', 'p4'), 'p100', 'p3'),
        (('p100', 'p5'), 'p101', 'p4'),
        (('p101', 'p4'), 'p102', 'p3'),
        (('p102', 'p4'), 'p103', 'p3'),
        (('p103', 'p1'), 'p104', None),
        (('p104', 'p4'), 'p105', 'p3'),
        (('p105', 'p5'), 'p106', 'p4'),
        (('p106', 'p4'), 'p107', 'p3'),
        (('p107', 'p4'), 'p108', 'p3'),
        (('p108', 'p1'), 'p109', None),
        (('p109', 'p4'), 'p110', 'p3'),
        (('p110', 'p4'), 'p111', 'p3'),
        (('p111', 'p3'), 'p112', 'p2'),
        (('p112', 'p1'), 'p113', None),
        (('p113', 'p6'), 'p114', 'p5'),
        (('p114', 'p5'), 'p115', 'p4'),
        (('p115', 'p1'), 'p116', None),
        (('p116', 'p3'), 'p117', 'p2'),
        (('p117', 'p4'), 'p118', 'p3'),
        (('p118', 'p4'), 'p119', 'p3'),
        (('p119', 'p1'), 'p120', None),
        (('p120', 'p6'), 'p121', 'p5'),
        (('p121', 'p3'), 'p122', 'p2'),
        (('p122', 'p4'), 'p123', 'p3'),
        (('p123', 'p5'), 'p124', 'p4'),
        (('p124', 'p5'), 'p125', 'p4'),
        (('p125', 'p5'), 'p126', 'p4'),
        (('p126', 'p5'), 'p127', 'p4'),
        (('p127', 'p5'), 'p128', 'p4'),
        (('p128', 'p4'), 'p129', 'p3'),
        (('p129', 'p4'), 'p130', 'p3'),
        (('p130', 'p3'), 'p131', 'p2'),
        (('p131', 'p5'), 'p132', 'p4'),
        (('p132', 'p4'), 'p133', 'p3'),
        (('p133', 'p3'), 'p134', 'p2'),
        (('p134', 'p5'), 'p135', 'p4'),
        (('p135', 'p3'), 'p136', 'p2'),
        (('p136', 'p7'), 'p137', 'p6'),
        (('p137', 'p5'), 'p138', 'p4'),
        (('p138', 'p6'), 'p139', 'p5'),
        (('p139', 'p1'), 'p140', None),
        (('p140', 'p5'), 'p141', 'p4'),
        (('p141', 'p1'), 'p142', None),
        (('p142', 'p3'), 'p143', 'p2'),
        (('p143', 'p1'), 'p144', None),
        (('p144', 'p5'), 'p145', 'p4'),
        (('p145', 'p7'), 'p146', 'p6'),
        (('p146', 'p3'), 'p147', 'p2'),
        (('p147', 'p1'), 'p148', None),
        (('p148', 'p3'), 'p149', 'p2'),
        (('p149', 'p7'), 'p150', 'p6'),
        (('p150', 'p3'), 'p151', 'p2'),
        (('p151', 'p1'), 'p152', None),
        (('p152', 'p3'), 'p153', 'p2'),
        (('p153', 'p9'), 'p154', 'p8'),
        (('p154', 'p3'), 'p155', 'p2'),
        (('p155', 'p5'), 'p156', 'p4'),
        (('p156', 'p5'), 'p157', 'p4'),
        (('p157', 'p5'), 'p158', 'p4'),
        (('p158', 'p3'), 'p159', 'p2'),
        (('p159', 'p4'), 'p160', 'p3'),
        (('p160', 'p4'), 'p161', 'p3'),
        (('p161', 'p7'), 'p162', 'p6'),
        (('p162', 'p3'), 'p163', 'p2'),
        (('p163', 'p4'), 'p164', 'p3'),
        (('p164', 'p4'), 'p165', 'p3'),
        (('p165', 'p5'), 'p166', 'p4'),
        (('p166', 'p4'), 'p167', 'p3'),
        (('p167', 'p6'), 'p168', 'p5'),
        (('p168', 'p3'), 'p169', 'p2'),
        (('p169', 'p4'), 'p170', 'p3'),
        (('p170', 'p1'), 'p171', None),
        (('p171', 'p5'), 'p172', 'p4'),
        (('p172', 'p1'), 'p173', None),
        (('p173', 'p4'), 'p174', 'p3'),
        (('p174', 'p5'), 'p175', 'p4'),
        (('p175', 'p1'), 'p176', None),
        (('p176', 'p5'), 'p177', 'p4'),
        (('p177', 'p1'), 'p178', None),
        (('p178', 'p4'), 'p179', 'p3'),
        (('p179', 'p8'), 'p180', 'p7'),
        (('p180', 'p3'), 'p181', 'p2'),
        (('p181', 'p1'), 'p182', None),
        (('p182', 'p3'), 'p183', 'p2'),
        (('p183', 'p4'), 'p184', 'p3'),
        (('p184', 'p4'), 'p185', 'p3'),
        (('p185', 'p5'), 'p186', 'p4'),
        (('p186', 'p4'), 'p187', 'p3'),
        (('p187', 'p4'), 'p188', 'p3'),
        (('p188', 'p9'), 'p189', 'p8'),
        (('p189', 'p1'), 'p190', None),
        (('p190', 'p5'), 'p191', 'p4'),
        (('p191', 'p5'), 'p192', 'p4'),
        (('p192', 'p5'), 'p193', 'p4'),
        (('p193', 'p4'), 'p194', 'p3'),
        (('p194', 'p4'), 'p195', 'p3'),
        (('p195', 'p5'), 'p196', 'p4'),
        (('p196', 'p6'), 'p197', 'p5'),
        (('p197', 'p3'), 'p198', 'p2'),
        (('p198', 'p4'), 'p199', 'p3'),
        (('p199', 'p4'), 'p200', 'p3')
    ]


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
        html.Div(id="total-fusion-count")
    ], style={'text-align':'center'}),

    dcc.Graph(id='live-update-graph'),

    html.Div(id='sliders', children=[
        dcc.Slider(
            id='center-slider',
            min=0,
            max=200,
            step=1,
            value=center_rule_index,
            marks={i: str(i) for i in range(0, 200, 10)},
            tooltip={"placement": "bottom", "always_visible": True},
        ),
        html.Div(id='center-slider-value', style={'margin-top': 10, 'margin-bottom':50, 'textAlign':'center'}),
        dcc.Slider(
            id='spread-slider',
            min=1,
            max=200,
            step=1,
            value=spread,
            marks={i: str(i) for i in range(0, 200, 10)},
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
    )
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
    y_counts = [prime_inventory.get(f"p{i+1}", 0) for i in range(200)]
    
    # Create bar chart figure
    fig = go.Figure([go.Bar(x=[f"p{i+1}" for i in range(200)], y=y_counts, name="Prime Counts")])
    
    # Define x-values across the original range (0 to 199)
    x_values = np.arange(0, 200)
    
    # Calculate Gaussian curve centered on `center_rule_index`
    gaussian_curve = np.exp(-0.5 * ((x_values - center_rule_index) / spread) ** 2)
    gaussian_curve = gaussian_curve * max(y_counts)  # Scale Gaussian to match the bar height
    
    # Add Gaussian curve as a red line overlay
    fig.add_trace(go.Scatter(x=[f"p{i+1}" for i in range(200)], y=gaussian_curve, mode='lines', line=dict(color='red'), name="Gaussian Curve"))

    fig.update_layout(
        xaxis_title="Prime Elements (p1 to p200)",
        yaxis_title="Counts",
        yaxis_type="linear",
        showlegend=False
    )
    
    # Display total fusion count
    total_fusion_text = f"Total Fusion Count: {total_fusion_count}"
    center_text = f"Center Rule Index: {center_value}"
    spread_text = f"Gaussian Spread: {spread_value}"

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
        prime_inventory = {f"p{i+1}": 0 for i in range(200)}
        prime_inventory["p1"] = 10000  # Initial count for p1 to start fusion
        total_fusion_count = 0    

    return False, True

if __name__ == '__main__':
    webbrowser.open_new("http://127.0.0.1:8050")
    app.run_server(debug=True)