#!/bin/bash
PATH=$PATH:/usr/local/bin
export PATH
scrapy crawl schedules

curl  "https://api.telegram.org/bot564873482:AAFhH9iE9Fyf1th-z-DSxznJBBgRSynPmvA/sendMessage" -d "chat_id=-273770462&text=обновлен"

