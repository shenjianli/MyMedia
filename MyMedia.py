#!/usr/bin/python
# -*- coding: UTF-8 -*-
import urllib.request
import ssl
from bs4 import BeautifulSoup
import glob
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import cv2
import time
from aip import AipSpeech
from ffmpy3 import FFmpeg
import os.path

# https://ai.baidu.com/tech/speech/tts
# 百度已经开始收费
APP_ID = '20003062'
API_KEY = '1RvffWpbCEM2Fl5ofvPyTWQ9'
SECRET_KEY = 'IjxZFL9GkrXn1nkyCtuSGXShzpkqz1BU'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

ssl._create_default_https_context = ssl._create_unverified_context
font = ImageFont.truetype('./font/breif.ttf',21)

requestNetAddress = "https://mp.weixin.qq.com/s/XM2YDOGcqqNZPxpBu7KH0Q"

text_conent = ['大肚能容，容天下难容之事','开口便笑，笑天下可笑之人']
# text_conent = ['遇到难过的事，尽快遗忘,','遇到气愤的人，赶紧忘记,','人生就是一删一留，','生活就是一加一减。']

# title = ['蒸窝头','翻花绳']
# text_conent = ['蒸窝头','翻花绳']

top_content = ['往日不谏，来者可追', '端午节，愿你初心不改', '愿你的世界星光满载']
bottom_content = ['感谢我的抖音能有你', '愿你一生无忧，端午安康']

TEXT_SPACE = 10
BG_WIDTH = 720
BG_HEIGHT = 655

IMAGE_WIDTH = 437
IMAGE_HEIGHT = 280


def get_html(url):
    page = urllib.request.urlopen(url)
    content = page.read()
    return content


def get_and_download_img(html):
    soup = BeautifulSoup(html,'html.parser')
    img = soup.find_all('img')
    print(img)
    x = 0
    img_prex = 'img'
    for image in img:
        img_src = image.get('data-src')
        data_type = image.get('data-type')
        print(img_src)
        if(img_src != None and (data_type == 'jpg' or data_type == 'jpeg' or data_type == 'png')):
            if x < 10:
                img_prex = 'img0'
            else:
                img_prex = 'img'
            urllib.request.urlretrieve(img_src, ('./image/' + img_prex + '%s.' + data_type) %x)
            x += 1
            print('正在下载第%d张' %x)


def img_2_video():
    image_list = glob.glob('./image/*')
    image_list.sort()
    print(image_list)

    video_name = 'input_' + time.strftime("%Y%m%d", time.localtime())
    video = cv2.VideoWriter('./video/' + video_name +'.avi',
                            cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 0.3,
                            (IMAGE_WIDTH,int(IMAGE_WIDTH * 1.778)))
    print('正在合成视频')
    for image_name in image_list:
        img = cv2.imread(image_name)
        img = cv2.resize(img,(IMAGE_WIDTH,int(IMAGE_WIDTH * 1.778)))
        video.write(img)
    video.release()
    cv2.destroyAllWindows()
    print('视频合成完成')
    return video_name


# 定义图像拼接函数
def image_compose(img_path):
    mode = 'RGB'
    if 'png' in img_path:
        mode = 'RGBA'

    to_image = Image.new(mode, (IMAGE_WIDTH,int(IMAGE_WIDTH * 1.778)),(0,0,0))  # 创建一个新图

    draw = ImageDraw.Draw(to_image)
    i = 1

    for text in text_conent:
        text_y = i * 40
        i += 1
        draw.text((20, text_y), text, font=font, fill=(255,255,255))

    # 循环遍历，把每张图片按顺序粘贴到对应位置上
    from_image = Image.open(img_path).resize(
        (IMAGE_WIDTH, IMAGE_HEIGHT), Image.ANTIALIAS)
    image_x = 0
    image_y = int((IMAGE_WIDTH * 1.778 - IMAGE_HEIGHT)/2)
    to_image.paste(from_image, (image_x, image_y))

    # text_x = 30
    # text_y = image_y + IMAGE_HEIGHT + 50
    # draw.text((text_x, text_y), "现在为一个月两三百的全勤奖", font=font, fill=(255, 255, 255))
    # text_x += 30
    # text_y += 50
    # draw.text((text_x, text_y), "一个月没有休息过", font=font, fill=(255, 255, 255))
    # text_x += 30
    # text_y += 50
    # draw.text((text_x, text_y), "还嫌加班少", font=font, fill=(255, 255, 255))

    return to_image.save(img_path)  # 保存新图


def image_add_text():
    image_list = glob.glob('./image/*')
    image_list.sort()
    i = 0
    for image_name in image_list:
        #sub_title = text_conent[i]
        print("增加文字：" + image_name)
        #print("文字" + sub_title)
        add_text(image_name)
        i = i + 1


