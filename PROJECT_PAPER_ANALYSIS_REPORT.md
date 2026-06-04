# Project vs IEEE Paper Analysis Report

Project: PhishShield AI - Phishing Website Detection Using Machine Learning  
Reference paper: `2227561_Phishing Website Detection Using Machine Learning.pdf`  
Analysis date: 04 June 2026

## 1. Executive Summary

Your project matches the IEEE paper at the main concept level. Both focus on phishing website detection using machine learning, URL feature extraction, supervised classification, and a user-facing system where a user submits a URL and receives a phishing or legitimate result.

However, the project is not yet a complete one-to-one implementation of the paper. The project mainly implements lexical and structural URL analysis, while the paper discusses a wider feature set including URL/address-bar features, abnormal features, HTML/JavaScript features, domain features, SSL details, website reputation, page content, and future host-information improvements.

Current project status: partially matching, with a strong working prototype.

## 2. Paper Methodology Summary

The IEEE paper proposes phishing website detection using machine learning. Its key ideas are:

- Use a labeled dataset containing legitimate and phishing websites.
- Extract useful website features from URLs and website behavior.
- Train supervised machine learning models.
- Compare model performance using accuracy.
- Select the best-performing model.
- Use the trained model in a user-facing detection system.

The paper specifically discusses:

- URL analysis, such as IP address in URL, URL length, URL shortening, `@` symbol, redirection, hyphen prefix/suffix, subdomains, HTTPS token, and SSL protocol.
- Abnormal page features, such as external page elements and suspicious anchor URLs.
- HTML and JavaScript features, such as redirection, disabled right click, pop-up windows, and iframe use.
- Domain features, such as domain age, DNS record, website traffic, PageRank, Google indexing, backlinks, and statistical reports.
- Algorithms such as Random Forest and Decision Tree.
- A final result where Random Forest achieves 97.31% accuracy.
- A future direction involving a scalable web service, host information, online learning, and advanced feature extraction.

## 3. What Your Project Has Implemented

### 3.1 Frontend Application

You built a multipage frontend inside `frontend/`:

- `index.html`: Home page with project branding, URL input, and quick scan entry point.
- `detection.html`: Main scanner page where users submit URLs for prediction.
- `features.html`: Explains important phishing detection features.
- `results.html`: Shows model comparison, confusion matrix, feature importance, ROC-style visualization, and dataset statistics.
- `about.html`: Explains the project pipeline and Random Forest logic.
- `contact.html`: Contact/feedback page.
- `css/style.css`: Main visual styling.
- `js/app.js`: Frontend logic for navigation, scanning, results display, scan history, stats loading, and animations.

The frontend supports:

- URL submission from the home page and detection page.
- Real-time result rendering.
- Confidence/risk visualization.
- Feature explanation output.
- Recent scan history display.
- Dynamic loading of model metrics from the backend endpoint.

### 3.2 Backend Application

You built a Django backend inside `backend/`:

- `manage.py`: Django project runner.
- `phishshield/settings.py`: Django configuration, frontend template paths, static paths, CORS, REST framework, database, and ML artifact paths.
- `phishshield/urls.py`: Routes frontend pages and API endpoints.
- `api/urls.py`: API route declarations.
- `api/views.py`: API logic for prediction, model stats, model comparison, and scan history.
- `api/models.py`: `URLScan` model for saving prediction history.

Implemented API endpoints:

- `POST /api/predict/`: Accepts a URL and returns prediction result.
- `GET /api/stats/`: Returns training metrics.
- `GET /api/models/`: Returns model comparison and feature importance.
- `GET /api/history/`: Returns recent scan history.

### 3.3 Machine Learning Pipeline

You implemented a machine learning pipeline inside `backend/ml/`:

- `train_model.py`: Trains multiple classifiers and saves the best model.
- `extract_real_features.py`: Builds a feature dataset from phishing and legitimate URL CSV files.
- `model.pkl`: Saved trained Random Forest model.
- `scaler.pkl`: Saved feature scaler.
- `metrics.json`: Saved model evaluation results.

Current trained models and accuracy from `metrics.json`:

