import numpy as np
import scipy as sc
import matplotlib.pyplot as plt
import pandas as pd

import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.api import ARDL
from scipy.fftpack import rfft, irfft

from typing import Union, List, Tuple, Dict, Optional


def simple_LR(
    fr_ts: Union[List[float], np.ndarray, pd.Series],
    behavior_ts: Union[List[Union[List[float], np.ndarray, pd.Series]], 
                       Dict[str, Union[List[float], np.ndarray, pd.Series]]],
    behavior_names: Optional[Union[str, List[str]]] = None,
    add_constant: bool = True
) -> object:
    """
    Fit a linear regression model between neural firing rates and one or more 
    behavioral variables.
    
    This function performs ordinary least squares (OLS) regression to analyze
    the linear relationship between neural activity and behavioral predictors.
    It handles multiple predictors and missing data.
    
    Parameters
    ----------
    fr_ts : array-like
        Time series of neural firing rates (dependent variable).
        Can be a list, numpy array, or pandas Series.
    
    behavior_ts : array-like or dict
        Time series of predictor variable(s). Can be:
        - Single array-like for one behavior
        - List of array-likes for multiple behaviors
        - Dict mapping behavior names to array-likes
    
    behavior_names : str, list of str, or None, optional
        Names of behavioral variables. Required if behavior_ts is a list.
        If behavior_ts is a dict, this parameter is ignored.
        If single behavior and str, uses that name.
        If None and single behavior, defaults to 'behavior'.
    
    add_constant : bool, default=True
        Whether to add an intercept term to the model.
        Set to False if data is already centered or intercept not needed.
    
    Returns
    -------
    results : RegressionResults
        Fitted OLS regression model results containing:
        - Coefficients and standard errors
        - t-statistics and p-values
        - R-squared and adjusted R-squared
        - F-statistic and model diagnostics
        - Residuals and fitted values
    
    Raises
    ------
    ValueError
        If input time series are empty or all data is missing after NA removal.
        If behavior_names not provided when behavior_ts is a list.
        If number of behavior names doesn't match number of behavior time series.
    
    Notes
    -----
    Model Specification:
    The linear regression model is:
    y = β₀ + β₁X₁ + β₂X₂ + ... + βₖXₖ + ε
    
    where:
    - y is the firing rate
    - β₀ is the intercept (if add_constant=True)
    - β₁, ..., βₖ are regression coefficients
    - X₁, ..., Xₖ are behavioral predictors
    - ε is the error term
    
    The function automatically:
    - Aligns all time series to the shortest length
    - Removes observations with any missing values
    - Adds an intercept term by default
    
    For neural data, consider:
    - Checking residual plots for heteroscedasticity
    - Testing for multicollinearity with multiple predictors
    
    Examples
    --------
    >>> import numpy as np
    >>> # Generate sample data
    >>> np.random.seed(42)
    >>> n_samples = 100
    >>> velocity = np.random.randn(n_samples)
    >>> acceleration = np.diff(np.concatenate([[0], velocity]))
    >>> fr_data = 5 + 2*velocity + 1.5*acceleration + np.random.randn(n_samples)
    >>> 
    >>> # Example 1: Single predictor
    >>> results = fit_linear_regression(
    ...     fr_data, 
    ...     velocity, 
    ...     'velocity'
    ... )
    >>> print(f"Velocity coefficient: {results.params['velocity']:.3f}")
    >>> 
    >>> # Example 2: Multiple predictors with list
    >>> results = fit_linear_regression(
    ...     fr_data,
    ...     [velocity, acceleration],
    ...     ['velocity', 'acceleration']
    ... )
    >>> 
    >>> # Example 3: Multiple predictors with dict
    >>> results = fit_linear_regression(
    ...     fr_data,
    ...     {'velocity': velocity, 'acceleration': acceleration},
    ... )
    
    See Also
    --------
    statsmodels.api.OLS : Underlying OLS implementation
    """
    
    # Input validation
    if len(fr_ts) == 0:
        raise ValueError("Firing rate time series cannot be empty")
    
    # Convert fr_ts to numpy array
    fr_ts = np.asarray(fr_ts)
    
    # Handle different behavior_ts input formats
    behavior_dict = {}
    
    if isinstance(behavior_ts, dict):
        # Already in dict format
        behavior_dict = {k: np.asarray(v) for k, v in behavior_ts.items()}
        
    elif isinstance(behavior_ts, list) and len(behavior_ts) > 0:
        # Check if it's a list of time series or a single time series
        if isinstance(behavior_ts[0], (list, np.ndarray, pd.Series)):
            # List of multiple behaviors
            if behavior_names is None:
                raise ValueError("behavior_names must be provided when behavior_ts is a list of arrays")
            
            if isinstance(behavior_names, str):
                behavior_names = [behavior_names]
                
            if len(behavior_names) != len(behavior_ts):
                raise ValueError(f"Number of behavior names ({len(behavior_names)}) must match "
                               f"number of behavior time series ({len(behavior_ts)})")
            
            for name, ts in zip(behavior_names, behavior_ts):
                behavior_dict[name] = np.asarray(ts)
        else:
            # Single time series as list
            name = behavior_names if isinstance(behavior_names, str) else 'behavior'
            behavior_dict[name] = np.asarray(behavior_ts)
            
    else:
        # Single time series (array-like)
        name = behavior_names if isinstance(behavior_names, str) else 'behavior'
        behavior_dict[name] = np.asarray(behavior_ts)
    
    # Validate all behavior time series are non-empty
    for name, ts in behavior_dict.items():
        if len(ts) == 0:
            raise ValueError(f"Behavior time series '{name}' cannot be empty")
    
    # Find minimum length across all time series
    all_lengths = [len(fr_ts)] + [len(ts) for ts in behavior_dict.values()]
    min_session_len = min(all_lengths)
    
    # Align all time series
    fr_ts_aligned = fr_ts[:min_session_len]
    behavior_dict_aligned = {name: ts[:min_session_len] for name, ts in behavior_dict.items()}
    
    # Create DataFrame
    df_data = pd.DataFrame({'fr': fr_ts_aligned})
    for name, ts in behavior_dict_aligned.items():
        df_data[name] = ts
    
    # Remove rows with any NA values
    df_clean = df_data.dropna()
    
    if len(df_clean) == 0:
        raise ValueError("No valid data remaining after removing NA values")
    
    if len(df_clean) < len(df_data):
        n_removed = len(df_data) - len(df_clean)
        warnings.warn(f"Removed {n_removed} observations due to missing values")
    
    # Prepare data for regression
    y = df_clean['fr']
    X = df_clean[list(behavior_dict.keys())]
    
    # Add constant if requested
    if add_constant:
        X = sm.add_constant(X)
    
    # Fit OLS model
    try:
        model_OLS = sm.OLS(y, X)
        results_OLS = model_OLS.fit()
            
    except Exception as e:
        raise RuntimeError(f"Failed to fit linear regression model: {str(e)}")
    
    return results_OLS


