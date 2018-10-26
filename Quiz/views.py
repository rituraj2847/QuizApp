from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login, authenticate
from django.utils import timezone
from .models import Quiz, Question, Choice
from .forms import *
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib import messages
from django.contrib.auth.decorators import login_required

score=0

def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == "POST":
        username = request.POST['username']
        r_password = request.POST['password']
        user = authenticate(request, username = username, password = r_password)
        if user:
            login(request, user)
        if request.user.is_authenticated:
            return redirect('dashboard')
        else:
            messages.warning(request, 'Incorrect Login Details')
            return render(request, 'home.html',{})
    else:
        return render(request, 'home.html', {})

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            r_password = form.cleaned_data.get('password1')
            user = authenticate(request, username = username, password = r_password)
            login(request, user)
            messages.success(request, f'Account created for {username}')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form' : form})

def dashboard_view(request):
    all_quizzes = Quiz.objects.all().order_by('-date_created')
    if request.user.is_authenticated:
        taken_quizzes = Score.objects.filter(user=request.user).order_by('-taken_on')
    else:
        taken_quizzes = {}
    return render(request, 'dashboard.html', {'all_quizzes' : all_quizzes, 'taken_quizzes':taken_quizzes})

@login_required(login_url='/')
def question_view(request, quiz_id, question_no):
    global score
    if request.method == "POST":
        selected_choice = Choice.objects.get(id = request.POST["choices"])
        if selected_choice.right_choice == True:
            score += 1
        return redirect('question', quiz_id=quiz_id, question_no=question_no+1)
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    if question_no == len(quiz.question_set.all())+1:
        quiz.taken_by += 1
        quiz.save()
        sc = str(score)
        s = Score.objects.create(score=score, user=request.user, quiz=quiz, taken_on=timezone.now())
        s.save()
        score = 0
        return render(request, 'score.html', {"score" : sc})
    ques = quiz.question_set.all()[question_no-1]
    done_p = int(100*question_no/len(quiz.question_set.all()))
    context = {'quiz' : quiz, 'ques' : ques, 'done_p' : done_p}
    return render(request, 'question_view.html', context)

@login_required(login_url='/')
def new_quiz_view(request):
    if request.method == "POST":
        date_created = timezone.now()
        author = request.user
        quiz_name = request.POST['quiz_name']
        quiz = Quiz.objects.create(date_created=date_created, author=author, quiz_name=quiz_name)
        quiz.save()
        return redirect('add_question', quiz_id=quiz.id, question_no=1)
    else:
        return render(request, 'new_quiz.html', {})

def add_question_view(request, quiz_id, question_no):
    error_message=""
    if request.method == "POST":
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        question_text = request.POST['question_text']
        q = Question(quiz=quiz, question_text=question_text, question_no=question_no)
        choice1 = Choice(ques = q, choice_text = request.POST['choice1'])
        choice2 = Choice(ques = q, choice_text = request.POST['choice2'])
        choice3 = Choice(ques = q, choice_text = request.POST['choice3'])
        choice4 = Choice(ques = q, choice_text = request.POST['choice4'])
        if request.POST['choice1'] == '' or request.POST['choice2']=='' or request.POST['choice3']=='' or request.POST['choice4']=='':
            context = {'quiz_name': Quiz.objects.get(pk=quiz_id).quiz_name, 'ques_no' : question_no, 'error_message' : "Please fill all choices"}
            return render(request, 'add_question.html', context)
        else:
            try:
                r_choice = request.POST['choice']
                if r_choice == 'choice1':
                    choice1.right_choice = True
                elif r_choice == 'choice2':
                    choice2.right_choice = True
                elif r_choice == 'choice3':
                    choice3.right_choice = True
                elif r_choice == 'choice4':
                    choice4.right_choice = True
                else:
                    error_message = "Please enter a valid choice"
                    return render(request, 'add_question.html', {'error_message' : error_message})
            except MultiValueDictKeyError:
                error_message = "Please mark the correct answer"
                context =  {'quiz_name': Quiz.objects.get(pk=quiz_id).quiz_name, 'ques_no' : question_no, "error_message" : error_message}
                return render(request, 'add_question.html', context)
            print("fad")
            q.save()
            quiz.no_of_ques = question_no+1
            quiz.save()
            choice1.save()
            choice2.save()
            choice3.save()
            choice4.save()
            return redirect('add_question', quiz_id=quiz_id, question_no=question_no+1)
    else:
        context =  {'quiz_name': Quiz.objects.get(pk=quiz_id).quiz_name, 'ques_no' : question_no}
        return render(request, 'add_question.html', context)

def result_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    scores = Score.objects.filter(quiz=quiz)
    return render(request, 'results.html', {'quiz':quiz, 'scores': scores})

def signout_view(request):
    logout(request)
    return redirect('home')