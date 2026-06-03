import os
import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt

warnings.simplefilter("always") 
# 
warnings.filterwarnings("always")  
# ==============================
# STEP 1 : SMART GRID CPS SYSTEM
# ==============================

# Number of smart devices
N = 50

# Number of edge substations
M = 5

# Total simulation time steps
T = 100

# ==============================
# State dimensions
# ==============================

# x_t ∈ R^n
n = 4

# a_t ∈ R^m
m = 4

# d_t ∈ R^p
p = 2

# ==============================
# Smart Grid State Vector
# ==============================

# State variables
# x1 : frequency deviation
# x2 : voltage deviation
# x3 : load imbalance
# x4 : power flow deviation

# ==============================
# Initial State
# ==============================

x_init = np.array([0.05, 0.02, 0.01, 0.03])

# ==============================
# Display System Info
# ==============================

print("SMART GRID CPS SYSTEM INITIALIZED\n")

print("Number of devices:", N)
print("Number of substations:", M)
print("Simulation steps:", T)

print("\nState dimension (n):", n)
print("Control dimension (m):", m)
print("Disturbance dimension (p):", p)

print("\nInitial State x0:", x_init)
# ==============================
# LOAD DATASET (FINAL FIX)
# ==============================

data_path = r"D:\CODE PYTHON\Python Code Objective 1\NEW CODE Objective1\eCO2mix_RTE_Annuel-Definitif_2023\smartgrid.xlsx"

# ✅ CORRECT separator = TAB
df = pd.read_csv(data_path, sep='\t', encoding='latin1')

print("✅ Eco2mix Dataset Loaded:", df.shape)

print("Columns:", df.columns)
print(df.head())

# ==============================
# STEP 2: RENAME (ADD HERE)
# ==============================

print("Original Columns:", df.columns)

df.rename(columns={
    "Consommation": "Load",
    "Nucléaire": "Nuclear",
    "Eolien": "Wind",
    "Solaire": "Solar"
}, inplace=True)

print("✅ Renamed Columns:", df.columns)


T = min(100, len(df))

x = np.zeros((T, n))
a = np.zeros((T, m))

print("✅ Power Grid Dataset Loaded:", df.shape)

# ==========================================
# STEP 3: DATA CLEANING (ECO2MIX FIX)
# ==========================================

# French decimal fix
df.replace(",", ".", regex=True, inplace=True)

# ==============================
# CLEAN + KEEP ONLY NUMERIC DATA
# ==============================

# convert ALL columns to numeric safely
df = df.apply(pd.to_numeric, errors='coerce')

# fill missing values
df.fillna(0, inplace=True)

#  KEEP ONLY NUMERIC COLUMNS
df = df.select_dtypes(include=[np.number])

print("After numeric filter:", df.shape)

# ==============================
# NORMALIZATION
# ==============================

df = (df - df.mean()) / (df.std() + 1e-8)

print("✅ Dataset Normalized")

# ==============================
# STEP 2 : CPS DYNAMIC MODEL
# ==============================


# ==============================
# System Matrices
# ==============================

# A : System dynamics matrix
A = np.array([
    [0.92, 0.03, 0.00, 0.00],
    [0.02, 0.91, 0.02, 0.00],
    [0.00, 0.02, 0.93, 0.03],
    [0.00, 0.00, 0.03, 0.92]
])

  
  # control sensitivity matrix
Gamma = np.eye(n)

# ==============================
# Simulation Parameters
# ==============================

T = 100

# State trajectory
x = np.zeros((T,n))

# Control input
a = np.zeros((T,m))



# Initial state
x[0] = np.array([0.05,0.02,0.01,0.03])

# ==============================
# CPS Update Function
# ==============================

B = np.eye(n) * 0.25
E = np.random.uniform(0.01,0.05,(n,p))

def cps_update(x_t, a_t, d_t):
    
    x_next = A @ x_t + B @ (Gamma @ a_t) + E @ d_t
    
    return x_next

# =====================================
# NOMINAL CPS TRAJECTORY (NO ATTACK)
# =====================================

x_nom = np.zeros((T,n))

x_nom[0] = np.array([0.05,0.02,0.01,0.03])

for t in range(T-1):

    # nominal control
    a_nom = -0.4 * x_nom[t]

    # no attack disturbance
    d_zero = np.zeros(p)

    x_nom[t+1] = A @ x_nom[t] + B @ a_nom + E @ d_zero



# control gain
K = np.eye(n) * 1.2
# ====================================
# RA-ETC PARAMETERS
# ====================================
x_devices = np.random.randn(N, n) * 0.01 + x[:N]

alpha1 = 0.03
alpha2 = 0.07
alpha3 = 0.07

# =========================================
# CPS BASED CYBER DISTURBANCE (FIXED)
# =========================================