###########################################################################
### NONPARAMETRIC PERMUTATION TEST ###

def session_permutation(
    fr_ts, 
    behavior_ts, 
    behavior_ts_ensemble, 
    behavior_name, 
    subsample_ensemble=None
):
    """
    Performs permutation testing to assess the statistical significance of a neuron's 
    behavioral correlation by comparing against a null distribution.
    
    This function:
    1. Calculates the t-statistic for the target session's linear regression
    2. Creates a null distribution by computing t-statistics from an ensemble of other sessions
    3. Determines the percentile rank of the target t-statistic within the null distribution
    
    Parameters
    ----------
    fr_ts : array-like
        Time series of neural firing rates for the target session
    behavior_ts : array-like
        Time series of behavioral variable for the target session
    behavior_ts_ensemble : array-like
        Collection of behavior time series from multiple sessions used to create
        the null distribution. Shape should be (n_sessions, max_timepoints)
    behavior_name : str
        Name of the behavioral variable being analyzed
    subsample_ensemble : int, optional
        If provided, randomly subsamples this many sessions from behavior_ts_ensemble
        to reduce computation time
        
    Returns
    -------
    float
        Percentile rank (0-100) of the target session's t-statistic within the null
        distribution. Values close to 0 or 100 indicate significant correlations.
        
    Examples
    --------
    >>> fr = [1.2, 3.4, 2.1, 4.5]
    >>> behavior = [0.1, 0.3, 0.2, 0.4]
    >>> behavior_null = np.random.rand(100, 4)  # 100 random sessions
    >>> percentile = session_permutation(fr, behavior, behavior_null, 'speed')
    >>> print(f"Percentile rank: {percentile}")
    
    Notes
    -----
    - The function assumes stationarity across sessions in the null distribution
    - Time series are truncated to match the shortest length between firing rate
      and behavior
    - The underlying linear regression is performed using statsmodels OLS
    """

    # calculate tvalue for the target session
    results_OLS = simple_LR(fr_ts, behavior_ts, behavior_name)
    tvalue_target = results_OLS.tvalues[behavior_name]
    
    # calculate ensemble of tvalues for null distribution
    tvalue_ensemble = []
    if subsample_ensemble is not None:
        idx = np.random.randint(len(behavior_ts_ensemble), size=subsample_ensemble)
        behavior_ts_ensemble = behavior_ts_ensemble[idx]
        
    for session_idx, behavior_ts in enumerate(behavior_ts_ensemble):
        # make sure both ts have same length
        min_session_len = min(len(fr_ts), len(behavior_ts))
        fr_ts = fr_ts[:min_session_len]
        behavior_ts = behavior_ts[:min_session_len]
        
        # OLS fit
        results_OLS = simple_LR(fr_ts, behavior_ts, behavior_name)
        tvalue_ensemble.append(results_OLS.tvalues[behavior_name])
        
    percentile = sc.stats.percentileofscore(tvalue_ensemble, tvalue_target)
    return percentile


