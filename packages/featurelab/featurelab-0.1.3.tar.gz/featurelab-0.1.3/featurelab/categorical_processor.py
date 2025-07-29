import pandas as pd
import numpy as np
from sklearn.preprocessing import (OneHotEncoder, OrdinalEncoder, 
                                 LabelEncoder, TargetEncoder)
from category_encoders import (BinaryEncoder, CountEncoder, 
                              WOEEncoder, CatBoostEncoder)
from .stats_advisor import StatsAdvisor
from .visualizer import Visualizer

class CategoricalProcessor:
    """
    Handle categorical variables with various encoding strategies
    """

    def __init__(self, df):
        self.df = df.copy()
        self.advisor = StatsAdvisor() # Assuming StatsAdvisor and Visualizer are defined elsewhere
        self.visualizer = Visualizer()

    def analyze_categorical(self, target=None):
        """Analyze categorical columns and suggest encoding methods"""
        # Determine categorical columns at the time of analysis
        cat_cols = self.df.select_dtypes(include=['object', 'category']).columns
        report = {}

        for col in cat_cols:
            stats = self.advisor.analyze_distribution(self.df[col])
            stats['suggestions'] = self._suggest_encoding(col, stats, target)
            report[col] = stats

            # Plot categorical distribution
            self.visualizer.plot_categorical(self.df[col])

        return report

    def _suggest_encoding(self, col, stats, target=None):
        """Suggest encoding methods based on column characteristics"""
        suggestions = []
        cardinality = stats['unique_values']

        if cardinality < 5:
            suggestions.append('one-hot encoding')
        elif 5 <= cardinality < 20:
            suggestions.append('ordinal encoding')
            suggestions.append('target encoding (if target available)')
        else:
            suggestions.append('frequency encoding')
            suggestions.append('binary encoding')
            suggestions.append('hash encoding')

        if target is not None:
            suggestions.append('target encoding')
            suggestions.append('WOE encoding (for classification)')
            suggestions.append('catboost encoding')

        if stats['most_common_pct'] > 70:  # High imbalance
            suggestions.append('consider grouping rare categories')

        return suggestions

    def encode_categorical(self, strategy='auto', target=None, **kwargs):
        """
        Encode categorical variables

        Parameters:
        -----------
        strategy : str or dict
            'auto' - follow recommendations
            'onehot' - one-hot encoding
            'ordinal' - ordinal encoding
            'target' - target encoding
            dict - column-specific strategies
        target : str
            Target column name for supervised encoding
        """
        if strategy == 'auto':
            # Re-analyze categorical columns to ensure they still exist
            report = self.analyze_categorical(target)
            for col, col_stats in report.items():
                # Check if the column still exists in the dataframe
                if col in self.df.columns:
                    if 'one-hot encoding' in col_stats['suggestions'] and col_stats['unique_values'] < 10:
                        self._onehot_encode(columns=[col], **kwargs) # Pass col as a list
                    elif 'ordinal encoding' in col_stats['suggestions']:
                        self._ordinal_encode(columns=[col], **kwargs) # Pass col as a list
                    elif target is not None and 'target encoding' in col_stats['suggestions']:
                        self._target_encode(columns=[col], target=target, **kwargs) # Pass col as a list
                    else: # Default to frequency encoding if other auto strategies not met
                         self._frequency_encode(columns=[col], **kwargs) # Pass col as a list
        elif isinstance(strategy, dict):
            for col, method in strategy.items():
                 # Check if the column exists before attempting to encode
                if col in self.df.columns:
                    if method == 'onehot':
                        self._onehot_encode(columns=[col], **kwargs) # Pass col as a list
                    elif method == 'ordinal':
                        self._ordinal_encode(columns=[col], **kwargs) # Pass col as a list
                    elif method == 'target' and target is not None:
                        self._target_encode(columns=[col], target=target, **kwargs) # Pass col as a list
                    elif method == 'frequency':
                        self._frequency_encode(columns=[col], **kwargs) # Pass col as a list
                    elif method == 'binary':
                         self._binary_encode(columns=[col], **kwargs) # Pass col as a list
        else:
            # This branch handles cases where a single strategy is applied to all categorical columns
            # Need to get the current list of categorical columns here as well
            cat_cols_current = self.df.select_dtypes(include=['object', 'category']).columns
            if strategy == 'onehot':
                self._onehot_encode(columns=cat_cols_current, **kwargs)
            elif strategy == 'ordinal':
                self._ordinal_encode(columns=cat_cols_current, **kwargs)
            elif strategy == 'target' and target is not None:
                self._target_encode(columns=cat_cols_current, target=target, **kwargs)
            elif strategy == 'binary':
                 self._binary_encode(columns=cat_cols_current, **kwargs)
             # Add other strategies if needed here for non-auto, non-dict cases

        return self.df

    def _onehot_encode(self, columns=None, drop_first=False):
        """One-hot encoding implementation"""
        # Ensure columns list is based on current dataframe columns
        if columns is None:
            columns = self.df.select_dtypes(include=['object', 'category']).columns
        # Only attempt to encode columns that are actually in the dataframe and are categorical
        columns_to_encode = [col for col in columns if col in self.df.columns and self.df[col].dtype in ['object', 'category']]
        if columns_to_encode:
             self.df = pd.get_dummies(self.df, columns=columns_to_encode, drop_first=drop_first)
        return self.df

    def _ordinal_encode(self, columns=None, categories='auto'):
        """Ordinal encoding implementation"""
         # Ensure columns list is based on current dataframe columns
        if columns is None:
            columns = self.df.select_dtypes(include=['object', 'category']).columns
        # Only attempt to encode columns that are actually in the dataframe and are categorical
        columns_to_encode = [col for col in columns if col in self.df.columns and self.df[col].dtype in ['object', 'category']]

        if columns_to_encode:
            encoder = OrdinalEncoder(categories=categories)
            # Fit and transform only on the selected columns
            self.df[columns_to_encode] = encoder.fit_transform(self.df[columns_to_encode])
        return self.df

    def _target_encode(self, columns=None, target=None, smoothing=1.0):
        """Target encoding implementation"""
         # Ensure columns list is based on current dataframe columns
        if columns is None:
            columns = self.df.select_dtypes(include=['object', 'category']).columns
         # Only attempt to encode columns that are actually in the dataframe and are categorical
        columns_to_encode = [col for col in columns if col in self.df.columns and self.df[col].dtype in ['object', 'category']]

        if columns_to_encode and target is not None and target in self.df.columns:
            encoder = TargetEncoder(smoothing=smoothing)
             # Fit and transform only on the selected columns
            self.df[columns_to_encode] = encoder.fit_transform(self.df[columns_to_encode], self.df[target])
        return self.df

    def _frequency_encode(self, columns=None):
        """Frequency encoding implementation"""
         # Ensure columns list is based on current dataframe columns
        if columns is None:
            columns = self.df.select_dtypes(include=['object', 'category']).columns
         # Only attempt to encode columns that are actually in the dataframe and are categorical
        columns_to_encode = [col for col in columns if col in self.df.columns and self.df[col].dtype in ['object', 'category']]


        for col in columns_to_encode:
            # Check again if the column still exists before processing
             if col in self.df.columns:
                freq = self.df[col].value_counts(normalize=True)
                self.df[col+'_freq'] = self.df[col].map(freq)
                self.df.drop(col, axis=1, inplace=True)

        return self.df

    def _binary_encode(self, columns=None):
        """Binary encoding implementation"""
         # Ensure columns list is based on current dataframe columns
        if columns is None:
            columns = self.df.select_dtypes(include=['object', 'category']).columns
         # Only attempt to encode columns that are actually in the dataframe and are categorical
        columns_to_encode = [col for col in columns if col in self.df.columns and self.df[col].dtype in ['object', 'category']]


        if columns_to_encode:
            encoder = BinaryEncoder(cols=columns_to_encode)
            self.df = encoder.fit_transform(self.df)
        return self.df