"""What the operator display shows for one window, from the prediction set."""


def policy(pred_set, names):
    k = len(pred_set)
    if k == 0:
        return {"mode": "NO_MATCH", "text": "Pattern not recognised - follow procedures, do not rely on automated diagnosis"}
    if k == 1:
        return {"mode": "SINGLE", "text": f"Likely: {names[pred_set[0]]} (certified set)"}
    return {"mode": "CANDIDATES", "text": "Candidates: " + ", ".join(names[i] for i in pred_set)}
