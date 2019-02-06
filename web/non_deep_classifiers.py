import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import StandardScaler
from scipy.spatial import distance

class Euclidean:
  
  def __init__(self):
    self.model = None
    self.auc_scores = []

  def train(self, train_data):
    self.model = train_data.mean().values

  def get_euclidean_distance(self, curr):
    currmean = curr.mean().values
    return distance.euclidean(self.model, currmean)
  
  def test(self, legitimate_data, imposter_data):
    scores_legitimate, scores_imposter = [], []
    
    for _, row in legitimate_data.iterrows():
      scores_legitimate.append(distance.euclidean(self.model, row.values))
    
    for _, row in imposter_data.iterrows():
      scores_imposter.append(distance.euclidean(self.model, row.values))

    return scores_legitimate, scores_imposter


class ScaledManhattan:
  
  def __init__(self):
    self.model = None
    self.auc_scores = []

  def train(self, train_data):
    self.model = train_data.mean().values
    self.mean_absolute_deviation = train_data.mad(axis = 0).values

  def get_scaled_manhattan_distance(self, curr):
    currmean = curr.mean().values
    return distance.cityblock(currmean, self.model) / self.mean_absolute_deviation[0]
  
  def test(self, legitimate_data, imposter_data):
    scores_legitimate, scores_imposter = [], []
    
    for _, row in legitimate_data.iterrows():
      score = 0
      for i in range(self.model.shape[0]):
        score += distance.cityblock(row.values[i], self.model[i]) / self.mean_absolute_deviation[i]
      scores_legitimate.append(score)
    
    for _, row in imposter_data.iterrows():
      score = 0
      for i in range(self.model.shape[0]):
        score += distance.cityblock(row.values[i], self.model[i]) / self.mean_absolute_deviation[i]
      scores_imposter.append(score)

    return scores_legitimate, scores_imposter


class NNMahalanobis:
  
  def __init__(self):
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
      scores_legitimate.append(self.get_nearest_neighbour_distance(legitimate_data.iloc[i].values))
        
    for i in range(len(imposter_data)):
      scores_imposter.append(self.get_nearest_neighbour_distance(imposter_data.iloc[i].values))

    return scores_legitimate, scores_imposter