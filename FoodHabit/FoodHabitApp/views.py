from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import FoodHabitModel, Board
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .forms import UploadFileForm
import os
from django.contrib.auth.decorators import login_required
from .service import Service

# アップロードしたファイルを保存するディレクトリ
UPLOAD_DIR = os.path.dirname(os.path.abspath(__file__)) + "/static/uploaded/"

service = Service()


# ユーザー登録
def sign_up_func(request):
    if request.method == 'POST':
        new_username = request.POST['username']
        new_password = request.POST['password']
        try:
            User.objects.get(username=new_username)
            return render(request, 'signup.html', {'error': 'このユーザーは既に登録されています。'})
        except:
            user = User.objects.create_user(new_username, '', new_password)
            return render(request, 'login.html')
    return render(request, 'signup.html')


# ログイン
def log_in_func(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('list')
        else:
            return render(request, 'login.html', {'error': 'ログインする権限がありません。登録されいないユーザーである、もしくはユーザー名かパスワードが間違っています。'})
    return render(request, 'login.html')


# ログアウト
def log_out_func(request):
    logout(request)
    return redirect('login')


# 新規投稿（ファイルのアップロード）
def create_post_func(request):
    if request.method == 'POST':
        post = Board.objects.create(author=request.user.get_username())
        post.save()
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            service.handle_uploaded_file(request.FILES['file'], UPLOAD_DIR, post.pk)
            return redirect('list')
    else:
        form = UploadFileForm()
        return render(request, 'create.html', {'form': form})
    return render(request, 'create.html', {'form': form})


# 記事一覧
@login_required()
def list_func(request):
    object_list = Board.objects.all()
    return render(request, 'list.html', {'object_list': object_list})


# 記事の詳細
def detail_func(request, pk):
    post_detail = Board.objects.get(pk=pk)
    return render(request, 'detail.html', {'post_detail': post_detail})


# いいね
def good_func(request, pk):
    service.press_good(pk)
    return redirect('list')


# 既読
def read_func(request, pk):
    return service.press_read(request, pk)


# 投稿削除
def delete_func(request, pk):
    # 記事の削除
    post = Board.objects.get(pk=pk)
    post.delete()
    # 削除する記事に紐づく食習慣データの削除
    FoodHabitModel.objects.filter(post_id=pk).delete()
    return redirect('list')


# 何もない時の画面
def hello_func(request):
    return HttpResponse("<h1>ようこそ</h1>")
