import math
import random
import time


# ============================================================
# 1. ΜΕΤΑΤΡΟΠΗ ΣΕ CSR (από τον κώδικά σου, 1-based indexing)
# ============================================================
def sparsify_csr(matrix):
    """Μετατρέπει 2D πίνακα σε μορφή CSR (κατά γραμμές)."""
    m = len(matrix)
    n = 0 if m == 0 else len(matrix[0])
    Anz = []
    IA = [1]
    JA = []

    i = 0
    while i < m:
        j = 0
        while j < n:
            if matrix[i][j] != 0:
                Anz.append(float(matrix[i][j]))
                JA.append(j + 1)
            j += 1
        IA.append(len(Anz) + 1)
        i += 1
    return Anz, IA, JA


def switch_csr_csc(Anz, IA, JA, outer_dim, inner_dim):
    """
    Μετατρέπει απευθείας CSR -> CSC (ή CSC -> CSR) χωρίς να φτιάχνει 2D πίνακα.
    - Για CSR -> CSC: outer_dim = m, inner_dim = n
    - Για CSC -> CSR: outer_dim = n, inner_dim = m
    """
    buckets = [[] for _ in range(inner_dim)]

    for idx in range(outer_dim):
        start = IA[idx] - 1
        end = IA[idx + 1] - 1
        for k in range(start, end):
            target = JA[k] - 1
            buckets[target].append((idx + 1, Anz[k]))

    new_Anz = []
    new_IA = [1]
    new_JA = []

    for b in buckets:
        for pos, val in b:
            new_Anz.append(val)
            new_JA.append(pos)
        new_IA.append(len(new_Anz) + 1)

    return new_Anz, new_IA, new_JA


# ============================================================
# 2. ΣΥΝΑΡΤΗΣΕΙΣ ΚΛΙΜΑΚΩΣΗΣ (ΠΑΝΩ ΣΤΑ Anz, IA)
# ============================================================
def geometric_scale_1d(Anz, IA, count):
    """Γεωμετρική κλιμάκωση για όλες τις γραμμές (CSR) ή στήλες (CSC)."""
    factors = []
    for idx in range(count):
        start = IA[idx] - 1
        end = IA[idx + 1] - 1

        if start == end:
            factors.append(1.0)
            continue

        v_min = abs(Anz[start])
        v_max = v_min
        for k in range(start + 1, end):
            val = abs(Anz[k])
            if val < v_min:
                v_min = val
            if val > v_max:
                v_max = val

        factor = 1.0 / (math.sqrt(v_min) * math.sqrt(v_max))
        factors.append(factor)

        for k in range(start, end):
            Anz[k] *= factor

    return Anz, factors


def equilibration_scale_1d(Anz, IA, count):
    """Ισορρόπηση (διαίρεση με το μέγιστο |a_ij|) για γραμμές (CSR) ή στήλες (CSC)."""
    factors = []
    for idx in range(count):
        start = IA[idx] - 1
        end = IA[idx + 1] - 1

        if start == end:
            factors.append(1.0)
            continue

        v_max = abs(Anz[start])
        for k in range(start + 1, end):
            val = abs(Anz[k])
            if val > v_max:
                v_max = val

        factor = 1.0 / v_max
        factors.append(factor)

        for k in range(start, end):
            Anz[k] *= factor

    return Anz, factors


def compute_spread(Anz):
    """Υπολογίζει min, max και λόγο max/min των μη μηδενικών |a_ij|."""
    abs_vals = [abs(x) for x in Anz if x != 0]
    v_min = min(abs_vals)
    v_max = max(abs_vals)
    return v_min, v_max, v_max / v_min


