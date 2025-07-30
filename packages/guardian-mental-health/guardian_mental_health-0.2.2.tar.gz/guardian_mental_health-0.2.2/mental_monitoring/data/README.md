# Guardian Training Dataset Guide

This directory contains datasets for training the Guardian mental health monitoring system.

## Expected Dataset Format

For training the mental health classifier, datasets should be in CSV format with at least the following columns:

- **text**: The message content to analyze
- **label**: The risk level (0: No risk, 1: Low risk, 2: High risk)

Example:
```csv
text,label
"I had a good day today!",0
"I'm feeling kind of down, not sure why.",1
"I can't take this pain anymore, I just want it to end.",2
```

## Recommended Datasets

The following datasets are recommended for training:

1. **Suicide and Depression Detection Dataset**
   - Available from: [Kaggle](https://www.kaggle.com/datasets/nikhileswarkomati/suicide-watch)
   - Contains labeled texts for suicide and depression detection

2. **Reddit SuicideWatch and Mental Health Collection (SWMH)**
   - Available from: [HuggingFace](https://huggingface.co/datasets/AIMH/SWMH)
   - Contains 54,000+ posts from mental health subreddits

3. **DepressionEmo Dataset**
   - Contains 6,037 examples annotated for depression-related emotions

## Data Preprocessing

The `train_model.py` script in the project root will:
1. Download datasets when possible
2. Preprocess them into the required format
3. Optionally balance the classes
4. Train the model

## Privacy & Ethics

When working with mental health datasets:
- Ensure data is anonymous
- Use data for training purposes only
- Follow ethical guidelines for AI in mental health
- Consider privacy implications

## Adding Custom Datasets

Place your custom datasets in this directory as CSV files and use the following command:

```bash
python train_model.py --dataset custom --csv-path mental_monitoring/data/your_dataset.csv
```
