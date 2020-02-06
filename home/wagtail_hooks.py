from wagtail.core import hooks
from wagtail.contrib.redirects.models import Redirect


@hooks.register('before_edit_page')
def create_redirect_on_slug_change(request, page):
    """
    Create redirect when editing slugs
    https://docs.wagtail.io/en/v2.7/reference/pages/model_recipes.html
    """
    if request.method == 'POST':
        if page.slug != request.POST['slug']:
            Redirect.objects.create(
                    old_path=page.url[:-1],
                    site=page.get_site(),
                    redirect_page=page
                )
