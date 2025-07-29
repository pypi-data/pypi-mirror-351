import os
from sys import exit

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.impute import KNNImputer
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import KBinsDiscretizer

from hyperimpute.plugins.imputers import Imputers

import pandas as pd
import numpy as np
from scipy.stats import norm, gaussian_kde
import matplotlib.pyplot as plt
from ..processing.utils import find_categorical_columns

from AutoImblearn.components.imputers import RunHyperImpute, RunSklearnImpute

# imps = ["MIRACLE"]
# imps = ["median", "knn", "ii", "gain", "MIRACLE", "MIWAE"]
imps = {
    # "dropna": RunSklearnImpute(model="dropna"),
    "median": RunSklearnImpute(model="median"),
    "mean": RunSklearnImpute(model="mean"),
    "knn": RunSklearnImpute(model="knn"),
    "ii": RunSklearnImpute(model="ii"),
    "gain": RunHyperImpute(model="gain"),
    "MIRACLE": RunHyperImpute(model="MIRACLE"),
    "MIWAE": RunHyperImpute(model="MIWAE"),
}

class CustomImputer(BaseEstimator, TransformerMixin):
    def __init__(self, method="median", aggregation=None):
        self.method = method

        if self.method in imps.keys():
            self.imp = imps[self.method]
            if not hasattr(self.imp, "data_folder_path"):
                raise Exception("Model {} does not have data_folder_path attribute".format(self.hbd))
            setattr(self.hbd, "data_folder_path", self.args.path)
        else:
            raise Exception("Model {} not defined in model.py".format(hbd))

        self.aggregation = aggregation

        self.data = None
        self.header_X = None
        self.feature2drop = []
        self.category_columns = None

    def fit(self, data: np.ndarray):
        self.imp.fit(data)

    def transform(self, data: np.ndarray) -> np.ndarray:
        self.imp.transform(data)

    def fit_transform(self, data: np.ndarray) -> np.ndarray:
        self.fit(data)
        data = self.transform(data)
        return data



