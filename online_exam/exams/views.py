from django.shortcuts import render
def home(request):
    return render(request, 'home.html')
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import redirect
from django.shortcuts import render


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'exams/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'exams/login.html', {'form': form})
@login_required
def create_exam(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        duration = request.POST['duration']
        Exam.objects.create(title=title, description=description, duration=duration)
        return redirect('exams:exam_list')
    return render(request, 'exams/create_exam.html')
from .models import Exam, Question
from django.shortcuts import get_object_or_404

@login_required
def add_question(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.method == 'POST':
        question_text = request.POST['question_text']
        answer_a = request.POST['answer_a']
        answer_b = request.POST['answer_b']
        answer_c = request.POST['answer_c']
        answer_d = request.POST['answer_d']
        correct_answer = request.POST['correct_answer']

        Question.objects.create(
            exam=exam,
            question_text=question_text,
            answer_a=answer_a,
            answer_b=answer_b,
            answer_c=answer_c,
            answer_d=answer_d,
            correct_answer=correct_answer,
        )
        return redirect('exam:exam_details', exam_id=exam.id)

    return render(request, 'exam/add_question.html', {'exam': exam})

@login_required
def exam_details(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.questions.all()
    return render(request, 'exam/exam_details.html', {'exam': exam, 'questions': questions})
from django.utils.timezone import now

@login_required
def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.questions.all()

    if request.method == 'POST':
        correct_count = 0
        for question in questions:
            user_answer = request.POST.get(f'question_{question.id}')
            if user_answer == question.correct_answer:
                correct_count += 1

        score = (correct_count / questions.count()) * 100
        StudentExam.objects.create(
            student=request.user,
            exam=exam,
            score=score,
            completed_at=now()
        )
        return redirect('exam:exam_results', exam_id=exam.id)

    return render(request, 'exam/take_exam.html', {'exam': exam, 'questions': questions})
@login_required
def exam_results(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    student_exam = StudentExam.objects.get(student=request.user, exam=exam)
    return render(request, 'exam/exam_results.html', {'exam': exam, 'student_exam': student_exam})

from django.db.models import Avg, Max, Min

@login_required
def performance_report(request):
    student_exams = StudentExam.objects.filter(student=request.user).select_related('exam')
    average_score = student_exams.aggregate(Avg('score'))['score__avg']
    highest_score = student_exams.aggregate(Max('score'))['score__max']
    lowest_score = student_exams.aggregate(Min('score'))['score__min']

    context = {
        'student_exams': student_exams,
        'average_score': average_score,
        'highest_score': highest_score,
        'lowest_score': lowest_score,
    }
    return render(request, 'exam/performance_report.html', context)

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_dashboard(request):
    total_students = User.objects.filter(is_staff=False).count()
    total_exams = Exam.objects.count()
    total_attempts = StudentExam.objects.count()
    average_score = StudentExam.objects.aggregate(Avg('score'))['score__avg']

    context = {
        'total_students': total_students,
        'total_exams': total_exams,
        'total_attempts': total_attempts,
        'average_score': average_score,
    }
    return render(request, 'exam/admin_dashboard.html', context)

# Create your views here.
