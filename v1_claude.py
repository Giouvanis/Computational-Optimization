import time
import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog


def bad_lp(m, n, density, seed=0, spread=2):
    """Εφικτό και φραγμένο ΓΠ  min c'x, Ax = b, x >= 0  με κακώς κλιμακωμένο A."""
    rng = np.random.default_rng(seed)
    A0 = sp.random(
        m, n, density=density, random_state=rng, format="csr",
        data_rvs=lambda k: rng.uniform(0.5, 2, k) * rng.choice([-1, 1], k)
    )
    A0 = A0 + sp.eye(m, n, format="csr")          # καμία κενή γραμμή
    R = 10.0 ** rng.uniform(-spread, spread, m)   # κακή κλιμάκωση γραμμών
    S = 10.0 ** rng.uniform(-spread, spread, n)   # κακή κλιμάκωση στηλών
    A = (sp.diags(R) @ A0 @ sp.diags(S)).tocsr()
    b = A @ rng.uniform(0.5, 2, n)                # πρωτεύουσα εφικτότητα
    colmax = abs(A).max(axis=0).toarray().ravel()
    c = A.T @ rng.standard_normal(m) + rng.uniform(0.1, 1, n) * colmax  # δυϊκή εφικτότητα
    return A, b, c


def _nonzero_minmax_along_compressed_axis(M):
    """
    Υπολογίζει το min και max των απόλυτων τιμών των μη μηδενικών στοιχείων
    κατά μήκος του συμπιεσμένου άξονα (γραμμές για CSR, στήλες για CSC).
    """
    n_slices = M.shape[0] if sp.isspmatrix_csr(M) else M.shape[1]
    min_vals = np.zeros(n_slices, dtype=np.float64)
    max_vals = np.zeros(n_slices, dtype=np.float64)

    indptr = M.indptr
    abs_data = np.abs(M.data)

    for i in range(n_slices):
        start, end = indptr[i], indptr[i + 1]
        if start < end:
            vals = abs_data[start:end]
            nz = vals[vals > 0]
            if nz.size > 0:
                min_vals[i] = nz.min()
                max_vals[i] = nz.max()

    return min_vals, max_vals


def _scale_rows_csr(A_csr, r):
    """Πολλαπλασιάζει κάθε γραμμή i του CSR πίνακα A_csr με r[i] (in-place στο data)."""
    row_nnz = np.diff(A_csr.indptr)
    A_csr.data *= np.repeat(r, row_nnz)


def _scale_cols_csc(A_csc, s):
    """Πολλαπλασιάζει κάθε στήλη j του CSC πίνακα A_csc με s[j] (in-place στο data)."""
    col_nnz = np.diff(A_csc.indptr)
    A_csc.data *= np.repeat(s, col_nnz)


def hybrid_scaling(A, b, c):
    """
    Εφαρμόζει υβριδική κλιμάκωση σε πρόβλημα ΓΠ: min c^T x, Ax = b, x >= 0.
    Στάδιο 1: Γεωμετρική κλιμάκωση (γραμμές, έπειτα στήλες).
    Στάδιο 2: Ισορρόπηση / Equilibration (γραμμές, έπειτα στήλες).

    Επιστρέφει:
        A_scaled (csr_matrix), b_scaled (ndarray), c_scaled (ndarray),
        r_total (ndarray), s_total (ndarray)
    """
    A_work = A.tocsr(copy=True).astype(np.float64)
    A_work.eliminate_zeros()

    # --- Στάδιο 1: Γεωμετρική Κλιμάκωση ---
    # 1α. Γραμμές
    r_min, r_max = _nonzero_minmax_along_compressed_axis(A_work)
    r1 = np.ones(A_work.shape[0], dtype=np.float64)
    mask_r = r_max > 0
    r1[mask_r] = 1.0 / np.sqrt(r_min[mask_r] * r_max[mask_r])
    _scale_rows_csr(A_work, r1)

    # 1β. Στήλες
    A_csc = A_work.tocsc()
    c_min, c_max = _nonzero_minmax_along_compressed_axis(A_csc)
    s1 = np.ones(A_csc.shape[1], dtype=np.float64)
    mask_c = c_max > 0
    s1[mask_c] = 1.0 / np.sqrt(c_min[mask_c] * c_max[mask_c])
    _scale_cols_csc(A_csc, s1)

    # --- Στάδιο 2: Ισορρόπηση (Equilibration) ---
    # 2α. Γραμμές
    A_work = A_csc.tocsr()
    _, r_max2 = _nonzero_minmax_along_compressed_axis(A_work)
    r2 = np.ones(A_work.shape[0], dtype=np.float64)
    mask_r2 = r_max2 > 0
    r2[mask_r2] = 1.0 / r_max2[mask_r2]
    _scale_rows_csr(A_work, r2)

    # 2β. Στήλες
    A_csc = A_work.tocsc()
    _, c_max2 = _nonzero_minmax_along_compressed_axis(A_csc)
    s2 = np.ones(A_csc.shape[1], dtype=np.float64)
    mask_c2 = c_max2 > 0
    s2[mask_c2] = 1.0 / c_max2[mask_c2]
    _scale_cols_csc(A_csc, s2)

    # Συνολικοί συντελεστές και μετασχηματισμός των A, b, c
    A_scaled = A_csc.tocsr()
    r_total = r1 * r2
    s_total = s1 * s2
    b_scaled = r_total * b
    c_scaled = s_total * c

    return A_scaled, b_scaled, c_scaled, r_total, s_total


