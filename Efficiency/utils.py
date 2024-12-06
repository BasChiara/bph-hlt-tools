# utility function for  efficiency calculation
import json
import numpy as np

from scipy import stats

########################
# ----  FUNCTIONS ---- #
########################

def clopper_pearson(x, n, alpha=0.32, return_errors=True):
    """Estimate the confidence interval for binomial distributions.
    `x` is the number of successes and `n` is the number trials (x <=
    n). `alpha` is the confidence level (i.e., the true probability is
    inside the confidence interval with probability 1-alpha). The
    function returns a `(low, high)` pair of numbers indicating the
    interval on the probability.
    https://root.cern.ch/doc/master/classTEfficiency.html#ae80c3189bac22b7ad15f57a1476ef75b
    """
    b = stats.beta.ppf
    #if isinstance(x, np.ndarray):
    #    alpha = alpha*np.ones_like(x)
    ratio = x / n
    ratio = np.nan_to_num(ratio, nan=0)
    
    lo = b(alpha / 2, x, n - x + 1)
    hi = b(1 - alpha / 2, x + 1, n - x)
    if isinstance(x, np.ndarray):
        lo = np.nan_to_num(lo, nan=0)
        hi = np.nan_to_num(hi, nan=1)
        if return_errors:
            lo = ratio - lo
            hi = hi -ratio
            hi = np.where((ratio==0) & (hi>0.5), 0, hi )
        to_return = np.array([lo, hi])
    else:
        to_return = [0.0 if np.isnan(lo) else lo, 
                    1.0 if np.isnan(hi) else hi]
        if return_errors:
            to_return[0] = ratio - to_return[0]
            to_return[1] = to_return[1] -ratio
    return to_return

class npEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(npEncoder, self).default(obj)

def get_and_store(data, var, denQuery, numQuery, tagPath, probePath, Bins1d, input_file, outputdir, v_name=''):
        
    h_all      = np.histogram(data.query(denQuery)[var], bins=Bins1d[var])
    ccomplete_numQuery = denQuery
    if numQuery:
        ccomplete_numQuery += " & "+numQuery 
    ccomplete_numQuery+= f' & muProbe_{probePath}==1'
    h_passprob = np.histogram(data.query(ccomplete_numQuery)[var], 
                                bins=Bins1d[var])        
    ratio = h_passprob[0]/h_all[0]
    err  = clopper_pearson(h_passprob[0], h_all[0])
    
    efficiency_output = dict(
        Bins    = h_all[1],
        Passing = h_passprob[0],
        All     = h_all[0],
        Ratio   = ratio,
        Error   = err,
        Probe   = probePath,
        Tag     = tagPath,
        DenQuery= denQuery,
        NumQuery= numQuery,
        Var     = var,
        input   = input_file
    )
    v_name = f'_v{v_name}' if v_name else ''
    with open(f'{outputdir}/Efficiency1D_{var}{v_name}.json', 'w+') as jj:
        json.dump(efficiency_output, jj, indent=4, cls=npEncoder)
    
    return h_all[1], ratio, err