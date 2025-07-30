from enum import Enum, auto
from typing import Dict, List, Optional, Tuple
import random
import time
import hashlib
import base64

class EvasionLevel(Enum):
    """Detection evasion levels."""
    BASIC = auto()
    ADVANCED = auto() 
    MAXIMUM = auto()


class DetectionSystem(Enum):
    """Known detection systems."""
    CLOUDFLARE = auto()
    AKAMAI = auto()
    IMPERVA = auto()
    DATADOME = auto()
    PERIMETERX = auto()
    SHAPE_SECURITY = auto()
    KASADA = auto()
    GENERIC = auto()


class EvasionStrategy:
    """Advanced evasion strategies."""
    
    def __init__(self, level: EvasionLevel = EvasionLevel.ADVANCED):
        self.level = level
        self.detection_patterns = self._init_detection_patterns()
        self.challenge_solvers = self._init_challenge_solvers()
        
    def _init_detection_patterns(self) -> Dict[DetectionSystem, Dict]:
        """Initialize known detection patterns."""
        return {
            DetectionSystem.CLOUDFLARE: {
                'status_codes': [403, 503],
                'headers': ['CF-RAY', 'CF-Cache-Status'],
                'body_patterns': ['Checking your browser', 'cf-browser-verification'],
                'challenge_types': ['js_challenge', 'captcha'],
            },
            DetectionSystem.AKAMAI: {
                'status_codes': [403],
                'headers': ['X-Akamai-Edgescape'],
                'body_patterns': ['Access Denied', 'akamai'],
                'challenge_types': ['sensor_data', 'pixel_challenge'],
            },
            DetectionSystem.IMPERVA: {
                'status_codes': [403],
                'headers': ['X-Iinfo'],
                'body_patterns': ['Incapsula incident', 'Robot check'],
                'challenge_types': ['reese84', 'cookie_challenge'],
            },
            DetectionSystem.DATADOME: {
                'status_codes': [403],
                'headers': ['X-DataDome'],
                'body_patterns': ['DataDome', 'dd-guard'],
                'challenge_types': ['js_challenge', 'captcha'],
            },
        }
        
    def _init_challenge_solvers(self) -> Dict[str, callable]:
        """Initialize challenge solvers."""
        return {
            'js_challenge': self._solve_js_challenge,
            'captcha': self._solve_captcha,
            'sensor_data': self._generate_sensor_data,
            'pixel_challenge': self._solve_pixel_challenge,
            'reese84': self._solve_reese84,
            'cookie_challenge': self._solve_cookie_challenge,
        }
        
    def detect_system(self, response_data: Dict) -> Optional[DetectionSystem]:
        """Detect which anti-bot system is in use."""
        status_code = response_data.get('status_code', 200)
        headers = response_data.get('headers', {})
        body = response_data.get('body', '')
        
        for system, patterns in self.detection_patterns.items():
            # Check status codes
            if status_code in patterns['status_codes']:
                # Check headers
                for header in patterns['headers']:
                    if header.lower() in (k.lower() for k in headers.keys()):
                        return system
                        
                # Check body patterns
                for pattern in patterns['body_patterns']:
                    if pattern.lower() in body.lower():
                        return system
                        
        return DetectionSystem.GENERIC if status_code in [403, 503] else None
        
    def get_evasion_headers(self, target_system: DetectionSystem) -> Dict[str, str]:
        """Get system-specific evasion headers."""
        headers = {}
        
        if self.level == EvasionLevel.BASIC:
            return headers
            
        # Common evasion headers
        if self.level >= EvasionLevel.ADVANCED:
            headers.update({
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
            })
            
        # System-specific headers
        if target_system == DetectionSystem.CLOUDFLARE:
            headers['CF-Visitor'] = '{"scheme":"https"}'
            if self.level == EvasionLevel.MAXIMUM:
                headers['CF-Connecting-IP'] = self._get_random_ip()
                
        elif target_system == DetectionSystem.AKAMAI:
            headers['X-Acf-Sensor-Data'] = self._generate_sensor_data()
            
        elif target_system == DetectionSystem.IMPERVA:
            headers['X-Forwarded-For'] = self._get_random_ip()
            
        return headers
        
    def apply_timing_evasion(self, request_number: int):
        """Apply timing-based evasion."""
        if self.level == EvasionLevel.BASIC:
            return
            
        if self.level == EvasionLevel.ADVANCED:
            # Simple random delay
            delay = random.uniform(0.5, 2.0)
        else:  # MAXIMUM
            # Human-like timing pattern
            base_delay = 1.0
            if request_number == 0:
                delay = random.uniform(2.0, 5.0)  # First request slower
            elif request_number < 5:
                delay = base_delay * (1 + random.uniform(-0.3, 0.3))
            else:
                # Occasional longer delays
                if random.random() < 0.1:
                    delay = random.uniform(5.0, 10.0)
                else:
                    delay = base_delay * (1 + random.uniform(-0.5, 0.5))
                    
        time.sleep(delay)
        
    def generate_mouse_movements(self) -> List[Tuple[int, int, int]]:
        """Generate realistic mouse movement data."""
        movements = []
        
        # Start position
        x, y = random.randint(100, 500), random.randint(100, 500)
        
        # Generate movement path
        for _ in range(random.randint(20, 50)):
            # Human-like movement with acceleration/deceleration
            dx = random.randint(-50, 50)
            dy = random.randint(-50, 50)
            
            # Apply smoothing
            steps = random.randint(3, 8)
            for i in range(steps):
                progress = i / steps
                # Ease-in-out curve
                t = progress * progress * (3.0 - 2.0 * progress)
                
                new_x = int(x + dx * t)
                new_y = int(y + dy * t)
                timestamp = int(time.time() * 1000) + i * random.randint(10, 30)
                
                movements.append((new_x, new_y, timestamp))
                
            x += dx
            y += dy
            
        return movements
        
    def _solve_js_challenge(self, challenge: str) -> str:
        """Solve JavaScript challenge (simplified)."""
        # In real implementation, would use JS engine
        # This is a placeholder for demonstration
        
        # Simple math challenge solver
        if '+' in challenge:
            parts = challenge.split('+')
            if len(parts) == 2:
                try:
                    result = int(parts[0]) + int(parts[1])
                    return str(result)
                except:
                    pass
                    
        # Return dummy solution
        return "challenge_solved"
        
    def _solve_captcha(self, captcha_data: Dict) -> str:
        """Solve CAPTCHA challenge."""
        # In real implementation, would use CAPTCHA solving service
        # or ML model
        return "captcha_token"
        
    def _generate_sensor_data(self) -> str:
        """Generate Akamai sensor data."""
        # Simplified sensor data generation
        sensor_data = {
            'sensor_data': {
                'version': '1.75',
                'pm': {  # Page metrics
                    'w': 1920,
                    'h': 1080,
                    'dpr': 1.0,
                },
                'navigation': {
                    'userAgent': 'Mozilla/5.0...',
                    'platform': 'Win32',
                    'language': 'en-US',
                },
                'screen': {
                    'width': 1920,
                    'height': 1080,
                    'colorDepth': 24,
                },
                'timing': {
                    'loadEventEnd': int(time.time() * 1000),
                    'navigationStart': int(time.time() * 1000) - 3000,
                },
                'mouse': self.generate_mouse_movements(),
            }
        }
        
        # Encode as base64
        import json
        json_str = json.dumps(sensor_data, separators=(',', ':'))
        return base64.b64encode(json_str.encode()).decode()
        
    def _solve_pixel_challenge(self, challenge_data: Dict) -> str:
        """Solve pixel/image challenge."""
        # Placeholder implementation
        return "pixel_solution"
        
    def _solve_reese84(self, challenge: str) -> str:
        """Solve Imperva Reese84 challenge."""
        # Simplified implementation
        # Real implementation would parse and execute obfuscated JS
        
        # Generate token
        timestamp = int(time.time() * 1000)
        random_str = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=16))
        
        token_data = f"{timestamp}:{random_str}"
        token_hash = hashlib.sha256(token_data.encode()).hexdigest()
        
        return base64.b64encode(f"reese84:{token_hash}".encode()).decode()
        
    def _solve_cookie_challenge(self, challenge_data: Dict) -> Dict[str, str]:
        """Solve cookie-based challenge."""
        cookies = {}
        
        # Generate challenge cookies
        session_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=32))
        timestamp = int(time.time())
        
        cookies['__session'] = session_id
        cookies['__timestamp'] = str(timestamp)
        
        # Generate verification token
        verify_string = f"{session_id}:{timestamp}:secret"
        verify_token = hashlib.md5(verify_string.encode()).hexdigest()
        cookies['__verify'] = verify_token
        
        return cookies
        
    def _get_random_ip(self) -> str:
        """Generate random IP address."""
        # Use common residential IP ranges
        ranges = [
            (24, 0, 255),    # 24.x.x.x
            (50, 0, 255),    # 50.x.x.x
            (68, 0, 255),    # 68.x.x.x
            (72, 0, 255),    # 72.x.x.x
            (98, 0, 255),    # 98.x.x.x
        ]
        
        first_octet, min_val, max_val = random.choice(ranges)
        return f"{first_octet}.{random.randint(min_val, max_val)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        
    def get_retry_strategy(self, attempt: int) -> Dict[str, any]:
        """Get retry strategy for failed requests."""
        strategy = {
            'should_retry': True,
            'delay': 1.0,
            'change_fingerprint': False,
            'change_proxy': False,
        }
        
        if self.level == EvasionLevel.BASIC:
            strategy['delay'] = 2 ** attempt  # Exponential backoff
            strategy['should_retry'] = attempt < 3
            
        elif self.level == EvasionLevel.ADVANCED:
            strategy['delay'] = random.uniform(1.0, 3.0) * (attempt + 1)
            strategy['should_retry'] = attempt < 5
            strategy['change_fingerprint'] = attempt >= 2
            
        else:  # MAXIMUM
            strategy['delay'] = self._calculate_intelligent_delay(attempt)
            strategy['should_retry'] = attempt < 10
            strategy['change_fingerprint'] = attempt >= 1
            strategy['change_proxy'] = attempt >= 3
            
        return strategy
        
    def _calculate_intelligent_delay(self, attempt: int) -> float:
        """Calculate intelligent retry delay."""
        # Base delay with jitter
        base_delay = 2.0
        jitter = random.uniform(-0.5, 0.5)
        
        # Increase delay for repeated failures
        if attempt < 3:
            delay = base_delay + jitter
        elif attempt < 6:
            delay = base_delay * 2 + jitter
        else:
            # Long delay with occasional quick retry
            if random.random() < 0.2:
                delay = 1.0  # Quick retry
            else:
                delay = random.uniform(10.0, 30.0)
                
        return delay


