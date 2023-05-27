import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from blog.models import Category, Comment, Post

from .forms import CommentForm, PostForm, UserForm


def get_post_filter():
    time_now = datetime.datetime.now()
    return Post.objects.filter(
        pub_date__lte=time_now,
        is_published=True,
        category__is_published=True,
    )


def index(request):
    template = "blog/index.html"
    post_list = get_post_filter().order_by("-pub_date")
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj}
    return render(request, template, context)


def post_detail(request, id):
    template = "blog/detail.html"
    post = get_object_or_404(get_post_filter(), id=id)
    context = {
        "post": post,
        "form": CommentForm(),
        "comments": Comment.objects.filter(post_id=id),
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    template = "blog/category.html"
    category = get_object_or_404(
        Category.objects.filter(slug=category_slug), is_published=True
    )
    post_list = (
        get_post_filter().order_by("-pub_date").filter(category=category)
    )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "post_list": post_list,
        "category": category,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def get_profile(request, username_slug):
    template = "blog/profile.html"
    user = get_object_or_404(User.objects.filter(username=username_slug))
    post_list = Post.objects.filter(author=user.id).order_by("-pub_date")
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"profile": user, "page_obj": page_obj}
    return render(request, template, context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def get_success_url(self):
        slug = self.request.user.username
        return reverse("blog:profile", kwargs={"username_slug": slug})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    instance = None
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Post, pk=kwargs["pk"])
        if self.instance.author != request.user:
            return redirect("blog:post_detail", id=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"id": self.instance.pk})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "blog/user.html"
    form_class = UserForm
    success_url = reverse_lazy("blog:index")


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Post, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.instance
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"id": self.instance.pk})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    template_name = "blog/comment.html"
    form_class = CommentForm
    success_url = reverse_lazy("blog:index")

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs["post_id"])
        if instance.author != request.user:
            return redirect("blog:post_detail", id=kwargs["post_id"])
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/create.html"
    success_url = reverse_lazy("blog:index")

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs["pk"])
        if instance.author != request.user:
            return redirect("blog:post_detail", id=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = "blog/comment.html"
    success_url = reverse_lazy("blog:index")
