import datetime
import requests
import json
import copy
import re
import time
from facebook_collector.constant import FacebookConstants
from facebook_collector.profile_handler.graphql_handler import FacebookGraphQLCollector
from facebook_collector.utils import convert_to_number


class FacebookHashtagCollector:
    """
    A class to collect Facebook posts by hashtag using cookie authentication.
    """

    def __init__(self, cookie, max_post_by_hashtag=100, max_hashtag_post_retry=3):
        """
        Initialize the collector with cookie and configuration.

        Args:
            cookie (str): Facebook authentication cookie
            max_post_by_hashtag (int): Maximum number of posts to collect per hashtag (default: 100)
            max_hashtag_post_retry (int): Maximum number of retries for hashtag post collection (default: 3)
        """
        self.cookie = cookie
        self.MAX_POST_BY_HASHTAG = max_post_by_hashtag
        self.MAX_HASHTAG_POST_RETRY = max_hashtag_post_retry
        self.graphql_collector = FacebookGraphQLCollector(cookie)

    def collect_posts_by_hashtag(self, hashtag):
        """
        Collect posts for a single hashtag.

        Args:
            hashtag (str): The hashtag to collect posts for

        Returns:
            list: A list of collected posts with their details
        """
        try:
            content_list = self._search_posts(hashtag)
            print(f"Found {len(content_list)} posts for hashtag {hashtag}")
            return content_list
        except Exception as e:
            print(f"Error collecting posts for hashtag {hashtag}: {e}")
            return []

    def _search_posts(self, hashtag, max_posts=100):
        """
        Search for posts using hashtag
        :param hashtag: Hashtag to search for
        :param max_posts: Maximum number of posts to collect
        :return: List of posts
        """
        posts = []
        seen_post_ids = set()
        retry_count = 0
        
        # Navigate to search page
        search_url = f"https://www.facebook.com/hashtag/{hashtag}"
        self.graphql_collector.navigate_to_url(search_url)
        
        # Scroll and collect posts until we reach max_posts or no more data
        while len(posts) < max_posts and retry_count < self.MAX_HASHTAG_POST_RETRY:
            # Get GraphQL requests
            logs = self.graphql_collector.get_performance_logs()
            
            # Process each log
            for log in logs:
                try:
                    body = log['body']
                    
                    # Parse lấy dict đầu tiên
                    try:
                        # Tìm vị trí bắt đầu của dict đầu tiên
                        start_idx = body.find('{')
                        if start_idx != -1:
                            # Tìm vị trí kết thúc của dict đầu tiên
                            stack = []
                            end_idx = start_idx
                            for i in range(start_idx, len(body)):
                                if body[i] == '{':
                                    stack.append(i)
                                elif body[i] == '}':
                                    if stack:
                                        stack.pop()
                                        if not stack:  # Nếu stack rỗng, đã tìm thấy dấu } tương ứng
                                            end_idx = i
                                            break
                            
                            # Lấy dict đầu tiên
                            first_dict = body[start_idx:end_idx + 1]
                            data = json.loads(first_dict)
                            
                            # Extract posts using _get_response_body
                            extracted_posts = self._get_response_body(data)
                            for post in extracted_posts:
                                post_id = post['id']
                                if post_id not in seen_post_ids:
                                    seen_post_ids.add(post_id)
                                    posts.append(post)
                                    
                                    if len(posts) >= self.MAX_POST_BY_HASHTAG:
                                        return posts
                    except Exception as e:
                        print(f"Error parsing first dict: {str(e)}")
                        retry_count += 1
                        if retry_count >= self.MAX_HASHTAG_POST_RETRY:
                            print(f"Max retries reached ({self.MAX_HASHTAG_POST_RETRY}). Stopping collection.")
                            return posts
                        continue
                except Exception as e:
                    print(f"Error processing log: {str(e)}")
                    retry_count += 1
                    if retry_count >= self.MAX_HASHTAG_POST_RETRY:
                        print(f"Max retries reached ({self.MAX_HASHTAG_POST_RETRY}). Stopping collection.")
                        return posts
                    continue
            
            # Scroll to load more content
            self.graphql_collector.scroll_page()
            time.sleep(2)  # Wait for new content to load
        
        return posts

    def _get_response_body(self, response_text):
        """
        Extracts and formats post data from the Facebook response JSON.
        """
        response_data = []
        print('-------process body---')
        response_text = json.loads(response_text)
        data = response_text.get('data') if response_text.get('data') is not None else {}
        data = data.get('topic_deep_dive') if data.get('topic_deep_dive') is not None else {}
        data = data.get('rendering_strategies') if data.get('rendering_strategies') is not None else {}
        data = data.get('edges') if data.get('edges') is not None else []

        if len(data) > 0:
            for item in data:
                item = item.get('rendering_strategy') if item.get('rendering_strategy') else {}
                item = item.get('explore_view_model') if item.get('explore_view_model') else {}
                item = item.get('story') if item.get('story') else None
                post_id = None
                caption = None
                is_page = True if '"delegate_page": {' in json.dumps(item) else False
                if is_page == False:
                    is_page = True if '"delegate_page":' not in json.dumps(item) else False

                if item:
                    post_id = item.get('post_id')
                    item = item.get('comet_sections') if item.get('comet_sections') else {}
                    taken_ats = _safe_get(item, 'context_layout', 'story', 'comet_sections', 'metadata')
                    comment = like = share = view = taken_at = taken_num = None
                    if taken_ats:
                        for taken in taken_ats:
                            taken = _safe_get(taken, 'story', 'creation_time')
                            if taken:
                                taken_num = taken
                                taken_at = datetime.datetime.utcfromtimestamp(taken).strftime("%m/%d/%Y")

                    feedback = _safe_get(item, 'feedback', 'story', 'story_ufi_container', 'story', 'feedback_context', 'feedback_target_with_context')
                    if feedback is None:
                        feedback = _safe_get(item, 'feedback', 'story', 'comet_feed_ufi_container', 'story', 'feedback_context', 'feedback_target_with_context', 'ufi_renderer', 'feedback', 'comet_ufi_summary_and_actions_renderer', 'feedback')

                    comment = feedback.get('total_comment_count') if feedback is not None else None
                    if comment is None:
                        try:
                            comment = _safe_get(feedback, 'comment_rendering_instance', 'comments', 'total_count')
                        except (TypeError, KeyError):
                            pass

                    like = feedback.get('comet_ufi_summary_and_actions_renderer',{}).get('feedback',{}).get('i18n_reaction_count') if feedback is not None else None
                    share = feedback.get('comet_ufi_summary_and_actions_renderer',{}).get('feedback',{}).get('i18n_share_count') if feedback is not None else None
                    view = feedback.get('comet_ufi_summary_and_actions_renderer',{}).get('feedback',{}).get('video_view_count') if feedback is not None else None

                    if feedback is None:
                        try:
                            feedback = _safe_get(item, 'feedback', 'story', 'comet_feed_ufi_container', 'story', 'story_ufi_container', 'story', 'feedback_context', 'feedback_target_with_context')
                            comment = _safe_get(feedback, 'comment_rendering_instance', 'comments', 'total_count')
                            like = _safe_get(feedback, 'comet_ufi_summary_and_actions_renderer', 'feedback', 'i18n_reaction_count')
                            share = _safe_get(feedback, 'comet_ufi_summary_and_actions_renderer', 'feedback', 'i18n_share_count')
                            view = _safe_get(feedback, 'comet_ufi_summary_and_actions_renderer', 'feedback', 'video_view_count')
                        except (TypeError, KeyError):
                            pass

                    item = item.get('content') if item.get('content') else {}
                    item = item.get('story') if item.get('story') else {}
                    actors = item.get('actors') if item.get('actors') else []
                    message = item.get('message') if item.get('message') else None
                    other_post = item.get('attached_story') if item.get('attached_story') else None
                    if message:
                        caption = message.get('text') if message.get('text') else None
                    user_id = user_name = profile_url = None
                    if len(actors) > 0:
                        user_id = actors[0].get('id') if actors[0].get('id') is not None else None
                        user_name = actors[0].get('name') if actors[0].get('name') is not None else None
                        profile_url = actors[0].get('url') if actors[0].get('url') is not None else None
                    post_url = item.get('wwwURL') if item.get('wwwURL') else None
                    item = item.get('comet_sections') if item.get('comet_sections') else {}
                    item = item.get('message') if item.get('message') else {}
                    item = item.get('story') if item.get('story') else {}
                    if other_post is None:
                        other_post = item.get('attached_story') if item.get('attached_story') else None
                    item = item.get('message') if item.get('message') else {}
                    if caption is None:
                        caption = item.get('text') if item.get('text') else None
                    if post_id:
                        username = _extract_facebook_username(profile_url)
                        account_type = 'profile'
                        if profile_url is not None:
                            if username == 'l.php':
                                account_type = 'instagram'
                            elif '/group/' in profile_url:
                                account_type = 'group'
                            elif '/people/' in profile_url:
                                account_type = 'profile'
                            elif is_page == True:
                                account_type = 'page'
                        response_data.append({
                            'user_id': user_id,
                            'name': user_name,
                            'profile_url': profile_url,
                            'username': username,
                            'link': post_url,
                            'id': post_id,
                            'caption': caption,
                            'like': convert_to_number(str(like).replace(',', '.')) if like is not None else '',
                            'comment': convert_to_number(str(comment).replace(',', '.')) if comment is not None else '',
                            'share': convert_to_number(str(share).replace(',', '.')) if share is not None else '',
                            'view': convert_to_number(str(view).replace(',', '.')) if view is not None else '',
                            'taken_at': taken_at,
                            'taken_num': taken_num,
                            'account_type': account_type
                        })
                    if other_post:
                        post_id = other_post.get('id') if other_post.get('id') else None
                        post_url = other_post.get('wwwURL') if other_post.get('wwwURL') else None
                        is_page = True if '"delegate_page": {' in json.dumps(other_post) else False
                        if is_page == False:
                            is_page = True if '"delegate_page":' not in json.dumps(item) else False
                        actors = item.get('actors') if item.get('actors') else []
                        comment = like = share = view = None
                        feedback = _safe_get(item, 'comet_sections', 'feedback', 'story', 'feedback_context', 'feedback_target_with_context', 'ufi_renderer', 'feedback', 'comet_ufi_summary_and_actions_renderer', 'feedback')
                        taken_ats = _safe_get(item, 'context_layout', 'story', 'comet_sections', 'metadata')
                        if feedback is None:
                            feedback = _safe_get(item, 'feedback', 'story', 'comet_feed_ufi_container', 'story', 'feedback_context', 'feedback_target_with_context', 'ufi_renderer', 'feedback', 'comet_ufi_summary_and_actions_renderer', 'feedback')
                        comment = feedback.get('total_comment_count') if feedback is not None else None
                        like = feedback.get('i18n_reaction_count') if feedback is not None else None
                        share = feedback.get('i18n_share_count') if feedback is not None else None
                        view = feedback.get('video_view_count') if feedback is not None else None
                        user_id = user_name = profile_url = taken_at = taken_num = None
                        if taken_ats:
                            for taken in taken_ats:
                                taken = _safe_get(taken, 'story', 'creation_time')
                                if taken:
                                    taken_num = taken
                                    taken_at = datetime.datetime.utcfromtimestamp(taken).strftime("%m/%d/%Y")
                        if len(actors) > 0:
                            user_id = actors[0].get('id') if actors[0].get('id') is not None else None
                            user_name = actors[0].get('name') if actors[0].get('name') is not None else None
                            profile_url = actors[0].get('url') if actors[0].get('url') is not None else None
                        other_post = other_post.get('message') if other_post.get('message') else {}
                        caption = other_post.get('text') if other_post.get('text') else None
                        if post_id:
                            username = _extract_facebook_username(profile_url)
                            account_type = 'profile'
                            if profile_url is not None:
                                if username == 'l.php':
                                    account_type = 'instagram'
                                elif '/group/' in profile_url:
                                    account_type = 'group'
                                elif '/people/' in profile_url:
                                    account_type = 'profile'
                                elif is_page == True:
                                    account_type = 'page'
                            response_data.append({
                                'user_id': user_id,
                                'name': user_name,
                                'profile_url': profile_url,
                                'username': username,
                                'link': post_url,
                                'id': post_id,
                                'caption': caption,
                                'like': convert_to_number(str(like).replace(',', '.')) if like is not None else '',
                                'comment': convert_to_number(str(comment).replace(',', '.')) if comment is not None else '',
                                'share': convert_to_number(str(share).replace(',', '.')) if share is not None else '',
                                'view': convert_to_number(str(view).replace(',', '.')) if view is not None else '',
                                'taken_at': taken_at,
                                'taken_num': taken_num,
                                'account_type': account_type
                            })

        return response_data

