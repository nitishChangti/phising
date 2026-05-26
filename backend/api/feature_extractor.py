"""
Feature Extractor for PhishShield AI
Extracts 30+ features from a raw URL for ML prediction.
Based on IEEE research methodology for phishing URL detection.
"""

import re
import math
from urllib.parse import urlparse, parse_qs
import socket


class FeatureExtractor:
    """Extract features from a URL for phishing detection."""

    # Suspicious keywords commonly found in phishing URLs
    SUSPICIOUS_KEYWORDS = [
        'login', 'verify', 'update', 'secure', 'account', 'banking',
        'confirm', 'password', 'signin', 'security', 'suspend',
        'alert', 'authenticate', 'wallet', 'paypal', 'ebay',
        'amazon', 'apple', 'microsoft', 'google', 'facebook',
        'netflix', 'bank', 'credit', 'urgent', 'immediately'
    ]

    # Shortening services
    SHORTENING_SERVICES = [
        'bit.ly', 'goo.gl', 'tinyurl.com', 't.co', 'ow.ly',
        'is.gd', 'buff.ly', 'adf.ly', 'bit.do', 'cutt.ly'
    ]

    # Suspicious TLDs
    SUSPICIOUS_TLDS = [
        '.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top',
        '.pw', '.cc', '.club', '.work', '.date', '.racing',
        '.win', '.bid', '.stream', '.download', '.review'
    ]

    def extract_features(self, url):
        """
        Extract all features from a URL.
        Returns a dictionary of feature_name: feature_value.
        """
        # Ensure URL has a scheme
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        try:
            parsed = urlparse(url)
        except Exception:
            parsed = urlparse('http://invalid.com')

        domain = parsed.netloc or ''
        path = parsed.path or ''
        query = parsed.query or ''

        features = {}

        # 1. URL Length
        features['url_length'] = len(url)

        # 2. Domain Length
        features['domain_length'] = len(domain)

        # 3. Path Length
        features['path_length'] = len(path)

        # 4. Number of dots in URL
        features['num_dots'] = url.count('.')

        # 5. Number of hyphens in domain
        features['num_hyphens'] = domain.count('-')

        # 6. Number of underscores
        features['num_underscores'] = url.count('_')

        # 7. Number of slashes in path
        features['num_slashes'] = path.count('/')

        # 8. Number of question marks
        features['num_query_marks'] = url.count('?')

        # 9. Number of ampersands
        features['num_ampersands'] = url.count('&')

        # 10. Number of equal signs
        features['num_equals'] = url.count('=')

        # 11. Number of @ symbols
        features['has_at_symbol'] = 1 if '@' in url else 0

        # 12. Has IP address as domain
        features['has_ip_address'] = self._has_ip_address(domain)

        # 13. Uses HTTPS
        features['uses_https'] = 1 if parsed.scheme == 'https' else 0

        # 14. Number of subdomains
        features['num_subdomains'] = self._count_subdomains(domain)

        # 15. Has suspicious TLD
        features['has_suspicious_tld'] = self._has_suspicious_tld(domain)

        # 16. Number of digits in URL
        features['num_digits'] = sum(c.isdigit() for c in url)

        # 17. Number of digits in domain
        features['num_digits_domain'] = sum(c.isdigit() for c in domain)

        # 18. Number of special characters
        features['num_special_chars'] = sum(
            not c.isalnum() and c not in './-:?' for c in url
        )

        # 19. Has port number
        features['has_port'] = 1 if parsed.port and parsed.port not in [80, 443] else 0

        # 20. URL entropy
        features['url_entropy'] = self._calculate_entropy(url)

        # 21. Domain entropy
        features['domain_entropy'] = self._calculate_entropy(domain)

        # 22. Has suspicious keywords
        features['num_suspicious_keywords'] = self._count_suspicious_keywords(url.lower())

        # 23. Is shortened URL
        features['is_shortened'] = self._is_shortened_url(domain.lower())

        # 24. Path has double slashes
        features['path_double_slash'] = 1 if '//' in path else 0

        # 25. Has redirect (multiple http in URL)
        features['has_redirect'] = 1 if url.count('http') > 1 else 0

        # 26. Domain has numbers
        features['domain_has_numbers'] = 1 if any(c.isdigit() for c in domain.split('.')[0] if domain) else 0

        # 27. Query string length
        features['query_length'] = len(query)

        # 28. Number of query parameters
        try:
            features['num_query_params'] = len(parse_qs(query))
        except Exception:
            features['num_query_params'] = 0

        # 29. Has fragment
        features['has_fragment'] = 1 if parsed.fragment else 0

        # 30. URL depth (number of subdirectories)
        features['url_depth'] = len([p for p in path.split('/') if p])

        return features

    def extract_feature_vector(self, url):
        """Extract features as an ordered list (for ML model input)."""
        features = self.extract_features(url)
        return list(features.values())

    def get_feature_names(self):
        """Return ordered list of feature names."""
        return [
            'url_length', 'domain_length', 'path_length', 'num_dots',
            'num_hyphens', 'num_underscores', 'num_slashes',
            'num_query_marks', 'num_ampersands', 'num_equals',
            'has_at_symbol', 'has_ip_address', 'uses_https',
            'num_subdomains', 'has_suspicious_tld', 'num_digits',
            'num_digits_domain', 'num_special_chars', 'has_port',
            'url_entropy', 'domain_entropy', 'num_suspicious_keywords',
            'is_shortened', 'path_double_slash', 'has_redirect',
            'domain_has_numbers', 'query_length', 'num_query_params',
            'has_fragment', 'url_depth'
        ]

    def _has_ip_address(self, domain):
        """Check if domain is an IP address."""
        # Remove port if present
        host = domain.split(':')[0]
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        if re.match(ip_pattern, host):
            return 1
        # Check for hex IP
        hex_pattern = r'^0x[0-9a-fA-F]+$'
        if re.match(hex_pattern, host):
            return 1
        return 0

    def _count_subdomains(self, domain):
        """Count number of subdomains."""
        host = domain.split(':')[0]
        parts = host.split('.')
        if len(parts) <= 2:
            return 0
        return len(parts) - 2

    def _has_suspicious_tld(self, domain):
        """Check if domain has a suspicious TLD."""
        for tld in self.SUSPICIOUS_TLDS:
            if domain.lower().endswith(tld):
                return 1
        return 0

    def _calculate_entropy(self, text):
        """Calculate Shannon entropy of a string."""
        if not text:
            return 0.0
        prob = [float(text.count(c)) / len(text) for c in set(text)]
        entropy = -sum([p * math.log2(p) for p in prob if p > 0])
        return round(entropy, 4)

    def _count_suspicious_keywords(self, url):
        """Count suspicious keywords in URL."""
        count = 0
        for keyword in self.SUSPICIOUS_KEYWORDS:
            if keyword in url:
                count += 1
        return count

    def _is_shortened_url(self, domain):
        """Check if URL uses a shortening service."""
        for service in self.SHORTENING_SERVICES:
            if service in domain:
                return 1
        return 0
