import re
from .pagescrape import pagescrape, get_html
import os
from bs4 import BeautifulSoup
import json

HTML_PARSE_FORMAT = 'html.parser'


def write_to_html(data: BeautifulSoup, filename, path):
    if not os.path.exists("Saved_MCQs"):
        os.mkdir("Saved_MCQs")
    # add mathjax
    #  <script>
    #   MathJax = {
    #     tex: {
    #       inlineMath: [['$', '$'], ['\\(', '\\)']]
    #     }
    #   };
    # </script>
    # <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js">
    # </script>
    head = BeautifulSoup("""
    <head>
    <script>
      MathJax = {
        tex: {
          inlineMath: [['$', '$'], ['\\(', '\\)']]
        }
      };
    </script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js">
    </script>
    </head>""", "lxml")
    data.body.insert_before(head)
    # print(data)
    with open(f"{path}/{filename}.html", "w+", encoding="utf-8") as file:
        file.write(str(data.prettify()))


def write_to_json(data: list, path):
    with open(f"{path}/questions.json", 'w+') as f:
        json.dump({"questions": data}, f)


def mcqscrape_json(url: str) -> list:
    # print(title)
    mcqs = []
    res = get_html(url)
    _soup = BeautifulSoup(res, HTML_PARSE_FORMAT)

    try:
        main_content = [x for x in _soup.find(
            "div", {"class": "entry-content"}).findAll('p') if re.search(r'\d\. .*', x.text)][0]

        split_content = ['<p>' + x for x in str(main_content).split('<p>')]

        for x in split_content:
            if re.search(r'<span', x):
                question_dict = {
                    "q": BeautifulSoup(x.split('<span')[0], HTML_PARSE_FORMAT).find('p').text,
                    "a": BeautifulSoup(x.split('<span')[1], HTML_PARSE_FORMAT).find('div').text
                }
                mcqs.append(question_dict)

    except Exception as err:
        print("Error: ", err)

    return mcqs


def mcqscrape_html(url: str, path: str) -> str:
    if '1000' in url:
        pages = pagescrape(url, path)
        mega_html = ''
        for k, v in pages.items():
            print("getting", k, "from ->", v, end=' ... ')
            mega_html += mcqscrape_html(v, path)
            print("Done!")
        write_to_html(BeautifulSoup(mega_html, 'lxml'),
                      url.split('/')[-2], path)
    res = get_html(url)
    soup = BeautifulSoup(res, 'lxml')
    content = soup.find('div', class_='entry-content')
    # print(content.prettify())
    paras = content.findAll('p')
    classes_to_remove = ["sf-mobile-ads",
                         "desktop-content", "mobile-content", "sf-nav-bottom"]
    tags_to_remove = ["script"]
    # remove the answer drop downs
    [sp.decompose() for sp in content.findAll('span', class_="collapseomatic")]
    for class_to_remove in classes_to_remove:
        [sp.decompose() for sp in content.findAll('div',
                                                  class_=class_to_remove)]
    for tag_to_remove in tags_to_remove:
        [sp.decompose() for sp in content.findAll(tag_to_remove)]
    for tag in paras[-3:]:
        tag.decompose()
    [tag.extract() for tag in content.find_all(
        "div") if tag.text == "advertisement"]
    # span attribute cleanup
    for tag in content.findAll(True):
        tag.attrs.pop("class", "")
        tag.attrs.pop("id", "")
    try:
        heading = soup.find(
            'h1', class_="entry-title").text.split('–')[1].strip()
        print(heading)
    except IndexError:
        print("cant get heading", IndexError)
        print(str(content)[:100])
        return ''
    return content.prettify()
