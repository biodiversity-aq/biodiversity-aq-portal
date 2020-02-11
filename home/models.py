from django.db import models
from django.shortcuts import redirect

from wagtail.core.models import Page, Orderable
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, InlinePanel
from wagtail.images.blocks import ImageChooserBlock
from wagtailmenus.models import MenuPage
from wagtailmenus.panels import menupage_panel
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from taggit.managers import TaggableManager


class HomePage(MenuPage):
    """
    Subclass MenuPage because the important page will just becomes toggles in multi-level menus
    https://wagtailmenus.readthedocs.io/en/stable/overview.html#solves-the-problem-of-important-page-links-becoming-just-toggles-in-multi-level-menus

    """
   
    body = StreamField([
        ('insert_html', blocks.RawHTMLBlock(required=False, help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element')),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock())        
        ], blank=True)

    content_panels = Page.content_panels + [                
        StreamFieldPanel('body'),
        InlinePanel('section_placements', label="Sections"),
    ]

    settings_panels = [menupage_panel]

    template = 'home/home_page.html'


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


@register_snippet
class Section(models.Model):
    title = models.CharField(null=True, blank=True, max_length=100)
    description = models.TextField(null=True, blank=True)
    card = models.ManyToManyField(Card)

    panels = [
        FieldPanel('title'),
        FieldPanel('description'),
        FieldPanel('card'),
    ]

    def __str__(self):
        return self.title


class SectionPlacement(Orderable, models.Model):
    page = ParentalKey('home.HomePage', on_delete=models.CASCADE, related_name='section_placements')
    section = models.ForeignKey('home.Section', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "section placement"
        verbose_name_plural = "section placements"

    panels = [
        SnippetChooserPanel('section'),
    ]

    def __str__(self):
        return self.page.title + " -> " + self.section.title


class RedirectDummyPage(MenuPage):
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


class PageTag(TaggedItemBase):
    """
    Tag for detail pages
    """
    content_object = ParentalKey('home.DetailPage', on_delete=models.CASCADE, related_name='tagged_items')


class DetailPage(MenuPage):
    short_description = StreamField([
        ('short_description', blocks.RichTextBlock(
            required=False, features=['bold', 'italic', 'link', 'superscript', 'subscript'],
            help_text='A one line description of the page that will appear in overview page.'))
    ])
    body = StreamField([
        ('insert_html', blocks.RawHTMLBlock(
            required=False, help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element')),
        ('paragraph', blocks.RichTextBlock(required=False)),
        ('image', ImageChooserBlock(required=False))
    ], blank=True)
    tags = ClusterTaggableManager(through=PageTag, blank=True)

    content_panels = Page.content_panels + [
        StreamFieldPanel('short_description'),
        StreamFieldPanel('body'),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel('tags'),
    ]

    settings_panels = [menupage_panel]
    # parent_page_types
    # subpage_types
    # tags stuffs
    template = 'home/detail_page.html'
