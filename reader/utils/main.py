from . import article_scraper #import get_article
from . import chunk_maker #import chunk_maker



def main(url_path, word_block=3):
    article_df = article_scraper.get_article(url_path)
    if type(article_df).__name__ == 'DataFrame':
        chunk_data, total_words = chunk_maker.chunk_maker(article_df, word_block)
        return {'data': chunk_data,
                'word count': total_words,
                'status': 'SUCCESS'}
    else:
        return {'data': article_df, 'status': 'FAIL'}

#url_link = 'https://en.wikipedia.org/wiki/Euler-Bernoulli_beam_theory'

#data = main(url_link)
