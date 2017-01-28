#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=I0011,C0111,C0103

from __future__ import print_function
from io import BytesIO
import threading

import telepot
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent
import requests
from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype('simhei.ttf', 28)

def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""

def on_chat_message(msg):
    content_type, _, chat_id = telepot.glance(msg, flavor='chat')

    if content_type == 'text':
        bot.sendMessage(chat_id, '新年快乐!')

def on_inline_query(msg):
    def compute():
        _, _, query_string = telepot.glance(msg, flavor='inline_query')
        print('Inline Query:', query_string)

        split = query_string.split(' ', 1)
        if len(split) > 1:
            text = u'我可能是%s了假%s' % tuple(split)

            img = Image.open('bg.jpg')
            draw = ImageDraw.Draw(img)
            draw.text((5, 10), text, font=font, fill=(0, 0, 0))

            out = BytesIO()
            img.save(out, format='JPEG')
            out.seek(0)

            r = requests.post('https://ptpb.pw/', files={'c': out}, data={'sunset': 120}, timeout=5)
            out.close()

            if r.status_code == requests.codes.ok: # pylint: disable=I0011,E1101
                # print(r.text)
                width, height = img.size
                url = find_between(r.text, 'url: ', '\n')
                resultid = find_between(r.text, 'digest: ', '\n')
                results = [InlineQueryResultPhoto(
                    id=resultid,
                    photo_url=url,
                    thumb_url=url,
                    photo_width=width,
                    photo_height=height
                )]
            else:
                threading.currentThread().cancel()
                return
        else:
            results = [InlineQueryResultArticle(
                id='usage',
                title='使用说明',
                description='输入"用 机器人"即可生成"我可能是用了假机器人"',
                input_message_content=InputTextMessageContent(
                    message_text='输入"用 机器人"即可生成"我可能是用了假机器人"'
                ))]

        return (results, 3600 * 2) # (results, cache_time)

    answerer.answer(msg, compute)

def on_chosen_inline_result(msg):
    result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
    print('Chosen Inline Result:', result_id, from_id, query_string)

if __name__ == '__main__':
    TOKEN = ''

    bot = telepot.Bot(TOKEN)
    answerer = telepot.helper.Answerer(bot)

    bot.message_loop({'chat': on_chat_message,
                      'inline_query': on_inline_query,
                      'chosen_inline_result': on_chosen_inline_result},
                     run_forever='Running...')
