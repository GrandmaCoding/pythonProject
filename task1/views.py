from django.http import HttpResponse
from django.shortcuts import render
from .forms import InputForm
from openai import OpenAI

from task1.models import Post
from django.utils import timezone
from django.contrib.auth.models import User


ME = User.objects.get(username='vladimir')
BOT = User.objects.get(username='bot')


def generate_answer(user_input):
    client = OpenAI(
        api_key="sk-KVD8VYoze5Ivy8BFwfV9KnCzdMvhnnyp",
        base_url="https://api.proxyapi.ru/openai/v1",
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
             "content": ''},  # Тут нужно написать промт, выдающий роль помощника
            {"role": "user",
             "content": user_input}
        ]
    )
    return completion.choices[0].message


def home(request):
    context = {'form': InputForm()}
    posts = Post.objects.all().order_by('published_date')
    return render(request, "home.html", {'posts': posts, 'context': context})


def addpage(request):
    if request.method == 'POST':
        context = {'form': InputForm()}

        text = str(request.POST['field_text'])
        Post.objects.create(author=ME, text=text, published_date=timezone.now())
        answer = generate_answer(text)
        answer_dict = {"POST": "ok", "answer": list(answer)[0][1]}

        Post.objects.create(author=BOT, text=answer_dict["answer"], published_date=timezone.now())
        posts = Post.objects.all().order_by('published_date')

        return render(request, "home.html", {'posts': posts, 'context': context})
    else:
        form = InputForm()
    return render(request, 'home.html', {'form': form})
