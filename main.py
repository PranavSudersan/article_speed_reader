from bs4 import BeautifulSoup
import requests
import re
import numpy as np
import pandas as pd
import string
##with open('simple.html') as html_file:
##    soup = BeautifulSoup(html_file, 'lxml')
##
###print(soup.prettify())
##
##match = soup.title.text
##print(match)
##
##article = soup.find('div', class_='article')
##print(article)
##
##headline = article.h2.a.text
##print(headline)
##
##summary = article.p.text
##print(summary)
##
##
##for article in soup.find_all('div', class_='article'):
##    headline = article.h2.a.text
##    summary = article.p.text
##    print(headline, summary)
    

#https://en.wikipedia.org/wiki/Euler-Bernoulli_beam_theory
#https://en.wikipedia.org/wiki/Frog
url_link = 'https://en.wikipedia.org/wiki/Euler-Bernoulli_beam_theory'
source = requests.get(url_link).text
soup = BeautifulSoup(source, 'lxml')
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
            if sub_child.name == 'span': #inline match
                math = sub_child.find('math').attrs
                tag_list.append('math_inline')
                text_list.append(math['alttext'][15:-1])
            else:
                tag_list.append('p' if sub_child.name == None else sub_child.name)
                text_list.append(sub_child.text)
            section_list.append(section_id)
        #print(child.contents[0])
    if tag == 'dl': #equations
        section_id += 1
        math = child.find('math').attrs
        tag_list.append('math')
        text_list.append(math['alttext'][15:-1])
        section_list.append(section_id)
    if tag == 'blockquote':
        for sub_child2 in child.children:
            if sub_child2.name == 'sup' or sub_child2.text.strip() == '' : #ignore citations
                continue
            if sub_child2.name == 'dl': #inline match
                math = sub_child2.find('math').attrs
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
counted_tags = ['a','b','i','p','math_inline'] #words counted only for these tags
article_df['Word count'] = np.where(article_df['Tag'].isin(counted_tags),
                                    article_df['Text'].str.count(' ') + 1,
                                    0)

article_df.to_excel('test article.xlsx')

total_words = article_df['Word count'].sum()

words_per_minute = 200
word_block = 3

for section_id in article_df['Section id'].unique():
    section_df = article_df[article_df['Section id'] == section_id].reset_index()
    slow_text = section_df.iloc[0]['Text'].strip()
    print('SLOWTEXT', slow_text)

    mathinline_ind = section_df[section_df['Tag'] == 'math_inline'].index
    if len(mathinline_ind) == 0:
        free_text = ''.join(section_df.iloc[1:]['Text'])
        section_text_list = free_text.replace('\n',' ').strip().split(' ')
    else:
        free_text = ''.join(section_df.iloc[1:mathinline_ind[0]]['Text'])
        section_text_list = free_text.replace('\n',' ').strip().split(' ')
    
    ind_start = 0
    for ind, mind in enumerate(mathinline_ind):
        #inline math
        math_text = section_df.iloc[mind]['Text'].strip()
        if len(math_text) == 1:
            section_text_list[-1] += f' {math_text}'
        else:
            section_text_list.append(math_text)
        #remaining text
        end_ind = len(section_df) if ind == len(mathinline_ind)-1 else mathinline_ind[ind+1]
        free_text = ''.join(section_df.iloc[mind+1:end_ind]['Text'])
        section_text_split = free_text.replace('\n',' ').strip().split(' ')
##        if len(section_text_split) == 1 and section_text_split[0] in string.punctuation:
##            section_text_list[-1] += section_text_split[0]
##        else:
        section_text_list.extend(section_text_split)       
    section_text_list = ' '.join(section_text_list).split() #remove empty elements
    for wb in range(int(len(section_text_list)/word_block)+1):
        wb_id = wb*word_block
        if wb_id >= len(section_text_list):
            continue
        wb_end = len(section_text_list) if wb_id+word_block > len(section_text_list) else wb_id+word_block
        fast_text = ' '.join(section_text_list[wb_id:wb_end]).strip()
        print('FASTTEXT', fast_text)
