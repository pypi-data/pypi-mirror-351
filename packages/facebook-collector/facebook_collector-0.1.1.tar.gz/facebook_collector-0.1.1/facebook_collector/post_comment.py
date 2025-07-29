import datetime
import json
import time
from facebook_collector.constant import FacebookConstants
from facebook_collector.profile_handler.graphql_handler import FacebookGraphQLCollector
from facebook_collector.utils import convert_to_number


class FacebookPostCommentCollector:
    """
    A class to collect Facebook post comments using cookie authentication.
    """

    def __init__(self, cookie, max_comments=100, max_comment_retry=3):
        """
        Initialize the collector with cookie and configuration.

        Args:
            cookie (str): Facebook authentication cookie
            max_comments (int): Maximum number of comments to collect per post (default: 100)
            max_comment_retry (int): Maximum number of retries for comment collection (default: 3)
        """
        self.cookie = cookie
        self.MAX_COMMENTS = max_comments
        self.MAX_COMMENT_RETRY = max_comment_retry
        self.graphql_collector = FacebookGraphQLCollector(cookie)

    def collect_post_comments(self, post_url):
        """
        Collect comments for a single post.

        Args:
            post_url (str): The URL of the post to collect comments from

        Returns:
            list: A list of collected comments with their details
        """
        try:
            comments_list = self._get_comments(post_url)
            print(f"Found {len(comments_list)} comments for post {post_url}")
            return comments_list
        except Exception as e:
            print(f"Error collecting comments for post {post_url}: {e}")
            return []

    def _get_comments(self, post_url, max_comments=100):
        """
        Get comments from a post
        :param post_url: URL of the post
        :param max_comments: Maximum number of comments to collect
        :return: List of comments
        """
        comments = []
        seen_comment_ids = set()
        retry_count = 0
        
        # Navigate to post page
        self.graphql_collector.navigate_to_url(post_url)
        
        # Scroll and collect comments until we reach max_comments or no more data
        while len(comments) < max_comments and retry_count < self.MAX_COMMENT_RETRY:
            # Get GraphQL requests
            logs = self.graphql_collector.get_performance_logs()
            
            # Process each log
            for log in logs:
                try:
                    body = log['body']
                    
                    # Parse first dict
                    try:
                        start_idx = body.find('{')
                        if start_idx != -1:
                            stack = []
                            end_idx = start_idx
                            for i in range(start_idx, len(body)):
                                if body[i] == '{':
                                    stack.append(i)
                                elif body[i] == '}':
                                    if stack:
                                        stack.pop()
                                        if not stack:
                                            end_idx = i
                                            break
                            
                            first_dict = body[start_idx:end_idx + 1]
                            data = json.loads(first_dict)
                            
                            # Extract comments
                            extracted_comments = self._get_response_body(data)
                            for comment in extracted_comments:
                                comment_id = comment['id']
                                if comment_id not in seen_comment_ids:
                                    seen_comment_ids.add(comment_id)
                                    comments.append(comment)
                                    
                                    if len(comments) >= self.MAX_COMMENTS:
                                        return comments
                    except Exception as e:
                        print(f"Error parsing first dict: {str(e)}")
                        retry_count += 1
                        if retry_count >= self.MAX_COMMENT_RETRY:
                            print(f"Max retries reached ({self.MAX_COMMENT_RETRY}). Stopping collection.")
                            return comments
                        continue
                except Exception as e:
                    print(f"Error processing log: {str(e)}")
                    retry_count += 1
                    if retry_count >= self.MAX_COMMENT_RETRY:
                        print(f"Max retries reached ({self.MAX_COMMENT_RETRY}). Stopping collection.")
                        return comments
                    continue
            
            # Scroll to load more comments
            self.graphql_collector.scroll_page()
            time.sleep(2)  # Wait for new content to load
        
        return comments

    def _get_response_body(self, response_text):
        """
        Extracts and formats comment data from the Facebook response JSON.
        """
        response_data = []
        print('-------process comments---')
        
        data = response_text.get('data') if response_text.get('data') is not None else {}
        data = data.get('node') if data.get('node') is not None else {}
        data = data.get('comments') if data.get('comments') is not None else {}
        edges = data.get('edges') if data.get('edges') is not None else []

        if len(edges) > 0:
            for edge in edges:
                node = edge.get('node') if edge.get('node') else {}
                if not node:
                    continue

                comment_id = node.get('id')
                message = node.get('message', {}).get('text') if node.get('message') else None
                created_time = node.get('created_time')
                taken_at = None
                taken_num = None
                
                if created_time:
                    taken_num = created_time
                    taken_at = datetime.datetime.utcfromtimestamp(created_time).strftime("%m/%d/%Y")

                # Get author information
                author = node.get('author') if node.get('author') else {}
                user_id = author.get('id')
                user_name = author.get('name')
                profile_url = author.get('url')
                username = _extract_facebook_username(profile_url) if profile_url else None

                # Get reaction counts
                reactions = node.get('reactions', {})
                like_count = reactions.get('count') if reactions else 0

                if comment_id:
                    response_data.append({
                        'id': comment_id,
                        'user_id': user_id,
                        'name': user_name,
                        'profile_url': profile_url,
                        'username': username,
                        'message': message,
                        'like': convert_to_number(str(like_count)) if like_count is not None else 0,
                        'taken_at': taken_at,
                        'taken_num': taken_num
                    })

        return response_data


def _extract_facebook_username(url):
    try:
        username_regex = re.compile(r'(?:https?://)?(?:www\.)?(?:m\.)?facebook\.com/(?:profile\.php\?id=)?([\w\-\.]+)')
        match = username_regex.search(url)
        if match:
            return match.group(1)
        else:
            return None
    except:
        return None


def main():
    cookie = "YOUR_FACEBOOK_COOKIE"
    collector = FacebookPostCommentCollector(
        cookie=cookie,
        max_comments=10,
        max_comment_retry=3
    )
    
    try:
        comments = collector.collect_post_comments('https://www.facebook.com/post_url_here')
        print("\nCollected comments:", comments)
    finally:
        if hasattr(collector, 'graphql_collector'):
            collector.graphql_collector.close()


if __name__ == '__main__':
    main()