def phase_randomization(
    fr_ts, 
    behavior_ts, 
    behavior_name, 
    ensemble_size=100
):
    """
    Performs statistical testing using phase randomization to assess the significance 
    of neural-behavioral correlations while preserving the power spectrum.
    
    This function creates a null distribution by phase-randomizing the firing rate 
    time series while maintaining its power spectrum, then computes correlation 
    statistics against the original behavioral time series.
    
    Parameters
    ----------
    fr_ts : array-like
        Time series of neural firing rates
    behavior_ts : array-like
        Time series of behavioral variable
    behavior_name : str
        Name of the behavioral variable being analyzed
    ensemble_size : int, optional (default=100)
        Number of phase-randomized time series to generate for null distribution
        
    Returns
    -------
    float
        Percentile rank (0-100) of the target correlation's t-statistic within 
        the null distribution of phase-randomized correlations
        
    Notes
    -----
    The phase randomization process:
    1. Computes FFT of the firing rate time series
    2. Preserves the power spectrum but randomizes the phase components
    3. Performs inverse FFT to generate surrogate time series
    4. Ensures non-negativity of the randomized firing rates
    """
    
    def phase_scrambled_ts(ts):
        """
        Generate a phase-randomized version of an input time series.
        
        Preserves the power spectrum of the original signal while randomizing 
        the phase components, creating a surrogate time series with similar 
        temporal structure but shuffled timing.
        
        Parameters
        ----------
        ts : array-like
            Input time series to be phase-randomized
            
        Returns
        -------
        array-like
            Phase-randomized version of the input time series
        
        Notes
        -----
        Process:
        1. Compute real FFT of time series
        2. Separate power and phase components
        3. Randomly shuffle phases while preserving power
        4. Reconstruct signal with inverse FFT
        """
        fs = rfft(ts)
        # rfft returns real and imaginary components in adjacent elements of a real array
        pow_fs = fs[1:-1:2]**2 + fs[2::2]**2
        phase_fs = np.arctan2(fs[2::2], fs[1:-1:2])
        phase_fsr = phase_fs.copy()
        np.random.shuffle(phase_fsr)
        
        # use broadcasting and ravel to interleave real and imaginary components
        # first and last elements in fourier array don't have phase information
        fsrp = np.sqrt(pow_fs[:, np.newaxis]) * np.c_[np.cos(phase_fsr), np.sin(phase_fsr)]
        fsrp = np.r_[fs[0], fsrp.ravel(), fs[-1]]
        tsr = irfft(fsrp)
        return tsr
    
    # calculate tvalue for the target session
    results_OLS = simple_LR(fr_ts, behavior_ts, behavior_name)
    tvalue_target = results_OLS.tvalues[behavior_name]
    
    # calculate ensemble of tvalues for null distribution
    tvalue_ensemble = []
    for randomize_id in range(ensemble_size):
        # generate phase randomized time series, make sure non-negative
        fr_phase_randomized = phase_scrambled_ts(fr_ts)
        fr_phase_randomized -= np.min(fr_phase_randomized)
        results_OLS = simple_LR(fr_phase_randomized, behavior_ts, behavior_name)
        tvalue_ensemble.append(results_OLS.tvalues[behavior_name])
        
    percentile = sc.stats.percentileofscore(tvalue_ensemble, tvalue_target)
    return percentile


