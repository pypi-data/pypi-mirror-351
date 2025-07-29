import pandas as pd
import numpy as np
from scipy import stats
from .stats_advisor import StatsAdvisor
from .visualizer import Visualizer

class OutlierDetector:
    """
    Detect and handle outliers with statistical methods and visualization
    """

    def __init__(self, df):
        self.df = df.copy()
        self.advisor = StatsAdvisor()
        self.visualizer = Visualizer()

    def detect_outliers(self, method='iqr', threshold=1.5):
        """
        Detect outliers using specified method

        Parameters:
        -----------
        method : str
            'iqr' - Interquartile Range
            'zscore' - Z-score method
            'modified_zscore' - Modified Z-score
            'percentile' - Percentile based
        threshold : float
            Threshold for outlier detection
        """
        outlier_report = {}

        numeric_cols = self.df.select_dtypes(include=['float64', 'int64']).columns

        for col in numeric_cols:
            data = self.df[col].dropna()
            outliers_series = pd.Series(index=self.df.index, data=False) # Use a different variable name

            if method == 'iqr':
                if len(data) < 2: # Handle cases with insufficient data
                    outliers_count = 0
                    outliers_percentage = 0.0
                    outlier_indices = []
                else:
                    q1 = data.quantile(0.25)
                    q3 = data.quantile(0.75)
                    iqr = q3 - q1
                    lower_bound = q1 - threshold * iqr
                    upper_bound = q3 + threshold * iqr
                    outliers_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
                    outliers_series = outliers_mask.fillna(False) # Handle potential NaNs in original col
                    outliers_count = outliers_series.sum()
                    outliers_percentage = outliers_series.mean() * 100
                    outlier_indices = self.df[outliers_series].index.tolist()

            elif method == 'zscore':
                 if len(data) == 0 or data.std() == 0: # Handle edge cases for z-score
                     outliers_count = 0
                     outliers_percentage = 0.0
                     outlier_indices = []
                 else:
                    # Align z_scores with the original index
                    z_scores = pd.Series(np.abs(stats.zscore(data)), index=data.index)
                    outliers_mask = z_scores > threshold
                    outliers_series[outliers_mask.index] = outliers_mask # Assign back to original index
                    outliers_count = outliers_series.sum()
                    outliers_percentage = outliers_series.mean() * 100
                    outlier_indices = self.df[outliers_series].index.tolist()


            elif method == 'modified_zscore':
                if len(data) == 0 or np.median(np.abs(data - np.median(data))) == 0: # Handle edge cases
                    outliers_count = 0
                    outliers_percentage = 0.0
                    outlier_indices = []
                else:
                    median = np.median(data)
                    mad = np.median(np.abs(data - median))
                    modified_z_scores = 0.6745 * (data - median) / mad
                    # Align modified_z_scores with the original index
                    mod_z_series = pd.Series(np.abs(modified_z_scores), index=data.index)
                    outliers_mask = mod_z_series > threshold
                    outliers_series[outliers_mask.index] = outliers_mask # Assign back to original index
                    outliers_count = outliers_series.sum()
                    outliers_percentage = outliers_series.mean() * 100
                    outlier_indices = self.df[outliers_series].index.tolist()


            elif method == 'percentile':
                if len(data) < 2: # Handle cases with insufficient data
                    outliers_count = 0
                    outliers_percentage = 0.0
                    outlier_indices = []
                else:
                    lower_bound = data.quantile((1 - threshold)/2)
                    upper_bound = data.quantile(1 - (1 - threshold)/2)
                    outliers_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
                    outliers_series = outliers_mask.fillna(False) # Handle potential NaNs in original col
                    outliers_count = outliers_series.sum()
                    outliers_percentage = outliers_series.mean() * 100
                    outlier_indices = self.df[outliers_series].index.tolist()

            # Explicitly convert to standard Python types
            outlier_report[col] = {
                'outliers': int(outliers_count),
                'percentage': float(outliers_percentage),
                'indices': outlier_indices,
                'method': method,
                'threshold': threshold
            }

            # Plot distribution with outliers highlighted
            # Pass the boolean Series indicating outliers
            self.visualizer.plot_outliers(self.df[col], outliers_series, col)

        return outlier_report

    def handle_outliers(self, strategy='winsorize', report=None, **kwargs):
        """
        Handle outliers based on specified strategy

        Parameters:
        -----------
        strategy : str or dict
            'remove' - Remove outliers
            'winsorize' - Cap outliers at percentiles
            'transform' - Apply log/sqrt transform
            'impute' - Replace with median/mean
            dict - column-specific strategies
        report : dict
            Outlier report from detect_outliers()
        """
        if report is None:
            # Need to capture the boolean Series for plotting if report is None
            # Let's regenerate the report structure including the boolean masks
             temp_report = self.detect_outliers(**kwargs)
             # Modify the report to include the boolean series for easier handling
             report = {}
             numeric_cols = self.df.select_dtypes(include=['float64', 'int64']).columns
             for col in numeric_cols:
                 data = self.df[col].dropna()
                 outliers_series = pd.Series(index=self.df.index, data=False) # Initialize

                 method = kwargs.get('method', 'iqr')
                 threshold = kwargs.get('threshold', 1.5)

                 if method == 'iqr':
                     if len(data) >= 2:
                         q1 = data.quantile(0.25)
                         q3 = data.quantile(0.75)
                         iqr = q3 - q1
                         lower_bound = q1 - threshold * iqr
                         upper_bound = q3 + threshold * iqr
                         outliers_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
                         outliers_series = outliers_mask.fillna(False)
                 elif method == 'zscore':
                      if len(data) > 0 and data.std() != 0:
                          z_scores = pd.Series(np.abs(stats.zscore(data)), index=data.index)
                          outliers_mask = z_scores > threshold
                          outliers_series[outliers_mask.index] = outliers_mask
                 elif method == 'modified_zscore':
                     if len(data) > 0 and np.median(np.abs(data - np.median(data))) != 0:
                          median = np.median(data)
                          mad = np.median(np.abs(data - median))
                          modified_z_scores = 0.6745 * (data - median) / mad
                          mod_z_series = pd.Series(np.abs(modified_z_scores), index=data.index)
                          outliers_mask = mod_z_series > threshold
                          outliers_series[outliers_mask.index] = outliers_mask
                 elif method == 'percentile':
                     if len(data) >= 2:
                         lower_bound = data.quantile((1 - threshold)/2)
                         upper_bound = data.quantile(1 - (1 - threshold)/2)
                         outliers_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
                         outliers_series = outliers_mask.fillna(False)

                 report[col] = {
                    'outliers': int(outliers_series.sum()),
                    'percentage': float(outliers_series.mean() * 100),
                    'indices': self.df[outliers_series].index.tolist(),
                    'outlier_mask': outliers_series, # Store the boolean mask
                    'method': method,
                    'threshold': threshold
                }


        for col, col_report in report.items():
            # Use the stored boolean mask for handling
            outliers_mask = col_report.get('outlier_mask', pd.Series(False, index=self.df.index)) # Default to all False if mask not present

            if outliers_mask.sum() == 0: # Use the sum of the mask
                continue

            if strategy == 'remove':
                # Filter rows where the mask is False (i.e., not an outlier)
                self.df = self.df[~outliers_mask].copy() # Use .copy() to avoid SettingWithCopyWarning
            elif strategy == 'winsorize':
                # Ensure winsorizing only happens if there's enough data
                if len(self.df[col].dropna()) >= 2:
                    lower = self.df[col].quantile(0.05)
                    upper = self.df[col].quantile(0.95)
                    self.df[col] = np.where(self.df[col] < lower, lower,
                                          np.where(self.df[col] > upper, upper, self.df[col]))
            elif strategy == 'transform':
                 # Apply transform only if there are values to transform
                if len(self.df[col].dropna()) > 0:
                    if self.df[col].min() > 0:
                        # Only apply log1p to non-outliers if you want to preserve outliers
                        # Or apply to the whole column if transforming includes outliers
                        # Assuming transforming the whole column including current outliers
                        self.df[col] = np.log1p(self.df[col])
                    else:
                        # Apply signed sqrt only if transforming includes outliers
                        self.df[col] = np.sign(self.df[col]) * np.sqrt(np.abs(self.df[col]))
            elif strategy == 'impute':
                 # Impute only if there are outliers to impute
                 if outliers_mask.sum() > 0:
                    median = self.df[col].median()
                    # Use .loc with the boolean mask for imputation
                    self.df.loc[outliers_mask, col] = median
            elif isinstance(strategy, dict) and col in strategy:
                 # Handle column-specific strategies from the dictionary
                 method = strategy[col]
                 if method == 'remove':
                     self.df = self.df[~outliers_mask].copy()
                 elif method == 'winsorize':
                     if len(self.df[col].dropna()) >= 2:
                         lower = self.df[col].quantile(0.05)
                         upper = self.df[col].quantile(0.95)
                         self.df[col] = np.where(self.df[col] < lower, lower,
                                               np.where(self.df[col] > upper, upper, self.df[col]))
                 elif method == 'transform':
                     if len(self.df[col].dropna()) > 0:
                        if self.df[col].min() > 0:
                             self.df[col] = np.log1p(self.df[col])
                        else:
                             self.df[col] = np.sign(self.df[col]) * np.sqrt(np.abs(self.df[col]))
                 elif method == 'impute':
                     if outliers_mask.sum() > 0:
                         median = self.df[col].median()
                         self.df.loc[outliers_mask, col] = median


        return self.df