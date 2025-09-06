# ML Trainer API Documentation

## Overview

The ML Trainer service trains machine learning models for intrusion detection using network feature data. It supports Decision Tree, k-NN, and Ensemble algorithms with hyperparameter optimization via GridSearchCV.

**Base URL**: `http://localhost:8002`  
**Service**: `ml-trainer`  
**Port**: `8002`

## Authentication

Currently, no authentication is required for API access.

## Endpoints

### Health Check

#### `GET /health`

Check the health status of the ML Trainer service.

**Response**

```json
{
  "status": "healthy",
  "service": "ml-trainer"
}
```

**Status Codes**
- `200 OK` - Service is healthy
- `503 Service Unavailable` - Service is unhealthy

---

### Train Models

#### `POST /train`

Train machine learning models using the provided dataset and hyperparameters.

**Request Body**

```json
{
  "dataset_filename": "string",
  "hyperparameters": {
    "decision_tree": {
      "max_depth": [10, 20, 30],
      "min_samples_split": [2, 5, 10],
      "min_samples_leaf": [1, 2, 4]
    },
    "knn": {
      "n_neighbors": [3, 5, 7, 9],
      "weights": ["uniform", "distance"],
      "metric": ["euclidean", "manhattan"]
    }
  },
  "test_size": 0.2,
  "random_state": 42,
  "cv_folds": 5
}
```

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dataset_filename` | string | Yes | Name of the CSV dataset file in `/data/datasets/` |
| `hyperparameters` | object | No | Hyperparameter grids for each algorithm |
| `test_size` | float | No | Proportion of dataset for testing (default: 0.2) |
| `random_state` | integer | No | Random seed for reproducibility (default: 42) |
| `cv_folds` | integer | No | Number of cross-validation folds (default: 5) |

**Example Request**

```bash
curl -X POST "http://localhost:8002/train" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_filename": "synthetic_network_traffic.csv",
    "hyperparameters": {
      "decision_tree": {
        "max_depth": [20],
        "min_samples_split": [2],
        "min_samples_leaf": [1]
      },
      "knn": {
        "n_neighbors": [5],
        "weights": ["distance"],
        "metric": ["euclidean"]
      }
    },
    "test_size": 0.2,
    "random_state": 42,
    "cv_folds": 5
  }'
```

**Response**

```json
{
  "status": "success",
  "message": "Models trained successfully",
  "training_results": {
    "decision_tree": {
      "accuracy": 0.996,
      "precision": 0.995,
      "recall": 0.997,
      "f1_score": 0.996,
      "training_time": 0.57,
      "best_params": {
        "max_depth": 20,
        "min_samples_split": 2,
        "min_samples_leaf": 1
      }
    },
    "knn": {
      "accuracy": 0.996,
      "precision": 0.994,
      "recall": 0.998,
      "f1_score": 0.996,
      "training_time": 0.22,
      "best_params": {
        "n_neighbors": 5,
        "weights": "distance",
        "metric": "euclidean"
      }
    },
    "ensemble": {
      "accuracy": 1.0,
      "precision": 1.0,
      "recall": 1.0,
      "f1_score": 1.0,
      "training_time": 0.92
    }
  },
  "best_algorithm": "ensemble",
  "model_files": {
    "decision_tree": "synthetic_network_traffic_decision_tree_model.joblib",
    "knn": "synthetic_network_traffic_knn_model.joblib",
    "ensemble": "synthetic_network_traffic_ensemble_model.joblib"
  },
  "feature_importance": [
    {"feature": "payload_entropy", "importance": 0.234},
    {"feature": "packets_per_second", "importance": 0.189},
    {"feature": "tcp_syn_ratio", "importance": 0.156},
    {"feature": "unique_dst_ips", "importance": 0.143},
    {"feature": "suspicious_flags", "importance": 0.098}
  ],
  "cross_validation_scores": {
    "decision_tree": [0.994, 0.996, 0.995, 0.997, 0.996],
    "knn": [0.995, 0.997, 0.994, 0.996, 0.998],
    "ensemble": [1.0, 1.0, 1.0, 1.0, 1.0]
  },
  "dataset_info": {
    "total_samples": 10000,
    "training_samples": 8000,
    "test_samples": 2000,
    "features": 25,
    "class_distribution": {
      "normal": 0.7,
      "attack": 0.3
    }
  },
  "processing_time_ms": 1247.3
}
```

**Status Codes**
- `200 OK` - Models trained successfully
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Dataset file not found
- `500 Internal Server Error` - Training error

---

### Evaluate Model

#### `POST /evaluate`

Evaluate a trained model on a test dataset.

**Request Body**

```json
{
  "model_filename": "string",
  "test_dataset_filename": "string"
}
```

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model_filename` | string | Yes | Name of the trained model file (.joblib) |
| `test_dataset_filename` | string | Yes | Name of the test dataset CSV file |

