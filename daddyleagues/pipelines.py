# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3
import requests
from scrapy.exceptions import NotConfigured
from scrapy.exceptions import DropItem


class DaddyleaguesPipeline(object):

    def __init__(self, chat_id=None, template=None):
        if chat_id is None or template is None:
            raise NotConfigured()
        else:
            self.chat_id = chat_id
            self.template = template

    def open_spider(self, spider):
        self.conn = sqlite3.connect('daddyleagues.db')

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        # import pdb; pdb.set_trace()
        if len(item) == 0:
            raise DropItem()
        c = self.conn.cursor()
        #c.execute('drop table  team')
        c.execute('CREATE TABLE IF NOT EXISTS  team (id, name)')
        new_item = False
        team1 = c.execute('select id, name from team where name = ?',
                          (item['team1'],)).fetchone()
        team2 = c.execute('select id, name from team where name = ?',
                          (item['team2'],)).fetchone()
        if team1 is not None and team2 is not None:
            persist = c.execute("""
select week from games where week = ? and team1_id = ? and team2_id = ?
            """, (item['week'], team1[0], team2[0])).fetchone()
            if persist is None:
                c.execute('insert into games values (?, ?, ?, ?, ?, ?)',
                          (item['week'], team1[0], item['score1'],
                           item['score2'], team2[0], item['vs']))
                new_item = True
        else:
            if team1 is None:
                c.execute('insert into team values (null, ?)', (item['team1'],))
                team1 = c.execute('select id, name from team where name = ?',
                                  (item['team1'],)).fetchone()
            if team2 is None:
                c.execute('insert into team values (null, ?)', (item['team2'],))
                team2 = c.execute('select id, name from team where name = ?',
                                  (item['team2'],)).fetchone()
            c.execute('insert into games values (?, ?, ?, ?, ?, ?)',
                      (item['week'], team1[0], item['score1'],
                       item['score2'], team2[0], item['vs']))
            new_item = True
        if new_item:
            try:
                r = requests.post("https://api.telegram.org/\
bot356404528:AAHg-TCSPkE9yLXAt0W3QwGhDhAc9fb0KSc/sendMessage",
                                  data={
                                      u"chat_id": self.chat_id,
                                      u"text": self.template.format(
                                          team1[1],
                                          item['score1'],
                                          item['vs'],
                                          item['score2'],
                                          team2[1]),
                                      u"parse_mode": u"Markdown"})
                js = r.json()
                if u"ok" in js and js["ok"]:
                    self.conn.commit()
                    requests.post("https://api.telegram.org/\
bot356404528:AAHg-TCSPkE9yLXAt0W3QwGhDhAc9fb0KSc/sendMessage",
                                  data={
                                      u"chat_id": -209460624,
                                      u"text": self.template.format(
                                          team1[1],
                                          item['score1'],
                                          item['vs'],
                                          item['score2'],
                                          team2[1]),
                                      u"parse_mode": u"Markdown"})
            except:
                self.conn.rollback()
        return item

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(**settings.getdict('TELEGRAM'))
