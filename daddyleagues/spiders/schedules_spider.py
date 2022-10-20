# -*- coding: utf-8 -*-

import scrapy
import sqlite3


class SchedulesSpider(scrapy.Spider):
    name = "schedules"
    league_name = 'mega'

    def start_requests(self):
        # import pdb; pdb.set_trace()
        self.conn = sqlite3.connect('daddyleagues.db')
        #url = 'http://old.daddyleagues.com/uflrus/schedules'
        url = f'http://www.daddyleagues.com/{league_name}/schedules'

        c = self.conn.cursor()
        #debug
        #c.execute('drop table week')
        c.execute('CREATE TABLE IF NOT EXISTS week (id, week, ended)')
        last_week = c.execute("""select week from week where ended = 0 order by id limit 1""").fetchone()
        count_week = c.execute("""select week from week""").fetchone()
# Первый запуск

        if last_week is None and count_week is None:
            return [scrapy.Request(url=url, callback=self.parse)]
        else:
            return [scrapy.FormRequest(url=url,
                                       formdata={"week": str(last_week[0])},
                                       meta={"week": last_week[0]},
                                       callback=self.parse_week)]

    def parse(self, response):
        #weeks = [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (11, 0), (12, 0), (13, 0), (14, 0), (15, 0), (16, 0), (17, 0), (18, 0), (19, 0), (21, 0)]
        weeks = [(int(w), 0)
                 for w
                 #in response.css('div.weekSelector li a::attr(rel)').extract()]
                 in response.css('.tab-pane.fadeshow.active div a::text').extract()]


        c = self.conn.cursor()
        c.executemany('insert into week values (null, ?, ?)', weeks)
        self.conn.commit()
        return [scrapy.FormRequest(url=response.url,
                                   formdata={"week": str(weeks[0][0])},
                                   meta={"week": weeks[0][0]},
                                   callback=self.parse_week)]

    def parse_week(self, response):
        # import pdb; pdb.set_trace()
        week = response.meta['week']
        games = response.css('div.card.b.mb-2')
        c = self.conn.cursor()
        #debug
        #c.execute('drop table games')
        c.execute('CREATE TABLE IF NOT EXISTS games (week INTEGER, team1_id, score1, score2, team2_id, vs, sended)')
        count = c.execute('select count(*) from games where week = ?',
                          (week,)).fetchone()
        if count[0] == len(games):
            # import pdb; pdb.set_trace()
            c.execute('update week set ended = 1 where week = ?', (week,))
            self.conn.commit()
            last_week = c.execute("""
select week from week where ended = 0 order by id limit 1
            """).fetchone()
            if last_week is not None:
                yield scrapy.FormRequest(url=response.url,
                                         formdata={"week": str(last_week[0])},
                                         meta={"week": last_week[0]},
                                         callback=self.parse_week)
            else:
                yield dict()
        else:
            for s in games:
                # Возможно потом добавить lower для названий
                # import pdb; pdb.set_trace()
               # names = s.css('div.name::text').extract()
               # scores = s.css('span.score > span::text').extract()
               # score1 = int(scores[0].strip())
               # score2 = int(scores[1].strip())
               # vs = s.css('a::attr(href)').extract()[0]
               # vs = vs.replace("old", "www", 3)

                name1 = s.css('.col-2 div.h2.m-0.text-bold::text').extract()
                name2 = s.css('.col-3 div.h2.m-0.text-bold::text').extract()
                scores = s.css('.col-6 div h4.mt-3 a::text').extract()
                scores = scores[0].strip().split('vs')
                vs = s.css('a::attr(href)').extract()[0]

                if int(scores[0].strip()) != 0 or int(scores[1].strip()) != 0:
                    yield {
                        'week': week,
                        'team1': name1[0].strip(),
                        'score1':  int(scores[0].strip()),
                        'team2': name2[0].strip(),
                        'score2': int(scores[1].strip()),
                        'vs': vs
                    }

    def closed(self, reason):
        self.conn.close()
