from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .utils import main

posts = [
    {
       'author': 'Rani',
       'title': 'Blog post 1',
       'content': r'The roots of a quadratic equation is \[x = {-b \pm \sqrt{b^2-4ac} \over 2a}.\]',
       'date_posted': 'August 27, 2018'
    },
    {
       'author': 'Ranita',
       'title': 'Blog post 2',
       'content': 'Second post content',
       'date_posted': 'August 28, 2018'
    },
]

word_chunks = [('SLOW',1),('FAST',2),('FAST',3),('FAST','latex coming'),
               ('SLOW',r'equation \(ax^2 + bx + c = 0\) is '),
               ('FAST',6),('SLOW','nonono')]
param_dict = {
                'word_block': 3,
                'url_path': ''
            }

def home(request):
    context = {
        'posts': posts,
        'update_function': return_word_chunk,
        #'title': 'Home',
    }
    return render(request,'reader/home.html', context)

def about(request):
    return render(request,'reader/about.html', {'title': 'About'})

def return_url_input(request):
    param_dict['url_path'] = request.POST['url_path']
    param_dict['word_block'] = int(request.POST['wordblock'])
    chunk_data = main.main(**param_dict)
    if chunk_data['status'] == 'SUCCESS':
        word_chunks.clear()
        word_chunks.extend(chunk_data['data'])
    if chunk_data['status'] == 'SUCCESS':
        response = {'message': 'Article loaded!',
                    'wordcount': str(chunk_data['word count']),
                    'chunkcount': str(len(chunk_data['data']))}
    elif chunk_data['status'] == 'FAIL':
        response = {'message': 'Invalid URL',
                    'wordcount': '0'}
    print(response)
    return JsonResponse(response, safe=False)

def return_word_chunk(request):
    try:
        #print('post request', request.POST['ind'])
        chunk_id = int(request.POST['ind'])
        speed, chunk = word_chunks[chunk_id]
        
    except Exception as e:
        print('EXCEPTION', e)
        chunk = 'END!'
    return HttpResponse(chunk)

def return_wb_input(request):
    param_dict['url_path'] = request.POST['url_path']
    param_dict['word_block'] = int(request.POST['wordblock'])
    chunk_data = main.main(**param_dict) #TODO: only run chunk_maker here
    print('im here')
    if chunk_data['status'] == 'SUCCESS':
        print('im here2')
        word_chunks.clear()
        word_chunks.extend(chunk_data['data'])
        print(word_chunks[5])
    return HttpResponse('response')


