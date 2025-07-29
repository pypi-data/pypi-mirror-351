from typing import List
import numpy as np
from jax import vmap, numpy as jnp, scipy as jsp
from functools import partial
from .probability import GammaDistribution, NormalDistribution, NumericalDistribution, _convolve_numerical

LOG_ZERO = -100.0 # exp(-100) = 3.7e-44 is a good approximation of zero in a PDF

def convert_GeneralGammaDistributionPositive(a, loc, scale, gaussian_standard_deviation):
    loc_scaled = loc/scale
    if gaussian_standard_deviation == 0:
        distribution_type = 'GammaDistributionPositive'
        parameters = {'a': a, 'loc': loc_scaled, 'scale': 1}
    else:
        distribution_type = 'NumericalDistribution'
        gamma_unscaled = GammaDistribution(a = a, loc = loc_scaled, scale = 1)
        norm_bg = NormalDistribution(0, gaussian_standard_deviation)
        numerical = [NumericalDistribution.from_pd(p, nsteps=1000) for p in [gamma_unscaled, norm_bg]]
        num_unscaled = _convolve_numerical(numerical, central_values='sum')
        x = np.array(num_unscaled.x)
        y = np.array(num_unscaled.y_norm)
        if loc_scaled in x:
            to_mirror = y[x<=loc_scaled][::-1]
            y_pos = y[len(to_mirror)-1:len(to_mirror)*2-1]
            y[len(to_mirror)-1:len(to_mirror)*2-1] += to_mirror[:len(y_pos)]
        else:
            to_mirror = y[x<loc_scaled][::-1]
            y_pos = y[len(to_mirror):len(to_mirror)*2]
            y[len(to_mirror):len(to_mirror)*2] += to_mirror[:len(y_pos)]
        y = y[x >= 0]
        x = x[x >= 0]
        if x[0] != 0:  #  make sure the PDF at 0 exists
            x = np.insert(x, 0, 0.)  # add 0 as first element
            y = np.insert(y, 0, y[0])  # copy first element
        x = x * scale
        y = np.maximum(0, y)  # make sure PDF is positive
        y = y /  np.trapz(y, x=x)  # normalize PDF to 1
        # ignore warning from log(0)=-np.inf
        with np.errstate(divide='ignore', invalid='ignore'):
            log_y = np.log(y)
        # replace -np.inf with a large negative number
        log_y[np.isneginf(log_y)] = LOG_ZERO
        parameters = {
            'x': x,
            'y': y,
            'log_y': log_y,
            'central_value': loc,
        }
    return distribution_type, parameters

interp_log_pdf = partial(jnp.interp, left=LOG_ZERO, right=LOG_ZERO)

def logpdf_numerical_distribution(
        predictions: jnp.array,
        selector_matrix: jnp.array,
        observable_indices: jnp.array,
        x: jnp.array,
        log_y: jnp.array,
    ) -> jnp.array:
    logpdf_total = jnp.zeros_like(predictions)
    predictions = jnp.take(predictions, observable_indices)
    logpdf = vmap(interp_log_pdf)(predictions, x, log_y)
    logpdf_total = logpdf_total.at[observable_indices].add(logpdf)
    return selector_matrix @ logpdf_total

def logpdf_normal_distribution(
        predictions: jnp.array,
        selector_matrix: jnp.array,
        observable_indices: jnp.array,
        mean: jnp.array,
        std: jnp.array,
    ) -> jnp.array:
    logpdf_total = jnp.zeros_like(predictions)
    predictions = jnp.take(predictions, observable_indices)
    logpdf = jsp.stats.norm.logpdf(predictions, loc=mean, scale=std)
    logpdf_total = logpdf_total.at[observable_indices].add(logpdf)
    return selector_matrix @ logpdf_total

def logpdf_folded_normal_distribution(
        predictions: jnp.array,
        selector_matrix: jnp.array,
        observable_indices: jnp.array,
        mean: jnp.array,
        std: jnp.array,
    ) -> jnp.array:
    logpdf_total = jnp.zeros_like(predictions)
    predictions = jnp.take(predictions, observable_indices)
    folded_logpdf = jnp.log(
        jsp.stats.norm.pdf(predictions, loc=mean, scale=std)
        + jsp.stats.norm.pdf(predictions, loc=-mean, scale=std)
    )
    logpdf = jnp.where(predictions >= 0, folded_logpdf, LOG_ZERO)
    logpdf_total = logpdf_total.at[observable_indices].add(logpdf)
    return selector_matrix @ logpdf_total

