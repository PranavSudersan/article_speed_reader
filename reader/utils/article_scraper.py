import requests
import re
import numpy as np
import pandas as pd
import string
from urllib.parse import urlparse
import urllib.request
from bs4 import BeautifulSoup

#https://en.wikipedia.org/wiki/Euler-Bernoulli_beam_theory
#https://en.wikipedia.org/wiki/Frog

def get_article(url_link):
#url_link = 'https://en.wikipedia.org/wiki/Euler-Bernoulli_beam_theory'
    try:
        con = urllib.request.urlopen(url_link)
    except Exception as e:
        print(e, 'ERROR')
        return 'INVALID URL'
    source = requests.get(url_link).text
    soup = BeautifulSoup(source, 'lxml')

    domain = urlparse(url_link).netloc
    if 'wikipedia' in domain:
        article_df = scrape_wiki(soup)
        return article_df
    else:
        return None

def scrape_wiki(soup):    
    article = soup.find('div', class_='mw-parser-output')

    title = soup.find('h1', class_='firstHeading mw-first-heading').text
    print(title)

    tag_list = ['h1']
    text_list = [title]

    #section id updated on each new heading/math equation (not inline)/boxquote
    section_id = 0
    section_list = [section_id]

    for child in article.children:
        if child.text == '\n':
            continue
        tag = str(child.name)
        if re.match(r'h[0-9]', tag): #headings
            section_id += 1
            heading_text = child.find('span', class_='mw-headline').text
            tag_list.append(tag)
            text_list.append(heading_text)
            section_list.append(section_id)
        if tag == 'p': #paragraphs
            for sub_child in child.children:
                if sub_child.name == 'sup' or sub_child.text.strip() == '' : #ignore citations
                    continue
                if sub_child.name == 'span' and 'class' in sub_child.attrs.keys():
                    if sub_child['class'][0] == 'mwe-math-element': #inline math
                        math = sub_child.find('math').attrs
                        tag_list.append('math_inline')
                        text_list.append(math['alttext'][15:-1])
                        section_list.append(section_id)
                else:
                    tag_list.append('p' if sub_child.name == None else sub_child.name)
                    text_list.append(sub_child.text)
                    section_list.append(section_id)
        if tag == 'dl' and 'dd' in child.attrs.keys():               
            sub_child1 = child.dd.contents[0]
            #math elements
            if sub_child1.name == 'span' and sub_child1['class'][0] == 'mwe-math-element':
                section_id += 1
                math = sub_child1.find('math').attrs
                tag_list.append('math')
                text_list.append(math['alttext'][15:-1])
                section_list.append(section_id)
        if tag in ['ul', 'ol']: #lists
            mk_id = 0 #ordered bullet marker
            for list_child in child.children:
                list_text = ' '.join(list_child.text.split()).strip()
                if len(list_text) != 0:
                    tag_list.append('li')
                    marker = '•' if tag == 'ul' else '('+str(mk_id+1)+')'
                    text_list.append(f' {marker} ' + list_child.text.strip())
                    section_list.append(section_id)
        if tag == 'blockquote': #boxes
            for sub_child2 in child.children:
                if sub_child2.name == 'sup' or sub_child2.text.strip() == '' : #ignore citations
                    continue
                if sub_child2.name == 'dl'  and 'dd' in child2.attrs.keys(): #inline match
                    sub_child3 = sub_child2.dd.contents[0]
                    if sub_child3.name == 'span' and sub_child3['class'][0] == 'mwe-math-element':
                        math = sub_child3.find('math').attrs
                        tag_list.append('math_box')
                        text_list.append(math['alttext'][15:-1])
                else:
                    tag_list.append('p' if sub_child2.name == None else sub_child2.name)
                    text_list.append(sub_child2.text)
                section_id += 1
                section_list.append(section_id)
                

            

    article_df = pd.DataFrame({'Tag': tag_list,
                               'Text': text_list,
                               'Section id': section_list})
    counted_tags = ['a','b','i','p','li','math_inline'] #words counted only for these tags
    article_df['Word count'] = np.where(article_df['Tag'].isin(counted_tags),
                                        article_df['Text'].str.count(' ') + 1,
                                        0)

    #article_df.to_excel('test article.xlsx') #save excel
    return article_df

