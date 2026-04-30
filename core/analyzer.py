import numpy as np
import warnings


def _calculate_r_squared(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculates the R-squared (coefficient of determination) to evaluate model fit."""
    rss = np.sum((y_true - y_pred) ** 2)
    tss = np.sum((y_true - np.mean(y_true)) ** 2)
    if tss == 0:
        return 1.0
    return 1 - rss / tss


def _expected_consecutive_ratios(
    name: str, x_arr: np.ndarray, y_arr: np.ndarray = None, eps: float = 1e-10
) -> np.ndarray:
    """Computes the theoretical asymptotic growth ratio T(x_{i+1})/T(x_i) for a given complexity class."""
    if name == "O(1)":
        return np.ones(len(x_arr) - 1)
    elif name == "O(n)":
        return x_arr[1:] / x_arr[:-1]
    elif name == "O(n log n)":
        f = x_arr * np.log(np.maximum(x_arr, eps))
        return f[1:] / f[:-1]
    elif name == "O(n^2)":
        return (x_arr[1:] / x_arr[:-1]) ** 2
    elif name == "O(n^3)":
        return (x_arr[1:] / x_arr[:-1]) ** 3
    elif name == "O(2^n)":
        # Dynamically estimate the base for exponential growth using boundary points
        if y_arr is not None and len(x_arr) > 1 and x_arr[-1] > x_arr[0]:
            base = (max(y_arr[-1], eps) / max(y_arr[0], eps)) ** (
                1.0 / (x_arr[-1] - x_arr[0])
            )
            return np.minimum(base ** (x_arr[1:] - x_arr[:-1]), 1e15)
        return np.minimum(2.0 ** (x_arr[1:] - x_arr[:-1]), 1e15)
    return x_arr[1:] / x_arr[:-1]


def _ratio_vote_scores(
    x_tail: np.ndarray, y_tail: np.ndarray, classes: list, eps: float = 1e-10
) -> dict:
    """Calculates confidence scores based on how closely observed tail ratios match theoretical expectations."""
    if len(x_tail) < 2:
        return {c: 1.0 / len(classes) for c in classes}

    obs = y_tail[1:] / np.maximum(y_tail[:-1], eps)

    exp = {
        name: _expected_consecutive_ratios(name, x_tail, y_tail, eps)
        for name in classes
    }

    votes = {c: 0 for c in classes}
    for i in range(len(obs)):
        best = min(classes, key=lambda c: abs(obs[i] - exp[c][i]) / max(exp[c][i], eps))
        votes[best] += 1

    n_votes = max(len(obs), 1)
    return {c: votes[c] / n_votes for c in classes}


def identify_complexity(n_sizes: list, times: list) -> tuple:
    """
    Estimates the Big-O time complexity by evaluating empirical execution times against input sizes.
    Returns a tuple containing the best-fit complexity string and a dictionary of top candidate probabilities.
    """
    # Suppress numpy polyfit rank warnings for ill-conditioned datasets
    try:
        rank_warning = np.exceptions.RankWarning
    except AttributeError:
        rank_warning = np.RankWarning

    warnings.simplefilter("ignore", rank_warning)

    x = np.array(n_sizes, dtype=float)
    y_raw = np.array(times, dtype=float)
    y_max = np.max(y_raw)
    eps = 1e-10

    # Short-circuit evaluations for O(1) detection
    if y_raw[-1] < 2_000:
        return "O(1)", {"O(1)": 1.0}

    normalised_range = (np.max(y_raw) - np.min(y_raw)) / y_max if y_max > 0 else 0.0
    if normalised_range < 0.05:
        return "O(1)", {"O(1)": 1.0}

    coeffs_slope = np.polyfit(x, y_raw, 1)
    slope_contribution = abs(coeffs_slope[0]) * (x[-1] - x[0]) / (y_max + eps)

    if slope_contribution < 0.05:
        return "O(1)", {"O(1)": 1.0}

    y = y_raw / y_max
    x_safe = np.where(x > 0, x, eps)

    # Calculate R-squared fits across standard complexity classes
    r2 = {}

    r2["O(1)"] = _calculate_r_squared(y, np.full_like(y, np.mean(y)))

    coeffs_lin = np.polyfit(x, y, 1)
    r2["O(n)"] = _calculate_r_squared(y, np.polyval(coeffs_lin, x))

    x_nlogn = x_safe * np.log(x_safe)
    coeffs_nlogn = np.polyfit(x_nlogn, y, 1)
    r2["O(n log n)"] = _calculate_r_squared(y, np.polyval(coeffs_nlogn, x_nlogn))

    coeffs_quad = np.polyfit(x**2, y, 1)
    r2["O(n^2)"] = _calculate_r_squared(y, np.polyval(coeffs_quad, x**2))

    coeffs_cub = np.polyfit(x**3, y, 1)
    r2["O(n^3)"] = _calculate_r_squared(y, np.polyval(coeffs_cub, x**3))

    y_log = np.log(np.maximum(y, eps))
    coeffs_exp = np.polyfit(x, y_log, 1, w=y)
    r2["O(2^n)"] = _calculate_r_squared(y, np.exp(np.polyval(coeffs_exp, x)))

    # Apply tail ratio voting using a smoothed signal
    def _median3(arr):
        out = arr.copy().astype(float)
        for i in range(1, len(arr) - 1):
            out[i] = float(np.median(arr[i - 1 : i + 2]))
        return out

    y_smooth = _median3(y_raw)
    n_pts = len(x)
    n_tail = min(max(3, n_pts - n_pts // 2), n_pts)

    x_tail = x_safe[-n_tail:]
    y_tail = y_smooth[-n_tail:]

    classes = list(r2.keys())
    ratio_votes = _ratio_vote_scores(x_tail, y_tail, classes, eps)

    # Blend statistical fit metrics
    RATIO_W = 0.30
    R2_W = 0.70

    combined = {
        name: R2_W * max(r2[name], 0.0) + RATIO_W * ratio_votes.get(name, 0.0)
        for name in r2
    }

    # Apply scaling domain constraints to prevent physical impossibility edge cases
    max_n = np.max(x)
    if max_n > 60:
        combined["O(2^n)"] = 0.0
    if max_n > 2000:
        combined["O(n^3)"] = 0.0
    if r2.get("O(n)", 0.0) > 0.90:
        combined["O(n)"] = min(1.0, combined["O(n)"] + 0.10)

    if not combined:
        return "O(1)", {"O(1)": 1.0}

    best_fit_class = max(combined, key=combined.get)
    top2_names = [
        k for k, _ in sorted(combined.items(), key=lambda kv: kv[1], reverse=True)[:2]
    ]

    # Heuristic tiebreaker for linear vs linearithmic ambiguity
    if {"O(n)", "O(n log n)"}.issubset(set(top2_names)) and len(x_tail) >= 3:
        score_n = combined.get("O(n)", 0.0)
        score_nlogn = combined.get("O(n log n)", 0.0)
        margin = abs(score_n - score_nlogn)

        if margin < 0.12:
            t_per_n = y_tail / x_tail
            log_x_tail = np.log(np.maximum(x_tail, eps))
            slope_coeff = np.polyfit(log_x_tail, t_per_n, 1)[0]
            noise_floor = 0.06 * np.mean(t_per_n)

            if slope_coeff > noise_floor:
                best_fit_class = "O(n log n)"
                combined["O(n log n)"] = min(1.0, max(score_n, score_nlogn) + 0.04)
                combined["O(n)"] = max(0.0, min(score_n, score_nlogn) - 0.04)
            else:
                best_fit_class = "O(n)"
                combined["O(n)"] = min(1.0, max(score_n, score_nlogn) + 0.04)
                combined["O(n log n)"] = max(0.0, min(score_n, score_nlogn) - 0.04)

    # Format the top 3 candidates for UI consumption
    top_candidates = dict(
        sorted(combined.items(), key=lambda kv: kv[1], reverse=True)[:3]
    )
    top_candidates = {k: float(np.clip(v, 0.0, 1.0)) for k, v in top_candidates.items()}

    return best_fit_class, top_candidates
