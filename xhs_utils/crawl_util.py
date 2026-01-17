import datetime
from loguru import logger
from apis.xhs_pc_apis import XHS_Apis

def fetch_note_detail_task(note, cookies_str, comment_count=10):
    """
    Fetch detail info and comments for a single note.
    Common function used by app.py and other tools.
    :param note: 笔记基本信息
    :param cookies_str: Cookie字符串
    :param comment_count: 要获取的评论数量，默认10条
    """
    try:
        xhs_pc_apis = XHS_Apis()
        note_id = note.get('id') or note.get('note_id')
        note['note_id'] = note_id  # Ensure note_id is present for frontend
        xsec_token = note.get('xsec_token', '')
        
        if not note_id:
            return note

        # 1. Fetch Content (Desc) and Stats
        # Construct a fake URL because get_note_info expects it to parse parameters
        # We pass xsec_token raw; xhs_pc_apis.py's simple parser should handle it now that we fixed the split limit.
        fake_url = f"https://www.xiaohongshu.com/explore/{note_id}?xsec_token={xsec_token}&xsec_source=pc_creatormng"
        
        succ, msg, detail = xhs_pc_apis.get_note_info(fake_url, cookies_str)
        logger.debug(f"笔记详情API返回: {msg}, 成功: {succ}")
        
        # 初始化图片相关字段
        note.setdefault('image_urls', [])
        note.setdefault('images_list', [])
        
        # 首先检查初始笔记数据中是否有可用的图片URL
        initial_image_urls = []
        if note.get('image_list') and isinstance(note['image_list'], list):
            for img in note['image_list']:
                if isinstance(img, dict):
                    if img.get('url'):
                        initial_image_urls.append(img['url'])
                elif isinstance(img, str):
                    initial_image_urls.append(img)
            logger.debug(f"初始数据中的图片URL: {initial_image_urls}")
        
        # 尝试从API响应中提取图片数据
        if succ and detail.get('data', {}).get('items'):
            item = detail['data']['items'][0]
            note_card = item.get('note_card', {})
            logger.debug(f"Note card包含的键: {list(note_card.keys())}")
            
            # Update desc
            note['desc'] = note_card.get('desc', '')
            
            # Update title
            if 'title' in note_card:
                note['display_title'] = note_card['title']
                note['title'] = note_card['title']
                
            # Update time
            if 'time' in note_card:
                note['time'] = note_card['time']
                note['upload_time'] = note_card['time']
            
            # Update stats
            interact_info = note_card.get('interact_info', {})
            note['liked_count'] = interact_info.get('liked_count', 0)
            note['collected_count'] = interact_info.get('collected_count', 0)
            note['comment_count'] = interact_info.get('comment_count', 0)
            note['share_count'] = interact_info.get('share_count', 0)
            
            # 提取图片URL
            extracted_image_urls = []
            processed_images = []
            
            # 1. 从note_card.image_list提取图片
            if 'image_list' in note_card:
                logger.debug(f"处理note_card.image_list: {len(note_card['image_list'])}")
                for img in note_card['image_list']:
                    try:
                        img_url = None
                        # 尝试不同的图片URL提取方式
                        if 'info_list' in img and isinstance(img['info_list'], list):
                            # 尝试多个info_list索引，从0开始
                            for idx in [0, 1, 2]:
                                if len(img['info_list']) > idx:
                                    info_item = img['info_list'][idx]
                                    if isinstance(info_item, dict) and info_item.get('url'):
                                        img_url = info_item['url']
                                        break
                        elif 'url' in img:
                            img_url = img['url']
                        elif 'src' in img:
                            img_url = img['src']
                        
                        if img_url:
                            extracted_image_urls.append(img_url)
                            processed_images.append({'url': img_url})
                            logger.debug(f"成功提取图片URL: {img_url}")
                    except Exception as e:
                        logger.debug(f"提取图片URL失败: {e}, 图片数据: {img}")
            
            # 2. 提取封面图片
            cover_url = None
            if 'cover' in note_card:
                cover = note_card['cover']
                if isinstance(cover, dict):
                    cover_url = cover.get('url') or cover.get('url_default') or cover.get('url_pre')
                    note['cover'] = {'url': cover_url}
                elif isinstance(cover, str):
                    cover_url = cover
                    note['cover'] = {'url': cover_url}
                logger.debug(f"提取到封面URL: {cover_url}")
            
            # 3. 如果没有封面，使用第一张图片作为封面
            if not cover_url and extracted_image_urls:
                cover_url = extracted_image_urls[0]
                note['cover'] = {'url': cover_url}
                logger.debug(f"使用第一张图片作为封面: {cover_url}")
            
            # 4. 合并图片URL，去重
            all_image_urls = list(set(extracted_image_urls + initial_image_urls))
            note['image_urls'] = all_image_urls
            note['images_list'] = [{'url': url} for url in all_image_urls]
            
            logger.debug(f"最终图片URL列表: {all_image_urls}")
            logger.debug(f"封面URL: {note.get('cover', {}).get('url')}")
            
            if 'video' in note_card:
                 note['video'] = note_card['video']
            
        else:
            note['desc'] = '' # Default empty if failed
            logger.debug(f"获取笔记详情失败，使用初始数据: {note.get('cover')}, {note.get('image_list')}")
            
            # 如果API调用失败，使用初始笔记数据中的图片信息
            if initial_image_urls:
                note['image_urls'] = initial_image_urls
                note['images_list'] = [{'url': url} for url in initial_image_urls]
                if not note.get('cover'):
                    note['cover'] = {'url': initial_image_urls[0]}
                logger.debug(f"API失败后，使用初始数据中的图片URL: {initial_image_urls}")
            
        # 最终验证：如果没有图片URL，尝试从cover中提取
        if not note.get('image_urls') and note.get('cover') and note['cover'].get('url'):
            cover_url = note['cover']['url']
            note['image_urls'] = [cover_url]
            note['images_list'] = [{'url': cover_url}]
            logger.debug(f"从封面提取图片URL: {cover_url}")
        
        logger.debug(f"笔记处理完成，图片URL数量: {len(note.get('image_urls', []))}, 封面URL: {note.get('cover', {}).get('url')}")

        # 2. Fetch Comments with custom count support
        note['comments_list'] = []
        
        # Only fetch comments if comment_count > 0
        if comment_count <= 0:
            return note
        
        try:
            if comment_count > 30:  # 如果需要的评论数超过30条，使用get_note_all_out_comment获取全部评论
                # 获取全部评论
                succ, msg, all_comments = xhs_pc_apis.get_note_all_out_comment(note_id, xsec_token, cookies_str)
                if succ:
                    # 只取指定数量的评论
                    comments = all_comments[:comment_count] if len(all_comments) > comment_count else all_comments
                else:
                    logger.error(f"获取全部评论失败: {msg}")
                    comments = []
            else:  # 如果需要的评论数少于等于30条，使用分页获取
                comments = []
                cursor = ""
                has_more = True
                
                while len(comments) < comment_count and has_more:
                    succ, msg, comments_res = xhs_pc_apis.get_note_out_comment(note_id, cursor, xsec_token, cookies_str)
                    if succ:
                        page_comments = comments_res.get('data', {}).get('comments', [])
                        if page_comments:
                            comments.extend(page_comments)
                            # 检查是否还有更多评论
                            has_more = comments_res.get('data', {}).get('has_more', False)
                            # 获取下一页的cursor
                            cursor = comments_res.get('data', {}).get('cursor', "")
                        else:
                            has_more = False
                    else:
                        logger.error(f"获取评论失败: {msg}")
                        break
                
                # 只取指定数量的评论
                if len(comments) > comment_count:
                    comments = comments[:comment_count]
            
            # Extract text from comments to keep it simple
            for c in comments:
                note['comments_list'].append({
                    'user': c.get('user_info', {}).get('nickname', 'Unknown'),
                    'content': c.get('content', ''),
                    'time': c.get('create_time', 0)
                })
        except Exception as e:
            logger.error(f"获取评论时发生错误: {e}")
            note['comments_list'] = []
            
    except Exception as e:
        logger.error(f"Error processing note {note.get('id')}: {e}")
    
    return note
