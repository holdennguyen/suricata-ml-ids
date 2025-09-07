#!/usr/bin/env python3
"""
Custom Dataset Preprocessing Template for Suricata ML-IDS

This script helps you prepare your own dataset for use with the ML-IDS system.
Modify the preprocessing functions according to your dataset format.

Usage:
    python3 data/custom_dataset_template.py

Requirements:
    - Your dataset should be in CSV format
    - Must have features and a target column
    - Target should be binary (normal vs attack)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def preprocess_custom_dataset(input_file, output_file):
    """
    Preprocess your custom dataset for ML training
    
    Args:
        input_file (str): Path to your raw dataset CSV
        output_file (str): Path for processed dataset CSV
    """
    
    logger.info(f"Loading dataset from {input_file}")
    
    try:
        # 1. Load your dataset
        df = pd.read_csv(input_file)
        logger.info(f"Original dataset shape: {df.shape}")
        
        # 2. Display basic information
        logger.info("Dataset columns:")
        for i, col in enumerate(df.columns):
            logger.info(f"  {i+1}. {col} ({df[col].dtype})")
        
        # 3. Handle missing values
        logger.info("Handling missing values...")
        missing_before = df.isnull().sum().sum()
        
        # Fill numeric columns with median
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if df[col].isnull().any():
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
                logger.info(f"  Filled {col} missing values with median: {median_val}")
        
        # Fill categorical columns with mode
        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if col != 'label' and df[col].isnull().any():
                mode_val = df[col].mode()[0] if not df[col].mode().empty else 'unknown'
                df[col] = df[col].fillna(mode_val)
                logger.info(f"  Filled {col} missing values with mode: {mode_val}")
        
        missing_after = df.isnull().sum().sum()
        logger.info(f"Missing values: {missing_before} → {missing_after}")
        
        # 4. Handle target column
        logger.info("Processing target column...")
        
        # Common target column names to look for
        target_candidates = ['label', 'class', 'target', 'attack', 'anomaly', 'malicious']
        target_col = None
        
        for candidate in target_candidates:
            if candidate in df.columns:
                target_col = candidate
                break
        
        if target_col is None:
            logger.warning("No standard target column found. Please specify manually.")
            logger.info("Available columns:", list(df.columns))
            return False
        
        # Rename target column to 'label'
        if target_col != 'label':
            df = df.rename(columns={target_col: 'label'})
            logger.info(f"Renamed target column '{target_col}' to 'label'")
        
        # Map target values to 'normal' and 'attack'
        unique_labels = df['label'].unique()
        logger.info(f"Original label values: {unique_labels}")
        
        # Common label mappings
        label_mappings = {
            # Binary numeric
            0: 'normal', '0': 'normal', 0.0: 'normal',
            1: 'attack', '1': 'attack', 1.0: 'attack',
            
            # Text variations for normal
            'normal': 'normal', 'benign': 'normal', 'legitimate': 'normal',
            'clean': 'normal', 'safe': 'normal', 'good': 'normal',
            
            # Text variations for attack
            'attack': 'attack', 'malicious': 'attack', 'anomaly': 'attack',
            'malware': 'attack', 'intrusion': 'attack', 'bad': 'attack',
            'suspicious': 'attack', 'threat': 'attack'
        }
        
        # Apply mapping
        df['label'] = df['label'].map(label_mappings)
        
        # Check for unmapped values
        unmapped = df['label'].isnull().sum()
        if unmapped > 0:
            logger.warning(f"Found {unmapped} unmapped label values")
            logger.info("Unmapped values:", df[df['label'].isnull()]['label'].unique())
            # You may need to add custom mappings here
            
        # Remove rows with unmapped labels
        df = df.dropna(subset=['label'])
        
        final_labels = df['label'].unique()
        logger.info(f"Final label values: {final_labels}")
        
        # 5. Encode categorical features
        logger.info("Encoding categorical features...")
        categorical_columns = df.select_dtypes(include=['object']).columns
        categorical_columns = [col for col in categorical_columns if col != 'label']
        
        original_features = len(df.columns) - 1  # Exclude label
        
        for col in categorical_columns:
            logger.info(f"  One-hot encoding: {col}")
            dummies = pd.get_dummies(df[col], prefix=col)
            df = pd.concat([df, dummies], axis=1)
            df = df.drop(col, axis=1)
        
        final_features = len(df.columns) - 1  # Exclude label
        logger.info(f"Features: {original_features} → {final_features}")
        
        # 6. Ensure all features are numeric
        logger.info("Converting features to numeric...")
        feature_columns = [col for col in df.columns if col != 'label']
        
        for col in feature_columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Fill any remaining NaN with 0
        df = df.fillna(0)
        
        # 7. Validate final dataset
        logger.info("Validating processed dataset...")
        
        # Check label distribution
        label_counts = df['label'].value_counts()
        logger.info("Label distribution:")
        for label, count in label_counts.items():
            percentage = (count / len(df)) * 100
            logger.info(f"  {label}: {count} ({percentage:.1f}%)")
        
        # Check for required labels
        required_labels = {'normal', 'attack'}
        actual_labels = set(df['label'].unique())
        if not required_labels.issubset(actual_labels):
            missing_labels = required_labels - actual_labels
            logger.error(f"Missing required labels: {missing_labels}")
            return False
        
        # 8. Save processed dataset
        logger.info(f"Saving processed dataset to {output_file}")
        df.to_csv(output_file, index=False)
        
        # 9. Final summary
        logger.info("✅ Dataset preprocessing completed successfully!")
        logger.info(f"Final dataset shape: {df.shape}")
        logger.info(f"Features: {len(feature_columns)}")
        logger.info(f"Normal samples: {len(df[df['label'] == 'normal'])}")
        logger.info(f"Attack samples: {len(df[df['label'] == 'attack'])}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing dataset: {e}")
        return False

def validate_processed_dataset(filepath):
    """
    Validate that the processed dataset meets ML-IDS requirements
    
    Args:
        filepath (str): Path to processed dataset
    """
    
    logger.info(f"Validating dataset: {filepath}")
    
    try:
        df = pd.read_csv(filepath)
        
        # Check required columns
        if 'label' not in df.columns:
            logger.error("❌ Missing 'label' column")
            return False
        
        # Check label values
        valid_labels = {'normal', 'attack'}
        actual_labels = set(df['label'].unique())
        if not actual_labels.issubset(valid_labels):
            invalid_labels = actual_labels - valid_labels
            logger.error(f"❌ Invalid label values: {invalid_labels}")
            return False
        
        # Check for numeric features
        feature_cols = [col for col in df.columns if col != 'label']
        non_numeric = []
        for col in feature_cols:
            if not pd.api.types.is_numeric_dtype(df[col]):
                non_numeric.append(col)
        
        if non_numeric:
            logger.error(f"❌ Non-numeric feature columns: {non_numeric}")
            return False
        
        # Check for missing values
        missing_values = df.isnull().sum().sum()
        if missing_values > 0:
            logger.error(f"❌ Found {missing_values} missing values")
            return False
        
        # Check dataset size
        if len(df) < 100:
            logger.warning(f"⚠️ Dataset is very small: {len(df)} samples")
        
        # Check class balance
        label_counts = df['label'].value_counts()
        min_class_ratio = label_counts.min() / label_counts.max()
        if min_class_ratio < 0.1:
            logger.warning(f"⚠️ Highly imbalanced dataset (ratio: {min_class_ratio:.2f})")
        
        logger.info("✅ Dataset validation passed!")
        logger.info(f"Shape: {df.shape}")
        logger.info(f"Features: {len(feature_cols)}")
        logger.info("Label distribution:")
        for label, count in label_counts.items():
            percentage = (count / len(df)) * 100
            logger.info(f"  {label}: {count} ({percentage:.1f}%)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Validation error: {e}")
        return False

def create_sample_dataset():
    """
    Create a sample dataset for testing purposes
    """
    
    logger.info("Creating sample dataset for testing...")
    
    np.random.seed(42)
    
    # Generate sample data
    n_samples = 1000
    n_normal = 800
    n_attack = 200
    
    # Normal traffic features
    normal_data = {
        'duration': np.random.exponential(2.0, n_normal),
        'src_bytes': np.random.lognormal(8, 1, n_normal),
        'dst_bytes': np.random.lognormal(9, 1, n_normal),
        'protocol_tcp': np.random.choice([0, 1], n_normal, p=[0.2, 0.8]),
        'protocol_udp': np.random.choice([0, 1], n_normal, p=[0.8, 0.2]),
        'failed_logins': np.random.poisson(0.1, n_normal),
        'count': np.random.poisson(5, n_normal),
        'srv_count': np.random.poisson(3, n_normal),
        'label': ['normal'] * n_normal
    }
    
    # Attack traffic features (different distributions)
    attack_data = {
        'duration': np.random.exponential(0.5, n_attack),  # Shorter duration
        'src_bytes': np.random.lognormal(6, 2, n_attack),   # Different size pattern
        'dst_bytes': np.random.lognormal(7, 2, n_attack),
        'protocol_tcp': np.random.choice([0, 1], n_attack, p=[0.1, 0.9]),
        'protocol_udp': np.random.choice([0, 1], n_attack, p=[0.9, 0.1]),
        'failed_logins': np.random.poisson(2.0, n_attack),  # More failed logins
        'count': np.random.poisson(20, n_attack),           # More connections
        'srv_count': np.random.poisson(15, n_attack),       # More services
        'label': ['attack'] * n_attack
    }
    
    # Combine data
    combined_data = {}
    for key in normal_data.keys():
        combined_data[key] = np.concatenate([normal_data[key], attack_data[key]])
    
    # Create DataFrame and shuffle
    df = pd.DataFrame(combined_data)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save sample dataset
    sample_file = "data/datasets/sample_custom_dataset.csv"
    Path("data/datasets").mkdir(parents=True, exist_ok=True)
    df.to_csv(sample_file, index=False)
    
    logger.info(f"✅ Sample dataset created: {sample_file}")
    logger.info(f"Shape: {df.shape}")
    logger.info("Use this file to test the preprocessing pipeline")
    
    return sample_file

def main():
    """
    Main function - modify paths and settings here
    """
    
    logger.info("🚀 Custom Dataset Preprocessing for Suricata ML-IDS")
    logger.info("=" * 60)
    
    # Configuration - MODIFY THESE PATHS
    input_file = "data/datasets/your_raw_dataset.csv"      # Your input dataset
    output_file = "data/datasets/your_processed_dataset.csv"  # Processed output
    
    # Check if input file exists
    if not Path(input_file).exists():
        logger.warning(f"Input file not found: {input_file}")
        logger.info("Creating a sample dataset for testing...")
        
        # Create sample dataset
        sample_file = create_sample_dataset()
        
        # Use sample as input
        input_file = sample_file
        output_file = "data/datasets/sample_processed_dataset.csv"
    
    # Process the dataset
    success = preprocess_custom_dataset(input_file, output_file)
    
    if success:
        # Validate the processed dataset
        validate_processed_dataset(output_file)
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 Next Steps:")
        logger.info(f"1. Review the processed dataset: {output_file}")
        logger.info("2. Test with ML trainer:")
        logger.info(f'   curl -X POST "http://localhost:8002/train" \\')
        logger.info(f'        -H "Content-Type: application/json" \\')
        logger.info(f'        -d \'{{"dataset_filename": "{Path(output_file).name}", "algorithms": ["decision_tree"]}}\'')
        logger.info("3. If successful, train all models:")
        logger.info(f'   ./scripts/demo.sh ml-training  # (after updating demo script)')
        
    else:
        logger.error("❌ Dataset preprocessing failed")
        logger.info("Please check the error messages above and modify the script accordingly")

if __name__ == "__main__":
    main()