def logpdf_half_normal_distribution(
        predictions: jnp.array,
        selector_matrix: jnp.array,
        observable_indices: jnp.array,
        std: jnp.array,
    ) -> jnp.array:
    return logpdf_folded_normal_distribution(predictions, selector_matrix, observable_indices, 0, std)

def logpdf_gamma_distribution_positive(
        predictions: jnp.array,
        selector_matrix: jnp.array,
        observable_indices: jnp.array,
        a: jnp.array,
        loc: jnp.array,
        scale: jnp.array,
    ) -> jnp.array:
    logpdf_total = jnp.zeros_like(predictions)
    predictions = jnp.take(predictions, observable_indices)
    log_pdf_scale = jnp.log(1/(1-jsp.stats.gamma.cdf(0, a, loc=loc, scale=scale)))
    positive_logpdf = jsp.stats.gamma.logpdf(
        predictions, a, loc=loc, scale=scale
    ) + log_pdf_scale
    logpdf = jnp.where(predictions>=0, positive_logpdf, LOG_ZERO)
    logpdf_total = logpdf_total.at[observable_indices].add(logpdf)
    return selector_matrix @ logpdf_total

def logpdf_multivariate_normal_distribution(
    predictions: jnp.array,
    selector_matrix: jnp.array,
    observable_indices: List[jnp.array],
    mean: List[jnp.array],
    standard_deviation: List[jnp.array],
    inverse_correlation: List[jnp.array],
    logpdf_normalization_per_observable: List[jnp.array],
) -> jnp.array:
    logpdf_rows = []
    for i in range(len(observable_indices)):
        d = (jnp.take(predictions, observable_indices[i]) - mean[i]) / standard_deviation[i]
        n_obs = d.shape[0]
        logpdf = -0.5 * jnp.dot(d, jnp.dot(inverse_correlation[i], d)) + n_obs * logpdf_normalization_per_observable[i]
        logpdf_rows.append(logpdf)
    logpdf_total = jnp.stack(logpdf_rows)
    return selector_matrix @ logpdf_total

logpdf_functions = {
    'NumericalDistribution': logpdf_numerical_distribution,
    'NormalDistribution': logpdf_normal_distribution,
    'HalfNormalDistribution': logpdf_half_normal_distribution,
    'GammaDistributionPositive': logpdf_gamma_distribution_positive,
    'MultivariateNormalDistribution': logpdf_multivariate_normal_distribution,
}

def coeff_cov_to_obs_cov(par_monomials, cov_th_scaled): # TODO (maybe) optimize
    n_sectors = len(par_monomials)

    cov = np.empty((n_sectors,n_sectors), dtype=object).tolist()

    for i in range(n_sectors):
        for j in range(n_sectors):
            if i>= j:
                cov[i][j] = jnp.einsum('ijkl,k,l->ij',cov_th_scaled[i][j],par_monomials[i],par_monomials[j])
            else:
                shape = cov_th_scaled[j][i].shape
                cov[i][j] = jnp.zeros((shape[1], shape[0]))
    cov_matrix_tril = jnp.tril(jnp.block(cov))
    return cov_matrix_tril + cov_matrix_tril.T - jnp.diag(jnp.diag(cov_matrix_tril))

def logpdf_correlated_sectors(
    predictions_scaled: jnp.array,
    std_sm_exp: jnp.array,
    selector_matrix: jnp.array,
    observable_indices: List[jnp.array],
    exp_central_scaled: jnp.array,
    cov_matrix_exp: jnp.array,
    cov_matrix_th: jnp.array,
) -> jnp.array:

    cov = cov_matrix_th + cov_matrix_exp
    std = jnp.sqrt(jnp.diag(cov))
    std_norm = std  * std_sm_exp
    C = cov / jnp.outer(std, std)
    D = (predictions_scaled - exp_central_scaled)/std

    logpdf_rows = []
    for i in range(len(observable_indices)):

        d = jnp.take(D, observable_indices[i])
        c = jnp.take(jnp.take(C, observable_indices[i], axis=0), observable_indices[i], axis=1)

        logdet_corr = jnp.linalg.slogdet(c)[1]
        logprod_std2 = 2 * jnp.sum(jnp.log(jnp.take(std_norm, observable_indices[i])))

        logpdf = -0.5 * (
            jnp.dot(d, jsp.linalg.cho_solve(jsp.linalg.cho_factor(c), d))
            + logdet_corr
            + logprod_std2
            + len(d) * jnp.log(2 * jnp.pi)
        )
        logpdf = jnp.where(jnp.isnan(logpdf), -len(d)*100., logpdf)
        logpdf_rows.append(logpdf)
    logpdf_total = jnp.array(logpdf_rows)
    return selector_matrix @ logpdf_total