def linear_shift(
    fr_ts, 
    behavior_ts, 
    behavior_name, 
    ensemble_size=100, 
    min_shift=3
):
    """
    Tests significance of neural-behavioral correlations using cyclic time shifts 
    of the behavioral time series.
    
    This function creates a null distribution by repeatedly shifting the behavioral 
    time series forward by random amounts and computing correlation statistics with 
    the original firing rate time series. This approach breaks temporal relationships 
    while preserving the behavioral time series' statistical properties.
    
    Parameters
    ----------
    fr_ts : array-like
        Time series of neural firing rates
    behavior_ts : array-like
        Time series of behavioral variable
    behavior_name : str
        Name of the behavioral variable being analyzed
    ensemble_size : int, optional (default=100)
        Number of shifted time series to generate for null distribution
    min_shift : int, optional (default=3)
        Minimum number of time points to shift the behavioral time series
        
    Returns
    -------
    float
        Percentile rank (0-100) of the target correlation's t-statistic within 
        the null distribution of shift-based correlations
        
    Notes
    -----
    The shifting process:
    1. Randomly selects a shift amount between min_shift and half the time series length
    2. Shifts behavioral time series forward by that amount
    3. Truncates both time series to match lengths
    4. Computes correlation statistics
    
    This method:
    - Preserves the temporal structure within each signal
    - Maintains behavioral time series statistics
    - Controls for spurious correlations while being computationally efficient
    - Assumes stationarity of the behavioral signal
    
    Examples
    --------
    >>> fr = np.array([1.2, 3.4, 2.1, 4.5, 3.2, 2.8])
    >>> behavior = np.array([0.1, 0.3, 0.2, 0.4, 0.3, 0.2])
    >>> percentile = linear_shift(fr, behavior, 'speed', ensemble_size=50)
    >>> print(f"Significance percentile: {percentile}")
    """

    # calculate tvalue for the target session
    results_OLS = simple_LR(fr_ts, behavior_ts, behavior_name)
    tvalue_target = results_OLS.tvalues[behavior_name]
    
    # calculate ensemble of tvalues for null distribution
    tvalue_ensemble = []
    for shift_id in range(ensemble_size):
        # generate linear shifted time series
        max_linear_shift = int(len(behavior_ts) / 2)
        shift_start_trial = np.random.randint(min_shift, high=max_linear_shift)
        behavior_ts_linear_shift = behavior_ts[shift_start_trial:]
        results_OLS = simple_LR(fr_ts[:len(behavior_ts_linear_shift)], 
                              behavior_ts_linear_shift, behavior_name)
        tvalue_ensemble.append(results_OLS.tvalues[behavior_name])
        
    percentile = sc.stats.percentileofscore(tvalue_ensemble, tvalue_target)
    return percentile


