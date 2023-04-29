import requests
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
import sqlite3
import datetime


URL_BASE = "https://api.football-data.org/v4/"
HEADERS = {"X-Auth-Token": "68e49e6ef59c4419be9ec06ec2687097"}
LEAGES = {"FIFA_World_Cup": "2000",
          "UEFA_Champions_League": "2001",
          "Bundesliga": "2002",
          "Eredivisie": "2003",
          "Campeonato_Brasileiro_Série_A": "2013",
          "Primera_Division": "2014",
          "Ligue_1": "2015",
          "Championship": "2016",
          "Primeira_Liga": "2017",
          "European_Championship": "2018",
          "Serie_A": "2019",
          "Premier_League": "2021",
          "Copa_Libertadores": "2152"}
DB = sqlite3.connect('vk_bet.db')
CUR = DB.cursor()


def main():
    vk_session = vk_api.VkApi(
        token="vk1.a.LZ7b5au9I6-cdtS8GChNfIMz8CW0dbrcmieIEkzpexm6tcWJUgZQVu21xDNwNGHwqEmHhfcoPjYLYl5aK4IK-cmay_Z87Y_kZpKvECpvScw0rwWWCV5GaBYKba1WvUrwCkn8qdVzamgEzYwG1TyApPgRsTJBGvDjtr-clPA8BWJIwS2AOzoagXEyuSOoJuX0-uY_TrYNiqoXvk3eXT5xiw"
    )
    longpoll = VkBotLongPoll(vk_session, 219958560)
    for event in longpoll.listen():
        vk = vk_session.get_api()
        if event.type == VkBotEventType.MESSAGE_NEW:
            txt = event.obj.message["text"].split()
            if event.obj.message["text"] == 'start':
                vk_ids = CUR.execute("""SELECT user_id FROM data""").fetchall()
                vk_ids = [i[0] for i in vk_ids]
                if event.obj.message["from_id"] not in vk_ids:
                    CUR.execute("""INSERT INTO data(user_id, balance, win_count, loss_count) VALUES(?, ?, ?, ?)""", (int(
                        event.obj.message["from_id"]), 1000, 0, 0))
                    DB.commit()
                vk.messages.send(
                    user_id=event.obj.message["from_id"],
                    message="Здравствуйте. Вы присоединились к группе для футбольных ставок. Никаких денежных операций не производится. Наш бот расчитан на увеличения интереса к футбольным событиям без затрачивания денег\nДля просмотра доступных комманд введите /commands",
                    random_id=random.randint(0, 2**64),
                )
                vk.messages.send(
                    user_id=event.obj.message["from_id"],
                    message="Вы можете сделать ставку на матч одного из этих чемпионатов:\nДля этого напишите /bet\nДоступные лиги:\nFIFA_World_Cup\nUEFA_Champions_League\nBundesliga\nEredivisie\nCampeonato_Brasileiro_Série_A\nPrimera_Division\nLigue_1\nChampionship\nPrimeira_Liga\nEuropean_Championship\nSerie_A\nPremier_League\nCopa_Libertadores ",
                    random_id=random.randint(0, 2**64),
                )
            if '/bet' in event.obj.message["text"].split():
                if len(txt) == 1:
                    vk.messages.send(
                        user_id=event.obj.message["from_id"],
                        message="Чтобы увидеть матчи, на которые можно сделать ставку, напишите /bet [название лиги]",
                        random_id=random.randint(0, 2**64),
                    )
                elif len(txt) == 2:
                    if txt[1] in LEAGES.keys():
                        leage_id = LEAGES[txt[1]]
                        t_day = datetime.date.today() + datetime.timedelta(days=1)
                        req_url = URL_BASE + 'competitions/' + leage_id + '/matches?dateFrom=' + \
                            datetime.date.today().strftime('%Y-%m-%d') + '&dateTo=' + \
                            t_day.strftime('%Y-%m-%d')
                        matches = requests.get(req_url, headers=HEADERS).json()[
                            'matches']
                        if matches:
                            for match in matches:
                                h_team = match['homeTeam']['name'].replace(
                                    ' ', '_')
                                a_team = match['awayTeam']['name'].replace(
                                    ' ', '_')
                                daytime = match['utcDate'][:-4].split('T')
                                moscow_daytime = datetime.datetime(int(daytime[0].split('-')[0]), int(daytime[0].split('-')[1]), int(daytime[0].split(
                                    '-')[2]), int(daytime[1].split(':')[0]), int(daytime[1].split(':')[1]), 0) + datetime.timedelta(hours=3)
                                if match['status'] == 'IN_PLAY' or match['status'] == 'TIMED':
                                    vk.messages.send(
                                        user_id=event.obj.message["from_id"],
                                        message=f"{h_team}-{a_team}.\nВремя: {moscow_daytime.strftime('%d.%m.%Y %H:%M')}",
                                        random_id=random.randint(0, 2**64),)
                                else:
                                    vk.messages.send(
                                        user_id=event.obj.message["from_id"],
                                        message=f"{h_team}-{a_team}.\nЭтот матч уже завершен. На него нельзя сделать ставку",
                                        random_id=random.randint(0, 2**64),)
                            vk.messages.send(
                                user_id=event.obj.message["from_id"],
                                message="Чтобы сделать ставку напишите /bet [лига] [матч] [победитель/DRAW] [ставка] \nили /bet [лига] [матч] [победитель/DRAW] [ставка] [итог в формате num:num]\nУбедитесь, что аргументы стоят в правильном порядке, а названия соответствуют выведенным ранее",
                                random_id=random.randint(0, 2**64),)
                            vk.messages.send(
                                user_id=event.obj.message["from_id"],
                                message="Чтобы узнать ваш текущий баланс, напишите /balance",
                                random_id=random.randint(0, 2**64),
                            )
                        else:
                            vk.messages.send(
                                user_id=event.obj.message["from_id"],
                                message="На сегодня нет матчей. Вы можете посмотреть расписание на неделю\nНапишите /timetable или /timetable [название лиги]",
                                random_id=random.randint(0, 2**64),)
                    else:
                        vk.messages.send(
                            user_id=event.obj.message["from_id"],
                            message="Такой лиги нет в нашем списке. Проверьте правильность написания названия и поробуйте еще раз",
                            random_id=random.randint(0, 2**64),)
                elif len(txt) == 5 or len(txt) == 6:
                    bets = CUR.execute("""SELECT current_bet_match FROM data WHERE user_id=?""", (int(
                        event.obj.message["from_id"]),)).fetchall()
                    if bets[0][0] == None:
                        if txt[1] in LEAGES.keys():
                            leage_id = LEAGES[txt[1]]
                            t_day = datetime.date.today() + datetime.timedelta(days=1)
                            req_url = URL_BASE + 'competitions/' + leage_id + '/matches?dateFrom=' + \
                                datetime.date.today().strftime('%Y-%m-%d') + '&dateTo=' + \
                                t_day.strftime('%Y-%m-%d')
                            matches = requests.get(req_url, headers=HEADERS).json()[
                                'matches']
                            matches = [match for match in matches if match['status']
                                       == 'IN_PLAY' or match['status'] == 'TIMED']
                            h_team = txt[2].split('-')[0].strip(' ')
                            a_team = txt[2].split('-')[1].strip(' ')
                            match_id = 0
                            is_match = False
                            enough_money = False
                            match_is_match = False
                            valid_res = False
                            for match in matches:
                                if h_team == match['homeTeam']['name'].replace(' ', '_') and a_team == match['awayTeam']['name'].replace(' ', '_'):
                                    is_match = True
                                    match_id = match['id']
                                    break
                            balance = CUR.execute("""SELECT balance FROM data WHERE user_id=?""", (int(
                                event.obj.message["from_id"]),)).fetchmany(1)[0][0]
                            if txt[4].replace(' ', '').isdigit():
                                if balance - int(txt[4].replace(' ', '')) >= 50:
                                    enough_money = True
                                else:
                                    vk.messages.send(
                                        user_id=event.obj.message["from_id"],
                                        message=f"Ваш баланс в случае проигрыша должен оказаться не менее 50.\nТекущий баланс:{balance}\nДля пополнения обратитесь к администратору сообщества",
                                        random_id=random.randint(0, 2**64),)
                                if txt[3] in [h_team, a_team, 'DRAW']:
                                    match_is_match = True
                                else:
                                    vk.messages.send(
                                        user_id=event.obj.message["from_id"],
                                        message="На эту команду нельзя поставить. Проверьте правильность написания",
                                        random_id=random.randint(0, 2**64),)
                                if len(txt) == 5:
                                    coeff = 2
                                    if is_match and enough_money and match_is_match:
                                        CUR.execute("""UPDATE data 
                                                        SET current_bet_competition=?, current_bet_rate=?, current_bet_match=?, current_bet_result=?, current_coeff=?, balance=?
                                                        WHERE user_id=?""", (txt[1], int(txt[4]), match_id, txt[3], coeff, balance - int(txt[4]), int(
                                            event.obj.message["from_id"]),))
                                        vk.messages.send(
                                            user_id=event.obj.message["from_id"],
                                            message="Ставка успешна принята",
                                            random_id=random.randint(0, 2**64),)
                                        DB.commit()
                                if len(txt) == 6:
                                    coeff = 4
                                    if txt[5].replace(':', '').replace(' ', '').isdigit():
                                        valid_res = True
                                    if valid_res and is_match and enough_money and match_is_match:
                                        CUR.execute("""UPDATE data 
                                                        SET current_bet_competition=?, current_bet_rate=?, current_bet_match=?, current_bet_result=?, current_coeff=?, balance=?
                                                        WHERE user_id=?""", (txt[1], int(txt[4]), match_id, txt[3] + ' ' + txt[5].replace(' ', ''), coeff, balance - int(txt[4]), int(
                                            event.obj.message["from_id"]),))
                                        vk.messages.send(
                                            user_id=event.obj.message["from_id"],
                                            message="Ставка успешна принята",
                                            random_id=random.randint(0, 2**64),)
                                        DB.commit()

                            else:
                                vk.messages.send(
                                    user_id=event.obj.message["from_id"],
                                    message="Неверный формат ставки. Ставка должна содержать одно число",
                                    random_id=random.randint(0, 2**64),)
                        else:
                            vk.messages.send(
                                user_id=event.obj.message["from_id"],
                                message="Такой лиги нет в нашем списке. Проверьте правильность написания названия и поробуйте еще раз",
                                random_id=random.randint(0, 2**64),)
                    else:
                        vk.messages.send(
                            user_id=event.obj.message["from_id"],
                            message="У вас может быть только 1 активная ставка",
                            random_id=random.randint(0, 2**64),)
                else:
                    vk.messages.send(
                        user_id=event.obj.message["from_id"],
                        message="Неправильная команда. Проверьте количество аргументов",
                        random_id=random.randint(0, 2**64),)
            elif '/timetable' in txt:
                if len(txt) == 1:
                    vk.messages.send(
                        user_id=event.obj.message["from_id"],
                        message="Вы можете получить расписание матчей лиги на 7 дней. Для этого напишите /timetable [название лиги]",
                        random_id=random.randint(0, 2**64),)
                elif len(txt) == 2:
                    leage_id = LEAGES[txt[1]]
                    t_day = datetime.date.today() + datetime.timedelta(days=7)
                    req_url = URL_BASE + 'competitions/' + leage_id + '/matches?dateFrom=' + \
                        datetime.date.today().strftime('%Y-%m-%d') + '&dateTo=' + \
                        t_day.strftime('%Y-%m-%d')
                    matches = requests.get(req_url, headers=HEADERS).json()[
                        'matches']
                    if matches:
                        for match in matches:
                            h_team = match['homeTeam']['name']
                            a_team = match['awayTeam']['name']
                            daytime = match['utcDate'][:-4].split('T')
                            moscow_daytime = datetime.datetime(int(daytime[0].split('-')[0]), int(daytime[0].split('-')[1]), int(daytime[0].split(
                                '-')[2]), int(daytime[1].split(':')[0]), int(daytime[1].split(':')[1]), 0) + datetime.timedelta(hours=3)
                            vk.messages.send(
                                user_id=event.obj.message["from_id"],
                                message=f"{h_team}-{a_team}.\nВремя: {moscow_daytime.strftime('%d.%m.%Y %H:%M')}. Статус: {match['status']}",
                                random_id=random.randint(0, 2**64),)
                    else:
                        vk.messages.send(
                            user_id=event.obj.message["from_id"],
                            message=f"На этой неделе нет матчей",
                            random_id=random.randint(0, 2**64),)
            elif '/balance' in txt:
                balance = CUR.execute("""SELECT balance FROM data WHERE user_id=?""", (int(
                    event.obj.message["from_id"]),)).fetchmany(1)[0][0]
                vk.messages.send(
                    user_id=event.obj.message["from_id"],
                    message=f"Ваш текущий баланс: {balance}",
                    random_id=random.randint(0, 2**64),)
            elif '/get_result' in txt:
                data = CUR.execute("""SELECT * FROM data WHERE user_id=?""", (int(
                    event.obj.message["from_id"]),)).fetchmany(1)[0]
                if data[2] == None:
                    vk.messages.send(
                        user_id=event.obj.message["from_id"],
                        message="Вы еще не сделали ставку",
                        random_id=random.randint(0, 2**64),)
                else:
                    your_match = requests.get(
                        URL_BASE + 'matches/' + data[4], headers=HEADERS).json()
                    if your_match['status'] == 'FINISHED':
                        your_result = CUR.execute("""SELECT current_bet_result FROM data WHERE user_id=?""", (int(
                            event.obj.message["from_id"]),)).fetchmany(1)[0][0]
                        if your_match['score']['winner'] == 'DRAW':
                            vk.messages.send(
                                user_id=event.obj.message["from_id"],
                                message=f"Матч {your_match['homeTeam']['name'].replace(' ', '_')}-{your_match['awayTeam']['name'].replace(' ', '_')} окончился ничьей. Счет {your_match['score']['fullTime']['home']}:{your_match['score']['fullTime']['away']}",
                                random_id=random.randint(0, 2**64),)
                            if len(your_result.split()) == 1:
                                if your_result.split()[0] == 'DRAW':
                                    CUR.execute("""UPDATE data 
                                                        SET current_bet_competition=?, current_bet_rate=?, current_bet_match=?, current_bet_result=?, current_coeff=?, balance=?, win_count=?
                                                        WHERE user_id=?""", (None, None, None, None, None, int(data[1]) + int(data[3]) * int(data[-1]), int(data[-3]) + 1, int(event.obj.message["from_id"]),))
                                    vk.messages.send(
                                        user_id=event.obj.message["from_id"],
                                        message=f'Ваша ставка сыграла. Выигрыш составил {int(data[3]) * int(data[-1])}',
                                        random_id=random.randint(0, 2**64),)
                                    DB.commit()
                                else:
                                    CUR.execute("""UPDATE data 
                                                        SET current_bet_competition=?, current_bet_rate=?, current_bet_match=?, current_bet_result=?, current_coeff=?, loss_count=?
                                                        WHERE user_id=?""", (None, None, None, None, None, int(data[-2]) + 1, int(event.obj.message["from_id"]),))
                                    vk.messages.send(
                                        user_id=event.obj.message["from_id"],
                                        message="К сожалению, ваша ставка не сыграла",
                                        random_id=random.randint(0, 2**64),)
                                    DB.commit()
                            if len(your_result.split()) == 2:
                                if your_result.split()[0] == 'DRAW' and your_result.split()[1] == f"{your_match['score']['fullTime']['home']}:{your_match['score']['fullTime']['away']}":
                                    CUR.execute("""UPDATE data 
                                                        SET current_bet_competition=?, current_bet_rate=?, current_bet_match=?, current_bet_result=?, current_coeff=?, balance=?, win_count=?
                                                        WHERE user_id=?""", (None, None, None, None, None, int(data[1]) + int(data[3]) * int(data[-1]), int(data[-3]) + 1, int(event.obj.message["from_id"]),))
                                    vk.messages.send(
                                        user_id=event.obj.message["from_id"],
                                        message=f'Ваша ставка сыграла. Выигрыш составил {int(data[3]) * int(data[-1])}',
                                        random_id=random.randint(0, 2**64),)
                                    DB.commit()
                                else:
                                    CUR.execute("""UPDATE data 
                                                        SET current_bet_competition=?, current_bet_rate=?, current_bet_match=?, current_bet_result=?, current_coeff=?, loss_count=?
                                                        WHERE user_id=?""", (None, None, None, None, None, int(data[-2]) + 1, int(event.obj.message["from_id"]),))
                                    vk.messages.send(
                                        user_id=event.obj.message["from_id"],
                                        message="К сожалению, ваша ставка не сыграла",
                                        random_id=random.randint(0, 2**64),)
                                    DB.commit()
                        else:
                            if your_match['score']['winner'] == 'HOME_TEAM':
                                winner = your_match['homeTeam']['name'].replace(
                                    ' ', '_')
                            else:
                                winner = your_match['awayTeam']['name'].replace(
                                    ' ', '_')
                            vk.messages.send(
                                user_id=event.obj.message["from_id"],
                                message=f"Матч {your_match['homeTeam']['name'].replace(' ', '_')}-{your_match['awayTeam']['name'].replace(' ', '_')} завершен.Победитель: {winner} Счет {your_match['score']['fullTime']['home']}:{your_match['score']['fullTime']['away']}",
                                random_id=random.randint(0, 2**64),)
                            if len(your_result.split()) == 1:
                                if your_result.split()[0] == winner:
                                    CUR.execute("""UPDATE data 
                                                        SET current_bet_competition=?, current_bet_rate=?, current_bet_match=?, current_bet_result=?, current_coeff=?, balance=?, win_count=?
                                                        WHERE user_id=?""", (None, None, None, None, None, int(data[1]) + int(data[3]) * int(data[-1]), int(data[-3]) + 1, int(event.obj.message["from_id"]),))
                                    vk.messages.send(
                                        user_id=event.obj.message["from_id"],
                                        message=f'Ваша ставка сыграла. Выигрыш составил {int(data[3]) * int(data[-1])}',
                                        random_id=random.randint(0, 2**64),)
                                    DB.commit()
                                else:
                                    CUR.execute("""UPDATE data 
                                                        SET current_bet_competition=?, current_bet_rate=?, current_bet_match=?, current_bet_result=?, current_coeff=?, loss_count=?
                                                        WHERE user_id=?""", (None, None, None, None, None, int(data[-2]) + 1, int(event.obj.message["from_id"]),))
                                    vk.messages.send(
                                        user_id=event.obj.message["from_id"],
                                        message="К сожалению, ваша ставка не сыграла",
                                        random_id=random.randint(0, 2**64),)
                                    DB.commit()
                            if len(your_result.split()) == 2:
                                if your_result.split()[0] == winner and your_result.split()[1] == f"{your_match['score']['fullTime']['home']}:{your_match['score']['fullTime']['away']}":
                                    CUR.execute("""UPDATE data 
                                                        SET current_bet_competition=?, current_bet_rate=?, current_bet_match=?, current_bet_result=?, current_coeff=?, balance=?, win_count=?
                                                        WHERE user_id=?""", (None, None, None, None, None, int(data[1]) + int(data[3]) * int(data[-1]), int(data[-3]) + 1, int(event.obj.message["from_id"]),))
                                    vk.messages.send(
                                        user_id=event.obj.message["from_id"],
                                        message=f'Ваша ставка сыграла. Выигрыш составил {int(data[3]) * int(data[-1])}',
                                        random_id=random.randint(0, 2**64),)
                                    DB.commit()
                                else:
                                    CUR.execute("""UPDATE data 
                                                        SET current_bet_competition=?, current_bet_rate=?, current_bet_match=?, current_bet_result=?, current_coeff=?, loss_count=?
                                                        WHERE user_id=?""", (None, None, None, None, None, int(data[-2]) + 1, int(event.obj.message["from_id"]),))
                                    vk.messages.send(
                                        user_id=event.obj.message["from_id"],
                                        message="К сожалению, ваша ставка не сыграла",
                                        random_id=random.randint(0, 2**64),)
                                    DB.commit()
                    else:
                        vk.messages.send(
                            user_id=event.obj.message["from_id"],
                            message="Матч еще не завершен или информации о его результатах пока нет",
                            random_id=random.randint(0, 2**64),)
            elif '/statistic' in txt:
                data = CUR.execute("""SELECT * FROM data WHERE user_id=?""", (int(
                    event.obj.message["from_id"]),)).fetchmany(1)[0]
                user = vk.users.get(user_ids=data[0])[0]
                vk.messages.send(
                    user_id=event.obj.message["from_id"],
                    message=f"Пользователь: {user['last_name']} {user['first_name']}\nВыиграно ставок: {data[-3]}\nПроиграно ставок: {data[-2]}",
                    random_id=random.randint(0, 2**64),)
            elif '/commands' in txt:
                vk.messages.send(
                    user_id=event.obj.message["from_id"],
                    message="Доступные комманды:\n/bet - сделать ставку\n/timetable - узнать расписание на неделю\n/statistic - ваша статистика\n/get_result - Вывести результат вашей ставки",
                    random_id=random.randint(0, 2**64),)


if __name__ == "__main__":
    main()
