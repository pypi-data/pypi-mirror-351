import pandas as pd
import numpy as np
import random
import string
from datetime import datetime, timedelta

def generate_random_dataframe(n_rows=None, n_cols=None):
    """
    Generates a pandas DataFrame with random data, including patterns for ML benchmarking.

    Args:
        n_rows (int, optional): Number of rows. Defaults to a random number between 50 and 500.
        n_cols (int, optional): Number of columns. Defaults to a random number between 3 and 20.

    Returns:
        pd.DataFrame: A randomly generated DataFrame.
    """
    if n_rows is None:
        n_rows = random.randint(50, 500)
    if n_cols is None:
        n_cols = random.randint(3, 20)

    data = {}
    column_names = [f'col_{i}' for i in range(n_cols)]

    for i in range(n_cols):
        col_name = column_names[i]
        col_type = random.choice(['int', 'float', 'bool', 'string', 'datetime', 'categorical_str', 'categorical_int'])

        if col_type == 'int':
            # Introduce a pattern: e.g., a sequence with some noise
            base_sequence = np.arange(n_rows) + random.randint(-10, 10)
            noise = np.random.randint(-n_rows * 0.1, n_rows * 0.1, size=n_rows)
            data[col_name] = base_sequence + noise
        elif col_type == 'float':
            # Introduce a pattern: e.g., a sine wave with noise or a linear trend with noise
            if random.random() < 0.5:
                # Sine wave pattern
                x = np.linspace(0, random.uniform(5, 20), n_rows)
                base_signal = np.sin(x * random.uniform(0.5, 2)) * random.uniform(1, 100)
                noise = np.random.normal(0, random.uniform(0.1, 5), n_rows)
                data[col_name] = base_signal + noise
            else:
                # Linear trend pattern
                slope = random.uniform(-10, 10)
                intercept = random.uniform(-100, 100)
                base_signal = slope * np.arange(n_rows) + intercept
                noise = np.random.normal(0, abs(slope * n_rows * 0.05) + 1, n_rows) # Noise proportional to range
                data[col_name] = base_signal + noise
        elif col_type == 'bool':
            # Introduce a pattern: e.g., higher probability of True for first half
            if random.random() < 0.3: # Simple random
                 data[col_name] = np.random.choice([True, False], size=n_rows)
            else: # Patterned
                pattern_split = int(n_rows * random.uniform(0.3, 0.7))
                prob_first_half = random.uniform(0.6, 0.9)
                prob_second_half = 1 - prob_first_half
                arr = np.concatenate([
                    np.random.choice([True, False], size=pattern_split, p=[prob_first_half, 1-prob_first_half]),
                    np.random.choice([True, False], size=n_rows - pattern_split, p=[prob_second_half, 1-prob_second_half])
                ])
                data[col_name] = arr
        elif col_type == 'string':
            # Random strings of varying length, could introduce some common prefixes/suffixes for pattern
            str_lengths = np.random.randint(5, 20, size=n_rows)
            common_prefix = ''.join(random.choices(string.ascii_lowercase, k=random.randint(0,3))) if random.random() < 0.5 else ''
            common_suffix = ''.join(random.choices(string.ascii_lowercase, k=random.randint(0,3))) if random.random() < 0.5 else ''
            data[col_name] = [common_prefix + ''.join(random.choices(string.ascii_letters + string.digits, k=length)) + common_suffix for length in str_lengths]
        elif col_type == 'datetime':
            start_date = datetime(2000, 1, 1) + timedelta(days=random.randint(0, 365*20))
            # Introduce a pattern: e.g., increasing trend or random walks
            if random.random() < 0.5:
                data[col_name] = [start_date + timedelta(days=x + random.randint(-5,5), hours=random.randint(0,23), minutes=random.randint(0,59)) for x in range(n_rows)]
            else:
                dates = [start_date]
                for _ in range(1, n_rows):
                    dates.append(dates[-1] + timedelta(days=random.randint(-2, 5), hours=random.randint(-12,12)))
                data[col_name] = dates
        elif col_type == 'categorical_str':
            num_categories = random.randint(2, 10)
            categories = [''.join(random.choices(string.ascii_uppercase, k=3)) + f'_{j}' for j in range(num_categories)]
            # Introduce a pattern: some categories more frequent than others
            probabilities = np.random.dirichlet(np.ones(num_categories) * random.uniform(0.5,5), size=1).flatten()
            data[col_name] = np.random.choice(categories, size=n_rows, p=probabilities)
        elif col_type == 'categorical_int':
            num_categories = random.randint(2, 10)
            categories = list(range(num_categories))
            # Introduce a pattern: some categories more frequent than others
            probabilities = np.random.dirichlet(np.ones(num_categories) * random.uniform(0.5,5), size=1).flatten()
            data[col_name] = np.random.choice(categories, size=n_rows, p=probabilities)

    df = pd.DataFrame(data)

    # Introduce some missing values randomly, but with a pattern (e.g. more in certain columns)
    for col in df.columns:
        if random.random() < 0.15: # 15% chance a column has NaNs
            nan_percentage = random.uniform(0.01, 0.1)
            nan_indices = np.random.choice(df.index, size=int(n_rows * nan_percentage), replace=False)
            if df[col].dtype == object and col_type not in ['categorical_str', 'string'] : # Avoid NaNs in string columns if not desired, or handle appropriately
                 # For object columns that are not explicitly strings, can insert None or np.nan
                 df.loc[nan_indices, col] = None
            elif pd.api.types.is_numeric_dtype(df[col]):
                df.loc[nan_indices, col] = np.nan
            # For other types like boolean or datetime, np.nan might convert them to float or NaT.
            # This behavior is generally acceptable for ML tasks.

    # Introduce a target variable (binary classification for simplicity) that has some dependency on other columns
    if n_cols > 1 and random.random() < 0.8: # 80% chance to add a target column
        # Select 1 to 3 features to base the target on
        num_base_features = random.randint(1, min(3, n_cols -1 ))
        base_feature_names = random.sample([c for c in df.columns if df[c].isnull().sum() == 0 and pd.api.types.is_numeric_dtype(df[c])], k=min(num_base_features, len([c for c in df.columns if df[c].isnull().sum() == 0 and pd.api.types.is_numeric_dtype(df[c])])))

        if base_feature_names:
            target_logit = pd.Series(np.zeros(n_rows))
            for feat_name in base_feature_names:
                # Normalize feature to avoid large logit values
                normalized_feat = (df[feat_name] - df[feat_name].mean()) / (df[feat_name].std() + 1e-6)
                target_logit += normalized_feat * random.uniform(-2, 2)
            
            # Add some interaction term (simple product)
            if len(base_feature_names) > 1 and random.random() < 0.5:
                f1, f2 = random.sample(base_feature_names, 2)
                norm_f1 = (df[f1] - df[f1].mean()) / (df[f1].std() + 1e-6)
                norm_f2 = (df[f2] - df[f2].mean()) / (df[f2].std() + 1e-6)
                target_logit += norm_f1 * norm_f2 * random.uniform(-1,1)

            # Add noise
            target_logit += np.random.normal(0, 0.5, n_rows)
            
            target_prob = 1 / (1 + np.exp(-target_logit))
            df['target'] = (target_prob > random.uniform(0.3, 0.7)).astype(int) # Threshold can be random

    return df

if __name__ == '__main__':
    # Example Usage:
    random_df = generate_random_dataframe()
    print("Generated DataFrame info:")
    random_df.info()
    print("\nFirst 5 rows:")
    print(random_df.head())

    specific_df = generate_random_dataframe(n_rows=10, n_cols=4)
    print("\nGenerated DataFrame with 10 rows and 4 columns info:")
    specific_df.info()
    print("\nFirst 5 rows of specific_df:")
    print(specific_df.head())

    # Check for patterns
    if 'target' in random_df.columns:
        print("\nTarget variable distribution:")
        print(random_df['target'].value_counts(normalize=True))

    # Check for NaNs
    print("\nNaN counts per column:")
    print(random_df.isnull().sum())
