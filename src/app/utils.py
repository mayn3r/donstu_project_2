import random
import time
import json
import re

from httpx import AsyncClient, Response
from loguru import logger

from asyncio import sleep
from typing import List, Dict, Optional

# import tracemalloc
# tracemalloc.start()


class ProblemGenerate:
    """_summary_
    """
    
    def __init__(self):
        self.client = AsyncClient()
        
    
    async def _get_data_by_api(self, lvl: int=0) -> Response:
        """ Генерация выражения через www.math-gpt.org
        
            Args: 
                lvl (int) -> Индекс сложности прмеров
        """
        
        difficult_levels = [
            'легким', 
            'средним',
            'выше среднего',
            'сложным (без интегралов, но могут быть использованы пределы, производные, небязательно)',
            'очень сложным (могут быть использованы пределы или интегралы, необязательно)'
        ]
        
        
        prompt = 'Сгенерируй математическое уравнение (без указании ответа в самом уравнении), ' + \
                f'с уровнем сложности: {difficult_levels[lvl]}, но ответом к уравнению должно быть целое число, ' \
                'затем с новой строки напиши ответ к уравнению, в ответе напиши уравнение ' \
                'без лишних слов, объясняющих это'
        
        headers = {
            'accept': '*/*',
            'accept-language': 'ru,en;q=0.9',
            'content-type': 'application/json',
            'cookie': '__client_uat=0; __client_uat_Do4ajzMV=0; ph_phc_mD5jgxfqkIw6GkIfwSV3JQqLQQWzLcQZU3Fia8PxANQ_posthog=%7B%22distinct_id%22%3A%220193fdbb-1621-7fe5-8b29-cd4f979df96c%22%2C%22%24sesid%22%3A%5B1735129186708%2C%220193fdbb-161a-7ba6-92f2-3d935ed5fdde%22%2C1735128716825%5D%7D',
            'origin': 'https://math-gpt.org',
            'priority': 'u=1, i',
            'referer': 'https://math-gpt.org/',
            'sec-ch-ua': '"Chromium";v="130", "YaBrowser";v="24.12", "Not?A_Brand";v="99", "Yowser";v="2.5"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 YaBrowser/24.12.0.0 Safari/537.36',
            'x-topic': 'math',
        }
        json_data = {'messages': [{'role': 'user', 'content': [{'type': 'text','text': prompt}]}]}
        
        response: Response = await self.client.post('https://math-gpt.org/api/v2/chat/completions', headers=headers, json=json_data)
        logger.debug(f'Отправлен запрос на генерацию выражения, lvl: {lvl}')
        
        return response

    
    def _parse_response(self, response: Response) -> str:
        """_summary_

        Args:
            lvl (int) -> Индекс сложности прмеров

        Returns:
            dict: _description_
        """
        
        data: List[str] = list(
            map(
                lambda x: x[:-2], filter(
                        lambda x: x,
                        response.content.decode().split('data: ')
                    )
                )
        )[:-1]
        
        json_data: List[dict] = list(
                map(
                    lambda x: json.loads(x),
                    data
                )
            )
        
        text = ''
        for i in json_data:
            try:
                text += i['choices'][0]['delta']['content']
            except (KeyError, TypeError) as e:
                text += str(i['choices'][0]['delta']['tool_calls'][0]['function']['arguments'])
        
        logger.debug('Ответ собран в целый текст')
        
        return text

    
    def _parse_problem_to_response(self, text: str) -> dict:
        """_summary_

        Args:
            text (str): _description_

        Returns:
            dict: _description_
        """
        
        data: list = list(
            filter(
                lambda x: (len(x) > 2) or x.isdecimal(),
                text.split('\n')
            )
        )
        
        problem = ''
        for i in data.copy():
            if 'x' in i or '\\' in i:
                problem = i
                data.remove(i)
                break
        
        if 'lim' in problem and '=' in problem:
            problem = re.sub('= [0-9-]+', '= ?', problem)
        
        answers: list = re.findall(r'[0-9]+', ''.join(data))
        
        logger.debug('Данные успешно извлечены из текста')
        
        if not problem:
            logger.error('Данные сгенерированы неверно!')
        
        return {
            'problem': problem.replace('$', '').strip(),
            'answers': answers
        }
    
    
    # # # # #
    async def _latext_to_img(self, data: Dict[str, str], percent: int=125) -> str:
        """_summary_

        Args:
            data (Dict[str, str]): _description_

        Returns:
            str: _description_
        """
        
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'ru,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://latex2image.joeraut.com',
            'priority': 'u=1, i',
            'referer': 'https://latex2image.joeraut.com/',
            'sec-ch-ua': '"Chromium";v="130", "YaBrowser";v="24.12", "Not?A_Brand";v="99", "Yowser";v="2.5"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 YaBrowser/24.12.0.0 Safari/537.36',
        }

        problem = data['problem'].replace('\\', '\\\\')

        data = r'{{"latexInput":"{0}","outputFormat":"PNG","outputScale":"{1}%"}}'.format(problem, percent)
        
        response = await self.client.post(
            'https://e1kf0882p7.execute-api.us-east-1.amazonaws.com/default/latex2image',
            headers=headers,
            data=data,
        )

        if response.json()['error']:
            data = r'{{"latexInput":"\\begin{{align*}}\n{0}\n\\end{{align*}}\n","outputFormat":"PNG","outputScale":"{1}%"}}'.format(problem, percent)
            
            response = await self.client.post(
                'https://e1kf0882p7.execute-api.us-east-1.amazonaws.com/default/latex2image',
                headers=headers,
                data=data,
            )
        
        logger.debug('Успешно отправлен запрос по генерации изображения')
        
        return response.json()
    
    
    async def _save_img(self, url: str, path: str, filename: str) -> str:
        """ Сохранение изображения текста

        Args:
            url (str): Ссылка на изоражение
            path (str): Путь для сохранения

        Returns:
            str: Путь с изображением
        """
        
        if not path.endswith('/'):
            path += '/'
        
        if filename is None:
            filename = '%d-%d.png' % (int(time.time()),  random.randint(1000, 10**5))
        
        response = await self.client.get(url)
        
        with open(path+filename, 'wb') as file:
            file.write(response.content)
            
        logger.debug(f'Изображение "{filename}" успешно сохранено')
        
        return path+filename
        
        
    
    
    async def generate(self, level: int, img_percent: int=200, img_save_path: str='attachments') -> Dict[str, str]:
        """ Генерация выражения

        Args:
            level (int): Уровень сложности примера
            img_percent (int): Процент качества фотографии, полученное из LaText. Defaults to 200.

        Returns:
            Dict[str, str]: Словарь содержащий problem (выражение), answer (ответ к выр-ю),
            img -> словарь, содержащий: url (ссылка на фотографию на сервере), path (путь до фотографии)
            
            Структура:
            {
                "problem": str,
                "answer": List[str],
                "img": {
                    "url": str,
                    "path": str
                }
            }
        """
        
        # Отправка запроса на генерацию выражения
        api_response: Response = await self._get_data_by_api(lvl=level)
        
        # Получение данных из ответа
        parse_response: str = self._parse_response(api_response)
        
        # Получение выражения и ответа на него из текста запроса
        data: Dict[str, str] = self._parse_problem_to_response(parse_response)
        
        if not data['problem']:
            return None
        
        # Преобразование LaText в изображение
        img_data: Dict[str, str] = await self._latext_to_img(data)
        
        # Путь к файлу
        save_path: str = await self._save_img(img_data['imageUrl'], img_save_path, None)
        
        
        return_data: Dict[str, str] = data.copy()
        return_data['img'] = {
            'url': img_data['imageUrl'],
            'path': save_path, 
            'filename': save_path.split('/')[-1]
        }
        
        logger.success('Уравнение сгенерировано окончательно!')
        
        return return_data

    
    async def generate_to_while(self, level: int, img_percent: int=200, 
                                img_save_path: Optional[str]=None, 
                                max_iters: int=15, sleep_seconds: int=5
            ) -> Dict[str, str]:
        """ 
        *См. документацию к функции ProblemGenerate.generate() 
        ==> Запуск функции ProblemGenerate.generate() в цикле
        """
        
        logger.info('Запущена генерация уравнения в цикле')
        
        iters = 0
        while iters < max_iters:
            iters += 1
            
            generate: Optional[dict] = await self.generate(
                level=level,
                img_percent=img_percent,
                img_save_path=img_save_path
            )
            
            if generate:
                return generate

            logger.info(f'Ошибка при генерации уравнения, попытка {iters}/{max_iters}')
            await sleep(sleep_seconds)
        
        
        
        
        
        
        



if __name__ == '__main__':
    import asyncio
    
    async def main():
        gen = ProblemGenerate()
        print(dir(gen))
        
        generate = await gen.generate_to_while(
            level=2,
            img_percent=500,
            img_save_path='attachments',
            
            sleep_seconds=5
        )
        
        print(generate)
        
        #s = await gen._save_img('https://latex2image-output.s3.amazonaws.com/img-jYce5D1FftGN.png', 'attachments', '0.png')
        #print(s)
        
        # parse = await gen._parse_response(
        #     lvl=1
        # )
        
        # print(parse)
        
        # problems = gen._parse_problem_to_response(parse)
        # if problems['problem']:
        #     print(problems)
            
        #     img = await gen._latext_to_img(problems, percent=500)
        #     print(img)
    
    
    
    asyncio.get_event_loop().run_until_complete(main())