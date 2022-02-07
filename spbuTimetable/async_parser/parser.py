import aiohttp
from bs4 import BeautifulSoup

__url = 'https://timetable.spbu.ru/'

__headers = {'ru': {'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'},
             'en': {}}

__filter_for_children = lambda x: x.name is not None


async def as_get_fields_of_study(lng='ru') -> dict:
    """
    Get studying directions

    :param lng: ru - Russian or en - English
    :return:
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(__url, headers=__headers[lng]) as resp:
            text = await resp.text()

    if resp.status != 200:
        raise Exception('Bad request!')
    soup = BeautifulSoup(text, 'lxml')
    divs = soup.find_all('div', {'class': 'panel-heading'})
    timetable = None
    for div in divs:
        if div.text == 'Направления' or div.text == 'Fields of study':
            timetable = div.parent
            break
    ans = {}
    for i in timetable.find_all('a'):
        ans[i.text] = i['href'][1:]
    return ans


async def as_get_programs(direction: str, lng='ru') -> dict:
    """
    Get studying programs by `direction`

    :param direction: Direction of studying. Example: AMCP
    :param lng: ru - Russian or en - English
    :return:
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{__url}/{direction}', headers=__headers[lng]) as resp:
            text = await resp.text()
    if resp.status != 200:
        raise Exception('Bad request!')
    soup = BeautifulSoup(text, 'lxml')
    programs = soup.find('ul', {'id': 'studyProgramLevel1'}).find_all('li')
    ans = {}
    for program in programs[1:]:
        _ = {}
        name: str = program.find('div').text.strip()
        for year in program.find_all('a'):
            _[year.text.strip()] = int(year['href'].split('/')[-1])
        ans[name] = _

    return ans


async def as_get_groups(direction: str, group_id: str or int, lng='ru') -> dict:
    """
    Get groups

    :param direction: Direction of studying. Example: AMCP
    :param group_id: Group id from website or func 'get_programs'
    :param lng: ru - Russian or en - English
    :return:
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{__url}/{direction}/StudyProgram/{group_id}', headers=__headers[lng]) as resp:
            text = await resp.text()
    if resp.status != 200:
        raise Exception('Bad request!')
    soup = BeautifulSoup(text, 'lxml')
    groups = soup.find('ul', id='studentGroupsForCurrentYear')
    ans = {}
    for i in groups.find_all('li'):
        group = list(filter(__filter_for_children, i.children))[0]
        name = group.find('div').text.strip()
        _ = group['onclick'].split('=')[-1][1:-1].split('/')
        ans[name] = [direction, int(_[-1])]

    return ans


async def as_get_lessons(direction: str, timesheet_id: str or int, start_date: str = '', lng='ru') -> dict:
    """
    Get lessons

    :param direction: Direction of studying. Example: AMCP
    :param timesheet_id: timesheet id from website or func 'get_groups'
    :param start_date: Example: 2021-11-20
    :param lng: ru - Russian or en - English
    :return:
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{__url}/{direction}/StudentGroupEvents/Primary/{timesheet_id}/{start_date}',
                               headers=__headers[lng]) as resp:
            text = await resp.text()
    if resp.status != 200:
        raise Exception('Bad request!')
    soup = BeautifulSoup(text, 'lxml')
    week = soup.find('div', id='accordion')
    ans = {}
    for day in filter(__filter_for_children, week.children):
        lessons = []
        day_name = list(filter(__filter_for_children, day.find('div').children))[0].text.strip()
        for less in day.find('ul').find_all('li'):
            _ = {}
            items = list(filter(__filter_for_children, less.children))
            _['time'] = items[0].find('span').text.strip()
            _['subject'] = items[1].find('span').text.strip()
            _['location'] = items[2].find('span').text.strip()
            _['teachers'] = items[3].find('span').text.strip()
            lessons.append(_)
        ans[day_name] = lessons

    return ans
