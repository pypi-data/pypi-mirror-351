from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self, n_estimators=100, contamination=0.1):
        self.model = IsolationForest(n_estimators=n_estimators, contamination=contamination)

    def fit(self, X):
        self.model.fit(X)

    def predict(self, X):
        return self.model.predict(X)

    def anomaly_scores(self, X):
        return self.model.decision_function(X)
