"""Published open-set scores on window features.

Mahalanobis: minimum class-conditional squared distance in a PCA subspace
with one shrinkage covariance shared by the known classes (Lee et al., 2018).
Energy: negative log-sum-exp of multinomial-logistic logits in that same
subspace (Liu et al., 2020). Higher means less like the accidents used to fit
the score. The subspace rank is fixed from the training-sample size; it is
not chosen using the held-out accident type.
"""
import numpy as np
from sklearn.covariance import LedoitWolf
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

KINDS = ("mahalanobis", "energy")


def upper_threshold(scores, alpha):
    """Smallest score that leaves about `alpha` of the calibration scores strictly above it."""
    s = np.sort(np.asarray(scores, float))
    n = len(s)
    if n == 0:
        raise ValueError("calibration scores are empty")
    k = min(int(np.ceil((n + 1) * (1.0 - alpha))), n)
    return float(s[k - 1])


def auroc(score_unknown, score_known):
    labels = np.concatenate([np.ones(len(score_unknown)), np.zeros(len(score_known))])
    values = np.concatenate([np.asarray(score_unknown, float), np.asarray(score_known, float)])
    return float(roc_auc_score(labels, values))


def _project(train, queries, n_components):
    rank = min(int(n_components), train.shape[0] - 1, train.shape[1])
    if rank < 1:
        raise ValueError("not enough training rows to fit a subspace")
    pca = PCA(n_components=rank, random_state=0).fit(train)
    return pca.transform(train), [pca.transform(q) for q in queries]


def _precision(centered):
    if len(centered) > centered.shape[1] + 1:
        return LedoitWolf().fit(centered).precision_
    cov = np.cov(centered, rowvar=False)
    if cov.ndim == 0:
        cov = np.array([[float(cov)]])
    cov = cov + 1e-6 * np.eye(cov.shape[0])
    return np.linalg.pinv(cov)


def _mahalanobis_fn(z_train, y_train):
    classes = np.unique(y_train)
    means, parts = [], []
    for c in classes:
        block = z_train[y_train == c]
        mu = block.mean(axis=0)
        means.append(mu)
        parts.append(block - mu)
    precision = _precision(np.vstack(parts))
    means = np.stack(means)

    def score(z):
        diff = z[:, None, :] - means[None, :, :]
        squared = np.einsum("ncd,de,nce->nc", diff, precision, diff)
        return np.min(np.maximum(squared, 0.0), axis=1)

    return score


def _energy_from_logits(logits):
    if logits.ndim == 1:
        logits = np.column_stack((-logits, logits))
    peak = np.max(logits, axis=1, keepdims=True)
    return -(peak.ravel() + np.log(np.exp(logits - peak).sum(axis=1)))


def _energy_fn(z_train, y_train):
    model = LogisticRegression(max_iter=2000, random_state=0)
    model.fit(z_train, y_train)

    def score(z):
        return _energy_from_logits(model.decision_function(z))

    return score


def scores(features_train, labels_train, queries, kind, n_components=10):
    """Fit `kind` on the training runs and score each query matrix."""
    if kind not in KINDS:
        raise ValueError(kind)
    labels = np.asarray(labels_train)
    z_train, projected = _project(features_train, queries, n_components)
    score_fn = _mahalanobis_fn(z_train, labels) if kind == "mahalanobis" else _energy_fn(z_train, labels)
    return [score_fn(z) for z in projected]
