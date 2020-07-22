from typing import List, Mapping, Optional

from peewee import ModelSelect

from .models import Attachment, Label, Page


def search_results(
            query: str, sections: Optional[List[str]] = None
        ) -> Mapping[str, ModelSelect]:
    """Extremely simple content search entrypoint. Search is performed against
    provided sections or all sections if not provided (Pages, Labels,
    Attachments). Returned results are partitioned by data type. Pages are
    returned ordered by modification date, labels by name, attachments by
    creation date.

    Search fields:

    * pages: title and text
    * labels: name
    * attachments: title and description

    :param query: search query
    :type query: str
    :param sections: where to search, defaults to None
    :type sections: Optional[List[str]], optional
    :return: search result partitioned by data type
    :rtype: Mapping[str, ModelSelect]
    """
    if not sections:
        sections = ['pages', 'labels', 'attachments']
    results = {}
    query = f'%{query}%'
    if 'pages' in sections:
        results['pages'] = (
            Page
            .select()
            .where((Page.title ** query) | (Page.text ** query))
            .order_by(-Page.updated)
        )
    if 'labels' in sections:
        results['labels'] = (
            Label.select().where(Label.name ** query).order_by(Label.name)
        )
    if 'attachments' in sections:
        results['attachments'] = (
            Attachment
            .select()
            .where(
                (Attachment.title ** query) | (Attachment.description ** query)
            )
            .order_by(-Attachment.created)
        )
    return results
