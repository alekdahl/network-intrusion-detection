# Network Intrusion Detection with Machine Learning

Multi-class classification of network traffic into **normal traffic** and **nine attack categories**
on the [UNSW-NB15](https://research.unsw.edu.au/projects/unsw-nb15-dataset) dataset, with a focus on
honest evaluation under heavy class imbalance and a bias-variance analysis of where the remaining error comes from.

![Model comparison](figures/model_comparison.png)

## Highlights

- **End-to-end pipeline:** EDA, one-hot encoding of nominal features, leakage-free scaling, stratified splitting,
  baseline models, imbalance handling and per-class evaluation.
- **Imbalance handling:** class weighting and SMOTE compared side by side. SMOTE raises recall on the rarest class
  (Worms, 0.07% of the data) from **0.14 to 0.54** while keeping overall accuracy.
- **Bias-variance diagnosis:** train/test gaps, a regularization (depth) sweep, learning curves, PCA and stratified
  cross-validation.
- **Root-cause finding:** about **19% of all rows share an identical feature vector with a row from another class**
  (85% for Backdoor). This irreducible error, not the choice of model, is what limits the hardest classes.

## Dataset

| | |
|---|---|
| Records | 257,673 network flows (official train + test sets combined and re-split 80/20, stratified) |
| Features | 31 numeric + 3 nominal (`proto`, `service`, `state`), giving 188 features after one-hot encoding |
| Classes | Normal, Generic, Exploits, Fuzzers, DoS, Reconnaissance, Analysis, Backdoor, Shellcode, Worms |
| Imbalance | 534x between the largest (Normal, 36%) and the smallest class (Worms, 174 rows) |

![Class distribution](figures/class_distribution.png)

The data is downloaded automatically from Kaggle ([`dhoogla/unswnb15`](https://www.kaggle.com/datasets/dhoogla/unswnb15))
with `kagglehub` the first time a notebook runs.

## Results

Macro F1 is the primary metric because it weights every class equally. Accuracy is reported for comparison.

| Model | Accuracy | Macro F1 | Weighted F1 |
|---|---|---|---|
| **Random forest + SMOTE** | 0.813 | **0.548** | 0.802 |
| Random forest (class-weighted) | 0.755 | 0.546 | 0.787 |
| Random forest | 0.816 | 0.527 | 0.802 |
| Decision tree, depth 10 (class-weighted) | 0.711 | 0.494 | 0.745 |
| Decision tree, depth 10 | 0.774 | 0.452 | 0.760 |
| Logistic regression (class-weighted) | 0.611 | 0.369 | 0.668 |
| Logistic regression | 0.736 | 0.345 | 0.700 |
| Dummy (always "Normal") | 0.361 | 0.053 | 0.191 |

![Per-class performance](figures/per_class_performance.png)

`Generic`, `Normal` and `Reconnaissance` are detected well (F1 0.83-0.99). `Backdoor`, `Analysis` and `DoS` remain
hard (F1 < 0.25), and most of their errors are predictions of `Exploits`:

![Confusion matrix](figures/confusion_matrix.png)

## Bias-variance analysis

| Finding | Evidence |
|---|---|
| Tree models have **high variance** | Train/test macro F1 gap of 0.17-0.24 for the random forest and the unrestricted tree |
| Logistic regression has **high bias** | Train and test scores nearly identical at a low level (~0.35); learning curves converge low |
| A depth limit of **15-20** is a good trade-off | Test F1 is 0.543-0.556 vs 0.561 unrestricted, with a much smaller gap |
| **PCA does not help** | 153 of 188 components needed for 95% variance; RF macro F1 drops from 0.545 to 0.48-0.50 |
| Results are **stable** | Stratified 3-fold CV gives the same model ranking (std 0.003-0.016) |

![Depth sweep](figures/depth_sweep.png)

### Label overlap: why some classes cannot be separated

Even a fully grown decision tree only reaches ~0.77 macro F1 *on its own training data*. The reason is that many flows
are identical on every feature but carry different attack labels:

![Label overlap](figures/label_overlap.png)

For `Backdoor`, `DoS` and `Analysis` the majority of rows cannot be told apart from other classes using these features.
Further improvement therefore needs richer features (payload- or time-window-based) or merging indistinguishable
categories, rather than more model tuning.

## Tech stack

Python, pandas, NumPy, scikit-learn, imbalanced-learn, matplotlib, seaborn, Jupyter

## License

[MIT](LICENSE)