T = min(T, len(df))

# ==============================
# STEP 4: CPS SIGNAL EXTRACTION (REAL DATA)
# ==============================

T = min(100, len(df))

#  RESOURCE (real smart grid load)
R = df["Load"].values[:T]

#  CYBER DISTURBANCE (synthetic)
d = 0.2 * np.random.randn(T, p)

#  ATTACK SEVERITY (load variation)
S = np.abs(np.gradient(R))
S = (S - np.min(S)) / (np.max(S) + 1e-8)
S = S[:T]

print("✅ CPS signals extracted")

# ======================================
# ADVANCED ATTACK MODE
# ======================================
ATTACK_MODE = 3   # 1: noise, 2: bias, 3: burst

print("d shape:", d.shape)
print("R shape:", R.shape)
print("S shape:", S.shape)


x[0] = np.array([0.05, 0.02, 0.01, 0.03])
# ==============================
# CPS SIMULATION
# ==============================

x = np.zeros((T,n))
a = np.zeros((T,m))

x[0] = np.array([0.05, 0.02, 0.01, 0.03])

for t in range(T-1):

    # APPLY ATTACK (ADD HERE)
    if ATTACK_MODE == 1:
        d[t] = d[t] + 0.02 * np.random.randn(p)

    elif ATTACK_MODE == 2:
        d[t] = d[t] + 0.1

    elif ATTACK_MODE == 3:
        if 30 < t < 60:
            d[t] = d[t] + 0.6 * np.random.randn(p)
    a[t] = 0
    x[t+1] = cps_update(x[t], a[t], d[t])

print("✅ CPS Simulation Completed")

# ======================================
#  MOEA/D PARAMETERS (MOVE HERE)
# ======================================

POP_SIZE = 80
OBJ = 6
DIM = 4
sigma = 0.3
ITER = 150

# initialize population
population = np.random.rand(POP_SIZE, DIM)

# weights
weights = np.random.dirichlet(np.ones(OBJ), size=POP_SIZE)

# neighbours
T_neigh = 5
dist_matrix = np.linalg.norm(weights[:,None,:] - weights[None,:,:], axis=2)
neighbours = np.argsort(dist_matrix, axis=1)[:, :T_neigh]

# convergence
convergence_history = []


# ======================================
# TCHEBYCHEFF FUNCTION
# ======================================

def tchebycheff(F, w, z):
    return np.max(w * np.abs(F - z))

# ======================================
#  CLOUD INTERVAL LOOP
# ======================================
Q = 10

# ======================================
# OBJECTIVE FUNCTIONS (FINAL)
# ======================================

def compute_objectives_array(x, x_nom, a):

    # Delay
    delay = np.mean(np.abs(np.diff(x, axis=0)))
    delay = delay / (np.max(np.abs(x)) + 1e-8)
    delay = np.clip(delay, 0, 1)

    # Error
    error_rate = np.mean((x - x_nom)**2)

    # Throughput (maximize)
    throughput = 1.0 / (1.0 + delay + error_rate)

    # Latency
    latency = np.mean(np.linalg.norm(x[1:] - x[:-1], axis=1))
    latency = latency / (np.max(np.abs(x)) + 1e-8)

    # Fairness
    resource_usage = np.mean(np.abs(x), axis=0)
    fairness = (np.sum(resource_usage)**2) / (
        len(resource_usage) * np.sum(resource_usage**2) + 1e-8
    )

    # Energy
    energy = np.mean(np.linalg.norm(a, axis=1)**2)

    # Final objectives (6)
    F = np.array([
        -throughput,   # maximize
        latency,
        delay,
        error_rate,
        -fairness,     # maximize
        energy
    ])

    return F


# ======================================
# CONSTRAINT FUNCTION (FULL FIX)
# ======================================

def check_constraints(P_psi, T_psi, f_d, f_e,
                      P_max, T_max, f_max):

    # Energy constraint
    energy_ok = P_psi <= P_max

    # Time constraint
    time_ok = T_psi <= T_max

    # Aggregation constraint
    agg_ok = (1 <= f_d <= f_max) and (1 <= f_e <= f_max)

    # feasibility
    feasible = energy_ok and time_ok and agg_ok

    # violations
    energy_violation = max(0.0, P_psi - P_max)
    time_violation   = max(0.0, T_psi - T_max)

    return feasible, energy_violation, time_violation


