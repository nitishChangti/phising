import os
import sys
import urllib.request
import pandas as pd
from pathlib import Path

# Add parent directory to path to import api.feature_extractor
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from api.feature_extractor import FeatureExtractor

def reconstruct_url(row):
    protocol = str(row['Protocol']).strip()
    domain = str(row['Domain']).strip()
    path = str(row['Path']).strip() if pd.notna(row['Path']) else ''
    
    # Clean up duplicate slashes or protocols if they exist
    if not protocol.endswith('://'):
        protocol = f"{protocol}://"
        
    url = f"{protocol}{domain}{path}"
    return url

def get_complex_legitimate_urls():
    """Generate a list of complex legitimate URLs with query parameters and paths."""
    base_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=g9w7b1YjK7s",
        "https://www.youtube.com/watch?v=9bZkp7q19f0",
        "https://www.youtube.com/watch?v=5qap5aO4i9A",
        "https://www.youtube.com/watch?v=y83x7MgzWOA",
        "https://www.youtube.com/watch?v=3JZ_D3Kz0OA",
        "https://www.youtube.com/watch?v=2Vv-BfVoq4g",
        "https://www.youtube.com/watch?v=FHEq79p4498",
        "https://www.youtube.com/watch?v=V-_O7nl0Ii0",
        "https://www.youtube.com/watch?v=9I-Y6Ts8uoI",
        "https://www.youtube.com/playlist?list=PL4cUxeGkc9hjgdkTBtJDMc8n58l05448C",
        "https://www.youtube.com/results?search_query=machine+learning+tutorial",
        "https://www.youtube.com/c/GoogleDevelopers",
        "https://www.google.com/search?q=phishing+detection+using+machine+learning",
        "https://www.google.com/search?q=django+rest+framework+tutorial",
        "https://www.google.com/search?q=how+to+train+random+forest+in+python",
        "https://www.google.com/maps/place/Googleplex/@37.4220041,-122.0862515,17z",
        "https://www.google.com/intl/en/about/products",
        "https://mail.google.com/mail/u/0/#inbox",
        "https://docs.google.com/document/d/12345/edit",
        "https://drive.google.com/drive/my-drive",
        "https://en.wikipedia.org/wiki/Phishing",
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://en.wikipedia.org/wiki/Random_forest",
        "https://en.wikipedia.org/wiki/Decision_tree",
        "https://github.com/scikit-learn/scikit-learn",
        "https://github.com/django/django",
        "https://github.com/pandas-dev/pandas",
        "https://github.com/numpy/numpy",
        "https://stackoverflow.com/questions/5064972/how-to-train-a-model-in-scikit-learn",
        "https://stackoverflow.com/questions/tagged/python?tab=votes",
        "https://stackoverflow.com/search?q=random+forest+classifier",
    ]
    
    # Generate variations dynamically
    topics = [
        'machine-learning', 'python', 'django', 'react', 'cybersecurity', 
        'artificial-intelligence', 'neural-networks', 'data-science', 
        'programming', 'web-development', 'data-structures', 'algorithms',
        'sql-database', 'rest-api', 'git-github', 'cloud-computing',
        'docker-containers', 'kubernetes', 'linux-commands', 'javascript'
    ]
    
    extra_urls = []
    for topic in topics:
        t_plus = topic.replace('-', '+')
        t_under = topic.replace('-', '_').capitalize()
        extra_urls.extend([
            f"https://www.google.com/search?q={t_plus}&hl=en&num=100&start=10",
            f"https://www.bing.com/search?q={t_plus}&form=QBLH&sp=-1&pq={t_plus}",
            f"https://en.wikipedia.org/wiki/{t_under}",
            f"https://github.com/search?q={t_plus}&type=repositories&ref=opensearch",
            f"https://stackoverflow.com/search?q={t_plus}",
            f"https://www.youtube.com/results?search_query={t_plus}",
            f"https://www.amazon.com/s?k={t_plus}&crid=12345&sprefix={t_plus}",
            f"https://www.reddit.com/r/{topic.replace('-', '')}",
            f"https://medium.com/search?q={t_plus}",
            f"https://www.youtube.com/watch?v=test_{topic[:5]}_id&feature=emb_title"
        ])
        
    return base_urls + extra_urls