def _safe_get(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct


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
    
def convert_to_number(string):
    if string is None:
        return string

    if isinstance(string, str):
        if 'K' in string:
            return int(float(string.replace('K', '')) * 1_000)
        elif 'M' in string:
            return int(float(string.replace('M', '')) * 1_000_000)
    return int(string)
        
def main():
    cookie = "sb=O7BCZ76WW9WsEOdAYM6yzAAv; ps_l=1; ps_n=1; datr=QTctaJBjzmCzCkvauajS22xQ; locale=en_US; c_user=100011101573199; fr=1JRRpgjJOzgRgOxl6.AWdieRsENWQeleuiwhzpnewJoICAn5M6AaY7LmAxWRKJwu_ZIsY.BoLp1_..AAA.0.0.BoLp1_.AWdkzB5ZOi3vQz2jn8RxUw7Zuog; xs=25%3AfCTnO2_KnAfdyQ%3A2%3A1747793760%3A-1%3A6199%3A%3AAcUi5q2xXhWZMKpDWSdeU-tANQyo0K6Jenk9EHKi8Q; wd=1014x966; presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1747885467766%2C%22v%22%3A1%7D"
    collector = FacebookHashtagCollector(
        cookie=cookie,
        max_post_by_hashtag=10,
        max_hashtag_post_retry=2
    )
    
    try:
        posts = collector.collect_posts_by_hashtag('test')
        print("\nCollected posts:", posts)
    finally:
        if hasattr(collector, 'graphql_collector'):
            collector.graphql_collector.close()


if __name__ == '__main__':
    main() 