def objective_function(psi, x_control):

    # =========================
    # Decision Variables
    # =========================
    Gamma_scale = np.clip(psi[0], 0.2, 0.7)
    attack_scale = psi[1]

    # FIX 2: attack penalty
    attack_penalty = 0.05 * attack_scale

    f_d = psi[2]
    f_e = np.clip(psi[3], 0.3, 0.9)

    # =========================
    # Modified Signals
    # =========================
    a_mod = a * (1 + Gamma_scale)

    # FIX 3: reduced attack influence
    x_mod = x_control * (1 + 0.1 * Gamma_scale) + 0.02 * attack_scale

    # =========================
    # Objective Values
    # =========================
    F = compute_objectives_array(x_mod, x_nom, a_mod)

    # FIX 2: add penalty to error objective
    F[3] = F[3] + attack_penalty

    # =========================
    # Resource Constraints
    # =========================
    P_local = np.mean(np.linalg.norm(a_mod, axis=1)**2)
    T_local = np.mean(np.linalg.norm(x_mod, axis=1))

    feasible, e_v, t_v = check_constraints(
        P_local, T_local, f_d, f_e,
        P_max=100, T_max=100, f_max=10
    )

    # =========================
    # Penalty for constraint violation
    # =========================
    penalty = 0.01 * (e_v + t_v)

    F = F + penalty * np.ones_like(F)

    return F

# ======================================
# CLOUD: HRA-MOEA/D OPTIMIZATION (FIXED)
# ======================================

for q in range(Q):

    print(f"\n===== Cloud Interval {q} =====")

    x_control = x.copy() + 0.01 * np.random.randn(*x.shape)

    z_star = np.min([
        objective_function(p, x_control) for p in population
    ], axis=0)

    for it in range(ITER):
        for i in range(POP_SIZE):

            psi = population[i]

            F = objective_function(psi, x_control)

            resource_factor = np.mean(R)
            attack_factor = np.mean(np.abs(d))

            sigma_adaptive = sigma * (1 + resource_factor + attack_factor)

            j = np.random.choice(neighbours[i])
            parent2 = population[j]

            adaptive_weight = 1 + 0.5*np.mean(R) - 0.3*np.mean(S)

            psi_new = adaptive_weight * psi + (1 - adaptive_weight) * parent2

            # CPS scaling
            psi_new = psi_new * (1 + 0.2*resource_factor - 0.1*attack_factor)

           # =========================
           # Mutation (stable)
           # =========================
            psi_new += np.random.normal(0, sigma_adaptive + 0.1, DIM)

            # ADD THIS LINE (YAHI ADD KARNA HAI)
            psi_new += 0.15 * np.random.rand(DIM)

            # ✅ FIXED SOFT DIVERSITY (INSIDE LOOP)
            psi_new = 0.85 * psi_new + 0.15 * np.random.rand(DIM)

            if np.random.rand() < (0.2 + 0.2*np.mean(S)):
                psi_new = 0.7 * psi_new + 0.3 * np.random.rand(DIM)

            psi_new = np.clip(psi_new, 0.05, 0.95)

            F_new = objective_function(psi_new, x_control)

            z_star = np.minimum(z_star, F_new)

            for j in neighbours[i]:

                wj = weights[j]

                F_old = objective_function(population[j], x_control)

                g_old = np.max(wj * np.abs(F_old - z_star))
                g_new = np.max(wj * np.abs(F_new - z_star))

                if g_new < g_old:
                    population[j] = psi_new

            # self update
            population[i] = psi_new

    # ===================================
    # RESTART
    # ===================================
    if q % 2 == 0:
        num_restart = int(0.1 * POP_SIZE)

        for _ in range(num_restart):
            idx = np.random.randint(POP_SIZE)
            population[idx] = np.clip(np.random.rand(DIM), 0.05, 0.95)

    # ===================================
    # FINAL CLOUD DECISION
    # ===================================
    best_idx = np.argmin([
        np.sum(objective_function(p, x_control)) for p in population
    ])

    psi_cloud = 0.7 * psi_cloud + 0.3 * population[best_idx] if q > 0 else population[best_idx]

    print("Cloud Optimal ψ:", psi_cloud)


# ====================================
# DEVICE → EDGE AGGREGATION
# ====================================

# number of devices
N = 50

# number of edge servers
M = 5

# state dimension
n = 4

# devices per edge
devices_per_edge = N // M

# DEFINE DEVICE STATES (BEFORE USE)
x_i = x.copy()

# each device has a state vector
x_devices = np.random.randn(N, n) * 0.01 + x[:N]

print("Device state matrix shape:", x_devices.shape)



# ------------------------------------
# Edge aggregation
# ------------------------------------

x_edge = np.zeros((M, n))

for j in range(M):

    start = j * devices_per_edge
    end   = (j + 1) * devices_per_edge

    devices = x_devices[start:end]

    weights = 1 / (1 + 0.5 * np.linalg.norm(devices, axis=1))
    weights = weights / np.sum(weights)

    x_edge[j] = np.sum(weights[:, None] * devices, axis=0)
    x_edge[j] = x_edge[j] * 1.1