def cyclic_shift(
    fr_ts, 
    behavior_ts, 
    behavior_name, 
    ensemble_size=100, 
    min_shift=3
):
   """
   Tests significance of neural-behavioral correlations using cyclic permutations
   of the behavioral time series.
   
   This function creates a null distribution by repeatedly performing cyclic shifts
   of the behavioral time series and computing correlation statistics with the original 
   firing rate time series. Unlike linear shift, cyclic shift preserves the full 
   length of the time series by wrapping around.
   
   Parameters
   ----------
   fr_ts : array-like
       Time series of neural firing rates
   behavior_ts : array-like
       Time series of behavioral variable 
   behavior_name : str
       Name of the behavioral variable being analyzed
   ensemble_size : int, optional (default=100)
       Number of shifted time series to generate for null distribution
   min_shift : int, optional (default=3)
       Minimum number of time points to shift the behavioral time series to ensure
       sufficient temporal decorrelation
       
   Returns
   -------
   float
       Percentile rank (0-100) of the target correlation's t-statistic within 
       the null distribution of cyclically-shifted correlations
       
   Notes
   -----
   The cyclic shifting process:
   1. Randomly selects a shift amount between min_shift and length-min_shift
   2. Splits behavioral time series at that point
   3. Recombines the pieces in reversed order to create shifted series
   4. Maintains original time series length
   
   Advantages over linear shift:
   - Preserves complete behavioral time series structure
   - No data loss from truncation
   - Maintains exact length matching between signals
   - Better for periodic or continuous recordings
   
   Assumptions:
   - Behavioral signal is approximately stationary
   - Temporal correlations decay within min_shift time points
   - Time series endpoints are meaningfully related
   
   Examples
   --------
   >>> fr = np.array([1.2, 3.4, 2.1, 4.5, 3.2, 2.8])
   >>> behavior = np.array([0.1, 0.3, 0.2, 0.4, 0.3, 0.2])
   >>> percentile = cyclic_shift(fr, behavior, 'speed', ensemble_size=50)
   >>> print(f"Significance percentile: {percentile}")
   """

   # calculate tvalue for the target session
   results_OLS = simple_LR(fr_ts, behavior_ts, behavior_name)
   tvalue_target = results_OLS.tvalues[behavior_name]
   
   # calculate ensemble of tvalues for null distribution  
   tvalue_ensemble = []
   for shift_id in range(ensemble_size):
       # generate cyclic shifted time series
       shift_start_trial = np.random.randint(min_shift, high=len(behavior_ts)-min_shift)
       behavior_ts_cyclic_shift = np.concatenate((behavior_ts[shift_start_trial:],
                                                behavior_ts[:shift_start_trial]))
       results_OLS = simple_LR(fr_ts, behavior_ts_cyclic_shift, behavior_name)
       tvalue_ensemble.append(results_OLS.tvalues[behavior_name])
       
   percentile = sc.stats.percentileofscore(tvalue_ensemble, tvalue_target)
   return percentile


###########################################################################
### PARAMETRIC ERROR CORRECTION MODELS ###

