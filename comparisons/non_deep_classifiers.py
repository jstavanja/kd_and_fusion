import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, auc
from scipy.spatial import distance

data_path = './DSL-StrongPasswordData.csv'


def main():
    n_samples_for_testing_on_imposters = 250

    used_features = [
        'H',
        'DD',
        'UD',
    ]

    models = [
        Euclidean(),
        ScaledManhattan(),
        Ratio()

        # NNMahalanobis() # NOTE: this is incorrect and performs bad
    ]

    print("\nAUC scores:", [(model.__class__.__name__, get_score(
        model, n_samples_for_testing_on_imposters, used_features)) for model in models])


def get_AUC(scores_legitimate, scores_imposter):
    labels = np.append(np.full(len(scores_legitimate), 0),
                       np.full(len(scores_imposter), 1))
    fpr, tpr, _ = roc_curve(
        labels, scores_legitimate + scores_imposter)

    return auc(fpr, tpr)


def get_score(model, test_sample, used_features):
    if len(used_features) == 0:
        raise Exception('No features specified for calculation.')

    header = list(model.data.loc[:, "H.period":"H.Return"])
    new_header = list()
    for feature in used_features:
        temp = filter((lambda x: x.startswith(feature)), header)
        new_header += temp

    print("\n------- Evaluating", model.__class__.__name__, "classifier. -------")
    print("------- Features used:", used_features, "-------\n")

    for subject in model.subjects:
        print("Subject: ", subject, "of", len(model.subjects))
        current_subject_data = model.data.loc[model.data.subject == subject, :]
        current_subject_data = current_subject_data[new_header]

        imposters_data = model.data.loc[model.data.subject != subject, :].sample(
            n=test_sample)
        imposters_data = imposters_data[new_header]

        # we take 3/4 of the subjects dataset for training
        model.train(current_subject_data[:200])
        # and 1/4 of legitimate data and all of the imposter data for testing
        scores_legitimate, scores_imposter = model.test(
            current_subject_data[200:], imposters_data)

        model.auc_scores.append(
            get_AUC(scores_legitimate, scores_imposter))
    return np.mean(model.auc_scores)


class Euclidean:

    def __init__(self):
        self.data = pd.read_csv(data_path)
        self.subjects = self.data["subject"].unique()
        self.model = None
        self.auc_scores = []

    def train(self, train_data):
        self.model = train_data.mean().values

    def test(self, legitimate_data, imposter_data):
        scores_legitimate, scores_imposter = [], []

        for _, row in legitimate_data.iterrows():
            scores_legitimate.append(
                distance.euclidean(self.model, row.values))

        for _, row in imposter_data.iterrows():
            scores_imposter.append(distance.euclidean(self.model, row.values))

        return scores_legitimate, scores_imposter


class ScaledManhattan:

    def __init__(self):
        self.data = pd.read_csv(data_path)
        self.subjects = self.data["subject"].unique()
        self.model = None
        self.auc_scores = []

    def train(self, train_data):
        self.model = train_data.mean().values
        self.mean_absolute_deviation = train_data.mad(axis=0).values

    def test(self, legitimate_data, imposter_data):
        scores_legitimate, scores_imposter = [], []

        for _, row in legitimate_data.iterrows():
            score = 0
            for i in range(self.model.shape[0]):
                score += distance.cityblock(
                    row.values[i], self.model[i]) / self.mean_absolute_deviation[i]
            scores_legitimate.append(score)

        for _, row in imposter_data.iterrows():
            score = 0
            for i in range(self.model.shape[0]):
                score += distance.cityblock(
                    row.values[i], self.model[i]) / self.mean_absolute_deviation[i]
            scores_imposter.append(score)

        return scores_legitimate, scores_imposter


class NNMahalanobis:

    def __init__(self):
        self.data = pd.read_csv(data_path)
        self.subjects = self.data["subject"].unique()
        self.model = None
        self.auc_scores = []

    def train(self, train_data):
        self.model = train_data
        self.covariance_matrix = self.model.cov().values
        self.inverse_covariance_matrix = np.linalg.inv(np.cov(self.model.T))

    def get_mahalanobis(self, diff):
        return np.dot(np.dot(diff.T, self.inverse_covariance_matrix), diff)

    def get_nearest_neighbour_distance(self, vector):
        return min(
            [self.get_mahalanobis(vector - self.model.iloc[i])
             for i in range(self.model.shape[0])]
        )

    def test(self, legitimate_data, imposter_data):
        scores_legitimate, scores_imposter = [], []

        for i in range(len(legitimate_data)):
            scores_legitimate.append(self.get_nearest_neighbour_distance(
                legitimate_data.iloc[i].values))

        for i in range(len(imposter_data)):
            scores_imposter.append(self.get_nearest_neighbour_distance(
                imposter_data.iloc[i].values))

        return scores_legitimate, scores_imposter


class Ratio:

    def __init__(self):
        self.data = pd.read_csv(data_path)
        self.subjects = self.data["subject"].unique()
        self.model = None
        self.auc_scores = []

    def train(self, train_data):
        self.model = train_data.mean().values

    def get_match_ratio(self, curr):
        matches = [max(a, b) / min(a, b)
                   for (a, b) in np.stack((self.model, curr), axis=-1)]
        return np.mean(matches)

    def test(self, legitimate_data, imposter_data):
        scores_legitimate, scores_imposter = [], []

        for _, row in legitimate_data.iterrows():
            scores_legitimate.append(self.get_match_ratio(row.values))

        for _, row in imposter_data.iterrows():
            scores_imposter.append(self.get_match_ratio(row.values))

        return scores_legitimate, scores_imposter


if __name__ == '__main__':
    main()
