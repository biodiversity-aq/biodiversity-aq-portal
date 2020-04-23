from django.utils.html import escape
from wagtail.images.formats import Format, register_image_format, unregister_image_format


class CaptionedImageFormat(Format):
    """
    To render generated caption for an Image inserted via Rich Text Editor.
    https://docs.wagtail.io/en/stable/advanced_topics/images/changing_rich_text_representation.html
    """

    def image_to_html(self, image, alt_text, extra_attributes=""):
        """
        Override the default `image_to_html` method to include image credit in the html rendered.
        """
        rendition = image.get_rendition(self.filter_spec)  # filter_spec is the image filter tag in template (string)
        img_class = ''
        if self.classnames:  # html class name for <figure> tag
            class_attr = escape(self.classnames)
            if class_attr == 'center':
                img_class = 'mx-auto d-block'
            if class_attr == 'left' or class_attr == '':
                img_class = 'float-left'  # see styles classes https://mdbootstrap.com/docs/jquery/content/images/
        else:
            class_attr = ''
        custom_html = """<figure {} class="figure {}">
        <img src="{}" width="{}" height="{}" alt="{}" class="figure-img img-fluid z-depth-1 {} "/>
        <figcaption class="figure-caption text-center">{}</figcaption>
        </figure>""".format(
            extra_attributes, class_attr, escape(rendition.url), rendition.width, rendition.height, alt_text,
            img_class, image.get_image_credit()  # return html string of image credit, see CustomImage class method
        )
        return custom_html


unregister_image_format(Format('right', 'Right-aligned', 'richtext-image right', 'width-500'))
register_image_format(CaptionedImageFormat('center_captioned_fullwidth', 'Full width, center-aligned, captioned', 'center', 'original'))
register_image_format(CaptionedImageFormat('center_captioned_width_500', 'Width: 500 px, center-aligned, captioned', 'center', 'width-500'))
register_image_format(CaptionedImageFormat('left_captioned_width_500', 'Width: 500 px, left-aligned, captioned', 'left', 'width-500'))
register_image_format(CaptionedImageFormat('center_captioned_width_750', 'Width: 750 px, center-aligned, captioned', 'center', 'width-750'))
register_image_format(CaptionedImageFormat('left_captioned_width_750', 'Width: 750 px, left-aligned, captioned', 'left', 'width-750'))