def ARMA_model(
    fr_ts: Union[List[float], np.ndarray, pd.Series],
    behavior_ts: Union[List[Union[List[float], np.ndarray, pd.Series]], 
                       Dict[str, Union[List[float], np.ndarray, pd.Series]]],
    behavior_names: Optional[Union[str, List[str]]] = None,
    ar_order: int = 3,
    ma_order: int = 0,
    trend: str = 'ct'
) -> object:

    """
    Fit an ARMA (Autoregressive Moving Average) model to analyze the relationship 
    between neural firing rates and one or more behavioral variables while accounting 
    for temporal autocorrelation.
    
    This function fits an ARIMA(p,0,q) model (equivalent to ARMA) where the firing rate 
    is the endogenous variable and behaviors are exogenous regressors. The model accounts 
    for temporal dependencies in the firing rate time series.
    
    Parameters
    ----------
    fr_ts : array-like
        Time series of neural firing rates (endogenous variable).
        Can be a list, numpy array, or pandas Series.
    
    behavior_ts : array-like or dict
        Time series of exogenous variable(s). Can be:
        - Single array-like for one behavior
        - List of array-likes for multiple behaviors
        - Dict mapping behavior names to array-likes
    
    behavior_names : str, list of str, or None, optional
        Names of behavioral variables. Required if behavior_ts is a list.
        If behavior_ts is a dict, this parameter is ignored.
        If single behavior and str, uses that name.
        If None and single behavior, defaults to 'behavior'.
    
    ar_order : int, default=3
        Order of the autoregressive component (number of AR lags).
        Common neural time series often show autocorrelation up to 3 lags.
    
    ma_order : int, default=0
        Order of the moving average component (number of MA lags).
        Set to 0 for pure AR model, which is often sufficient for neural data.
    
    trend : str, default='ct'
        The trend to include in the model:
        - 'n' or 'nc': No deterministic trend
        - 'c': Constant only
        - 't': Linear time trend only
        - 'ct': Constant and linear time trend
    
    Returns
    -------
    results : ARIMAResults
        Fitted ARIMA model results containing:
        - Model coefficients (AR, MA, and behavioral regression parameters)
        - Standard errors and confidence intervals
        - Information criteria (AIC, BIC, HQIC)
        - Model diagnostics and residual analysis tools
    
    Raises
    ------
    ValueError
        If input time series are empty or have incompatible lengths.
        If behavior_names not provided when behavior_ts is a list.
        If number of behavior names doesn't match number of behavior time series.
        If time series is too short for the specified model order.
    
    Notes
    -----
    Model Specification:
    The ARMA(p,q) model with exogenous variables is:
    y_t = c + δt + Σ(φ_i * y_{t-i}) + Σ(θ_j * ε_{t-j}) + β'X_t + ε_t
    
    where:
    - y_t is the firing rate at time t
    - c is the constant term
    - δ is the time trend coefficient
    - φ_i are AR coefficients
    - θ_j are MA coefficients
    - β are regression coefficients for exogenous behaviors
    - X_t are exogenous behavioral variables
    - ε_t is white noise
    
    The function automatically aligns all time series to the shortest length.
    
    Model Selection Guidelines:
    - AR order: Start with 1-5 lags, use AIC/BIC for selection
    - MA order: Often 0-2 is sufficient for neural data
    - Check residual diagnostics to validate model adequacy
    
    Examples
    --------
    >>> import numpy as np
    >>> # Generate sample data
    >>> np.random.seed(42)
    >>> fr_data = np.cumsum(np.random.randn(100)) + 50
    >>> velocity_data = np.cumsum(np.random.randn(100)) + 10
    >>> acceleration_data = np.diff(np.concatenate([[0], velocity_data]))
    >>> 
    >>> # Example 1: Single behavior
    >>> results = fit_arma_model(
    ...     fr_data, 
    ...     velocity_data, 
    ...     'velocity',
    ...     ar_order=2,
    ...     ma_order=1
    ... )
    >>> 
    >>> # Example 2: Multiple behaviors with list
    >>> results = fit_arma_model(
    ...     fr_data,
    ...     [velocity_data, acceleration_data],
    ...     ['velocity', 'acceleration'],
    ...     ar_order=3
    ... )
    >>> 
    >>> # Example 3: Multiple behaviors with dict
    >>> results = fit_arma_model(
    ...     fr_data,
    ...     {'velocity': velocity_data, 'acceleration': acceleration_data},
    ...     ar_order=2,
    ...     ma_order=1
    ... )
    >>> 
    >>> # Print summary and check diagnostics
    >>> print(results.summary())
    >>> print(f"AIC: {results.aic:.2f}, BIC: {results.bic:.2f}")
    
    See Also
    --------
    statsmodels.tsa.arima.model.ARIMA : Underlying ARIMA model implementation
    """
    
    # Input validation
    if len(fr_ts) == 0:
        raise ValueError("Firing rate time series cannot be empty")
    
    # Convert fr_ts to numpy array
    fr_ts = np.asarray(fr_ts)
    
    # Handle different behavior_ts input formats
    behavior_dict = {}
    
    if isinstance(behavior_ts, dict):
        # Already in dict format
        behavior_dict = {k: np.asarray(v) for k, v in behavior_ts.items()}
        
    elif isinstance(behavior_ts, list) and len(behavior_ts) > 0:
        # Check if it's a list of time series or a single time series
        if isinstance(behavior_ts[0], (list, np.ndarray, pd.Series)):
            # List of multiple behaviors
            if behavior_names is None:
                raise ValueError("behavior_names must be provided when behavior_ts is a list of arrays")
            
            if isinstance(behavior_names, str):
                behavior_names = [behavior_names]
                
            if len(behavior_names) != len(behavior_ts):
                raise ValueError(f"Number of behavior names ({len(behavior_names)}) must match "
                               f"number of behavior time series ({len(behavior_ts)})")
            
            for name, ts in zip(behavior_names, behavior_ts):
                behavior_dict[name] = np.asarray(ts)
        else:
            # Single time series as list
            name = behavior_names if isinstance(behavior_names, str) else 'behavior'
            behavior_dict[name] = np.asarray(behavior_ts)
            
    else:
        # Single time series (array-like)
        name = behavior_names if isinstance(behavior_names, str) else 'behavior'
        behavior_dict[name] = np.asarray(behavior_ts)
    
    # Validate all behavior time series are non-empty
    for name, ts in behavior_dict.items():
        if len(ts) == 0:
            raise ValueError(f"Behavior time series '{name}' cannot be empty")
    
    # Find minimum length across all time series
    all_lengths = [len(fr_ts)] + [len(ts) for ts in behavior_dict.values()]
    min_session_len = min(all_lengths)
    
    # Check if time series is long enough for the model
    min_required_length = max(ar_order, ma_order) + 1
    if min_session_len < min_required_length:
        raise ValueError(
            f"Time series too short ({min_session_len} points) for "
            f"specified model order (AR={ar_order}, MA={ma_order}). "
            f"Need at least {min_required_length} points."
        )
    
    # Align all time series
    fr_ts_aligned = fr_ts[:min_session_len]
    behavior_dict_aligned = {name: ts[:min_session_len] for name, ts in behavior_dict.items()}
    
    # Create DataFrames for the model
    df_var_endo = pd.DataFrame({'fr': fr_ts_aligned})
    df_var_exog = pd.DataFrame(behavior_dict_aligned)
    
    # ARIMA order specification (p, d, q)
    arima_order = (ar_order, 0, ma_order)  # d=0 for ARMA
    
    # Fit ARIMA model
    try:
        model_ARMA = sm.tsa.arima.ARIMA(
            endog=df_var_endo,
            exog=df_var_exog,
            order=arima_order,
            trend=trend
        )
        results_ARMA = model_ARMA.fit()
        
    except Exception as e:
        raise RuntimeError(f"Failed to fit ARMA model: {str(e)}")
    
    return results_ARMA


