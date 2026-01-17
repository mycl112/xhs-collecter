import json
import os
import re
import time
import openpyxl
import requests
from loguru import logger
from retry import retry


def norm_str(str):
    new_str = re.sub(r"|[\\/:*?\"<>| ]+", "", str).replace('\n', '').replace('\r', '')
    return new_str

def norm_text(text):
    ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
    text = ILLEGAL_CHARACTERS_RE.sub(r'', text)
    return text


def timestamp_to_str(timestamp):
    time_local = time.localtime(timestamp / 1000)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt

def handle_user_info(data, user_id):
    home_url = f'https://www.xiaohongshu.com/user/profile/{user_id}'
    nickname = data['basic_info']['nickname']
    avatar = data['basic_info']['imageb']
    red_id = data['basic_info']['red_id']
    gender = data['basic_info']['gender']
    if gender == 0:
        gender = '男'
    elif gender == 1:
        gender = '女'
    else:
        gender = '未知'
    ip_location = data['basic_info']['ip_location']
    desc = data['basic_info']['desc']
    follows = data['interactions'][0]['count']
    fans = data['interactions'][1]['count']
    interaction = data['interactions'][2]['count']
    tags_temp = data['tags']
    tags = []
    for tag in tags_temp:
        try:
            tags.append(tag['name'])
        except:
            pass
    return {
        'user_id': user_id,
        'home_url': home_url,
        'nickname': nickname,
        'avatar': avatar,
        'red_id': red_id,
        'gender': gender,
        'ip_location': ip_location,
        'desc': desc,
        'follows': follows,
        'fans': fans,
        'interaction': interaction,
        'tags': tags,
    }

def handle_note_info(data):
    note_id = data['id']
    note_url = data['url']
    note_type = data['note_card']['type']
    if note_type == 'normal':
        note_type = '图集'
    else:
        note_type = '视频'
    user_id = data['note_card']['user']['user_id']
    home_url = f'https://www.xiaohongshu.com/user/profile/{user_id}'
    nickname = data['note_card']['user']['nickname']
    avatar = data['note_card']['user']['avatar']
    title = data['note_card']['title']
    if title.strip() == '':
        title = f'无标题'
    desc = data['note_card']['desc']
    liked_count = data['note_card']['interact_info']['liked_count']
    collected_count = data['note_card']['interact_info']['collected_count']
    comment_count = data['note_card']['interact_info']['comment_count']
    share_count = data['note_card']['interact_info']['share_count']
    image_list_temp = data['note_card']['image_list']
    image_list = []
    for image in image_list_temp:
        try:
            # 优先尝试info_list[1]['url']，如果失败则尝试其他索引
            if 'info_list' in image and isinstance(image['info_list'], list):
                # 尝试不同的info_list索引，从1开始，然后是0
                for idx in [1, 0]:
                    if len(image['info_list']) > idx and image['info_list'][idx].get('url'):
                        image_list.append(image['info_list'][idx]['url'])
                        break
            # 如果没有info_list，直接尝试image['url']
            elif image.get('url'):
                image_list.append(image['url'])
        except Exception as e:
            logger.debug(f"提取图片URL失败: {e}")
    if note_type == '视频':
        video_cover = image_list[0]
        video_addr = 'https://sns-video-bd.xhscdn.com/' + data['note_card']['video']['consumer']['origin_video_key']
        # success, msg, video_addr = XHS_Apis.get_note_no_water_video(note_id)
    else:
        video_cover = None
        video_addr = None
    tags_temp = data['note_card']['tag_list']
    tags = []
    for tag in tags_temp:
        try:
            tags.append(tag['name'])
        except:
            pass
    upload_time = timestamp_to_str(data['note_card']['time'])
    if 'ip_location' in data['note_card']:
        ip_location = data['note_card']['ip_location']
    else:
        ip_location = '未知'
    return {
        'note_id': note_id,
        'note_url': note_url,
        'note_type': note_type,
        'user_id': user_id,
        'home_url': home_url,
        'nickname': nickname,
        'avatar': avatar,
        'title': title,
        'desc': desc,
        'liked_count': liked_count,
        'collected_count': collected_count,
        'comment_count': comment_count,
        'share_count': share_count,
        'video_cover': video_cover,
        'video_addr': video_addr,
        'image_list': image_list,
        'tags': tags,
        'upload_time': upload_time,
        'ip_location': ip_location,
    }

