import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineStyleElementHandler, BlockElementHandler
from wagtail.contrib.redirects.models import Redirect
from wagtail.core import hooks


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


# ----------------------------------
# Extends Draftail editor features
# ----------------------------------
inline_features_list = [
    ('mark', 'MARK', 'mark', None, None),
    ('underline', 'UNDERLINE', 'underline', None, None),
]


@hooks.register('register_rich_text_features')
def register_inline_style_feature(features):
    """
    Register inline style feature
    https://github.com/facebook/draft-js/blob/master/src/model/immutable/DefaultDraftInlineStyle.js
    """
    for feature in inline_features_list:
        feature_name = feature[0]
        type_ = feature[1]
        tag = feature[2]
        label = feature[3]
        style = feature[4]
        # Configure how Draftail handles the feature in its toolbar.
        control = {
            'type': type_,
            'label': label,
            'description': feature_name.title(),
            'style': style
        }
        # Call register_editor_plugin to register the configuration for Draftail.
        features.register_editor_plugin(
            'draftail', feature_name, draftail_features.InlineStyleFeature(control)
        )
        # Configure the content transform from the DB to the editor and back.
        db_conversion = {
            'from_database_format': {tag: InlineStyleElementHandler(type_)},
            'to_database_format': {'style_map': {type_: tag}},
        }
        # Call register_converter_rule to register the content transformation conversion.
        features.register_converter_rule('contentstate', feature_name, db_conversion)
        features.default_features.append(feature_name)


@hooks.register('register_rich_text_features')
def register_blockquote_feature(features):
    """
    Use mdbootstrap blockquote class in <blockquote>
    <blockquote class="blockquote>My blockquote</blockquote>
    """
    feature_name = 'bsblockquote'  # need to use another name. couldn't override using the same name
    type_ = 'bsblockquote'
    tag = 'blockquote'

    control = {
        'type': type_,
        'label': '"',
        'description': 'Blockquote',
        # Optionally, we can tell Draftail what element to use when displaying those blocks in the editor.
        'element': 'blockquote',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.BlockFeature(control)
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'blockquote[class]': BlockElementHandler(type_)},
        'to_database_format': {
            'block_map': {
                type_: {
                    'element': tag,
                    'props': {
                        'class': 'blockquote',
                    },
                },
            },
        },
    })

