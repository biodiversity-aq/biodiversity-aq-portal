from django.db import models
from django.shortcuts import redirect

from wagtail.core.models import Page, Orderable
from wagtail.core import blocks
from wagtail.core.fields import StreamField, RichTextField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.models import Image, AbstractImage, AbstractRendition
from wagtailmenus.models import MenuPage
from wagtailmenus.panels import menupage_panel
from wagtail.snippets.models import register_snippet

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from taggit.managers import TaggableManager


class BaseMenuPage(MenuPage):
    """
    Subclass MenuPage because the important page will just becomes toggles in multi-level menus
    https://wagtailmenus.readthedocs.io/en/stable/overview.html#solves-the-problem-of-important-page-links-becoming-just-toggles-in-multi-level-menus

    To be inherited as MenuPage for all MenuPage in this project
    """
    cover = models.ForeignKey('home.CustomImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    short_description = RichTextField(
        blank=True, null=True, features=['bold', 'italic', 'link', 'superscript', 'subscript'],
        help_text='A one line description of the page that will appear in overview page.')

    class Meta:
        abstract = True


class OverviewPage(BaseMenuPage):
    subtitle = RichTextField(features=['bold', 'italic', 'underline', 'link', 'superscript', 'subscript'], blank=True)
    body = StreamField([
        ('insert_html', blocks.RawHTMLBlock(required=False, help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element')),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock())        
        ], blank=True)

    content_panels = Page.content_panels + [                
        FieldPanel('subtitle'),
        StreamFieldPanel('body'),
    ]

    settings_panels = [menupage_panel]

    template = 'home/overview_page.html'


class PageTag(TaggedItemBase):
    """
    Tag for detail pages
    """
    content_object = ParentalKey('home.DetailPage', on_delete=models.CASCADE, related_name='tagged_items')


class DetailPage(BaseMenuPage):
    body = StreamField([
        ('insert_html', blocks.RawHTMLBlock(
            required=False, help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element')),
        ('paragraph', blocks.RichTextBlock(required=False)),
        ('image', ImageChooserBlock(required=False))
    ], blank=True)
    tags = ClusterTaggableManager(through=PageTag, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('short_description'),
        ImageChooserPanel('cover'),
        StreamFieldPanel('body'),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel('tags'),
    ]

    settings_panels = [menupage_panel]
    # parent_page_types
    # subpage_types
    template = 'home/detail_page.html'


class OneColumnPage(Page):
  
    body = StreamField([
        ('insert_html', blocks.RawHTMLBlock(required=False,help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element')),
        ('paragraph', blocks.RichTextBlock(features=['bold','italic','ol','ul','h1','h2','h3','h4','hr','link','image','document-link'])),
        ('image', ImageChooserBlock())
        ], blank=True)
    
    content_panels = Page.content_panels + [        
        StreamFieldPanel('body')
    ]
    
    template = 'base_pages/one_column.html'


class TwoColumnPage(Page):
  
    column_one = StreamField([
        ('insert_html', blocks.RawHTMLBlock(required=False,help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element')),
        ('paragraph', blocks.RichTextBlock(features=['bold','italic','ol','ul','h1','h2','h3','h4','hr','link','image','document-link'])),
        ('image', ImageChooserBlock())
        ],blank=True)
    
    column_two = StreamField([
        ('insert_html', blocks.RawHTMLBlock(required=False,help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element')),
        ('paragraph', blocks.RichTextBlock(features=['bold','italic','ol','ul','h1','h2','h3','h4','hr','link','image','document-link'])),
        ('image', ImageChooserBlock())
        ],blank=True)

    content_panels = Page.content_panels + [        
        StreamFieldPanel('column_one'),
        StreamFieldPanel('column_two')
    ]
    
    template = 'base_pages/two_columns.html'


class ThreeColumnPage(Page):
  
    column_one = StreamField([
        ('insert_html', blocks.RawHTMLBlock(required=False,help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element')),
        ('paragraph', blocks.RichTextBlock(features=['bold','italic','ol','ul','h1','h2','h3','h4','hr','link','image','document-link'])),
        ('image', ImageChooserBlock())
        ],blank=True)
    
    column_two = StreamField([
        ('insert_html', blocks.RawHTMLBlock(required=False,help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element')),
        ('paragraph', blocks.RichTextBlock(features=['bold','italic','ol','ul','h1','h2','h3','h4','hr','link','image','document-link'])),
        ('image', ImageChooserBlock())
        ],blank=True)

    column_three = StreamField([
        ('insert_html', blocks.RawHTMLBlock(required=False,help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element')),
        ('paragraph', blocks.RichTextBlock(features=['bold','italic','ol','ul','h1','h2','h3','h4','hr','link','image','document-link'])),
        ('image', ImageChooserBlock())
        ],blank=True)

    content_panels = Page.content_panels + [        
        StreamFieldPanel('column_one'),
        StreamFieldPanel('column_two'),
        StreamFieldPanel('column_three')
    ]
    
    template = 'base_pages/three_columns.html'


class CardTag(TaggedItemBase):
    content_object = ParentalKey('home.Card', on_delete=models.CASCADE, related_name='tagged_items')


@register_snippet
class Card(ClusterableModel):
    html = StreamField([
        ('insert_html', blocks.RawHTMLBlock(
            required=False, help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element'))], blank=True)
    title = models.CharField(null=True, blank=True, max_length=100)
    description = models.TextField(null=True, blank=True)
    tags = TaggableManager(through=CardTag, blank=True)

    panels = [
        StreamFieldPanel('html'),
        FieldPanel('title'),
        FieldPanel('description'),
        FieldPanel('tags'),
    ]

    def __str__(self):
        return self.title


class RedirectDummyPage(BaseMenuPage):
    """
    A dummy page that can be added to wagtailmenus, but its sole purpose is to redirect to a page specified in the
    redirect_to field. This is intended to be used for pages like ipt.biodiversity.aq that is not part of Django app.

    If it is an existing wagtail page, edit redirection in wagtail cms: Settings > Redirects
    """
    redirect_to = models.URLField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('redirect_to'),
        ]

    settings_panels = [menupage_panel]

    def serve(self, request, **kwargs):
        # redirect the page to url specified in redirect_to
        return redirect(self.redirect_to)


class CustomImage(AbstractImage):
    """
    Custom image model to include license and author for credits
    """
    CC_BY = 'https://creativecommons.org/licenses/by/4.0/'
    CC_BY_SA = 'https://creativecommons.org/licenses/by-sa/4.0/'
    CC_BY_ND = 'https://creativecommons.org/licenses/by-nd/4.0/'
    CC_BY_NC = 'https://creativecommons.org/licenses/by-nc/4.0/'
    CC_BY_NC_SA = 'https://creativecommons.org/licenses/by-nc-sa/4.0/'
    CC_BY_NC_ND = 'https://creativecommons.org/licenses/by-nc-nd/4.0/'
    CC0 = 'https://creativecommons.org/publicdomain/zero/1.0/'

    LICENSE_CHOICES = [
        (CC_BY, 'CC BY 4.0'),
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
    license = models.CharField(max_length=200, choices=LICENSE_CHOICES, default=CC_BY, blank=True, null=True,
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
            caption = '"{}"'.format(self.caption[3:][:-4])
        if self.owner:
            owner = ' by {}'.format(self.owner)
        if self.license:
            img_license = ' licensed under <a href="{}">{}</a>.'.format(self.license, self.get_license_display())
        img_credit = caption + owner + img_license
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