print("\nEdge aggregated states:\n", x_edge)
print("\nEdge state shape:", x_edge.shape)

# ======================================
# EDGE → DEVICE FEEDBACK SIGNAL (DEFINE FIRST)
# ======================================

edge_feedback_vector = x_edge if x_edge.ndim == 1 else np.mean(x_edge, axis=0)

print("Edge Feedback Vector:", edge_feedback_vector)

# ======================================
# PARAMETERS
# ======================================

# number of devices connected to edge j
N_j = 5

# state dimension
n = 4

# ADMM penalty parameter
rho = 1.2

# ADMM iterations
max_iter = 20

# initialize cloud state
x_cloud = np.zeros(n)

#====================================
# DEVICE STATES (from Step-5)
# ======================================

x_i = x_devices[:N_j].copy()

# initial edge state
x_edge = np.mean(x_i, axis=0)

# dual variables
lambda_i = np.zeros((N_j, n))

# ======================================
# OBJECTIVE FUNCTIONS
# ======================================

def f_i(x):
    return 0.5*np.linalg.norm(x)**2 + 0.1*np.sum(x)
def g(x):
    # edge coordination cost
    return np.linalg.norm(x)**2
# ======================================
# ADMM OPTIMIZATION (FINAL CORRECT)
# ======================================

for k in range(max_iter):

    # =========================
    # DEVICE UPDATE
    # =========================
    for i in range(N_j):

        resource_weight = 1 + np.mean(R)
        attack_weight   = 1 - np.mean(S)

        resource_factor = 1 + np.mean(R)
        attack_factor = 1 - np.mean(S)

        x_i[i] = (rho * x_edge - lambda_i[i]) / (1 + rho)

# CPS-aware modification
        x_i[i] = x_i[i] * resource_factor * attack_factor

# feedback integration
        x_i[i] = x_i[i] + 0.1 * x_cloud

# adaptive damping
        x_i[i] = 0.85 * x_i[i] + 0.15 * x_edge

        # proposed CPS-aware scaling
        x_i[i] = x_i[i] * resource_weight * attack_weight

        # diversity
        x_i[i] = x_i[i] + 0.01 * np.random.randn(n)

        # momentum
        x_i[i] = 0.9 * x_i[i] + 0.1 * x_edge


    # =========================
    # EDGE UPDATE
    # =========================
    resource_weight = 1 + np.mean(R)
    attack_weight   = 1 - np.mean(S)

    x_edge = np.mean(x_i + lambda_i / rho, axis=0)

    # proposed scaling
    x_edge = x_edge * (1 + np.mean(R) - np.mean(S))

    # cloud feedback
    x_edge = x_edge + 0.1 * x_cloud


    # =========================
    # DUAL UPDATE
    # =========================
    for i in range(N_j):
        lambda_i[i] = lambda_i[i] + rho * (x_i[i] - x_edge)


    # =========================
    # DEBUG
    # =========================
    if k % 5 == 0:
        print(f"ADMM Iter {k} | x_edge norm:", np.linalg.norm(x_edge))

print("\nDevice states after ADMM:")
print(x_i)
# =====================================
# STEP 7 : EDGE → CLOUD AGGREGATION
# =====================================

# number of edge servers
M = 5

# state dimension
n = 4

# -------------------------------------
# Example edge states (from STEP-6)
# -------------------------------------

# x_edge already obtained from ADMM optimization


print("Edge states:\n", x_edge)

# -------------------------------------
# Cloud aggregation
# -------------------------------------

if x_edge.ndim == 1:
    x_cloud = x_edge   # already vector
else:
    x_cloud = np.mean(x_edge, axis=0)

print("\nCloud aggregated state:")
print(x_cloud)

print("\nCloud state shape:", x_cloud.shape)
# ======================================
# UPDATED EDGE FEEDBACK (AFTER ADMM + CLOUD)
# ======================================

edge_feedback_vector = x_edge if x_edge.ndim == 1 else np.mean(x_edge, axis=0)
print("Edge Feedback Shape:", edge_feedback_vector.shape)

print("Updated Edge Feedback Vector:", edge_feedback_vector)

# ======================================
# PARAMETER ESTIMATION
# ======================================

def estimate_params(x, x_edge, x_cloud):
    rho = np.linalg.norm(x[-1] - x_edge) + 1e-5   # 🔥 FIX
    beta = np.linalg.norm(x_edge - x_cloud) + 1e-5
    delta = np.std(x)
    Delta = np.std(x_edge)
    return rho, beta, delta, Delta
rho, beta, delta, Delta = estimate_params(x, x_edge, x_cloud)

# ====================================
# FINAL RA-ETC CONTROL (CORRECTED)
# ====================================

