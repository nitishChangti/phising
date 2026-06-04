import os
import sys
import urllib.request
import pandas as pd
import random
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

def get_popular_legitimate_urls():
    domains = [
        "google.com", "youtube.com", "facebook.com", "amazon.com", "yahoo.com",
        "wikipedia.org", "instagram.com", "twitter.com", "linkedin.com", "reddit.com",
        "ebay.com", "pinterest.com", "netflix.com", "github.com", "openai.com",
        "stackoverflow.com", "microsoft.com", "apple.com", "wordpress.com", "tumblr.com",
        "blogspot.com", "paypal.com", "imgur.com", "medium.com", "quora.com",
        "zoom.us", "vimeo.com", "dailymail.co.uk", "cnn.com", "nytimes.com",
        "bbc.co.uk", "reuters.com", "bloomberg.com", "forbes.com", "techcrunch.com",
        "wired.com", "guardian.co.uk", "nationalgeographic.com", "imdb.com", "espn.com"
    ]
    
    urls = []
    for d in domains:
        urls.extend([
            f"https://{d}",
            f"http://{d}",
            f"https://www.{d}",
            f"http://www.{d}",
            f"https://{d}/",
            f"https://www.{d}/"
        ])
    return urls

def get_simulated_phishing_root_urls():
    keywords = ['paypal', 'amazon', 'netflix', 'google', 'microsoft', 'apple', 'facebook', 'login', 'secure', 'verify', 'update', 'banking', 'confirm', 'alert', 'signin', 'ebay']
    tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.club', '.info', '.com', '.net']
    
    urls = []
    # Seed random for deterministic generation
    random.seed(42)
    for _ in range(250):
        # Pick 2-3 random keywords and join with hyphens
        num_kws = random.choice([2, 3])
        kws = random.sample(keywords, num_kws)
        domain = "-".join(kws)
        tld = random.choice(tlds)
        
        # Variations of scheme
        scheme = random.choice(['http://', 'https://'])
        
        # 50% chance of www prefix
        if random.random() < 0.5:
            url = f"{scheme}www.{domain}{tld}"
        else:
            url = f"{scheme}{domain}{tld}"
            
        urls.append(url)
    return urls

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
    
    # 3. Get complex, popular legitimate, and simulated phishing root URLs to mix in
    complex_legit_urls = get_complex_legitimate_urls()
    popular_legit_urls = get_popular_legitimate_urls()
    simulated_phish_urls = get_simulated_phishing_root_urls()
    
    print(f"Loaded {len(df_phish)} phishing rows and {len(df_legit)} standard legitimate rows.")
    print(f"Generating {len(complex_legit_urls)} complex legitimate, {len(popular_legit_urls)} popular legitimate, and {len(simulated_phish_urls)} simulated phishing root URLs.")
    
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
            
    # Process Simulated Phishing Root URLs
    urls_processed = 0
    print("\nExtracting features from Simulated Phishing Root URLs (label = 1)...")
    for url in simulated_phish_urls:
        try:
            features = extractor.extract_features(url)
            extracted_features.append(features)
            labels.append(1) # Phishing
        except Exception as e:
            print(f"Error extracting features for {url}: {e}")
            
        urls_processed += 1
        if urls_processed % 50 == 0:
            print(f"Processed {urls_processed} simulated phishing root URLs...")
            
    # Process Standard Legitimate URLs
    urls_processed = 0
    print("\nExtracting features from Standard Legitimate URLs (label = 0)...")
    for idx, row in df_legit.iterrows():
        url = reconstruct_url(row)
        # Randomly strip 'www.' 50% of the time to train model to be invariant to it
        if idx % 2 == 0:
            url_lower = url.lower()
            if '://www.' in url_lower:
                url = url.replace('://www.', '://', 1)
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
    for idx, url in enumerate(complex_legit_urls):
        # Randomly strip 'www.' 50% of the time to train model to be invariant to it
        if idx % 2 == 0:
            url_lower = url.lower()
            if '://www.' in url_lower:
                url = url.replace('://www.', '://', 1)
        try:
            features = extractor.extract_features(url)
            extracted_features.append(features)
            labels.append(0) # Legitimate
        except Exception as e:
            print(f"Error extracting features for {url}: {e}")
            
        urls_processed += 1
        if urls_processed % 50 == 0:
            print(f"Processed {urls_processed} complex legitimate URLs...")
            
    # Process Popular Legitimate URLs
    urls_processed = 0
    print("\nExtracting features from Popular Legitimate URLs (label = 0)...")
    for url in popular_legit_urls:
        try:
            features = extractor.extract_features(url)
            extracted_features.append(features)
            labels.append(0) # Legitimate
        except Exception as e:
            print(f"Error extracting features for {url}: {e}")
            
        urls_processed += 1
        if urls_processed % 50 == 0:
            print(f"Processed {urls_processed} popular legitimate URLs...")
            
    # 5. Build and save dataset
    print("\nBuilding dataset DataFrame...")
    df_features = pd.DataFrame(extracted_features)
    df_features['label'] = labels
    
    output_path = data_dir / 'dataset_real.csv'
    df_features.to_csv(output_path, index=False)
    print(f"Extraction complete! Saved real dataset ({len(df_features)} rows) to {output_path}")

if __name__ == '__main__':
    main()

