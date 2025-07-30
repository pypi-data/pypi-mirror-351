from bs4 import BeautifulSoup
import re
from graphql_handler import FacebookGraphQLCollector

class FacebookProfileCollector:
    def __init__(self, cookie):
        """
        Initialize the collector with cookie
        :param cookie: Facebook cookie string
        """
        self.cookie = cookie
        self.collector = None

    def setup(self):
        """
        Setup the Selenium collector
        """
        self.collector = FacebookGraphQLCollector(self.cookie)

    def extract_profile_info(self, html_content, file_name):
        """
        Extract profile information from HTML content
        :param html_content: HTML content of the profile page
        :param file_name: Username from URL
        :return: Dictionary containing profile information
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract username from URL
        username = file_name
        
        # Extract full name
        name_raw = soup.find('h1', class_="html-h1 xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1vvkbs x1heor9g x1qlqyl8 x1pd3egz x1a2a7pz")
        full_name = name_raw.text if name_raw else None
        
        # Extract followers count
        data_raw = soup.find_all('a', class_="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xkrqix3 x1sur9pj xi81zsa x1s688f")
        
        # Pattern to match different types of connections
        patterns = {
            'followers': r'(\d+(?:\.\d+)?[KkMm]?)\s+followers',
            'friends': r'(\d+(?:\.\d+)?[KkMm]?)\s+friends',
            'following': r'(\d+(?:\.\d+)?[KkMm]?)\s+following'
        }
        
        # Store all connection counts
        connections = {}
        
        for i in data_raw:
            text = i.text.lower()
            for conn_type, pattern in patterns.items():
                match = re.search(pattern, text)
                if match:
                    connections[conn_type] = match.group(1)
                    break
        
        # Extract bio
        bio_raw = soup.find('span', class_="x193iq5w xeuugli x13faqbe x1vvkbs x10flsy6 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x41vudc x6prxxf xvq8zen xo1l8bm xzsf02u")
        bio = bio_raw.text if bio_raw else None
        
        return {
            "username": username,
            "full_name": full_name,
            "followers": connections.get('followers'),
            "friends": connections.get('friends'),
            "following": connections.get('following'),
            "bio": bio
        }

    def get_profile_info(self, profile_url):
        """
        Get profile information using Selenium and GraphQL handler
        :param profile_url: Facebook profile URL
        :return: Dictionary containing profile information
        """
        if not self.collector:
            self.setup()
            
        try:
            # Navigate to profile page
            self.collector.navigate_to_url(profile_url)
            
            # Get page source after navigation
            html_content = self.collector.driver.page_source
            
            # Extract profile information
            profile_info = self.extract_profile_info(html_content, profile_url.split('/')[-1])
            
            return profile_info
        except Exception as e:
            print(f"Error getting profile info: {str(e)}")
            return None

    def close(self):
        """
        Close the Selenium collector
        """
        if self.collector:
            self.collector.close()
            self.collector = None