| Model | Accuracy | Precision | Recall | F1 Score |
| --- | ---: | ---: | ---: | ---: |
| Random Forest | 90.9% | 91.3% | 88.4% | 89.8% |
| Decision Tree | 87.6% | 89.2% | 82.8% | 85.9% |
| Logistic Regression | 86.7% | 88.0% | 82.0% | 84.9% |
| Naive Bayes | 51.5% | 48.4% | 98.4% | 64.9% |

The project correctly selects Random Forest as the best current model.

### 3.4 Dataset Work

Current dataset files:

- `backend/data/dataset_real.csv`: 2,737 rows, 30 features plus label.
- `backend/data/dataset.csv`: 11,055 rows, 30 features plus label.
- `backend/phishing-urls.csv`: 998 phishing URL rows.
- `backend/data/legitimate-urls.csv`: 1,017 legitimate URL rows.

Current real dataset class balance:

- Legitimate URLs: 1,489
- Phishing URLs: 1,248
- Total: 2,737

The project has a useful dataset pipeline, but the final reported model currently appears to be trained on `dataset_real.csv`, not the full synthetic `dataset.csv`.

### 3.5 Feature Extraction

Your `FeatureExtractor` extracts 30 features:

- `url_length`
- `domain_length`
- `path_length`
- `num_dots`
- `num_hyphens`
- `num_underscores`
- `num_slashes`
- `num_query_marks`
- `num_ampersands`
- `num_equals`
- `has_at_symbol`
- `has_ip_address`
- `uses_https`
- `num_subdomains`
- `has_suspicious_tld`
- `num_digits`
- `num_digits_domain`
- `num_special_chars`
- `has_port`
- `url_entropy`
- `domain_entropy`
- `num_suspicious_keywords`
- `is_shortened`
- `path_double_slash`
- `has_redirect`
- `domain_has_numbers`
- `query_length`
- `num_query_params`
- `has_fragment`
- `url_depth`

These features strongly support URL lexical and structural phishing detection.

## 4. Matching Analysis

| Paper Requirement / Idea | Project Status | Notes |
| --- | --- | --- |
| Detect phishing websites using ML | Matched | The project predicts phishing vs legitimate URLs. |
| User enters URL and gets result | Matched | Implemented through frontend and `/api/predict/`. |
| Labeled phishing and legitimate dataset | Matched | Project contains phishing and legitimate datasets. |
| Feature extraction before classification | Matched | `FeatureExtractor` creates 30-feature vectors. |
| Random Forest algorithm | Matched | Implemented and saved as `model.pkl`. |
| Decision Tree algorithm | Matched | Trained and compared in `train_model.py`. |
| Accuracy-based model comparison | Matched | Metrics stored in `metrics.json`. |
| Random Forest selected as best model | Matched | Current best model is Random Forest. |
| URL/address-bar features | Mostly matched | IP, length, shortener, `@`, redirect, hyphen, subdomains, HTTPS are covered. |
| Domain registration length | Missing | Not currently calculated from WHOIS/domain age. |
| DNS record | Missing | Mentioned in UI, not implemented in backend feature extraction. |
| Website traffic | Missing | Mentioned in UI, not implemented in backend. |
| PageRank / Google Index | Missing | Not implemented. |
| HTML/JavaScript features | Missing | Popups, iframe, right-click disabled, anchors, forms are not actually fetched/analyzed. |
| SSL certificate details | Partially missing | HTTPS presence is checked, but certificate issuer, expiry, and chain are not analyzed. |
| NLP/textual analysis | Missing | The paper discusses NLP, but the current project does not analyze email/page text. |
| Chrome plugin | Missing | The paper conclusion mentions a Chrome plugin, but your project is a Django web app. |
| 97.31% Random Forest accuracy | Not matched | Current backend metric is 90.9%. |
| Scalable web service / online learning | Not implemented | Current app is a local Django development system. |

## 5. Important Mismatches and Issues

### 5.1 Accuracy Difference

The paper reports Random Forest accuracy of 97.31%. Your current trained Random Forest model reports 90.9% accuracy.

This is not a failure, but the report/presentation should not claim exact paper accuracy unless you reproduce the same dataset, feature set, and evaluation process.

### 5.2 UI Shows Some Hardcoded Paper-Like Metrics