def ARDL_model(
    fr_ts: Union[List[float], np.ndarray, pd.Series],
    behavior_ts: Union[List[Union[List[float], np.ndarray, pd.Series]], 
                       Dict[str, Union[List[float], np.ndarray, pd.Series]]],
    behavior_names: Optional[Union[str, List[str]]] = None,
    y_lags: Union[int, List[int]] = 5,
    x_order: Union[int, Dict[str, int]] = 0,
    trend: str = 'ct'
) -> object:

    """
    Fit an Autoregressive Distributed Lag (ARDL) model to analyze the relationship
    between a dependent variable (firing rate) and one or more exogenous variables (behaviors).
    
    The ARDL model captures both the autoregressive nature of the dependent variable
    and the distributed lag effects of the exogenous variables, making it suitable
    for analyzing dynamic relationships in time series data.
    
    Parameters
    ----------
    fr_ts : array-like
        Time series of the dependent variable (e.g., firing rate).
        Can be a list, numpy array, or pandas Series.
    
    behavior_ts : array-like or dict
        Time series of exogenous variable(s). Can be:
        - Single array-like for one behavior
        - List of array-likes for multiple behaviors
        - Dict mapping behavior names to array-likes
    
    behavior_names : str, list of str, or None, optional
        Names of behavioral variables. Required if behavior_ts is a list.
        If behavior_ts is a dict, this parameter is ignored.
        If single behavior and str, uses that name.
        If None and single behavior, defaults to 'behavior'.
    
    y_lags : int or list of int, default=5
        Number of lags to include for the dependent variable.
        If int, includes lags 1 to y_lags.
        If list, includes specific lags (e.g., [1, 2, 5]).
    
    x_order : int or dict, default=0
        Order of distributed lags for exogenous variables.
        If int, applies the same order to all exogenous variables.
        If dict, specifies order for each variable {behavior_name: order}.
    
    trend : {'n', 'c', 't', 'ct'}, default='ct'
        Trend to include in the model:
        - 'n': no trend
        - 'c': constant only
        - 't': time trend only
        - 'ct': constant and time trend
    
    Returns
    -------
    results : ARDLResults
        Fitted ARDL model results object containing parameter estimates,
        statistics, and methods for further analysis.
    
    Raises
    ------
    ValueError
        If input time series are empty or have incompatible lengths after alignment.
        If behavior_names not provided when behavior_ts is a list.
        If number of behavior names doesn't match number of behavior time series.
    
    Notes
    -----
    The function automatically aligns all time series to ensure equal length
    by truncating to the shortest series. This prevents errors from mismatched
    dimensions but may result in data loss if series lengths differ significantly.
    
    The ARDL(p, q1, q2, ..., qk) model with k exogenous variables is specified as:
    y_t = c + δt + Σ(φ_i * y_{t-i}) + Σ(β1_j * x1_{t-j}) + ... + Σ(βk_j * xk_{t-j}) + ε_t
    
    where:
    - p is the number of lags of the dependent variable (y_lags)
    - q1, ..., qk are the orders of distributed lags for each exogenous variable
    
    Examples
    --------
    >>> import numpy as np
    >>> # Generate sample data
    >>> np.random.seed(42)
    >>> fr_data = np.cumsum(np.random.randn(100)) + 50
    >>> velocity_data = np.cumsum(np.random.randn(100)) + 10
    >>> acceleration_data = np.diff(np.concatenate([[0], velocity_data]))
    >>> 
    >>> # Example 1: Single behavior
    >>> results = ARDL_model(
    ...     fr_data, 
    ...     velocity_data, 
    ...     'velocity',
    ...     y_lags=3,
    ...     x_order=2
    ... )
    >>> 
    >>> # Example 2: Multiple behaviors with list
    >>> results = ARDL_model(
    ...     fr_data,
    ...     [velocity_data, acceleration_data],
    ...     ['velocity', 'acceleration'],
    ...     y_lags=3,
    ...     x_order={'velocity': 2, 'acceleration': 1}
    ... )
    >>> 
    >>> # Example 3: Multiple behaviors with dict
    >>> results = ARDL_model(
    ...     fr_data,
    ...     {'velocity': velocity_data, 'acceleration': acceleration_data},
    ...     y_lags=3,
    ...     x_order=2  # Same order for all
    ... )
    """
    
    # Input validation
    if len(fr_ts) == 0:
        raise ValueError("Firing rate time series cannot be empty")
    
    # Convert fr_ts to numpy array
    fr_ts = np.asarray(fr_ts)
    
    # Handle different behavior_ts input formats
    behavior_dict = {}
    
    if isinstance(behavior_ts, dict):
        # Already in dict format
        behavior_dict = {k: np.asarray(v) for k, v in behavior_ts.items()}
        
    elif isinstance(behavior_ts, list) and len(behavior_ts) > 0:
        # Check if it's a list of time series or a single time series
        if isinstance(behavior_ts[0], (list, np.ndarray, pd.Series)):
            # List of multiple behaviors
            if behavior_names is None:
                raise ValueError("behavior_names must be provided when behavior_ts is a list of arrays")
            
            if isinstance(behavior_names, str):
                behavior_names = [behavior_names]
                
            if len(behavior_names) != len(behavior_ts):
                raise ValueError(f"Number of behavior names ({len(behavior_names)}) must match "
                               f"number of behavior time series ({len(behavior_ts)})")
            
            for name, ts in zip(behavior_names, behavior_ts):
                behavior_dict[name] = np.asarray(ts)
        else:
            # Single time series as list
            name = behavior_names if isinstance(behavior_names, str) else 'behavior'
            behavior_dict[name] = np.asarray(behavior_ts)
            
    else:
        # Single time series (array-like)
        name = behavior_names if isinstance(behavior_names, str) else 'behavior'
        behavior_dict[name] = np.asarray(behavior_ts)
    
    # Validate all behavior time series are non-empty
    for name, ts in behavior_dict.items():
        if len(ts) == 0:
            raise ValueError(f"Behavior time series '{name}' cannot be empty")
    
    # Find minimum length across all time series
    all_lengths = [len(fr_ts)] + [len(ts) for ts in behavior_dict.values()]
    min_session_len = min(all_lengths)
    
    if min_session_len < y_lags + 1:
        raise ValueError(
            f"Time series too short ({min_session_len} points) for "
            f"specified lag order ({y_lags} lags)"
        )
    
    # Align all time series
    fr_ts_aligned = fr_ts[:min_session_len]
    behavior_dict_aligned = {name: ts[:min_session_len] for name, ts in behavior_dict.items()}
    
    # Create DataFrames for the model
    df_var_endo = pd.DataFrame({'fr': fr_ts_aligned})
    df_var_exog = pd.DataFrame(behavior_dict_aligned)
    
    # Handle x_order parameter
    if isinstance(x_order, int):
        # Same order for all exogenous variables
        order_param = x_order
    else:
        # Dictionary specifying order per variable
        # Validate that all behavior names are in x_order
        missing_vars = set(behavior_dict.keys()) - set(x_order.keys())
        if missing_vars:
            raise ValueError(f"x_order dict missing specifications for: {missing_vars}")
        order_param = x_order
    
    # Fit ARDL model
    try:
        model_ARDL = ARDL(
            endog=df_var_endo,
            lags=y_lags,
            exog=df_var_exog,
            order=order_param,
            trend=trend
        )
        results_ARDL = model_ARDL.fit()
        
    except Exception as e:
        raise RuntimeError(f"Failed to fit ARDL model: {str(e)}")
    
    return results_ARDL