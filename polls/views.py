from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic

from .models import Question, Choice


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.voted_users.filter(pk=request.user.pk).exists() or not \
                request.user.is_authenticated:
            return redirect('polls:results', pk=self.object.pk)
        else:
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


@login_required()
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes= F('votes') + 1
        selected_choice.save(update_fields=['votes'])
        question.voted_users.add(request.user)
        question.save()
        return redirect('polls:results', pk=question.id)


