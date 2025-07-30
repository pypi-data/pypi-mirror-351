from enum import Enum, auto
from typing import Dict, List, Optional, Tuple
import random

class BrowserProfile(Enum):
    """Available browser profiles for fingerprint simulation."""
    CHROME_LATEST = auto()
    CHROME_120 = auto()
    CHROME_110 = auto()
    FIREFOX_LATEST = auto()
    FIREFOX_115 = auto()
    SAFARI_17 = auto()
    SAFARI_16 = auto()
    EDGE_LATEST = auto()
    CHROME_MOBILE = auto()
    SAFARI_IOS = auto()
    SAMSUNG_BROWSER = auto()
    CUSTOM = auto()


class RotationStrategy(Enum):
    """Fingerprint rotation strategies."""
    NONE = auto()
    RANDOM = auto()
    SEQUENTIAL = auto()
    WEIGHTED = auto()
    INTELLIGENT = auto()
    TIME_BASED = auto()


def get_browser_profile(browser_name: str) -> BrowserProfile:
    """Get browser profile from simple name."""
    browser_map = {
        'chrome': BrowserProfile.CHROME_LATEST,
        'firefox': BrowserProfile.FIREFOX_LATEST,
        'safari': BrowserProfile.SAFARI_17,
        'edge': BrowserProfile.EDGE_LATEST,
        'chrome_mobile': BrowserProfile.CHROME_MOBILE,
        'safari_ios': BrowserProfile.SAFARI_IOS,
        'samsung': BrowserProfile.SAMSUNG_BROWSER,
    }
    
    browser_lower = browser_name.lower()
    if browser_lower in browser_map:
        return browser_map[browser_lower]
    
    # Try to parse version
    if browser_lower.startswith('chrome'):
        if '120' in browser_lower:
            return BrowserProfile.CHROME_120
        elif '110' in browser_lower:
            return BrowserProfile.CHROME_110
    elif browser_lower.startswith('firefox'):
        if '115' in browser_lower:
            return BrowserProfile.FIREFOX_115
    elif browser_lower.startswith('safari'):
        if '16' in browser_lower:
            return BrowserProfile.SAFARI_16
            
    return BrowserProfile.CHROME_LATEST


