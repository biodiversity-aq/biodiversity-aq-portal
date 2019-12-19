from django.db import models

from wagtail.core.models import Page, Orderable
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, InlinePanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import TaggedItemBase
from taggit.managers import TaggableManager


class HomePage(Page):
   
    body = StreamField([
        ('insert_html', blocks.RawHTMLBlock(required=False, help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element')),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock())        
        ], blank=True)

    content_panels = Page.content_panels + [                
        StreamFieldPanel('body'),
        InlinePanel('section_placements', label="Sections"),
    ]

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