**Example Request**

```bash
curl -X POST "http://localhost:8002/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "model_filename": "ensemble_model.joblib",
    "test_dataset_filename": "test_data.csv"
  }'
```

**Response**

```json
{
  "status": "success",
  "message": "Model evaluation completed",
  "model_file": "ensemble_model.joblib",
  "test_dataset": "test_data.csv",
  "evaluation_results": {
    "accuracy": 0.998,
    "precision": 0.997,
    "recall": 0.999,
    "f1_score": 0.998,
    "confusion_matrix": [[1400, 2], [1, 597]],
    "classification_report": {
      "normal": {"precision": 0.999, "recall": 0.999, "f1-score": 0.999},
      "attack": {"precision": 0.997, "recall": 0.998, "f1-score": 0.998}
    }
  },
  "test_samples": 2000,
  "processing_time_ms": 45.2
}
```

---

### List Models

#### `GET /models`

List all available trained models.

**Response**

```json
{
  "models": [
    {
      "name": "synthetic_network_traffic_decision_tree_model.joblib",
      "algorithm": "decision_tree",
      "accuracy": 0.996,
      "created_at": "2024-01-15T10:30:00Z",
      "size_mb": 0.5,
      "dataset": "synthetic_network_traffic.csv"
    },
    {
      "name": "synthetic_network_traffic_ensemble_model.joblib",
      "algorithm": "ensemble",
      "accuracy": 1.0,
      "created_at": "2024-01-15T10:30:00Z",
      "size_mb": 2.1,
      "dataset": "synthetic_network_traffic.csv"
    }
  ],
  "total_models": 2
}
```

---

### Get Model Info

#### `GET /models/{model_name}`

Get detailed information about a specific model.

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model_name` | string | Yes | Name of the model file |

**Example Request**

```bash
curl "http://localhost:8002/models/ensemble_model.joblib"
```

**Response**

```json
{
  "model_name": "synthetic_network_traffic_ensemble_model.joblib",
  "algorithm": "ensemble",
  "performance": {
    "accuracy": 1.0,
    "precision": 1.0,
    "recall": 1.0,
    "f1_score": 1.0
  },
  "training_info": {
    "dataset": "synthetic_network_traffic.csv",
    "training_samples": 8000,
    "test_samples": 2000,
    "features": 25,
    "training_time": 0.92,
    "created_at": "2024-01-15T10:30:00Z"
  },
  "model_details": {
    "size_mb": 2.1,
    "feature_importance": [
      {"feature": "payload_entropy", "importance": 0.234},
      {"feature": "packets_per_second", "importance": 0.189}
    ]
  }
}
```

## Hyperparameter Schema

### Decision Tree Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_depth` | array[int] | [10, 20, 30] | Maximum depth of the tree |
| `min_samples_split` | array[int] | [2, 5, 10] | Minimum samples required to split |
| `min_samples_leaf` | array[int] | [1, 2, 4] | Minimum samples required at leaf |
| `criterion` | array[string] | ["gini", "entropy"] | Split quality measure |

### k-NN Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `n_neighbors` | array[int] | [3, 5, 7, 9] | Number of neighbors |
| `weights` | array[string] | ["uniform", "distance"] | Weight function |
| `metric` | array[string] | ["euclidean", "manhattan"] | Distance metric |
| `algorithm` | array[string] | ["auto", "ball_tree"] | Algorithm to compute neighbors |

### Ensemble Parameters

The ensemble model combines Decision Tree and k-NN using voting. It automatically uses the best hyperparameters found for each base model.