def unscale_solution(x_scaled, s_total):
    """Επαναφέρει τη λύση του κλιμακωμένου προβλήματος στον αρχικό χώρο: x = S * x_tilde."""
    return s_total * x_scaled


def matrix_spread(A):
    """Υπολογίζει το min, max και τον λόγο max/min των μη μηδενικών |a_ij|."""
    abs_nz = np.abs(A.data)
    abs_nz = abs_nz[abs_nz > 0]
    a_min = abs_nz.min()
    a_max = abs_nz.max()
    return a_min, a_max, a_max / a_min


def run_experiment(m=200, n=400, density=0.05, seed=0, spread=4):
    A, b, c = bad_lp(m, n, density, seed=seed, spread=spread)

    min_before, max_before, ratio_before = matrix_spread(A)

    t0 = time.perf_counter()
    A_s, b_s, c_s, r, s = hybrid_scaling(A, b, c)
    t_scale = time.perf_counter() - t0

    min_after, max_after, ratio_after = matrix_spread(A_s)

    # Επίλυση αρχικού και κλιμακωμένου ΓΠ
    t1 = time.perf_counter()
    res_orig = linprog(c, A_eq=A, b_eq=b, bounds=(0, None), method="highs")
    t_orig = time.perf_counter() - t1

    t2 = time.perf_counter()
    res_scaled = linprog(c_s, A_eq=A_s, b_eq=b_s, bounds=(0, None), method="highs")
    t_scaled = time.perf_counter() - t2

    print(f"=== Πείραμα (m={m}, n={n}, density={density}, spread={spread}) ===")
    print(f"Πριν  : min={min_before:.3e}, max={max_before:.3e}, ratio={ratio_before:.3e}")
    print(f"Μετά  : min={min_after:.3e}, max={max_after:.3e}, ratio={ratio_after:.3e}")
    print(f"Χρόνος κλιμάκωσης: {t_scale*1000:.2f} ms")
    print(f"Χρόνος linprog (αρχικό vs κλιμακωμένο): {t_orig*1000:.2f} ms vs {t_scaled*1000:.2f} ms")

    if res_orig.success and res_scaled.success:
        x_unscaled = unscale_solution(res_scaled.x, s)
        obj_diff = abs(res_orig.fun - float(c @ x_unscaled))
        primal_res = np.linalg.norm(A @ x_unscaled - b, ord=np.inf)
        min_x = x_unscaled.min()

        print(f"Διαφορά αντικειμενικής |f_orig - f_unscaled|: {obj_diff:.3e}")
        print(f"Πρωτεύον υπόλοιπο ||Ax - b||_inf           : {primal_res:.3e}")
        print(f"Ελάχιστο x_j (έλεγχος x >= 0)              : {min_x:.3e}")
    else:
        print("Status αρχικού:", res_orig.message)
        print("Status κλιμακωμένου:", res_scaled.message)


if __name__ == "__main__":
    run_experiment(m=200, n=400, density=0.05, seed=0, spread=4)