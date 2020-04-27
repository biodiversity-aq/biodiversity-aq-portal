from django.db import models
from django.http import Http404
from django.shortcuts import redirect, render

from wagtail.admin.edit_handlers import PageChooserPanel, MultiFieldPanel, InlinePanel, FieldPanel, StreamFieldPanel
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.core.models import Page, Orderable
from wagtail.core import blocks
from wagtail.core.fields import StreamField, RichTextField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.models import Image, AbstractImage, AbstractRendition
from wagtail.snippets.models import register_snippet
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtailmenus.models import MenuPage, AbstractLinkPage
from wagtailmenus.panels import menupage_panel

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase


class BaseMenuPage(MenuPage):
    """
    A base menu page for all pages in this app.
    Subclass MenuPage because the important page will just becomes toggles in multi-level menus
    https://wagtailmenus.readthedocs.io/en/stable/overview.html#solves-the-problem-of-important-page-links-becoming-just-toggles-in-multi-level-menus

    To be inherited as MenuPage for all MenuPage in this project
    """
    cover = models.ForeignKey('home.CustomImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    short_description = RichTextField(
        blank=True, null=True, features=['bold', 'italic', 'underline', 'link', 'superscript', 'subscript'],
        help_text='A one line description of the page to help user discover this page.')
    body = StreamField([
        ('insert_html', blocks.RawHTMLBlock(
            required=False,
            help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element')),
        ('paragraph', blocks.RichTextBlock(required=False)),
        ('image', ImageChooserBlock(required=False)),
        ('table', TableBlock(required=False, template='home/blocks/table_block.html'))
    ], blank=True)
    show_in_recent = models.BooleanField(
        default=False, null=True, blank=True,
        help_text='If true, this page will appear in the "Recent" section of its parent if it is an AppLandingPage '
                  'order by last published date'
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            ImageChooserPanel('cover'),
            FieldPanel('short_description'),
        ]),
        FieldPanel('show_in_recent'),
        StreamFieldPanel('body'),
    ]

    settings_panels = [menupage_panel]

    class Meta:
        abstract = True
        ordering = ['-last_published_at']


class LinkPage(AbstractLinkPage):
    """
    AbstractLinkPage model can be used to add additional links to menus,
    by adding additional pages to the page tree.
    https://wagtailmenus.readthedocs.io/en/stable/abstractlinkpage.html
    """
    pass


class OverviewPage(BaseMenuPage):
    """
    An overview page which list all its children pages
    """
    pin = StreamField([
        ('pinned_pages', blocks.PageChooserBlock(required=False, help_text='Select page to be pinned in this page')),
    ], blank=True, null=True)

    template = 'home/overview_page.html'

    content_panels = BaseMenuPage.content_panels + [
        StreamFieldPanel('pin')
    ]


class PageTag(TaggedItemBase):
    """
    Tag for detail pages
    """
    content_object = ParentalKey('home.DetailPage', on_delete=models.CASCADE, related_name='tagged_items')


class DetailPage(BaseMenuPage):
    """
    Page for details
    """
    tags = ClusterTaggableManager(through=PageTag, blank=True)

    promote_panels = Page.promote_panels + [
        FieldPanel('tags'),
    ]

    template = 'home/detail_page.html'


class DetailIndexPage(Page):
    """
    An index page that returns Pages which are tagged with the tag specified.
    """
    template = 'home/detail_page_index.html'

    def serve(self, request, *args, **kwargs):
        """
        Only return DetailPages which are live and tagged with the tag provided.
        """
        detail_pages = DetailPage.objects.live()
        tag = request.GET.get('tag')
        detail_pages = detail_pages.filter(tags__name=tag)
        if tag:
            return render(request, self.template, {
                'page': self,
                'tag': tag,
                'detail_pages': detail_pages,
            })
        else:
            raise Http404


class RedirectDummyPage(BaseMenuPage):
    """
    A dummy page that can be added to wagtailmenus, but its sole purpose is to redirect to a page specified in the
    redirect_to field. This is intended to be used for pages like ipt.biodiversity.aq that is not part of Django app.

    If it is an existing wagtail page, edit redirection in wagtail cms: Settings > Redirects
    """
    redirect_to = models.URLField(blank=True, null=True)

    content_panels = BaseMenuPage.content_panels + [
        FieldPanel('redirect_to'),
    ]

    def serve(self, request, **kwargs):
        # redirect the page to url specified in redirect_to
        return redirect(self.redirect_to)


