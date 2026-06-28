import numpy as np
import scipy.stats as stats

def process_descriptive_stats(data):
    dataset = data.get('dataset', [])
    sample = data.get('sample', True)

    if not dataset:
        raise ValueError("The 'dataset' array cannot be empty.")

    # Convert to numpy array
    arr = np.array(dataset, dtype=float)
    n = len(arr)

    # 1. Basic counts
    count = int(n)

    # 2. Central tendency
    mean_val = float(np.mean(arr))
    median_val = float(np.median(arr))
    
    # mode calculation
    mode_res = stats.mode(arr, keepdims=True)
    mode_val = [float(x) for x in mode_res.mode.flatten()]

    # 3. Dispersion
    ddof = 1 if sample else 0
    if sample and n <= 1:
        raise ValueError("Sample variance requires at least 2 data points.")

    variance_val = float(np.var(arr, ddof=ddof))
    std_dev_val = float(np.std(arr, ddof=ddof))
    range_val = float(np.max(arr) - np.min(arr))

    # 4. Position (Quartiles)
    min_val = float(np.min(arr))
    q1 = float(np.percentile(arr, 25))
    q2 = float(np.percentile(arr, 50))
    q3 = float(np.percentile(arr, 75))
    max_val = float(np.max(arr))
    iqr = float(q3 - q1)

    # 5. Outliers
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = arr[(arr < lower_bound) | (arr > upper_bound)]
    outliers_list = [float(x) for x in outliers]

    # 6. Histogram (Sturges' Rule)
    k = int(np.ceil(1 + 3.322 * np.log10(n)))
    k = max(1, k)
    
    frequencies, bin_edges = np.histogram(arr, bins=k)
    frequencies_list = [int(x) for x in frequencies]
    bin_edges_list = [float(x) for x in bin_edges]

    return {
        "status": "success",
        "data": {
            "count": count,
            "central_tendency": {
                "mean": round(mean_val, 4),
                "median": round(median_val, 4),
                "mode": [round(x, 4) for x in mode_val]
            },
            "dispersion": {
                "variance": round(variance_val, 4),
                "standard_deviation": round(std_dev_val, 4),
                "range": round(range_val, 4)
            },
            "position": {
                "min": round(min_val, 4),
                "q1": round(q1, 4),
                "q2": round(q2, 4),
                "q3": round(q3, 4),
                "max": round(max_val, 4),
                "iqr": round(iqr, 4)
            },
            "outliers": [round(x, 4) for x in outliers_list],
            "chart_data": {
                "histogram": {
                    "bins": [round(x, 4) for x in bin_edges_list],
                    "frequencies": frequencies_list
                }
            }
        }
    }

def process_probability(data):
    dist_name = data.get('distribution', '').lower()
    parameters = data.get('parameters', {})
    query_type = data.get('query_type', '')
    query_val = data.get('query_value')

    if dist_name == 'normal':
        mu = float(parameters.get('mu', 0))
        sigma = float(parameters.get('sigma', 1))
        if sigma <= 0:
            raise ValueError("Standard deviation (sigma) must be greater than 0.")
        dist = stats.norm(loc=mu, scale=sigma)
        is_discrete = False
        
        x_start = mu - 4 * sigma
        x_end = mu + 4 * sigma
        x_points = np.linspace(x_start, x_end, 100)

    elif dist_name == 't_student':
        df = float(parameters.get('df', 1))
        loc = float(parameters.get('loc', 0))
        scale = float(parameters.get('scale', 1))
        if df <= 0:
            raise ValueError("Degrees of freedom (df) must be greater than 0.")
        if scale <= 0:
            raise ValueError("Scale (scale) must be greater than 0.")
        dist = stats.t(df=df, loc=loc, scale=scale)
        is_discrete = False
        
        x_start = loc - 4 * scale
        x_end = loc + 4 * scale
        x_points = np.linspace(x_start, x_end, 100)

    elif dist_name == 'binomial':
        n = int(parameters.get('n', 1))
        p = float(parameters.get('p', 0.5))
        if n < 0:
            raise ValueError("Number of trials (n) cannot be negative.")
        if not (0 <= p <= 1):
            raise ValueError("Probability (p) must be between 0 and 1.")
        dist = stats.binom(n=n, p=p)
        is_discrete = True
        
        mean_val = n * p
        std_val = np.sqrt(n * p * (1 - p))
        if n <= 50:
            x_points = np.arange(0, n + 1)
        else:
            start = max(0, int(mean_val - 4 * std_val))
            end = min(n, int(mean_val + 4 * std_val))
            x_points = np.arange(start, end + 1)

    elif dist_name == 'poisson':
        lam = float(parameters.get('lambda', 1))
        if lam <= 0:
            raise ValueError("Parameter lambda must be greater than 0.")
        dist = stats.poisson(mu=lam)
        is_discrete = True
        
        mean_val = lam
        std_val = np.sqrt(lam)
        start = max(0, int(mean_val - 4 * std_val))
        end = int(mean_val + 4 * std_val)
        x_points = np.arange(start, end + 1)

    else:
        raise ValueError(f"Unsupported distribution: {dist_name}")

    probability = 0.0
    calc_desc = ""

    if query_type == 'exact':
        if not is_discrete:
            val = float(query_val)
            probability = 0.0
            calc_desc = f"P(X = {val})"
        else:
            val = int(query_val)
            probability = float(dist.pmf(val))
            calc_desc = f"P(X = {val})"

    elif query_type == 'cumulative_less':
        val = float(query_val)
        probability = float(dist.cdf(val))
        calc_desc = f"P(X <= {val})"

    elif query_type == 'cumulative_greater':
        val = float(query_val)
        probability = float(dist.sf(val))
        calc_desc = f"P(X > {val})"

    elif query_type == 'between':
        if not isinstance(query_val, list) or len(query_val) != 2:
            raise ValueError("For query_type 'between', query_value must be a two-element array [a, b].")
        a, b = float(query_val[0]), float(query_val[1])
        if a > b:
            a, b = b, a
        probability = float(dist.cdf(b) - dist.cdf(a))
        calc_desc = f"P({a} <= X <= {b})"
    else:
        raise ValueError(f"Unsupported query type: {query_type}")

    curve_points = []
    for x in x_points:
        y = float(dist.pmf(x)) if is_discrete else float(dist.pdf(x))
        curve_points.append({"x": float(x), "y": float(y)})

    x_min_gen = float(x_points[0])
    x_max_gen = float(x_points[-1])
    
    if query_type == 'exact':
        shaded_min = float(query_val)
        shaded_max = float(query_val)
    elif query_type == 'cumulative_less':
        shaded_min = x_min_gen
        shaded_max = float(query_val)
    elif query_type == 'cumulative_greater':
        shaded_min = float(query_val)
        shaded_max = x_max_gen
    elif query_type == 'between':
        a, b = float(query_val[0]), float(query_val[1])
        if a > b:
            a, b = b, a
        shaded_min = a
        shaded_max = b

    return {
        "status": "success",
        "distribution": dist_name,
        "calculation": {
            "type": calc_desc,
            "probability": round(probability, 4)
        },
        "chart_data": {
            "curve_points": curve_points,
            "shaded_region": {
                "x_min": round(shaded_min, 4),
                "x_max": round(shaded_max, 4)
            }
        }
    }
