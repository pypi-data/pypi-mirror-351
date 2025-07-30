import factory

from ..models import Blog, BlogPluginModel


class BlogFactory(factory.django.DjangoModelFactory):
    """
    Factory to create instance of a Blog.
    """
    title = factory.Faker("text", max_nb_chars=50)

    class Meta:
        model = Blog


class BlogPluginModelFactory(factory.django.DjangoModelFactory):
    """
    Factory to create instance of a BlogPluginModel.
    """
    blog = factory.SubFactory(BlogFactory)
    limit = factory.Faker("random_int", min=1, max=5)

    class Meta:
        model = BlogPluginModel
