import datetime
import requests
import json
import copy
import re
import time
from constant import FacebookConstants
from profile_handler.profile_by_selenium import FacebookGraphQLCollector
from utils import convert_to_number


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

    def _search_posts(self, hashtag):
        """
        Search posts for a given hashtag using Facebook's GraphQL API.

        Args:
            hashtag (str): The hashtag to search for

        Returns:
            list: A list of posts
        """
        print("get hashtag", hashtag)
        retry = 0
        collected_posts = []
        posts_check = 0
        prev_len = -1
        same_len_count = 0
        loop_index = 0
        payload = {}

        # Get headers and payload from GraphQL collector
        graphql_data = self.graphql_collector.parse_graphql_data()
        if not graphql_data:
            print("Failed to get GraphQL data")
            return collected_posts

        # Get headers and base body from first GraphQL request
        first_request = next(iter(graphql_data.values()))
        headers = FacebookConstants.HEADERS_KW
        headers['Cookie'] = self.cookie  # Add cookie to headers
        
        base_body_str = first_request['payload'] if first_request['payload'] else ''
        
        # Parse form data into dictionary
        base_body = {
            "av": 100011101573199,
            "__aaid": 0,
            "__user": 100011101573199,
            "__a": 1,
            "__req": "9c",
            "__hs": "20230.HYP:comet_pkg.2.1...0",
            "dpr": 1,
            "__ccg": "EXCELLENT",
            "__rev": 1019313438,
            "__s": "z7l8nr:vo1dds:t6nu9l",
            "__hsi": 7507110896699711822,
            "__dyn": "7xeXzWK1ixt0mUyEqxemh0noeEb8nwgUao4ubyQdwSwAyUco2qwJyE24wJwpUe8hwaG0Z82_CxS320qa321Rwwwqo462mcwfG12wOx62G5Usw9m1YwBgK7o6C0Mo4G1hx-3m1mzXw8W58jwGzEaE5e3ym2SU4i5oe8464-5pUfEe88o4Wm7-2K0-obUG2-azqwaW223908O3216xi4UK2K2WEjxK2B08-269wkopg6C13xe3a3Gfw-KufxamEbbxG1fBG2-2K0E8461wwVxG0No",
            "__csr": "g4r9d3i913fbds8MDspNyuZMJ5Tf8ICJd8LJEhWkRbFqYy5iWmR9vexlGgCFa8ZfLILuyqH9syKWFB8ZWHAnabGQGAh7hHyqBLBGqlqjiqACJ5KiKqFGlUDBByUClGWiyUKHKVp9axpqV99HDzaxaiFp9d6y8OVvAACGdHBAFeELBG4K44UC6V8oUkz8B4Bz8S5pGg-78sUK2S9xe498cEshohgaUG2ifwyGbxSeGfwXwDKUhy4m2_yUgxu9G9z8gG2e227ofU52mE4G2yuaxe8DxC2q1lxq2W265U86m2e1fG265omz8b9oC3SU1NE4e1MYxS0sNwDw9a0Uo8U5G2O2sg0MiepVF62B120hK5EpwgQ0zF7g6p0HwhE1240AUOm1Yg1spE1jfo3KwlE1rGvGdgaWyLKrJobHam0JGxiewxxC3Wp39EG8wnUhw0o7e1-w12G080w15K00BEE04I-0dxw4Iw6xgaE2Lwai0q60j20HU2nw2hU0kiw2081eomOzA0pi2K0qu5k1Hw1cK0EU2jw2xo7i0ri0Fomwc60lGgJw3EO00x3wdy0fXg0Bm8wbO09Tw2Qouw3jGo1u4q8gKOw22U0AS0jkw0K0xoy0-8",
            "__hblp": "0rt09G744Uy2CEc8b827x-2612CwMwb-2O740VEaU7y3-q0WE5i12y8doy2OqtuUlBy8S2a3m1cyo461CK1vwYxm2O2aczo3kUmwdG8DwlUhwUxurw9OdwPwaeEK2u1ow9a4o8i0Kw8e0AEC1rweW5UrwBgcE9o2rg4W1rwro1kEeE2jCG6Hw8rxS3y1Lwd-2u0CUnw8O3e2GcwWwJwmU6a1Lwlo24wh831wbK7E8UG1KG3W09mwoEmyE2DwbO8wEzo2dDwc-1dCBwbem6U7S3q2-2-0DE520jS5EfUG0IU4e0V8mxa368wzwDCgy3q0G8eUW4o1GE3kwc2267Au5Q11x23m0gq3W0py0vO0vGi0isx8y1bx6E4G3y0VE5G1Qg4y2K0yp8qw",
            "__comet_req": 15,
            "fb_dtsg": "NAfvgi7H6SVrFqOd8BoDv0snCeSE9IrVb06sw4AgQCIayZHUhN1MqFQ:25:1747793760",
            "jazoest": 25543,
            "lsd": "VyvkXLYQE9sZ4N7xxLp7IH",
            "__spin_r": 1023077640,
            "__spin_b": "trunk",
            "__spin_t": 1736236027,
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "SearchCometInterestsDeepDivePostsListQuery",
            "server_timestamps": "true",
            "doc_id": 9432471083510735
        }

        # Update base_body with values from GraphQL request if available
        if base_body_str:
            for item in base_body_str.split('&'):
                if '=' in item:
                    key, value = item.split('=', 1)
                    # Convert numeric values to int
                    try:
                        if value.isdigit():
                            value = int(value)
                    except ValueError:
                        pass
                    base_body[key] = value

        # Close GraphQL collector after getting headers and body
        self.graphql_collector.close()

        while True:
            posts = []
            var_request = copy.deepcopy(FacebookConstants.VARIABLES)
            input = var_request.get('input')
            input.update({'topic_id': '#' + hashtag})
            var_request.update({'input': input})
            if payload.get('next_cursor'):
                var_request.update({'topic_results_paginating_after_cursor': payload.get('next_cursor')})
            body = base_body.copy()
            body.update({
                "variables": json.dumps(var_request)
            })
            header = FacebookConstants.HEADERS_KW
            # header.update({'cookie': cookie})
            payload = {
                "url": FacebookConstants.API_URL_COLLECT_HASHTAG,
                "headers": header,
                "body": body,
                "method": 'post',
            }

            try:
                response = requests.post(payload.get('url'), headers=payload.get('headers'), data=payload.get('body'))
                response_text = response.text
                
                # Remove "for (;;);" prefix if exists
                if response_text.startswith('for (;;);'):
                    response_text = response_text[9:]
                
                try:
                    response_json = json.loads(response_text)
                    if response_json.get('error'):
                        print(f"Facebook API error: {response_json.get('errorDescription')}")
                        return collected_posts
                except json.JSONDecodeError:
                    pass
                    
                data = self._format_data_response_fb(response_text)
                if data:
                    posts = self._get_response_body(data)
                    cursor = self._get_next_cursor_by_response_fb(data)
                    payload['next_cursor'] = cursor.get('end_cursor')
                    has_more = cursor.get('has_next_page')
                if len(posts) > 0:
                    for post in posts:
                        check = [element for element in collected_posts if post["id"] == element["id"]]
                        if len(check) <= 0:
                            collected_posts.append(post)
                if not cursor.get('has_next_page'):
                    break
                if not has_more:
                    break
                else:
                    time.sleep(3)
            except Exception as e:
                print("Load post by hashtag error", e)
                retry += 1

            posts_check = len(collected_posts)
            print(f"Loop {loop_index} | Total post {posts_check}")

            if retry > self.MAX_HASHTAG_POST_RETRY:
                break
            if posts_check > self.MAX_POST_BY_HASHTAG:
                break

            if posts_check == prev_len:
                same_len_count += 1
                if same_len_count >= 2:  # Break nếu không đổi sau 2 lần
                    break
            else:
                same_len_count = 0
            prev_len = posts_check
            loop_index += 1

        return collected_posts

    def _format_data_response_fb(self, response_text):
        """
        Cleans and formats the Facebook response text by removing unwanted sections.
        """
        label_dict = re.search(r',"extensions":{', response_text)
        if label_dict:
            label_dict_position = label_dict.regs[0][0]
            response_text = response_text[0:label_dict_position]
            response_text = response_text + '}'
        array = response_text.split('xml version')
        i = 0
        html = ''
        for item in array:
            if i == 0:
                html = item
            else:
                label_dict = re.search(r'","', item)
                if label_dict:
                    label_dict_position = label_dict.regs[0][0]
                    xml = item[0:label_dict_position]
                    item = item.replace(xml, '')
                    html = html + item
            i = i + 1
        html = html.replace('"drm_info":[],', '')
        html = html.replace('"drm_info":{},', '')
        array = html.split('"drm_info":"{')
        i = 0
        html = ''
        for item in array:
            if i == 0:
                html = item
            else:
                label_dict = re.search(r'}",', item)
                if label_dict:
                    label_dict_position = label_dict.regs[0][0]
                    xml = item[0:label_dict_position + 3]
                    item = item.replace(xml, '')
                    html = html + item
            i = i + 1
        html = html.replace('"tracking":{},', '')
        array = html.split('"tracking":"{')
        i = 0
        html = ''
        for item in array:
            if i == 0:
                html = item
            else:
                label_dict = re.search(r'}",', item)
                if label_dict:
                    label_dict_position = label_dict.regs[0][0]
                    xml = item[0:label_dict_position + 3]
                    item = item.replace(xml, '')
                    html = html + item
            i = i + 1
        return html

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
                    taken_ats = self._safe_get(item, 'context_layout', 'story', 'comet_sections', 'metadata')
                    comment = like = share = view = taken_at = taken_num = None
                    if taken_ats:
                        for taken in taken_ats:
                            taken = self._safe_get(taken, 'story', 'creation_time')
                            if taken:
                                taken_num = taken
                                taken_at = datetime.datetime.utcfromtimestamp(taken).strftime("%m/%d/%Y")

                    feedback = self._safe_get(item, 'feedback', 'story', 'story_ufi_container', 'story', 'feedback_context', 'feedback_target_with_context')
                    if feedback is None:
                        feedback = self._safe_get(item, 'feedback', 'story', 'comet_feed_ufi_container', 'story', 'feedback_context', 'feedback_target_with_context', 'ufi_renderer', 'feedback', 'comet_ufi_summary_and_actions_renderer', 'feedback')

                    comment = feedback.get('total_comment_count') if feedback is not None else None
                    if comment is None:
                        try:
                            comment = self._safe_get(feedback, 'comment_rendering_instance', 'comments', 'total_count')
                        except (TypeError, KeyError):
                            pass

                    like = feedback.get('comet_ufi_summary_and_actions_renderer',{}).get('feedback',{}).get('i18n_reaction_count') if feedback is not None else None
                    share = feedback.get('comet_ufi_summary_and_actions_renderer',{}).get('feedback',{}).get('i18n_share_count') if feedback is not None else None
                    view = feedback.get('comet_ufi_summary_and_actions_renderer',{}).get('feedback',{}).get('video_view_count') if feedback is not None else None

                    if feedback is None:
                        try:
                            feedback = self._safe_get(item, 'feedback', 'story', 'comet_feed_ufi_container', 'story', 'story_ufi_container', 'story', 'feedback_context', 'feedback_target_with_context')
                            comment = self._safe_get(feedback, 'comment_rendering_instance', 'comments', 'total_count')
                            like = self._safe_get(feedback, 'comet_ufi_summary_and_actions_renderer', 'feedback', 'i18n_reaction_count')
                            share = self._safe_get(feedback, 'comet_ufi_summary_and_actions_renderer', 'feedback', 'i18n_share_count')
                            view = self._safe_get(feedback, 'comet_ufi_summary_and_actions_renderer', 'feedback', 'video_view_count')
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
                        username = self._extract_facebook_username(profile_url)
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
                        feedback = self._safe_get(item, 'comet_sections', 'feedback', 'story', 'feedback_context', 'feedback_target_with_context', 'ufi_renderer', 'feedback', 'comet_ufi_summary_and_actions_renderer', 'feedback')
                        taken_ats = self._safe_get(item, 'context_layout', 'story', 'comet_sections', 'metadata')
                        if feedback is None:
                            feedback = self._safe_get(item, 'feedback', 'story', 'comet_feed_ufi_container', 'story', 'feedback_context', 'feedback_target_with_context', 'ufi_renderer', 'feedback', 'comet_ufi_summary_and_actions_renderer', 'feedback')
                        comment = feedback.get('total_comment_count') if feedback is not None else None
                        like = feedback.get('i18n_reaction_count') if feedback is not None else None
                        share = feedback.get('i18n_share_count') if feedback is not None else None
                        view = feedback.get('video_view_count') if feedback is not None else None
                        user_id = user_name = profile_url = taken_at = taken_num = None
                        if taken_ats:
                            for taken in taken_ats:
                                taken = self._safe_get(taken, 'story', 'creation_time')
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
                            username = self._extract_facebook_username(profile_url)
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

    def _get_next_cursor_by_response_fb(self, body) -> dict:
        try:
            body = json.loads(body)
            resource_response_dict = self._safe_get(body, 'data', 'topic_deep_dive', 'rendering_strategies', 'page_info')
            cursor = {
                'has_next_page': resource_response_dict['has_next_page'],
                'end_cursor': resource_response_dict['end_cursor']
            }
        except (TypeError, KeyError):
            cursor = {'has_next_page': False, 'end_cursor': None}

        return cursor

    @staticmethod
    def _safe_get(dct, *keys):
        for key in keys:
            try:
                dct = dct[key]
            except KeyError:
                return None
        return dct

    @staticmethod
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

