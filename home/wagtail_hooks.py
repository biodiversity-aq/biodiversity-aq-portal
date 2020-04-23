import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineStyleElementHandler, BlockElementHandler
from wagtail.core import hooks


# ----------------------------------
# Extends Draftail editor features
# ----------------------------------
inline_features_list = [
    # feature name, type, label, style in editor, from database format, to database format
    ('mark', 'MARK', '☆', None,
     {'mark': InlineStyleElementHandler('mark')}, {'style_map': {'mark': 'mark'}}),
    ('underline', 'UNDERLINE', 'U', None,
     {'underline': InlineStyleElementHandler('underline')}, {'style_map': {'underline': 'underline'}}),
    ('pdf-icon', 'PDF-ICON', 'pdf', {'color': 'red'},
     {'i[class=pdf-icon]': InlineStyleElementHandler('pdf-icon')},
     {'style_map': {'PDF-ICON': {'element': 'i', 'props': {'class': 'far fa-file-pdf'}}}}),
]


@hooks.register('register_rich_text_features')
def register_inline_style_feature(features):
    """
    Register inline style feature
    https://docs.wagtail.io/en/v2.7.1/advanced_topics/customisation/extending_draftail.html
    https://github.com/facebook/draft-js/blob/master/src/model/immutable/DefaultDraftInlineStyle.js
    """
    for feature in inline_features_list:
        feature_name = feature[0]
        type_ = feature[1]
        label = feature[2]
        style_in_editor = feature[3]
        from_db_format = feature[4]
        to_db_format = feature[5]
        # Configure how Draftail handles the feature in its toolbar.
        control = {
            'type': type_,
            'label': label,
            'description': feature_name.title(),
            'style': style_in_editor
        }
        # Call register_editor_plugin to register the configuration for Draftail.
        features.register_editor_plugin(
            'draftail', feature_name, draftail_features.InlineStyleFeature(control)
        )
        # Configure the content transform from the DB to the editor and back.
        db_conversion = {
            'from_database_format': from_db_format,
            'to_database_format': to_db_format,
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