# use previous CPS states (do NOT reset)
x_control = x.copy()
a = np.zeros((T, m))
x_trigger = x_control[0]

for t in range(T-1):

    # ===============================
    # Trigger condition
    # ===============================
    prediction = A @ x_control[t]
    trigger_value = np.linalg.norm(prediction - x_control[t])

    # ===============================
    # EDGE FEEDBACK
    # ===============================
    if 'edge_feedback_vector' in globals():
        edge_feedback = np.mean(edge_feedback_vector)
    else:
        edge_feedback = np.mean(x_control)

    # ===============================
    # CLOUD FEEDBACK
    # ===============================
    if 'x_cloud' in globals():
        cloud_feedback = np.mean(x_cloud)
    else:
        cloud_feedback = np.mean(x_control)

    # ===============================
    # THRESHOLD
    # ===============================
    threshold = (
        alpha1
        + alpha2 * R[t]
        + alpha3 * S[t]
        + 0.2 * np.linalg.norm(x_control[t])
        + 0.1 * edge_feedback
        + 0.1 * cloud_feedback
    )

    # ===============================
    # CONTROL WEIGHT
    # ===============================
    if trigger_value > threshold:
     control_weight = 0.8
    else:
     control_weight = 0.2

    # ===============================
    # CONTROL SIGNAL
    # ===============================
    gain_factor = np.minimum(2.5, 1.2 + R[t] - S[t])
    adaptive_gain = 1.05 * gain_factor * K
    a[t] = control_weight * (
    -adaptive_gain @ x_control[t]
    + 0.14 * edge_feedback_vector
    + 0.09 * x_cloud
    + 0.0025 * np.random.randn(n)
    )
    a[t] = np.clip(a[t], -0.3, 0.3)

# ======================================
# DELAY MODEL (FINAL CORRECT)
# ======================================
delay = int(1 + 3*np.linalg.norm(d[t]) + 1.5*S[t])
delay = np.clip(delay, 1, 3)

idx = max(0, t - delay)

# ======================================
# DEBUG
# ======================================
if t % 20 == 0:
    print(f"t={t}, delay={delay}, attack={np.linalg.norm(d[t]):.2f}, S={S[t]:.2f}")

# ======================================
# STATE UPDATE (BEST VERSION)
# ======================================
x_control[t+1] = cps_update(
    x_control[idx],
    a[idx],
    d[t]  
)
# ====================================
# STEP 8 : DECISION VARIABLE VECTOR
# ====================================

# state dimension
n = 4

# disturbance dimension
p = 2



# ------------------------------------
# Decision Variable 2 : Attack influence matrix E
# ------------------------------------

E = np.random.uniform(0.01, 0.05, (n, p))

def adaptive_aggregation(R, S):
    l1 = int(1 + 5 * (1 - np.mean(S)))
    l2 = int(1 + 5 * np.mean(R))
    return max(1,l1), max(1,l2)

f_d, f_e = adaptive_aggregation(R, S)




# =====================================
# STEP 9 : RESOURCE MODEL
# =====================================


# =====================================
# Resource parameters
# =====================================

T_local = 0.08     # time for local computation
T_comm  = 0.12     # communication delay

P_comp = 0.6       # computation energy
P_comm = 1.0       # communication energy

# ==============================
#  REAL RESOURCE ALLOCATION
# ==============================

# number of devices
N = 50

# CPU frequency per device
f_i = np.random.uniform(1.0, 2.5, N)



# bandwidth total
B_total = 10

# bandwidth allocation
b_i = np.random.dirichlet(np.ones(N)) * B_total

# parameters
c = 1.0
k = 0.5
D_i = np.random.randint(50,100,N)
SNR = 10
data_size = 5

T_comp_i = c * D_i / f_i
E_comp_i = k * (f_i ** 2) * D_i

T_comm_i = data_size / (b_i + 1e-6)
E_comm_i = P_comm * T_comm_i

# communication
r_i = b_i * np.log2(1 + SNR)
T_comm_i = data_size / (r_i + 1e-8)

#  ADD THIS HERE
T_comp_i = np.clip(T_comp_i, 0, 100)
T_comm_i = np.clip(T_comm_i, 0, 100)

# total
T_psi = np.sum(T_comp_i + T_comm_i) / N
P_psi = np.mean(E_comp_i)

print("✅ Advanced Time:", T_psi)
print("✅ Advanced Energy:", P_psi)



print("Communication Time T(ψ):", T_psi)
print("Energy Consumption P(ψ):", P_psi)


# ======================================
# STEP 10 : MULTI OBJECTIVE FUNCTION
# ======================================




