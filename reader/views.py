from django.shortcuts import render
from django.http import HttpResponse

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

word_chunks = [1,2,3,'latex coming',r'equation \(ax^2 + bx + c = 0\) is ',
               6,'nonono']

def home(request):
    context = {
        'posts': posts,
        'update_function': return_word_chunk,
        #'title': 'Home',
    }
    return render(request,'reader/home.html', context)

def about(request):
    return render(request,'reader/about.html', {'title': 'About'})


def return_word_chunk(request):
    try:
        print('post request', request.POST['ind'])
        chunk_id = int(request.POST['ind'])
        chunk = word_chunks[chunk_id]
        
    except Exception as e:
        print('EXCEPTION', e)
        chunk = 'END!'
    return HttpResponse(chunk)