class MLEvasionEngine:
    """Machine learning-based evasion engine."""
    
    def __init__(self):
        self.success_history = {}
        self.detection_features = {}
        
    def analyze_detection(self, response_data: Dict) -> Dict[str, float]:
        """Analyze response for detection signals."""
        features = {
            'status_code': response_data.get('status_code', 200),
            'response_time': response_data.get('response_time', 0),
            'content_length': len(response_data.get('body', '')),
            'has_challenge': 0,
            'has_captcha': 0,
            'confidence': 0.0,
        }
        
        body = response_data.get('body', '').lower()
        
        # Check for challenges
        challenge_keywords = ['challenge', 'verify', 'robot', 'human', 'security check']
        if any(keyword in body for keyword in challenge_keywords):
            features['has_challenge'] = 1
            
        # Check for CAPTCHA
        captcha_keywords = ['captcha', 'recaptcha', 'hcaptcha', 'puzzle']
        if any(keyword in body for keyword in captcha_keywords):
            features['has_captcha'] = 1
            
        # Calculate detection confidence
        if features['status_code'] in [403, 503]:
            features['confidence'] = 0.9
        elif features['status_code'] == 429:
            features['confidence'] = 0.8
        elif features['has_challenge'] or features['has_captcha']:
            features['confidence'] = 0.7
        elif features['response_time'] > 5000:  # Slow response
            features['confidence'] = 0.3
            
        return features
        
    def predict_best_strategy(self, target_domain: str, current_fingerprint: Dict) -> Dict:
        """Predict best evasion strategy using ML."""
        # Simplified prediction - real implementation would use trained model
        
        strategy = {
            'fingerprint_profile': 'chrome_latest',
            'use_proxy': False,
            'add_delay': True,
            'delay_ms': 1000,
            'headers_to_add': {},
            'confidence': 0.8,
        }
        
        # Check success history
        domain_history = self.success_history.get(target_domain, {})
        
        if domain_history:
            # Use successful strategies
            successful_strategies = [
                s for s, success_rate in domain_history.items()
                if success_rate > 0.7
            ]
            
            if successful_strategies:
                strategy['fingerprint_profile'] = random.choice(successful_strategies)
                strategy['confidence'] = 0.9
                
        # Adjust based on domain
        if 'cloudflare' in target_domain:
            strategy['delay_ms'] = 2000
            strategy['headers_to_add']['CF-Visitor'] = '{"scheme":"https"}'
            
        return strategy
        
    def update_model(self, target_domain: str, strategy: Dict, success: bool):
        """Update ML model with result."""
        if target_domain not in self.success_history:
            self.success_history[target_domain] = {}
            
        strategy_key = strategy.get('fingerprint_profile', 'unknown')
        
        if strategy_key not in self.success_history[target_domain]:
            self.success_history[target_domain][strategy_key] = 0.5
            
        # Update success rate with exponential moving average
        alpha = 0.1
        current_rate = self.success_history[target_domain][strategy_key]
        new_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * current_rate
        
        self.success_history[target_domain][strategy_key] = new_rate