def check_constraints(P_psi, T_psi, f_d, f_e,
                      P_max, T_max, f_max):

    # ------------------------------
    # Energy Constraint
    # ------------------------------
    energy_ok = P_psi <= P_max

    # ------------------------------
    # Time Constraint
    # ------------------------------
    time_ok = T_psi <= T_max

    # ------------------------------
    # Aggregation Frequency Constraint
    # ------------------------------
    agg_ok = (1 <= f_d <= f_max) and (1 <= f_e <= f_max)

    # ------------------------------
    # Feasibility
    # ------------------------------
    feasible = energy_ok and time_ok and agg_ok

    # ------------------------------
    # Violation values
    # ------------------------------
    energy_violation = max(0.0, P_psi - P_max)
    time_violation   = max(0.0, T_psi - T_max)

    return feasible, energy_violation, time_violation

# ======================================
# Tchebycheff Decomposition
# ======================================

def tchebycheff(F, w, z):

    return np.max(w * np.abs(F - z))

convergence_history = []


# ======================================
#  STABILITY CHECK
# ======================================

eig_vals = np.linalg.eigvals(A)

stability_index = max(np.abs(eig_vals))

print("\nStability Index:", stability_index)

if stability_index < 1:
    print("✅ System Stable")
else:
    print("⚠ System Unstable")



# =====================================
# PARETO DOMINANCE CHECK
# =====================================

def dominates(F_a, F_b):
    
    # F_a dominates F_b if all objectives <=
    # and at least one strictly <
    
    return np.all(F_a <= F_b) and np.any(F_a < F_b)


# =====================================
# EXTRACT PARETO SET
# =====================================

def get_pareto_set(population, objective_function, x_control):

    pareto_set = []

    for i in range(len(population)):

        psi_i = population[i]
        F_i = objective_function(psi_i, x_control)

        dominated = False

        for j in range(len(population)):

            if i == j:
                continue

            psi_j = population[j]
            F_j = objective_function(psi_j, x_control)

            if dominates(F_j, F_i):
                dominated = True
                break

        if not dominated:
            pareto_set.append((psi_i, F_i))

    # =========================
    # REMOVE DUPLICATES
    # =========================
    unique = []

    for psi, F in pareto_set:
        if not any(np.allclose(psi, u[0]) for u in unique):
            unique.append((psi, F))

    return unique
# =====================================
# Example Usage
# =====================================

# example population from STEP-12
population = population


# compute Pareto solutions
pareto_solutions = get_pareto_set(population, objective_function, x_control)

print("Total Population:", len(population))
print("Pareto Optimal Solutions:", len(pareto_solutions))

print("\nSample Pareto Solutions:\n")

for psi,F in pareto_solutions[:3]:
    print("ψ:",psi)
    print("Objectives:",F,"\n")


# =====================================
# STEP 14 : CPS PERFORMANCE METRICS
# =====================================

def compute_cps_metrics(states, states_nom, controls, attacks, A):

    K = len(states)

    # ===============================
    # Latency
    # ===============================
    latency = np.mean(np.linalg.norm(states, axis=1))

    # ===============================
    # Throughput
    # ===============================
    state_norms = np.linalg.norm(states, axis=1)
    threshold = np.mean(state_norms)
    throughput = np.sum(state_norms < threshold) / (K + 1e-8)

    # ===============================
    # Error Rate
    # ===============================
    deviation = np.linalg.norm(states - states_nom, axis=1)
    error_rate = np.mean(deviation)

    # ===============================
    # REAL CPS DELAY
    # ===============================
    delay_values = []
    for t in range(1, K):
        d_val = int(1 + 2 * np.linalg.norm(attacks[t]))
        d_val = np.clip(d_val, 1, 5)
        delay_values.append(d_val)

    delay = float(np.mean(delay_values))

    # ===============================
    # Energy Cost
    # ===============================
    energy_cost = (
        10 * np.mean(np.linalg.norm(controls, axis=1)**2)
        + 5 * np.mean(np.linalg.norm(attacks, axis=1)**2)
    )

    # ===============================
    # CPS Loss
    # ===============================
    cps_loss = np.mean((states - states_nom)**2)

    # ===============================
    # Resource Utilization
    # ===============================
    resource_utilization = np.mean(np.linalg.norm(states, axis=1))

    # ===============================
    # Node Criticality
    # ===============================
    node_criticality = np.mean(np.max(np.abs(states), axis=0))

    # ===============================
    # Convergence Speed
    # ===============================
    conv_idx = np.where(np.linalg.norm(states, axis=1) < 0.1)[0]
    convergence_speed = 1 / (conv_idx[0] + 1) if len(conv_idx) > 0 else 0

    # ===============================
    # Attack Impact
    # ===============================
    attack_impact = np.mean(deviation)

    # ===============================
    # Safety
    # ===============================
    threshold_safe = 1.2 * np.mean(state_norms)
    safety = np.sum(state_norms < threshold_safe) / K

    # ===============================
    # Fairness
    # ===============================
    resource_usage = np.mean(np.abs(states), axis=0)
    fairness = (np.sum(resource_usage)**2) / (
        len(resource_usage) * np.sum(resource_usage**2) + 1e-8
    )

    # ===============================
    # Load Balancing
    # ===============================
    load = np.mean(np.abs(states), axis=1)
    load_balancing = (np.sum(load)**2) / (
        len(load) * np.sum(load**2) + 1e-8
    )

    # ===============================
    # Energy Used
    # ===============================
    energy_used = np.mean(np.linalg.norm(controls, axis=1)**2)

    # ===============================
    # Utility
    # ===============================
    utility = throughput / (energy_cost + delay + 1e-8)

    # ===============================
    # Stability
    # ===============================
    stability_index = np.max(np.abs(np.linalg.eigvals(A)))

    # ===============================
    # Reliability
    # ===============================
    reliability = np.sum(state_norms < 1.2*np.mean(state_norms)) / K

    # ===============================
    # Resilience
    # ===============================
    resilience = 1 / (delay + 1)

    return {
        "Latency": latency,
        "Throughput": throughput,
        "Error Rate": error_rate,
        "Delay": delay,
        "Energy Cost": energy_cost,
        "Attack Impact": attack_impact,
        "Safety": safety,
        "Fairness": fairness,
        "Stability Index": stability_index,
        "Resilience Index": resilience,
        "CPS Loss": cps_loss,
        "Resource Utilization": resource_utilization,
        "Node Criticality": node_criticality,
        "Convergence Speed": convergence_speed,
        "Load Balancing": load_balancing,
        "Energy Used": energy_used,
        "Utility": utility,
        "System Reliability": reliability,
    }