class _CustomImputer(BaseEstimator, TransformerMixin):
    def __init__(self, method="median", aggregation=None):
        self.method = method
        self.aggregation = aggregation

        self.data = None
        self.header_X = None
        self.feature2drop = []
        self.category_columns = None

    def apply_rounding(self):
        # Add rounding to categorical features after imputation
        self.category_columns = [i for i in self.category_columns if i in self.data.columns.values]
        for column in self.category_columns:
            self.data[column] = self.data[column].round(0)

    def handle_missing(self):
        # Apply imputation to data
        if self.method == "dropna":
            self.data.dropna(inplace=True)

        elif self.method == "median":
            medians = self.data.median()
            self.data = self.data.fillna(medians)

        elif self.method == "mean":
            means = self.data.mean()
            self.data = self.data.fillna(means)

        elif self.method == "knn":
            data_file_name = "knnimputer.csv"
            file_path = os.path.join("../..", "data", "interim", data_file_name)
            if os.path.isfile(file_path):
                self.data[:] = pd.read_csv(file_path)
            else:
                impute = KNNImputer(weights='distance', n_neighbors=1)
                self.data[:] = impute.fit_transform(self.data)
                self.apply_rounding()
                del impute

        elif self.method == "ii":
            data_file_name = "iiimputer.csv"
            file_path = os.path.join("../..", "data", "interim", data_file_name)
            if os.path.isfile(file_path):
                self.data[:] = pd.read_csv(file_path)
            else:
                impute = IterativeImputer(
                )
                self.data[:] = impute.fit_transform(self.data)
                self.apply_rounding()
                del impute

        elif self.method in ['gain', 'MIRACLE']:
            dict_types = dict(self.data.dtypes)
            old_columns = self.data.columns.values

            impute = Imputers().get(self.method.lower())
            self.data = impute.fit_transform(self.data.astype('float32').copy())
            # Change back to old column names
            rename_dict = dict(map(lambda i, j: (i, j), self.data.columns.values, old_columns))
            self.data.rename(rename_dict, axis=1, inplace=True)

            # Change back to old column dtypes
            self.data = self.data.astype(dict_types)
            self.apply_rounding()
            del impute

        elif self.method in ['MIWAE']:
            dict_types = dict(self.data.dtypes)
            old_columns = self.data.columns.values

            impute = Imputers().get(self.method.lower(), random_state=42, batch_size = 128)
            self.data = impute.fit_transform(self.data.astype('float32').copy())
            # Change back to old column names
            rename_dict = dict(map(lambda i, j: (i, j), self.data.columns.values, old_columns))
            self.data.rename(rename_dict, axis=1, inplace=True)

            # Change back to old column dtypes
            self.data = self.data.astype(dict_types)
            self.apply_rounding()
            del impute

        else:
            raise Exception("Error with handling missing value")

    def find_categorical(self, X: pd.DataFrame):
        """ Predict which columns are categorical """
        self.category_columns = find_categorical_columns(X).keys()
        # self.category_columns = []
        # # TODO make this one a feature
        # categorical_threshold = 0.5
        # for feature_name in X.columns.values:
        #     is_categorical = True
        #     # Calculate the derivatives in the Probability Density Function (PDF)
        #     feature = X[feature_name]
        #     unique_values = np.unique(feature)
        #     unique_count = len(unique_values)
        #
        #     # delete empty value from unique_count
        #     if np.isnan(unique_values).any():
        #         unique_count -= 1
        #
        #     # skip binary features
        #     if unique_count == 2:
        #         continue
        #
        #     total_count = feature.shape[0]
        #
        #     # TODO make the second condition a parameter
        #     if unique_count / total_count < 0.05 and unique_count < 20:
        #         self.category_columns.append(feature_name)
        #         continue
        #
        #     # Find unique value count
        #     # feature_min = feature.min()
        #     # feature_max = feature.max()
        #     # x_values = np.linspace(feature_min, feature_max, 1000)
        #     # kde_values = sum(norm(xi).pdf(x_values) for xi in feature)
        #     kde = gaussian_kde(feature)
        #
        #     x_values = np.linspace(feature.min(), feature.max(), 1000)
        #     kde_values = kde(x_values)
        #
        #     # df data structure: [feature value range, value kde_values, derivative]
        #     df = pd.DataFrame(np.transpose(np.vstack((x_values, kde_values))), columns=['X', 'y'])
        #     df = df.assign(derivative=df.diff().eval('y/X'))
        #
        #     max_density = df['y'].max()
        #
        #     # Find where the local minimal is in the PDF
        #     trough_points = []  # trough_points stores the 'major' trough points of PDF
        #     crest_points = []   # crest_points stores the all crest points of PDF
        #
        #     derivative = df['derivative']
        #     for i in range(len(derivative) - 1):
        #         previous_state = derivative[i]
        #         current_state = derivative[i+1]
        #         if current_state * previous_state <= 0 and previous_state < 0:
        #             # if df['y'].iat[i] - feature_min < categorical_threshold * (feature_max - feature_min):
        #             if max_density - df['y'].iat[i] > categorical_threshold * max_density:
        #                 trough_points.append(i)
        #         elif current_state * previous_state <= 0 and previous_state > 0:
        #             crest_points.append(i)
        #
        #     if not trough_points or not is_categorical:
        #         continue
        #
        #     # shrink the size of the major trough points
        #     index = 0
        #     back = None
        #     front = 0
        #     edges = []
        #     for i in range(len(trough_points) - 1):
        #         trough = df['y'].iat[trough_points[i]]
        #         # find the largest crest before point 'i'
        #         end = trough_points[i]
        #         if back is None:
        #             back = 0
        #             while crest_points[index] < end:
        #                 tmp = df['y'].iat[crest_points[index]]
        #                 if tmp > back:
        #                     back = tmp
        #                 index += 1
        #
        #         # find the largest crest after point 'i'
        #         if i == len(trough_points)-1:
        #             end = len(x_values)
        #         else:
        #             end = trough_points[i + 1]
        #
        #         while index < len(crest_points) and crest_points[index] < end:
        #             tmp = df['y'].iat[crest_points[index]]
        #             if tmp > front:
        #                 front = tmp
        #             index += 1
        #
        #         # TODO determine if treat the 0.3 threshold as parameter
        #         if abs(front - trough) > 0.3 * max_density or abs(back - trough) > 0.3 * max_density:
        #             edges.append(df['X'].iat[trough_points[i]])
        #
        #         back = front
        #         front = 0
        #
        #     if len(edges) < 1:
        #         continue
        #
        #     use_KBinsDiscretizer = True
        #     if use_KBinsDiscretizer:
        #         discretizer = KBinsDiscretizer(n_bins=len(edges) + 1, encode='ordinal', strategy='kmeans')
        #         enc = discretizer.fit_transform(feature.to_numpy().reshape(-1, 1)).reshape(1, -1)[0]
        #         X[feature_name] = pd.Series(enc)
        #     else:
        #         def convert2cal(x, edges):
        #             result = 0
        #             while result < len(edges):
        #                 if x <= edges[result]:
        #                     break
        #                 result += 1
        #             return result
        #
        #         X[feature_name] = X[feature_name].map(lambda x: convert2cal(x, edges))
        #
        #     self.category_columns.append(feature_name)
        #
        #     ### Plot the Probability Density Function (PDF)
        #     # plt.fill_between(x_values, kde_values, alpha=0.5)
        #     # plt.plot(feature, np.full_like(feature, -0.1), '|k', markeredgewidth=1)
        #     # plt.show()
        # return self.category_columns

    def transform_categorical(self, columns=None):
        if columns is not None:
            self.category_columns = columns

        # Transform the categorical
        self.category_columns = [i for i in self.category_columns if i in self.data.columns.values]

        self.data = pd.get_dummies(data=self.data, columns=self.category_columns)

    # def data_scaling(self):
    #     """ Scale Features """
    #     min_max_columns = [
    #     min_max_columns = [item for item in min_max_columns if item in self.data.columns.values]
    #
    #     self.data[min_max_columns] = MinMaxScaler().fit_transform(self.data[min_max_columns])
    def data_scaling(self):
        """ Scale Features """
        min_max_columns = [item for item in self.data.columns.values if item not in self.category_columns]

        self.data[min_max_columns] = MinMaxScaler().fit_transform(self.data[min_max_columns])

    def data_aggregation(self):
        # Transform pandas columns with only 2 unique string values to 0 and 1
        for column in self.data.columns:
            unique_values = pd.Series(self.data[column].unique()).dropna()

            # Check if the column has exactly two unique string values
            if len(unique_values) == 2 and self.data[column].dtype == 'object':
                # Map the two unique values to 0 and 1
                mapping = {unique_values[0]: 0, unique_values[1]: 1}
                self.data[column] = self.data[column].map(mapping)

    def fit(self, X, y = None):
        self.data = X
        return self

    def transform(self, X):
        # Predict which columns are categorical
        self.find_categorical(X)

        self.data_aggregation()

        self.transform_categorical()

        self.handle_missing()

        # Scale data to the same interval
        self.data_scaling()

        self.header_X = self.data.columns.values

        return self.data