class CustomImage(AbstractImage):
    """
    Custom image model to include license and author for credits
    """
    CC_BY_3 = 'https://creativecommons.org/licenses/by/3.0/'
    CC_BY_4 = 'https://creativecommons.org/licenses/by/4.0/'
    CC_BY_SA = 'https://creativecommons.org/licenses/by-sa/4.0/'
    CC_BY_ND = 'https://creativecommons.org/licenses/by-nd/4.0/'
    CC_BY_NC = 'https://creativecommons.org/licenses/by-nc/4.0/'
    CC_BY_NC_SA = 'https://creativecommons.org/licenses/by-nc-sa/4.0/'
    CC_BY_NC_ND = 'https://creativecommons.org/licenses/by-nc-nd/4.0/'
    CC0 = 'https://creativecommons.org/publicdomain/zero/1.0/'

    LICENSE_CHOICES = [
        (CC_BY_3, 'CC BY 3.0'),
        (CC_BY_4, 'CC BY 4.0'),
        (CC_BY_SA, 'CC BY-SA 4.0'),
        (CC_BY_ND, 'CC BY-ND 4.0'),
        (CC_BY_NC, 'CC BY-NC 4.0'),
        (CC_BY_NC_SA, 'CC BY-NC-SA 4.0'),
        (CC_BY_NC_ND, 'CC BY-NC-ND 4.0'),
        (CC0, 'CC0 1.0')
    ]
    # should not use "title" for this field because it will cause compatibility issue
    caption = RichTextField(
        features=['bold', 'italic', 'underline', 'link', 'superscript', 'subscript'], blank=True, null=True,
        help_text='Description of the image. Image attribution will be generated in the form of '
                  '"{caption}" by {owner} licensed under {license}.')
    owner = models.CharField(max_length=255, blank=True, null=True,
                             help_text='Please fill in this field to give credit to the owner of the image.')
    license = models.CharField(max_length=200, choices=LICENSE_CHOICES, default=CC_BY_NC, blank=True, null=True,
                               help_text='Please select a license.')

    admin_form_fields = Image.admin_form_fields + (
        # Then add the field names here to make them appear in the form:
        'owner', 'license', 'caption'
    )

    def get_image_credit(self):
        """
        Generate image caption using caption, author and license provided.

        The caption is a RichTextField that by default always wrapped within <p></p>. To avoid owner and license being
        split into different lines, this function strip the <p></p> tags and concatenate all the values into a string.

        It is important to wrap the value returned by this function with |richtext filter in the template to ensure
        that the html tags are not escaped. This is consistent with the feature of RichTextField:
        https://docs.wagtail.io/en/stable/advanced_topics/customisation/page_editing_interface.html#rich-text-html

        :return: A string consists of caption, owner and image license.
        """
        caption = ''
        owner = ''
        img_license = ''
        if self.caption.startswith('<p>') and self.caption.endswith('</p>'):
            caption = '"{}" '.format(self.caption[3:][:-4])
        if self.owner:
            owner = 'by {} '.format(self.owner)
        if self.license:
            img_license = 'licensed under <a href="{}">{}</a>.'.format(self.license, self.get_license_display())
        if self.caption:
            img_credit = caption + owner + img_license
        else:
            img_credit = 'Photo/Image ' + owner + img_license
        return img_credit


class CustomRendition(AbstractRendition):
    """
    Since custom image model is used (CustomImage), a custom rendition which inherits from
    `wagtail.images.models.AbstractRendition` is necessary.
    https://docs.wagtail.io/en/stable/advanced_topics/images/custom_image_model.html
    """
    image = models.ForeignKey(CustomImage, on_delete=models.CASCADE, related_name='renditions')

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )


class AppLandingPage(OverviewPage):
    """
    Landing page for app
    """
    logo = models.ForeignKey('home.CustomImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    template = "home/app_landing_page.html"
    content_panels = OverviewPage.content_panels + [
        ImageChooserPanel('logo'),
        MultiFieldPanel(
            [
                InlinePanel('link_buttons', label='Buttons', min_num=0, max_num=4,
                            help_text='Buttons that link to other pages')
            ]
        ),
    ]


# ---------
# Snippets
# ---------
class LinkButtonOrderable(Orderable):
    """
    This allows us to select one or more link buttons from Snippets.
    """
    page = ParentalKey('wagtailcore.Page', related_name="link_buttons")
    button = models.ForeignKey(
        "home.LinkedButton",
        on_delete=models.CASCADE,
    )

    panels = [
        SnippetChooserPanel('button'),
    ]


@register_snippet
class LinkedButton(models.Model):
    """
    Button that refers to a linked_page or an external url.
    """
    linked_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='linked_button',
        help_text='The page which this button directs the users to.'
    )
    external_url = models.URLField(
        null=True, blank=True, help_text='A valid url if the button is to link to an external page not managed via '
                                         'this CMS.')
    text = models.CharField(max_length=100, help_text='The text to be displayed on the button.')
    icon = models.CharField(
        max_length=100, null=True, blank=True,
        help_text="The html code of the icon to be displayed on the button, e.g. 'fas fa-arrow-left', "
                  "Fontawesome icons available: https://bit.ly/2wYnKyD")
    color = models.CharField(
        max_length=100, null=True, blank=True, default='btn-outline-white',
        help_text="Button class e.g. 'btn-primary'. Button classes available (free version only): "
                  "https://bit.ly/3ctJtir")

    panels = [
        MultiFieldPanel([
            PageChooserPanel('linked_page'),
            FieldPanel('external_url'),
        ], heading='Link to'),
        FieldPanel('text'),
        FieldPanel('icon'),
        FieldPanel('color'),
    ]

    def __str__(self):
        return '{}, {}'.format(self.text, self.color)

    class Meta:
        # check if the button is already exist
        unique_together = (
            ('linked_page', 'text', 'color')
        )


@register_snippet
class Footer(models.Model):
    footer_page = StreamField([
        ('footer_pages', blocks.PageChooserBlock(required=False, help_text='Select page to render in footer')),
    ], blank=True, null=True)
    logo = StreamField([
        ('logos', blocks.StructBlock([
            ('logo_image', ImageChooserBlock(required=False, help_text='Select a logo.')),
            ('logo_url', blocks.URLBlock(required=False, help_text='Set a url which the logo refers to.')),
        ])),
    ], blank=True, null=True)
    text = StreamField([
        ('text', blocks.RichTextBlock(
            required=False, features=['bold', 'italic', 'underline', 'link', 'superscript', 'subscript'],
            help_text='A short line of text to be displayed at the bottom of footer.'
        ))
    ], blank=True, null=True)

    panels = [
        StreamFieldPanel('footer_page'),
        StreamFieldPanel('logo'),
        StreamFieldPanel('text'),
    ]