# ==========================================
# STEP 15 : FINAL OUTPUT (FINAL FIX)
# ==========================================
pareto_solutions = get_pareto_set(population, objective_function, x_control)

print("Pareto size:", len(pareto_solutions))

# ✅ DEFINE BEST SOLUTION
best_solution = None
best_score = np.inf

for psi, F in pareto_solutions:

    score = np.linalg.norm(F)

    if score < best_score:
        best_score = score

        best_solution = (psi, F)

if best_solution is not None:
    psi_star, F_star = best_solution

    
else:
    print("⚠️ Pareto empty → fallback used")
    psi_star = population[0]
    F_star = objective_function(psi_star)

# extract optimal solution


print("Optimal Decision Vector ψ* :")
print(psi_star)

print("\nOptimal Objective Values F(ψ*):")
print(F_star)

print("\nOptimal Smart Grid State Trajectory shape:")
print(x_control.shape)

# ==========================================
# COMPUTE FINAL CPS PERFORMANCE METRICS
# ==========================================

# ==========================================
# COMPUTE FINAL CPS PERFORMANCE METRICS
# ==========================================

metrics = compute_cps_metrics(
    x_control,          # system states
    x_nom,      # nominal states
    a,          # control signals
    d,          # attack signals
    A           # system matrix
)

# ==========================================
# DEFINE TIME (IMPORTANT)
# ==========================================

time = np.arange(T)

# ==========================================
# PRINT METRICS (ERROR FIXED)
# ==========================================

print("\n===== CPS PERFORMANCE METRICS =====\n")

for key, value in metrics.items():
    
    if not np.isscalar(value):
        value = float(np.mean(value))

    print(f"{key} : {value:.4f}")

# ==========================================
# PLOTS
# ==========================================

# 1️⃣ State Trajectory
plt.figure(figsize=(8,5))

for i in range(n):
    plt.plot(time, x_control[:,i], label=f"x{i+1}")

plt.xlabel("Time Step")
plt.ylabel("State Value")
plt.title("CPS State Trajectory")
plt.legend()
plt.grid(True)
plt.show()


#  Nominal vs Attack
plt.figure(figsize=(8,5))

plt.plot(time, np.linalg.norm(x_control,axis=1), label="Actual State")
plt.plot(time, np.linalg.norm(x_nom,axis=1), label="Nominal State")

plt.xlabel("Time Step")
plt.ylabel("State Norm")
plt.title("Nominal vs Attack CPS State")
plt.legend()
plt.grid(True)
plt.show()


# Control Signals
plt.figure(figsize=(8,5))

for i in range(m):
    plt.plot(time, a[:,i], label=f"u{i+1}")

plt.xlabel("Time Step")
plt.ylabel("Control Input")
plt.title("Control Signals")
plt.legend()
plt.grid(True)
plt.show()


# Cyber Disturbance
plt.figure(figsize=(8,5))

for i in range(p):
    plt.plot(time, d[:,i], label=f"d{i+1}")