def handle_comment_info(data):
    note_id = data['note_id']
    note_url = data['note_url']
    comment_id = data['id']
    user_id = data['user_info']['user_id']
    home_url = f'https://www.xiaohongshu.com/user/profile/{user_id}'
    nickname = data['user_info']['nickname']
    avatar = data['user_info']['image']
    content = data['content']
    show_tags = data['show_tags']
    like_count = data['like_count']
    upload_time = timestamp_to_str(data['create_time'])
    try:
        ip_location = data['ip_location']
    except:
        ip_location = '未知'
    pictures = []
    try:
        pictures_temp = data['pictures']
        for picture in pictures_temp:
            try:
                pictures.append(picture['info_list'][1]['url'])
                # success, msg, img_url = XHS_Apis.get_note_no_water_img(picture['info_list'][1]['url'])
                # pictures.append(img_url)
            except:
                pass
    except:
        pass
    return {
        'note_id': note_id,
        'note_url': note_url,
        'comment_id': comment_id,
        'user_id': user_id,
        'home_url': home_url,
        'nickname': nickname,
        'avatar': avatar,
        'content': content,
        'show_tags': show_tags,
        'like_count': like_count,
        'upload_time': upload_time,
        'ip_location': ip_location,
        'pictures': pictures,
    }
def save_to_xlsx(datas, file_path, type='note'):
    wb = openpyxl.Workbook()
    ws = wb.active
    if type == 'note':
        headers = ['笔记id', '笔记url', '笔记类型', '用户id', '用户主页url', '昵称', '头像url', '标题', '描述', '点赞数量', '收藏数量', '评论数量', '分享数量', '视频封面url', '视频地址url', '图片地址url列表', '标签', '上传时间', 'ip归属地']
    elif type == 'user':
        headers = ['用户id', '用户主页url', '用户名', '头像url', '小红书号', '性别', 'ip地址', '介绍', '关注数量', '粉丝数量', '作品被赞和收藏数量', '标签']
    else:
        headers = ['笔记id', '笔记url', '评论id', '用户id', '用户主页url', '昵称', '头像url', '评论内容', '评论标签', '点赞数量', '上传时间', 'ip归属地', '图片地址url列表']
    ws.append(headers)
    for data in datas:
        data = {k: norm_text(str(v)) for k, v in data.items()}
        ws.append(list(data.values()))
    wb.save(file_path)
    logger.info(f'数据保存至 {file_path}')