Some frontend sections still contain default values such as 97.3% accuracy and 11,055 samples. The JavaScript updates many of these values dynamically from `/api/models/`, but if the API fails or loads slowly, the page may show older placeholder values.

Recommendation: align all static fallback values with the current `metrics.json`, or clearly label 97.31% as the IEEE paper result and 90.9% as your project result.

### 5.3 Feature Page Mentions Features Not Implemented

The frontend mentions DNS record, website traffic, domain registrar, SSL certificate age, JavaScript popups, external resources, right-click disabled, and form action URL. These are valid paper features, but the backend currently does not extract most of them.

Recommendation: either implement these features or mark them as future scope in documentation.

### 5.4 Scaler Is Saved But Not Used for Random Forest

The project saves `scaler.pkl`, but Random Forest prediction uses the raw feature vector. This is acceptable because tree-based models do not require scaling, but the presence of `scaler.pkl` can confuse readers.

Recommendation: explain that scaling is used only for algorithms like Logistic Regression and Naive Bayes during training, while Random Forest uses raw features.

### 5.5 No Browser Extension Yet

The paper conclusion mentions a Chrome plugin. Your project currently provides a web interface, not a browser extension.

Recommendation: mention Chrome extension as future enhancement unless you plan to build it.

## 6. What Is Missing

To make the project match the paper more completely, the following should be added:

1. Domain and WHOIS features:
   - Domain age.
   - Domain registration length.
   - DNS record availability.
   - Registrar information.

2. SSL certificate features:
   - Certificate issuer.
   - Certificate expiration.
   - Certificate validity period.
   - Self-signed or trusted certificate detection.

3. HTML and JavaScript page features:
   - Iframe detection.
   - Pop-up detection.
   - Disabled right-click detection.
   - Form action URL analysis.
   - External resource ratio.
   - Anchor URL ratio.

4. Website reputation features:
   - Search engine index status.
   - Website traffic/rank.
   - Backlink count.
   - IP/domain blacklist lookup.

5. NLP/textual analysis:
   - Suspicious wording in page text.
   - Fake login/payment language detection.
   - Urgency and credential-harvesting phrase detection.

6. Stronger evaluation:
   - ROC-AUC calculation from model probabilities.
   - Cross-validation scores saved numerically.
   - Train/test dataset version documented.
   - Confusion matrix screenshots or exported plots.

7. Deployment/final product:
   - Production settings.
   - Browser extension, if matching the paper conclusion.
   - Public hosted demo or local deployment guide.

## 7. Suggested Final-Year / Internship Explanation

This project implements an ML-based phishing detection system inspired by the IEEE paper "Phishing Website Detection Using Machine Learning." The system extracts 30 URL-based lexical and structural features, trains multiple supervised learning models, selects Random Forest as the best classifier, and deploys the model through a Django REST API with a responsive web interface.

The project currently implements the core detection workflow described in the paper: URL input, feature extraction, model prediction, confidence scoring, result display, and algorithm comparison. The current Random Forest model achieves 90.9% accuracy on the available dataset.

The project partially implements the full feature methodology of the paper. Address-bar and URL-based features are well covered, while domain reputation, SSL certificate analysis, HTML/JavaScript behavior analysis, and NLP-based content analysis remain future work.

## 8. Recommended Next Steps

Priority 1:

- Update frontend fallback metrics to match `metrics.json`.
- Clearly separate "IEEE paper accuracy: 97.31%" from "our trained model accuracy: 90.9%".
- Add documentation explaining that the current feature set is URL-based.

Priority 2:

- Add domain age, DNS record, and domain registration length features.
- Add SSL certificate age/issuer/expiry checks.
- Save ROC-AUC in `metrics.json`.

Priority 3:

- Add HTML fetching and page-content feature extraction.
- Add JavaScript/iframe/form/anchor analysis.
- Build Chrome extension only if required by the project rubric.

## 9. Final Verdict

Your project matches the IEEE paper in concept, algorithm choice, workflow, and core URL-based detection approach.

It does not fully match the paper in complete feature coverage, reported accuracy, Chrome plugin implementation, or advanced reputation/content/NLP analysis.

Overall assessment: strong partial implementation, suitable as a working prototype and presentation-ready if the missing features are honestly described as future scope.