plt.xlabel("Time Step")
plt.ylabel("Disturbance")
plt.title("Cyber Disturbance Signal")
plt.legend()
plt.grid(True)
plt.show()
import numpy as np
import matplotlib.pyplot as plt

# ==============================
# SAFETY CHECKS
# ==============================

# Ensure arrays exist
x = np.array(x)
x_nom = np.array(x_nom)
a = np.array(a)
d = np.array(d)

time = np.arange(len(x))

# ==============================
# 1. PARETO FRONT
# ==============================

if len(pareto_solutions) > 0:
    F_vals = np.array([F for _, F in pareto_solutions])

    plt.figure()
    plt.scatter(F_vals[:,0], F_vals[:,1])
    plt.xlabel("Latency (J1)")
    plt.ylabel("Energy (J2)")
    plt.title("Pareto Front")
    plt.grid()
    plt.show()
else:
    print("⚠️ Pareto set empty")

# ==============================
# 2. NOMINAL vs CONTROLLED vs ATTACK
# ==============================

plt.figure()
plt.plot(time, np.linalg.norm(x_nom,axis=1), label="Nominal")
plt.plot(time, np.linalg.norm(x_control,axis=1), label="Controlled")

# safe attack approx
d_pad = np.zeros_like(x_nom)
d_pad[:len(d), :d.shape[1]] = d

plt.plot(time, np.linalg.norm(x_nom + d_pad,axis=1), label="Attack Approx")

plt.legend()
plt.title("System Behavior Comparison")
plt.grid()
plt.show()

# ==============================
# 3. RESOURCE vs ATTACK
# ==============================

plt.figure()
plt.plot(R, label="Resource")
plt.plot(S, label="Attack Severity")
plt.legend()
plt.title("Resource vs Attack Variation")
plt.grid()
plt.show()

# ==============================
# 4. RA-ETC TRIGGER
# ==============================

trigger_events = np.linalg.norm(x_control, axis=1)

plt.figure()
plt.plot(trigger_events)
plt.title("RA-ETC Trigger Activity")
plt.xlabel("Time")
plt.ylabel("Trigger Value")
plt.grid()
plt.show()

# ==============================
# 5. EDGE vs CLOUD
# ==============================

plt.figure()
plt.plot(x_edge.flatten(), label="Edge")
plt.plot(np.tile(x_cloud, len(x_edge)).flatten(), label="Cloud")
plt.legend()
plt.title("Edge vs Cloud State")
plt.grid()
plt.show()

# ==============================
# 6. ENERGY CONSUMPTION
# ==============================

energy = np.linalg.norm(a, axis=1)**2

plt.figure()
plt.plot(energy)
plt.title("Control Energy Consumption")
plt.xlabel("Time")
plt.grid()
plt.show()

# ==============================
# 7. STABILITY (STATE NORM)
# ==============================

state_norm = np.linalg.norm(x_control, axis=1)

plt.figure()
plt.plot(state_norm)
plt.title("System Stability (State Norm)")
plt.grid()
plt.show()

import numpy as np
import matplotlib.pyplot as plt

labels = [
    'Throughput','Latency','Delay',
    'Error','Fairness','Energy'
]

v = np.array(F_star).astype(float)
v = np.nan_to_num(v)
v = v / (np.max(v) + 1e-8)

angles = np.linspace(0, 2*np.pi, len(v), endpoint=False)

# close loop
v = np.append(v, v[0])
angles = np.append(angles, angles[0])

plt.figure(figsize=(6,6))
ax = plt.subplot(111, polar=True)

ax.plot(angles, v, linewidth=2)
ax.fill(angles, v, alpha=0.2)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels)

plt.title("CPS Radar")
plt.show()

plt.figure()
plt.plot(np.linalg.norm(a, axis=1))
plt.xlabel("Time Step")
plt.ylabel("Control Magnitude")
plt.title("Control Signal with Feedback")
plt.grid()
plt.show()

trigger = np.linalg.norm(x_control, axis=1)

plt.figure()
plt.plot(trigger)
plt.xlabel("Time Step")
plt.ylabel("Trigger Value")
plt.title("Event Trigger Activity (RA-ETC)")
plt.grid()
plt.show()

plt.figure()
plt.plot(np.linalg.norm(x_nom, axis=1), label="Without Feedback (Nominal)")
plt.plot(np.linalg.norm(x_control, axis=1), label="With Feedback (RA-ETC)")
plt.xlabel("Time Step")
plt.ylabel("State Norm")
plt.title("Effect of Feedback on CPS Stability")
plt.legend()
plt.grid()
plt.show()

plt.plot(np.linalg.norm(x_control, axis=1))
plt.title("System Stability")
plt.show()

plt.plot(convergence_history)
plt.title("Optimization Convergence")
plt.show()

