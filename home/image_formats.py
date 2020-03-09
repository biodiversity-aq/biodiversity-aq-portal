from django.utils.html import escape
from wagtail.images.formats import Format, register_image_format


class CaptionedImageFormat(Format):
    """
    To render generated caption for an Image inserted via Rich Text Editor.
    https://docs.wagtail.io/en/stable/advanced_topics/images/changing_rich_text_representation.html
    """

    def image_to_html(self, image, alt_text, extra_attributes=None):
        """
        Override the default `image_to_html` method to include image credit in the html rendered.
        """
        rendition = image.get_rendition(self.filter_spec)  # filter_spec is the image filter tag in template (string)
        if self.classnames:  # html class name for <figure> tag
            class_attr = escape(self.classnames)
        else:
            class_attr = ''
        custom_html = """<figure {} class="figure {}">
        <img src="{}" width="{}" height="{}" alt="{}" class="figure-img img-fluid z-depth-1 mx-auto d-block "/>
        <figcaption class="figure-caption text-center">{}</figcaption>
        </figure>""".format(
            extra_attributes, class_attr, escape(rendition.url), rendition.width, rendition.height, alt_text,
            image.get_image_credit()  # return html string of image credit, see CustomImage model class method
        )
        return custom_html


register_image_format(
    CaptionedImageFormat('captioned_fullwidth', 'Full width captioned', 'center', 'original')
)