## Dataset Requirements

### CSV Format

The dataset must be a CSV file with the following requirements:

- **Header Row**: First row must contain feature names
- **Label Column**: Must contain a column named `label` with values `normal` or `attack`
- **Feature Columns**: 25+ numeric features as generated by the Feature Extractor
- **Encoding**: UTF-8 encoding
- **Separator**: Comma-separated values

### Example Dataset Structure

```csv
total_packets,total_bytes,avg_packet_size,duration,tcp_ratio,udp_ratio,label
150,15000,100.0,5.0,0.8,0.2,normal
300,45000,150.0,10.0,0.6,0.4,attack
```

### Data Validation

The service automatically validates:
- Required columns are present
- Numeric features are valid numbers
- Label column contains only `normal` or `attack`
- No missing values in critical columns
- Minimum dataset size (100+ samples)

## Error Handling

### Common Errors

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `DATASET_NOT_FOUND` | 404 | Dataset file does not exist |
| `INVALID_DATASET` | 400 | Dataset format is invalid |
| `INSUFFICIENT_DATA` | 400 | Dataset too small for training |
| `TRAINING_FAILED` | 500 | Model training encountered an error |
| `MODEL_NOT_FOUND` | 404 | Requested model file not found |

### Error Response Format

```json
{
  "status": "error",
  "message": "Dataset file not found: invalid_dataset.csv",
  "error_code": "DATASET_NOT_FOUND",
  "details": {
    "expected_path": "/data/datasets/invalid_dataset.csv",
    "suggestion": "Check if the file exists and has correct permissions"
  }
}
```

## Performance Metrics

- **Training Time**: 0.2-1.0 seconds per algorithm (depends on dataset size)
- **Memory Usage**: ~500MB during training
- **Model Size**: 0.5-2.5MB per trained model
- **Concurrent Training**: 1 training job at a time (queued if multiple requests)

## Rate Limits

- **Train Models**: 5 requests per hour
- **Evaluate Model**: 20 requests per hour
- **List Models**: 100 requests per hour
- **Health Check**: No limit

## Examples

### Python Client Example

```python
import requests
import json

# Train models with custom hyperparameters
training_request = {
    "dataset_filename": "network_features.csv",
    "hyperparameters": {
        "decision_tree": {
            "max_depth": [15, 25],
            "min_samples_split": [2, 5]
        },
        "knn": {
            "n_neighbors": [3, 7],
            "weights": ["distance"]
        }
    },
    "test_size": 0.3,
    "cv_folds": 10
}

response = requests.post(
    "http://localhost:8002/train",
    headers={"Content-Type": "application/json"},
    json=training_request
)

if response.status_code == 200:
    result = response.json()
    print(f"Best algorithm: {result['best_algorithm']}")
    print(f"Ensemble accuracy: {result['training_results']['ensemble']['accuracy']}")
    
    # Print feature importance
    for feature in result['feature_importance'][:5]:
        print(f"{feature['feature']}: {feature['importance']:.3f}")
else:
    error = response.json()
    print(f"Training failed: {error['message']}")
```

### JavaScript Client Example

```javascript
const trainModels = async (dataset, hyperparams) => {
  try {
    const response = await fetch('http://localhost:8002/train', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        dataset_filename: dataset,
        hyperparameters: hyperparams,
        test_size: 0.2,
        cv_folds: 5
      })
    });
    
    const result = await response.json();
    
    if (response.ok) {
      console.log(`Training completed in ${result.processing_time_ms}ms`);
      console.log(`Best algorithm: ${result.best_algorithm}`);
      return result;
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error('Training failed:', error);
  }
};

// Usage
const hyperparams = {
  decision_tree: {
    max_depth: [20],
    min_samples_split: [2]
  },
  knn: {
    n_neighbors: [5],
    weights: ["distance"]
  }
};

trainModels('synthetic_network_traffic.csv', hyperparams);
```

## Integration Notes

- Trained models are automatically saved to `/data/models/` directory
- Models are compatible with the Real-time Detector service
- Feature importance data helps with feature selection and model interpretation
- Cross-validation scores provide insight into model stability
- The service supports incremental learning for model updates
