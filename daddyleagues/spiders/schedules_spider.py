# -*- coding: utf-8 -*-

import scrapy
import sqlite3


class SchedulesSpider(scrapy.Spider):
    name = "schedules"

    def start_requests(self):
        # import pdb; pdb.set_trace()
        self.conn = sqlite3.connect('daddyleagues.db')
        url = 'http://www.daddyleagues.com/uflrus/schedules'

        c = self.conn.cursor()
        last_week = c.execute("""
select week from week where ended = 0 order by id limit 1
        """).fetchone()
        # Первый запуск
        if last_week is None:
            return [scrapy.Request(url=url, callback=self.parse)]
        else:
            return [scrapy.FormRequest(url=url,
                                       formdata={"week": str(last_week[0])},
                                       meta={"week": last_week[0]},
                                       callback=self.parse_week)]

    def parse(self, response):
        weeks = [(int(w), 0)
                 for w
                 in response.css('div.weekSelector li a::attr(rel)').extract()]
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
        li = response.css('li')
        c = self.conn.cursor()
        count = c.execute('select count(*) from games where week = ?',
                          (week,)).fetchone()
        if count[0] == len(li):
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
            for s in li:
                # Возможно потом добавить lower для названий
                # import pdb; pdb.set_trace()
                names = s.css('div.name::text').extract()
                scores = s.css('span.score > span::text').extract()
                score1 = int(scores[0].strip())
                score2 = int(scores[1].strip())
                vs = s.css('a::attr(href)').extract()[0]
                if score1 != 0 or score2 != 0:
                    yield {
                        'week': week,
                        'team1': names[0].strip(),
                        'score1': score1,
                        'team2': names[1].strip(),
                        'score2': score2,
                        'vs': vs
                    }

    def closed(self, reason):
        self.conn.close()