# ============================================================
# 3. ΥΒΡΙΔΙΚΗ ΚΛΙΜΑΚΩΣΗ ΑΠΕΥΘΕΙΑΣ ΣΕ ΑΡΑΙΑ ΜΟΡΦΗ (CSR <-> CSC)
# ============================================================
def hybrid_scaling_sparse(Anz, IA, JA, m, n, b=None, c=None):
    # Κάνουμε αντίγραφο του Anz για να μην αλλοιωθεί ο αρχικός πίνακας
    Anz_work = Anz[:]

    # --- ΣΤΑΔΙΟ 1: Γεωμετρική Κλιμάκωση ---
    # 1α. Γραμμές (CSR)
    Anz_work, r1 = geometric_scale_1d(Anz_work, IA, m)

    # 1β. Στήλες (απευθείας μετατροπή CSR -> CSC)
    Anz_csc, IA_csc, JA_csc = switch_csr_csc(Anz_work, IA, JA, m, n)
    Anz_csc, s1 = geometric_scale_1d(Anz_csc, IA_csc, n)

    # --- ΣΤΑΔΙΟ 2: Ισορρόπηση (Equilibration) ---
    # 2α. Γραμμές (απευθείας μετατροπή CSC -> CSR)
    Anz_csr, IA_csr, JA_csr = switch_csr_csc(Anz_csc, IA_csc, JA_csc, n, m)
    Anz_csr, r2 = equilibration_scale_1d(Anz_csr, IA_csr, m)

    # 2β. Στήλες (απευθείας μετατροπή CSR -> CSC)
    Anz_csc, IA_csc, JA_csc = switch_csr_csc(Anz_csr, IA_csr, JA_csr, m, n)
    Anz_csc, s2 = equilibration_scale_1d(Anz_csc, IA_csc, n)

    # Τελική μορφή CSR
    Anz_final, IA_final, JA_final = switch_csr_csc(Anz_csc, IA_csc, JA_csc, n, m)

    # Συνολικοί συντελεστές
    r_total = [r1[i] * r2[i] for i in range(m)]
    s_total = [s1[j] * s2[j] for j in range(n)]

    b_scaled = [r_total[i] * b[i] for i in range(m)] if b is not None else None
    c_scaled = [s_total[j] * c[j] for j in range(n)] if c is not None else None

    return Anz_final, IA_final, JA_final, b_scaled, c_scaled, r_total, s_total


# ============================================================
# 4. ΓΕΝΝΗΤΡΙΑ ΠΙΝΑΚΑ & ΕΚΤΕΛΕΣΗ (ΜΟΝΟ Ο ΜΕΓΑΛΟΣ ΠΙΝΑΚΑΣ)
# ============================================================
def generate_bad_matrix(m, n, density=0.05, seed=0, spread=4):
    """Φτιάχνει έναν κακώς κλιμακωμένο αραιό πίνακα m x n χωρίς NumPy/SciPy."""
    rng = random.Random(seed)
    R = [10.0 ** rng.uniform(-spread, spread) for _ in range(m)]
    S = [10.0 ** rng.uniform(-spread, spread) for _ in range(n)]

    matrix = [[0.0 for _ in range(n)] for _ in range(m)]
    for i in range(m):
        for j in range(n):
            val = 0.0
            if rng.random() < density:
                val = rng.uniform(0.5, 2.0) * rng.choice([-1.0, 1.0])
            if i == j:
                val += 1.0
            if val != 0.0:
                matrix[i][j] = R[i] * val * S[j]
    return matrix


if __name__ == "__main__":
    m, n, density, seed, spread = 200, 400, 0.05, 0, 4
    repeats = 10

    # Δημιουργία πίνακα και μετατροπή σε CSR μία φορά (όπως κάνει η bad_lp)
    A_dense = generate_bad_matrix(m, n, density=density, seed=seed, spread=spread)
    Anz, IA, JA = sparsify_csr(A_dense)

    min_b, max_b, ratio_b = compute_spread(Anz)

    # Μέτρηση χρόνου κλιμάκωσης (μέσος όρος σε 10 επαναλήψεις)
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        Anz_s, IA_s, JA_s, _, _, r_total, s_total = hybrid_scaling_sparse(Anz, IA, JA, m, n)
        times.append((time.perf_counter() - t0) * 1000)

    avg_ms = sum(times) / len(times)
    min_a, max_a, ratio_a = compute_spread(Anz_s)

    print(f"=== Πίνακας {m}x{n} (density={density}, spread={spread}, repeats={repeats}) ===")
    print(f"ΠΡΙΝ  -> min: {min_b:.3e}, max: {max_b:.3e}, λόγος (max/min): {ratio_b:.3e}")
    print(f"ΜΕΤΑ  -> min: {min_a:.3e}, max: {max_a:.3e}, λόγος (max/min): {ratio_a:.3e}")
    print(f"Μέσος χρόνος κλιμάκωσης: {avg_ms:.3f} ms")