class BrowserCharacteristics:
    """Browser-specific characteristics and headers."""
    
    def __init__(self, profile: BrowserProfile):
        self.profile = profile
        self._init_characteristics()
        
    def _init_characteristics(self):
        """Initialize browser-specific characteristics."""
        if self.profile in [BrowserProfile.CHROME_LATEST, BrowserProfile.CHROME_120]:
            self.user_agent = self._get_chrome_user_agent()
            self.accept_headers = self._get_chrome_accept_headers()
            self.sec_ch_ua = self._get_chrome_client_hints()
        elif self.profile in [BrowserProfile.FIREFOX_LATEST, BrowserProfile.FIREFOX_115]:
            self.user_agent = self._get_firefox_user_agent()
            self.accept_headers = self._get_firefox_accept_headers()
            self.sec_ch_ua = None  # Firefox doesn't send Client Hints
        elif self.profile in [BrowserProfile.SAFARI_17, BrowserProfile.SAFARI_16]:
            self.user_agent = self._get_safari_user_agent()
            self.accept_headers = self._get_safari_accept_headers()
            self.sec_ch_ua = None
        elif self.profile == BrowserProfile.EDGE_LATEST:
            self.user_agent = self._get_edge_user_agent()
            self.accept_headers = self._get_chrome_accept_headers()
            self.sec_ch_ua = self._get_edge_client_hints()
        elif self.profile == BrowserProfile.CHROME_MOBILE:
            self.user_agent = self._get_chrome_mobile_user_agent()
            self.accept_headers = self._get_chrome_accept_headers()
            self.sec_ch_ua = self._get_chrome_mobile_client_hints()
        elif self.profile == BrowserProfile.SAFARI_IOS:
            self.user_agent = self._get_safari_ios_user_agent()
            self.accept_headers = self._get_safari_accept_headers()
            self.sec_ch_ua = None
            
    def _get_chrome_user_agent(self) -> str:
        """Get Chrome user agent string."""
        os_strings = [
            "Windows NT 10.0; Win64; x64",
            "Macintosh; Intel Mac OS X 10_15_7",
            "X11; Linux x86_64",
        ]
        os_string = random.choice(os_strings)
        return f"Mozilla/5.0 ({os_string}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
    def _get_firefox_user_agent(self) -> str:
        """Get Firefox user agent string."""
        os_strings = [
            "Windows NT 10.0; Win64; x64",
            "Macintosh; Intel Mac OS X 10.15",
            "X11; Linux x86_64",
        ]
        os_string = random.choice(os_strings)
        return f"Mozilla/5.0 ({os_string}) Gecko/20100101 Firefox/115.0"
        
    def _get_safari_user_agent(self) -> str:
        """Get Safari user agent string."""
        return "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
        
    def _get_edge_user_agent(self) -> str:
        """Get Edge user agent string."""
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        
    def _get_chrome_mobile_user_agent(self) -> str:
        """Get Chrome Mobile user agent string."""
        devices = [
            "Linux; Android 13; Pixel 7",
            "Linux; Android 13; SM-S918B",
            "Linux; Android 12; Pixel 6",
        ]
        device = random.choice(devices)
        return f"Mozilla/5.0 ({device}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        
    def _get_safari_ios_user_agent(self) -> str:
        """Get Safari iOS user agent string."""
        return "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        
    def _get_chrome_accept_headers(self) -> Dict[str, str]:
        """Get Chrome accept headers."""
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        
    def _get_firefox_accept_headers(self) -> Dict[str, str]:
        """Get Firefox accept headers."""
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        
    def _get_safari_accept_headers(self) -> Dict[str, str]:
        """Get Safari accept headers."""
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        
    def _get_chrome_client_hints(self) -> Dict[str, str]:
        """Get Chrome Client Hints headers."""
        return {
            'Sec-CH-UA': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"',
        }
        
    def _get_edge_client_hints(self) -> Dict[str, str]:
        """Get Edge Client Hints headers."""
        return {
            'Sec-CH-UA': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"',
        }
        
    def _get_chrome_mobile_client_hints(self) -> Dict[str, str]:
        """Get Chrome Mobile Client Hints headers."""
        return {
            'Sec-CH-UA': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-CH-UA-Mobile': '?1',
            'Sec-CH-UA-Platform': '"Android"',
        }
        
    def get_headers(self, host: str, path: str = '/', method: str = 'GET') -> Dict[str, str]:
        """Get complete header set for request."""
        headers = {
            'Host': host,
            'User-Agent': self.user_agent,
            'Accept': self.accept_headers['Accept'],
            'Accept-Language': self.accept_headers['Accept-Language'],
            'Accept-Encoding': self.accept_headers['Accept-Encoding'],
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Add Client Hints if available
        if self.sec_ch_ua:
            headers.update(self.sec_ch_ua)
            
        # Add Sec-Fetch headers for Chrome/Edge
        if self.profile in [BrowserProfile.CHROME_LATEST, BrowserProfile.CHROME_120,
                           BrowserProfile.EDGE_LATEST, BrowserProfile.CHROME_MOBILE]:
            headers.update({
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
            })
            
        # Add DNT for Firefox
        if self.profile in [BrowserProfile.FIREFOX_LATEST, BrowserProfile.FIREFOX_115]:
            headers['DNT'] = '1'
            
        return headers


class ProfileManager:
    """Manage browser profiles and rotation."""
    
    def __init__(self):
        self.profiles = list(BrowserProfile)
        self.current_index = 0
        self.profile_weights = self._init_weights()
        
    def _init_weights(self) -> Dict[BrowserProfile, float]:
        """Initialize market share-based weights."""
        return {
            BrowserProfile.CHROME_LATEST: 0.65,
            BrowserProfile.SAFARI_17: 0.19,
            BrowserProfile.EDGE_LATEST: 0.05,
            BrowserProfile.FIREFOX_LATEST: 0.03,
            BrowserProfile.CHROME_MOBILE: 0.05,
            BrowserProfile.SAFARI_IOS: 0.03,
        }
        
    def get_next_profile(self, strategy: RotationStrategy) -> BrowserProfile:
        """Get next browser profile based on rotation strategy."""
        if strategy == RotationStrategy.NONE:
            return BrowserProfile.CHROME_LATEST
        elif strategy == RotationStrategy.RANDOM:
            return random.choice(self.profiles)
        elif strategy == RotationStrategy.SEQUENTIAL:
            profile = self.profiles[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.profiles)
            return profile
        elif strategy == RotationStrategy.WEIGHTED:
            return self._weighted_choice()
        elif strategy == RotationStrategy.INTELLIGENT:
            # Would use ML to select optimal profile
            return self._weighted_choice()
        elif strategy == RotationStrategy.TIME_BASED:
            # Select based on time of day
            import datetime
            hour = datetime.datetime.now().hour
            if 6 <= hour < 9 or 17 <= hour < 22:
                # Peak hours - more mobile
                return random.choice([
                    BrowserProfile.CHROME_MOBILE,
                    BrowserProfile.SAFARI_IOS,
                    BrowserProfile.CHROME_LATEST
                ])
            else:
                # Work hours - more desktop
                return self._weighted_choice()
                
        return BrowserProfile.CHROME_LATEST
        
    def _weighted_choice(self) -> BrowserProfile:
        """Choose profile based on market share weights."""
        profiles = list(self.profile_weights.keys())
        weights = list(self.profile_weights.values())
        return random.choices(profiles, weights=weights)[0]