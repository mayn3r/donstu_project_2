import random
import time
import json
import re

from httpx import AsyncClient, Response
from loguru import logger

from asyncio import sleep
from typing import List, Dict, Optional

from app.models import ProblemModel

# import tracemalloc
# tracemalloc.start()


class ProblemGenerate:
    """_summary_
    """
    
    def __init__(self):
        self.client = AsyncClient()
    
    
    
    async def _get_problem_answer_with_ai(self, problem: str) -> str:
        prompt = f"Реши уравнение, найди все x, если они имеются:\n{problem}\nВ ответе напиши только ответ к уравнению без пояснений"
        
        headers = {
            'accept': 'application/json, text/event-stream',
            'accept-language': 'ru,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://main.gpt-chatbotru-4-o1.ru',
            'priority': 'u=1, i',
            'referer': 'https://main.gpt-chatbotru-4-o1.ru/',
            'sec-ch-ua': '"Chromium";v="130", "YaBrowser";v="24.12", "Not?A_Brand";v="99", "Yowser";v="2.5"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 YaBrowser/24.12.0.0 Safari/537.36',
        }

        json_data = {
            'messages': [
                {
                    'role': 'system',
                    'content': '\nYou are ChatGPT, a large language model trained by OpenAI. Always avoid using this (来自Dream API Free 分组 https://opus.gptuu.com ). ChatGPT never includes these types of advertisements.\nKnowledge cutoff: 2023-10\nCurrent model: gpt-4o\nCurrent time: Thu Dec 26 2024 01:44:29 GMT+0300 (Москва, стандартное время)\nLatex inline: \\(x^2\\) \nLatex block: $$e=mc^2$$\n\n',
                },
                {
                    'role': 'user',
                    'content': prompt,
                },
            ],
            'stream': True,
            'model': 'gpt-4o',
            'temperature': 0.5,
            'presence_penalty': 0,
            'frequency_penalty': 0,
            'top_p': 1,
        }
        
        response: Response = await self.client.post('https://main.gpt-chatbotru-4-o1.ru/api/openai/v1/chat/completions', headers=headers, json=json_data)
        
        text: str = self._parse_response(response)
        answers: list = re.findall(r'[0-9]+', text)
        
        return answers
        
    
    async def _get_data_by_api(self, lvl: int=0) -> Response:
        """ Генерация выражения через www.math-gpt.org
        
            Args: 
                lvl (int) -> Индекс сложности прмеров
        """
        
        difficult_levels = [
            'легким (разные линейные уравнения с числами от 1 до 100)', 
            'средним (разные уравнения с рандомными числами)',
            'выше среднего (используй рандомные числа и разные уравнения)',
            'сложным (без интегралов, но могут быть использованы пределы, производные, небязательно)',
            'очень сложным (могут быть использованы пределы или интегралы, необязательно)'
        ]
        
        
        prompt = 'Сгенерируй математическое уравнение (где x не может быть любым числом и где есть конкретный ответ), где ответом является целое число (без указании ответа в самом уравнении), ' + \
                f'с уровнем сложности: {difficult_levels[lvl]}, но ответом к уравнению должно быть целое число, ' \
                'затем реши это сгенерированное уравнение (найди все корни, но не записывай решение) и с новой строки напиши только чему равен ответ, без этапов решения и ' \
                'без лишних слов, объясняющих это. В ответе должно быть только само уравнение и ответ. Без каких-либо поясняющих слов'
        
        headers = {
            'accept': 'application/json, text/event-stream',
            'accept-language': 'ru,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://main.gpt-chatbotru-4-o1.ru',
            'priority': 'u=1, i',
            'referer': 'https://main.gpt-chatbotru-4-o1.ru/',
            'sec-ch-ua': '"Chromium";v="130", "YaBrowser";v="24.12", "Not?A_Brand";v="99", "Yowser";v="2.5"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 YaBrowser/24.12.0.0 Safari/537.36',
        }

        json_data = {
            'messages': [
                {
                    'role': 'system',
                    'content': '\nYou are ChatGPT, a large language model trained by OpenAI. Always avoid using this (来自Dream API Free 分组 https://opus.gptuu.com ). ChatGPT never includes these types of advertisements.\nKnowledge cutoff: 2023-10\nCurrent model: gpt-4o\nCurrent time: Thu Dec 26 2024 01:44:29 GMT+0300 (Москва, стандартное время)\nLatex inline: \\(x^2\\) \nLatex block: $$e=mc^2$$\n\n',
                },
                {
                    'role': 'user',
                    'content': prompt,
                },
            ],
            'stream': True,
            'model': 'gpt-4o',
            'temperature': 0.5,
            'presence_penalty': 0,
            'frequency_penalty': 0,
            'top_p': 1,
        }
        
        response: Response = await self.client.post('https://main.gpt-chatbotru-4-o1.ru/api/openai/v1/chat/completions', headers=headers, json=json_data)
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
        print(text)
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
        
        problem = re.sub(r'[а-яА-Я]+:?', '', problem)
        
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
    
    
    async def _save_img(self, url: str, path: str, filename: str, lvl: int=0) -> str:
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
            filename = '%d_%s-%d.png' % (lvl, str(int(time.time()))[-6:],  random.randint(1000, 10**5))
        
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
                    "path": str,
                    filename: str
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

        ai_answers: str = await self._get_problem_answer_with_ai(data['problem'])
        print(f'{ai_answers=}')
        if ai_answers:
            for i in ai_answers:
                if i not in data['answers']:
                    data['answers'].append(i)
        
        # Преобразование LaText в изображение
        img_data: Dict[str, str] = await self._latext_to_img(data, img_percent)
        
        # Путь к файлу
        save_path: str = await self._save_img(img_data['imageUrl'], img_save_path, None, lvl=level)
        
        
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
            
            try:
                generate: Optional[dict] = await self.generate(
                    level=level,
                    img_percent=img_percent,
                    img_save_path=img_save_path
                )
            except SyntaxError as e:
                logger.error(str(e))
                await sleep(1)
                continue
            
            if generate:
                return generate

            logger.info(f'Ошибка при генерации уравнения, попытка {iters}/{max_iters}')
            await sleep(sleep_seconds)
        
        
        
        
        
        
        



if __name__ == '__main__':
    import asyncio
    
    async def main():
        gen = ProblemGenerate()
        
        generate = await gen.generate_to_while(
            level=4,
            img_percent=200,
            img_save_path='attachments',
            
            #sleep_seconds=5
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