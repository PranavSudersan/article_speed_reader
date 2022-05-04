def chunk_maker(article_df, word_block=3):

    total_words = article_df['Word count'].sum()

    #word_block = 5
    chunk_data = []
    for section_id in article_df['Section id'].unique():
        section_df = article_df[article_df['Section id'] == section_id].reset_index()
        slow_text = section_df.iloc[0]['Text'].strip()
        #print('SLOWTEXT', slow_text)
        if section_df.iloc[0]['Tag'] in ['math', 'math_box']:
            slow_text = r'\(' + slow_text + r'\)' #mathjax formatting for display
        chunk_data.append(('SLOW', slow_text))

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
            section_text_list.append(r'\(' + math_text + r'\)') #mathjax formatting for display
            #remaining text
            end_ind = len(section_df) if ind == len(mathinline_ind)-1 else mathinline_ind[ind+1]
            free_text = ''.join(section_df.iloc[mind+1:end_ind]['Text'])
            section_text_split = free_text.replace('\n',' ').strip().split(' ')
            section_text_list.extend(section_text_split)       
        section_text_list[:] = [x for x in section_text_list if x != ''] #remove empty elements
        for wb in range(int(len(section_text_list)/word_block)+1):
            wb_id = wb*word_block
            if wb_id >= len(section_text_list):
                continue
            wb_end = len(section_text_list) if wb_id+word_block > len(section_text_list) else wb_id+word_block
            fast_text = ' '.join(section_text_list[wb_id:wb_end]).strip()
            #print('FASTTEXT', fast_text)
            chunk_data.append(('FAST', fast_text))

    return chunk_data, total_words