def main():
    ml_dir = Path(__file__).resolve().parent
    backend_dir = ml_dir.parent
    data_dir = backend_dir / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load local phishing dataset
    phish_csv_path = backend_dir / 'phishing-urls.csv'
    if not phish_csv_path.exists():
        print(f"Error: local phishing-urls.csv not found at {phish_csv_path}")
        sys.exit(1)
        
    print("Loading local phishing URLs...")
    df_phish = pd.read_csv(phish_csv_path)
    
    # 2. Download remote legitimate dataset if not already downloaded
    legit_csv_path = data_dir / 'legitimate-urls.csv'
    if not legit_csv_path.exists():
        print("Downloading remote legitimate URLs...")
        legit_url = "https://raw.githubusercontent.com/jishnusaurav/Phishing-attack-PCAP-analysis-using-scapy/master/Phishing-Website-Detection/datasets/legitimate-urls.csv"
        try:
            urllib.request.urlretrieve(legit_url, legit_csv_path)
            print(f"Downloaded legitimate URLs to {legit_csv_path}")
        except Exception as e:
            print(f"Failed to download legitimate URLs: {e}")
            sys.exit(1)
    else:
        print("Loading cached legitimate URLs...")
        
    df_legit = pd.read_csv(legit_csv_path)
    
    # 3. Get complex legitimate URLs to mix in
    complex_legit_urls = get_complex_legitimate_urls()
    print(f"Loaded {len(df_phish)} phishing rows and {len(df_legit)} standard legitimate rows.")
    print(f"Generating {len(complex_legit_urls)} complex legitimate URLs to prevent query param bias.")
    
    # 4. Extract features
    extractor = FeatureExtractor()
    extracted_features = []
    labels = []
    
    # Process Phishing URLs
    urls_processed = 0
    print("\nExtracting features from Phishing URLs (label = 1)...")
    for idx, row in df_phish.iterrows():
        url = reconstruct_url(row)
        try:
            features = extractor.extract_features(url)
            extracted_features.append(features)
            labels.append(1) # Phishing
        except Exception as e:
            print(f"Error extracting features for {url}: {e}")
            
        urls_processed += 1
        if urls_processed % 200 == 0:
            print(f"Processed {urls_processed} phishing URLs...")
            
    # Process Standard Legitimate URLs
    urls_processed = 0
    print("\nExtracting features from Standard Legitimate URLs (label = 0)...")
    for idx, row in df_legit.iterrows():
        url = reconstruct_url(row)
        try:
            features = extractor.extract_features(url)
            extracted_features.append(features)
            labels.append(0) # Legitimate
        except Exception as e:
            print(f"Error extracting features for {url}: {e}")
            
        urls_processed += 1
        if urls_processed % 200 == 0:
            print(f"Processed {urls_processed} standard legitimate URLs...")
            
    # Process Complex Legitimate URLs
    urls_processed = 0
    print("\nExtracting features from Complex Legitimate URLs (label = 0)...")
    for url in complex_legit_urls:
        try:
            features = extractor.extract_features(url)
            extracted_features.append(features)
            labels.append(0) # Legitimate
        except Exception as e:
            print(f"Error extracting features for {url}: {e}")
            
        urls_processed += 1
        if urls_processed % 50 == 0:
            print(f"Processed {urls_processed} complex legitimate URLs...")
            
    # 5. Build and save dataset
    print("\nBuilding dataset DataFrame...")
    df_features = pd.DataFrame(extracted_features)
    df_features['label'] = labels
    
    output_path = data_dir / 'dataset_real.csv'
    df_features.to_csv(output_path, index=False)
    print(f"Extraction complete! Saved real dataset ({len(df_features)} rows) to {output_path}")

if __name__ == '__main__':
    main()