def add_text(img_path):
    mode = 'RGB'
    if 'png' in img_path:
        mode = 'RGBA'

    to_image = Image.new(mode, (IMAGE_WIDTH,int(IMAGE_WIDTH * 1.778)),(0,0,0))  # 创建一个新图

    draw = ImageDraw.Draw(to_image)

    image_y = int((IMAGE_WIDTH * 1.778 - IMAGE_HEIGHT) / 2)

    i = 0
    for text in top_content:
        # 获取字体宽度
        sum_width = 0
        sum_height = 0
        text_space = TEXT_SPACE
        if i == 0:
            text_space = 0
        for char in text:
            width, height = draw.textsize(char, font)
            sum_width += width
            sum_height = height
        draw.text(((IMAGE_WIDTH - sum_width)/2,
                   (image_y - len(top_content) * sum_height)/2
                   + (i * sum_height) + i * text_space),
                  text, font=font, fill=(255, 255, 255))
        i = i + 1

    # 循环遍历，把每张图片按顺序粘贴到对应位置上
    from_image = Image.open(img_path).resize(
        (IMAGE_WIDTH, IMAGE_HEIGHT), Image.Resampling.LANCZOS )
    image_x = 0
    image_y = int((IMAGE_WIDTH * 1.778 - IMAGE_HEIGHT)/2)
    to_image.paste(from_image, (image_x, image_y))

    i = 0
    for text in bottom_content:
        # 获取字体宽度
        sum_width = 0
        sum_height = 0
        text_space = TEXT_SPACE
        if i == 0:
            text_space = 0
        for char in text:
            width, height = draw.textsize(char, font)
            sum_width += width
            sum_height = height
        draw.text(((IMAGE_WIDTH - sum_width) / 2,
                   (image_y + IMAGE_HEIGHT) + (image_y - len(bottom_content) * sum_height) / 2
                   + i * sum_height + i * text_space),
                  text, font=font, fill=(255, 255, 255))
        i = i + 1

    return to_image.save(img_path)  # 保存新图


def image_compose_text(img_path, title, sub_title):
    mode = 'RGB'
    if 'png' in img_path:
        mode = 'RGBA'

    to_image = Image.new(mode, (IMAGE_WIDTH,int(IMAGE_WIDTH * 1.778)),(0,0,0))  # 创建一个新图

    draw = ImageDraw.Draw(to_image)
    image_y = int((IMAGE_WIDTH * 1.778 - IMAGE_HEIGHT) / 2)
    # 获取字体宽度
    sum_width = 0
    sum_height = 0
    for char in title:
        width, height = draw.textsize(char, font)
        sum_width += width
        sum_height = height
    draw.text(((IMAGE_WIDTH - sum_width)/2, (image_y - sum_height)/2), title, font=font, fill=(255,255,255))

    # 循环遍历，把每张图片按顺序粘贴到对应位置上
    from_image = Image.open(img_path).resize(
        (IMAGE_WIDTH, IMAGE_HEIGHT), Image.ANTIALIAS)
    image_x = 0
    image_y = int((IMAGE_WIDTH * 1.778 - IMAGE_HEIGHT)/2)
    to_image.paste(from_image, (image_x, image_y))

    # 获取字体宽度
    sum_width = 0
    sum_height = 0
    for char in sub_title:
        width, height = draw.textsize(char, font)
        sum_width += width
        sum_height = height
    draw.text(((IMAGE_WIDTH - sum_width) / 2, (image_y + IMAGE_HEIGHT) + (image_y - sum_height) / 2), sub_title, font=font, fill=(255, 255, 255))

    return to_image.save(img_path)  # 保存新图


def create_audio(text):
    result = client.synthesis(text, 'zh', 1, {
        'vol': 5,
        'per': 4,
    })

    # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
    if not isinstance(result, dict):
        out_audio = "audio_" + time.strftime("%Y%m%d", time.localtime()) + ".mp3"
        with open(out_audio, 'wb') as f:
            f.write(result)
            print("成功转化音频")


def video_2_mp4():
    out_name = "out_" + time.strftime("%Y%m%d", time.localtime()) + ".mp4"
    if os.path.isfile(out_name):
        os.remove(out_name)
        print("删除已经存在mp4文件")
    ff = FFmpeg(executable="./ffmpeg",
        inputs={'./video/input_' + time.strftime("%Y%m%d", time.localtime()) + '.avi': None},
        outputs={out_name: None}).run()


def delete_small_img_file():
    file_list = os.listdir("./image")
    for file in file_list:
        path = os.path.join("./image", file)
        size = os.path.getsize(path)
        # 删除小于20k的图片文件
        if size < 1024*20:
            os.remove(path)
            print("删除小文件 ",path)


def delete_all_img_file():
    file_list = os.listdir("./image")
    for file in file_list:
        path = os.path.join("./image", file)
        os.remove(path)
    print("删除所有文件")


delete_all_img_file()
html = get_html(requestNetAddress)
get_and_download_img(html)
delete_small_img_file()
image_add_text()
img_2_video()
video_2_mp4()


# 百度已经开始收费
audio_text = ''
for str in text_conent:
    audio_text = audio_text + str + ',    '
print(audio_text)
create_audio(audio_text)