def save_creator_data_to_xlsx(datas, file_path):
    """
    将创作者数据保存到Excel文件
    :param datas: 数据列表
    :param file_path: 文件路径
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    headers = ['笔记ID', '标题', '发布时间', '笔记类型', '点赞数', '收藏数', '评论数', '分享数', '阅读数', '笔记链接', '封面链接', '图片URL列表', '笔记内容', '评论内容']
    ws.append(headers)
    
    for data in datas:
        # 确保data是字典类型
        if not isinstance(data, dict):
            logger.warning(f"跳过无效数据类型: {type(data)}")
            continue
        
        note_id = data.get('note_id', data.get('id', ''))
        title = data.get('display_title', data.get('title', ''))
        upload_time = data.get('time', data.get('upload_time', data.get('display_time', '')))
        
        # 处理时间戳
        if isinstance(upload_time, (int, float)):
            upload_time = timestamp_to_str(upload_time)
        elif not isinstance(upload_time, str):
            upload_time = str(upload_time)
        
        note_type = data.get('type', 'normal')
        
        # 处理数字类型，确保是整数
        def safe_int(value, default=0):
            """安全转换为整数"""
            if isinstance(value, (int, float)):
                return int(value)
            elif isinstance(value, str):
                try:
                    return int(float(value))
                except:
                    return default
            return default
        
        likes = safe_int(data.get('likes', data.get('liked_count', 0)))
        collects = safe_int(data.get('collected_count', 0))
        comments = safe_int(data.get('comments_count', data.get('comment_count', 0)))
        shares = safe_int(data.get('shared_count', data.get('share_count', 0)))
        views = safe_int(data.get('view_count', 0))
        
        # 构建笔记链接
        note_url = f"https://www.xiaohongshu.com/explore/{note_id}" if note_id else ""
        
        # 获取封面链接
        cover = ""
        if 'cover' in data and isinstance(data['cover'], dict):
            cover = data['cover'].get('url', '')
        elif 'images_list' in data and isinstance(data['images_list'], list) and data['images_list']:
            img_item = data['images_list'][0]
            if isinstance(img_item, dict):
                cover = img_item.get('url', '')
        elif 'video' in data and isinstance(data['video'], dict):
            cover = data['video'].get('cover_url', '')
        
        # 处理描述和评论
        desc = data.get('desc', '')
        if not isinstance(desc, str):
            desc = str(desc)
        
        comments_str = ""
        if 'comments_list' in data and isinstance(data['comments_list'], list):
            c_list = []
            for c in data['comments_list']:
                if not isinstance(c, dict):
                    continue
                user = c.get('user', 'Unknown')
                if not isinstance(user, str):
                    user = 'Unknown'
                content = c.get('content', '')
                if not isinstance(content, str):
                    content = ''
                c_list.append(f"{user}: {content}")
            comments_str = "\n".join(c_list)

        # 处理图片URL列表
        image_urls = ""
        if 'image_urls' in data and isinstance(data['image_urls'], list):
            image_urls = "\n".join(data['image_urls'])
        elif 'images_list' in data and isinstance(data['images_list'], list):
            # 兼容旧的images_list格式
            img_urls = []
            for img_item in data['images_list']:
                if isinstance(img_item, dict):
                    url = img_item.get('url', '')
                    if url:
                        img_urls.append(url)
            image_urls = "\n".join(img_urls)
        elif 'image_list' in data and isinstance(data['image_list'], list):
            # 兼容handle_note_info返回的image_list格式
            image_urls = "\n".join(data['image_list'])
        
        # 构建行数据，确保所有字段都是字符串类型，避免Excel导入错误
        row = [
            str(note_id), 
            norm_text(str(title)), 
            str(upload_time), 
            str(note_type),
            likes, collects, comments, shares, views,
            str(note_url), str(cover),
            norm_text(str(image_urls)),
            norm_text(str(desc)),
            norm_text(str(comments_str))
        ]
        
        # 确保行数据长度与标题一致
        if len(row) != len(headers):
            logger.warning(f"行数据长度与标题不一致: {len(row)} != {len(headers)}")
            continue
        
        ws.append(row)
    
    try:
        wb.save(file_path)
        logger.info(f'Creator data saved to {file_path}')
    except Exception as e:
        logger.error(f'保存Excel文件失败: {e}')
        raise

def download_media(path, name, url, type):
    if type == 'image':
        content = requests.get(url).content
        with open(path + '/' + name + '.jpg', mode="wb") as f:
            f.write(content)
    elif type == 'video':
        res = requests.get(url, stream=True)
        size = 0
        chunk_size = 1024 * 1024
        with open(path + '/' + name + '.mp4', mode="wb") as f:
            for data in res.iter_content(chunk_size=chunk_size):
                f.write(data)
                size += len(data)

def save_user_detail(user, path):
    with open(f'{path}/detail.txt', mode="w", encoding="utf-8") as f:
        # 逐行输出到txt里
        f.write(f"用户id: {user['user_id']}\n")
        f.write(f"用户主页url: {user['home_url']}\n")
        f.write(f"用户名: {user['nickname']}\n")
        f.write(f"头像url: {user['avatar']}\n")
        f.write(f"小红书号: {user['red_id']}\n")
        f.write(f"性别: {user['gender']}\n")
        f.write(f"ip地址: {user['ip_location']}\n")
        f.write(f"介绍: {user['desc']}\n")
        f.write(f"关注数量: {user['follows']}\n")
        f.write(f"粉丝数量: {user['fans']}\n")
        f.write(f"作品被赞和收藏数量: {user['interaction']}\n")
        f.write(f"标签: {user['tags']}\n")

def save_note_detail(note, path):
    with open(f'{path}/detail.txt', mode="w", encoding="utf-8") as f:
        # 逐行输出到txt里
        f.write(f"笔记id: {note['note_id']}\n")
        f.write(f"笔记url: {note['note_url']}\n")
        f.write(f"笔记类型: {note['note_type']}\n")
        f.write(f"用户id: {note['user_id']}\n")
        f.write(f"用户主页url: {note['home_url']}\n")
        f.write(f"昵称: {note['nickname']}\n")
        f.write(f"头像url: {note['avatar']}\n")
        f.write(f"标题: {note['title']}\n")
        f.write(f"描述: {note['desc']}\n")
        f.write(f"点赞数量: {note['liked_count']}\n")
        f.write(f"收藏数量: {note['collected_count']}\n")
        f.write(f"评论数量: {note['comment_count']}\n")
        f.write(f"分享数量: {note['share_count']}\n")
        f.write(f"视频封面url: {note['video_cover']}\n")
        f.write(f"视频地址url: {note['video_addr']}\n")
        f.write(f"图片地址url列表: {note['image_list']}\n")
        f.write(f"标签: {note['tags']}\n")
        f.write(f"上传时间: {note['upload_time']}\n")
        f.write(f"ip归属地: {note['ip_location']}\n")



@retry(tries=3, delay=1)
def download_note(note_info, path, save_choice):
    note_id = note_info['note_id']
    user_id = note_info['user_id']
    title = note_info['title']
    title = norm_str(title)[:40]
    nickname = note_info['nickname']
    nickname = norm_str(nickname)[:20]
    if title.strip() == '':
        title = f'无标题'
    save_path = f'{path}/{nickname}_{user_id}/{title}_{note_id}'
    check_and_create_path(save_path)
    with open(f'{save_path}/info.json', mode='w', encoding='utf-8') as f:
        f.write(json.dumps(note_info) + '\n')
    note_type = note_info['note_type']
    save_note_detail(note_info, save_path)
    if note_type == '图集' and save_choice in ['media', 'media-image', 'all']:
        for img_index, img_url in enumerate(note_info['image_list']):
            download_media(save_path, f'image_{img_index}', img_url, 'image')
    elif note_type == '视频' and save_choice in ['media', 'media-video', 'all']:
        download_media(save_path, 'cover', note_info['video_cover'], 'image')
        download_media(save_path, 'video', note_info['video_addr'], 'video')
    return save_path


def check_and_create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
