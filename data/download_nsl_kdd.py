#!/usr/bin/env python3
"""
Download and preprocess NSL-KDD dataset for network intrusion detection
NSL-KDD is an improved version of the KDD Cup 1999 dataset
"""

import pandas as pd
import numpy as np
import urllib.request
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NSL-KDD dataset URLs
NSL_KDD_URLS = {
    'train': 'https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTrain%2B.txt',
    'test': 'https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTest%2B.txt'
}

# NSL-KDD feature names (41 features + label + difficulty)
FEATURE_NAMES = [
    'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
    'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in',
    'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
    'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login',
    'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate',
    'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate',
    'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
    'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
    'dst_host_srv_diff_host_rate', 'dst_host_serror_rate', 'dst_host_srv_serror_rate',
    'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'attack_type', 'difficulty'
]

# Attack type mappings to binary classification
ATTACK_TYPES = {
    'normal': 'normal',
    # DoS attacks
    'back': 'attack', 'land': 'attack', 'neptune': 'attack', 'pod': 'attack',
    'smurf': 'attack', 'teardrop': 'attack', 'mailbomb': 'attack', 'apache2': 'attack',
    'processtable': 'attack', 'udpstorm': 'attack',
    # Probe attacks  
    'satan': 'attack', 'ipsweep': 'attack', 'nmap': 'attack', 'portsweep': 'attack',
    'mscan': 'attack', 'saint': 'attack',
    # R2L attacks
    'guess_passwd': 'attack', 'ftp_write': 'attack', 'imap': 'attack', 'phf': 'attack',
    'multihop': 'attack', 'warezmaster': 'attack', 'warezclient': 'attack', 'spy': 'attack',
    'xlock': 'attack', 'xsnoop': 'attack', 'snmpread': 'attack', 'snmpwrite': 'attack',
    'httptunnel': 'attack', 'worm': 'attack', 'named': 'attack', 'sendmail': 'attack',
    'xterm': 'attack', 'ps': 'attack', 'sqlattack': 'attack',
    # U2R attacks
    'buffer_overflow': 'attack', 'loadmodule': 'attack', 'perl': 'attack', 'rootkit': 'attack',
    'xterm': 'attack', 'ps': 'attack', 'sqlattack': 'attack'
}

def download_file(url: str, filename: str) -> bool:
    """Download file from URL"""
    try:
        logger.info(f"Downloading {filename} from {url}")
        urllib.request.urlretrieve(url, filename)
        logger.info(f"Successfully downloaded {filename}")
        return True
    except Exception as e:
        logger.error(f"Failed to download {filename}: {e}")
        return False

def load_nsl_kdd_data(filepath: str) -> pd.DataFrame:
    """Load NSL-KDD data from file"""
    try:
        # Read the data (no header in NSL-KDD files)
        df = pd.read_csv(filepath, header=None, names=FEATURE_NAMES)
        
        # Remove difficulty column (last column)
        df = df.drop('difficulty', axis=1)
        
        # Map attack types to binary classification
        df['label'] = df['attack_type'].map(ATTACK_TYPES)
        df = df.drop('attack_type', axis=1)
        
        # Handle categorical features
        categorical_features = ['protocol_type', 'service', 'flag']
        
        # One-hot encode categorical features
        for feature in categorical_features:
            if feature in df.columns:
                dummies = pd.get_dummies(df[feature], prefix=feature)
                df = pd.concat([df, dummies], axis=1)
                df = df.drop(feature, axis=1)
        
        # Ensure all numeric columns are properly typed
        numeric_columns = [col for col in df.columns if col != 'label']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Fill any NaN values with 0
        df = df.fillna(0)
        
        logger.info(f"Loaded {len(df)} samples with {len(df.columns)-1} features")
        logger.info(f"Label distribution:\n{df['label'].value_counts()}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading NSL-KDD data: {e}")
        raise

def preprocess_nsl_kdd() -> pd.DataFrame:
    """Download and preprocess NSL-KDD dataset"""
    
    # Create datasets directory
    datasets_dir = Path('datasets')
    datasets_dir.mkdir(exist_ok=True)
    
    # Download training and test data
    train_file = datasets_dir / 'KDDTrain+.txt'
    test_file = datasets_dir / 'KDDTest+.txt'
    
    # Download files if they don't exist
    if not train_file.exists():
        if not download_file(NSL_KDD_URLS['train'], str(train_file)):
            raise Exception("Failed to download training data")
    
    if not test_file.exists():
        if not download_file(NSL_KDD_URLS['test'], str(test_file)):
            raise Exception("Failed to download test data")
    
    # Load and combine datasets
    logger.info("Loading training data...")
    train_df = load_nsl_kdd_data(str(train_file))
    
    logger.info("Loading test data...")
    test_df = load_nsl_kdd_data(str(test_file))
    
    # Combine training and test data
    combined_df = pd.concat([train_df, test_df], ignore_index=True)
    
    # Shuffle the combined dataset
    combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save processed dataset
    output_file = datasets_dir / 'nsl_kdd_processed.csv'
    combined_df.to_csv(output_file, index=False)
    
    logger.info(f"Processed NSL-KDD dataset saved to {output_file}")
    logger.info(f"Total samples: {len(combined_df)}")
    logger.info(f"Features: {len(combined_df.columns)-1}")
    logger.info(f"Final label distribution:\n{combined_df['label'].value_counts()}")
    
    return combined_df

def create_sample_subset(df: pd.DataFrame, sample_size: int = 5000) -> pd.DataFrame:
    """Create a smaller sample for faster training during demos"""
    
    # Stratified sampling to maintain class distribution
    normal_samples = df[df['label'] == 'normal'].sample(
        n=min(int(sample_size * 0.8), len(df[df['label'] == 'normal'])), 
        random_state=42
    )
    attack_samples = df[df['label'] == 'attack'].sample(
        n=min(int(sample_size * 0.2), len(df[df['label'] == 'attack'])), 
        random_state=42
    )
    
    sample_df = pd.concat([normal_samples, attack_samples], ignore_index=True)
    sample_df = sample_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save sample dataset
    sample_file = Path('datasets/nsl_kdd_sample.csv')
    sample_df.to_csv(sample_file, index=False)
    
    logger.info(f"Created sample dataset with {len(sample_df)} samples")
    logger.info(f"Sample label distribution:\n{sample_df['label'].value_counts()}")
    
    return sample_df

def main():
    """Main function to download and preprocess NSL-KDD dataset"""
    try:
        logger.info("Starting NSL-KDD dataset preparation...")
        
        # Download and preprocess full dataset
        df = preprocess_nsl_kdd()
        
        # Create a smaller sample for demos
        sample_df = create_sample_subset(df, sample_size=5000)
        
        logger.info("NSL-KDD dataset preparation completed successfully!")
        
        # Print feature information
        print("\n" + "="*60)
        print("NSL-KDD Dataset Information")
        print("="*60)
        print(f"Full dataset: {len(df)} samples")
        print(f"Sample dataset: {len(sample_df)} samples")
        print(f"Features: {len(df.columns)-1}")
        print("\nFeature columns:")
        for i, col in enumerate([col for col in df.columns if col != 'label']):
            print(f"{i+1:2d}. {col}")
        
        print(f"\nDatasets saved to:")
        print(f"- Full: datasets/nsl_kdd_processed.csv")
        print(f"- Sample: datasets/nsl_kdd_sample.csv")
        
    except Exception as e:
        logger.error(f"Error in NSL-KDD preparation: {e}")
        raise

if __name__ == "__main__":
    main()
