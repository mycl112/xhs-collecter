import datetime
from apis.xhs_pc_apis import XHS_Apis

def fetch_note_detail_task(note, cookies_str):
    """
    Fetch detail info and comments for a single note.
    Common function used by app.py and other tools.
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
        if succ and detail.get('data', {}).get('items'):
            item = detail['data']['items'][0]
            note_card = item.get('note_card', {})
            
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
            
            # Update cover/images
            if 'image_list' in note_card:
                # Map 'image_list' from API to 'images_list' for data_util
                # note_card['image_list'] elements usually have 'info_list'
                processed_images = []
                for img in note_card['image_list']:
                    if 'info_list' in img and len(img['info_list']) > 0:
                        # Try to find the best quality image, usually index 1 or 0
                        # handle_note_info uses index 1, let's try that or fallback to 0
                        idx = 1 if len(img['info_list']) > 1 else 0
                        url = img['info_list'][idx].get('url', '')
                        processed_images.append({'url': url})
                    elif 'url' in img:
                         processed_images.append({'url': img['url']})
                
                note['images_list'] = processed_images
            
            if 'cover' in note_card:
                note['cover'] = note_card['cover']
                # Fix empty url in cover by using url_default or url_pre
                if not note['cover'].get('url'):
                    note['cover']['url'] = note['cover'].get('url_default', '') or note['cover'].get('url_pre', '')
                
            if 'video' in note_card:
                 note['video'] = note_card['video']
            
        else:
            note['desc'] = '' # Default empty if failed

        # 2. Fetch Comments (First page only for performance)
        # We use get_note_out_comment directly
        succ, msg, comments_res = xhs_pc_apis.get_note_out_comment(note_id, "", xsec_token, cookies_str)
        if succ:
            comments = comments_res.get('data', {}).get('comments', [])
            # Extract text from comments to keep it simple
            note['comments_list'] = []
            for c in comments:
                note['comments_list'].append({
                    'user': c.get('user_info', {}).get('nickname', 'Unknown'),
                    'content': c.get('content', ''),
                    'time': c.get('create_time', 0)
                })
        else:
            note['comments_list'] = []
            
    except Exception as e:
        print(f"Error processing note {note.get('id')}: {e}")
    
    return note
