from django.db import models

from wagtail.core.models import Page
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.blocks import ImageChooserBlock

from djconfig import config


class HomePage(Page):
   
    body = StreamField([
        ('insert_html', blocks.RawHTMLBlock(required=False, help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element')),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock())        
        ], blank=True)

    #sidebar = StreamField([])
    
    content_panels = Page.content_panels + [                
        StreamFieldPanel('body')
    ]

    template = 'home/home_page.html'



class OneColumnPage(Page):
  
    body = StreamField([
        ('insert_html',blocks.RawHTMLBlock(required=False,help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element')),
        ('paragraph', blocks.RichTextBlock(features=['bold','italic','ol','ul','h1','h2','h3','h4','hr','link','image','document-link'])),
        ('image', ImageChooserBlock())
        ],blank=True)
    
    content_panels = Page.content_panels + [        
        StreamFieldPanel('body')
    ]
    
    template = 'base_pages/one_column.html'


class TwoColumnPage(Page):
  
    column_one = StreamField([
        ('insert_html',blocks.RawHTMLBlock(required=False,help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element')),
        ('paragraph', blocks.RichTextBlock(features=['bold','italic','ol','ul','h1','h2','h3','h4','hr','link','image','document-link'])),
        ('image', ImageChooserBlock())
        ],blank=True)
    
    column_two = StreamField([
        ('insert_html',blocks.RawHTMLBlock(required=False,help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element')),
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
        ('insert_html',blocks.RawHTMLBlock(required=False,help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element')),
        ('paragraph', blocks.RichTextBlock(features=['bold','italic','ol','ul','h1','h2','h3','h4','hr','link','image','document-link'])),
        ('image', ImageChooserBlock())
        ],blank=True)
    
    column_two = StreamField([
        ('insert_html',blocks.RawHTMLBlock(required=False,help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element')),
        ('paragraph', blocks.RichTextBlock(features=['bold','italic','ol','ul','h1','h2','h3','h4','hr','link','image','document-link'])),
        ('image', ImageChooserBlock())
        ],blank=True)

    column_three = StreamField([
        ('insert_html',blocks.RawHTMLBlock(required=False,help_text='This is a standard HTML block. Anything written in HTML here will be rendered in a DIV element')),
        ('paragraph', blocks.RichTextBlock(features=['bold','italic','ol','ul','h1','h2','h3','h4','hr','link','image','document-link'])),
        ('image', ImageChooserBlock())
        ],blank=True)

    content_panels = Page.content_panels + [        
        StreamFieldPanel('column_one'),
        StreamFieldPanel('column_two'),
        StreamFieldPanel('column_three')
    ]
    
    template = 'base_pages/three_columns.html'