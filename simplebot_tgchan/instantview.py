"""Unsupported PageBlock types:

PageBlockMap
PageBlockCollage
PageBlockRelatedArticles
PageBlockSlideshow
PageBlockChannel
PageBlockAudio
PageBlockVideo
"""

# pylama:ignore=C0103

import base64
import html


async def _download_image(logger, client, img) -> str:
    try:
        return base64.b64encode(await client.download_media(img, bytes)).decode()
    except Exception as ex:
        logger.exception(ex)
        return ""


async def blocks2html(blocks: list, client=None, msg=None, logger=None) -> str:
    html_text = ""
    for block in blocks:
        html_text += await block2html(block, client=client, msg=msg, logger=logger)
    return html_text


async def block2html(block, **kwargs) -> str:
    to_html = globals().get(type(block).__name__ + "2HTML")
    return (await to_html(block, **kwargs)) if to_html else ""


async def TextPlain2HTML(block, **kwargs) -> str:  # noqa
    return html.escape(block.text).replace("\n", "<br>")


async def TextFixed2HTML(block, **kwargs) -> str:
    return await block2html(block.text, **kwargs)


async def TextMarked2HTML(block, **kwargs) -> str:
    return await block2html(block.text, **kwargs)


async def TextBold2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f"<b>{html_text}</b>"


async def TextItalic2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f"<i>{html_text}</i>"


async def TextStrike2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f"<del>{html_text}</del>"


async def TextUnderline2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f"<u>{html_text}</u>"


async def TextSubscript2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f"<sub>{html_text}</sub>"


async def TextSuperscript2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f"<sup>{html_text}</sup>"


async def TextAnchor2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f'<span id="{block.name}">{html_text}</span>'


async def TextEmail2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f'<a href="mailto:{block.email}">{html_text}</a>'


async def TextPhone2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f'<a href="tel:{block.phone}">{html_text}</a>'


async def TextUrl2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f'<a href="{block.url}">{html_text}</a>'


async def TextConcat2HTML(block, **kwargs) -> str:
    html_text = ""
    for text in block.texts:
        html_text += await block2html(text, **kwargs)
    return html_text


async def TextImage2HTML(block, **kwargs) -> str:
    photo = None
    for doc in kwargs["msg"].web_preview.cached_page.documents:
        if doc.id == block.document_id:
            photo = doc
            break
    if photo:
        img = await _download_image(kwargs["logger"], kwargs["client"], photo)
        width = str(block.w) if block.w else "100%"
        height = str(block.h) if block.h else "auto"
        return f'<img src="data:image/png;base64,{img}" style="width:{width}; height: {height};"/>'
    return ""


async def PageBlockCover2HTML(block, **kwargs) -> str:
    return await block2html(block.cover, **kwargs)


async def PageBlockTitle2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f"<h1>{html_text}</h1>"


async def PageBlockSubtitle2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f"<h2>{html_text}</h2>"


async def PageBlockHeader2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f"<h2>{html_text}</h2>"


async def PageBlockSubheader2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f"<h3>{html_text}</h3>"


async def PageBlockParagraph2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f"<p>{html_text}</p>"


async def PageBlockPullquote2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f"<center>{html_text}</center>"


async def PageBlockBlockquote2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f"<blockquote>{html_text}</blockquote>"


async def PageBlockFooter2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f"<footer>{html_text}</footer>"


async def PageBlockOrderedList2HTML(block, **kwargs) -> str:
    html_text = await blocks2html(block.items, **kwargs)
    return f"<ol>{html_text}</ol>"


async def PageListOrderedItemText2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f"<li>{html_text}</li>"


async def PageListOrderedItemBlocks2HTML(block, **kwargs) -> str:
    html_text = await blocks2html(block.blocks, **kwargs)
    return f"<li>{html_text}</li>"


async def PageBlockList2HTML(block, **kwargs) -> str:
    html_text = await blocks2html(block.items, **kwargs)
    return f"<ul>{html_text}</ul>"


async def PageListItemText2HTML(block, **kwargs) -> str:
    html_text = await block2html(block.text, **kwargs)
    return f"<li>{html_text}</li>"


async def PageListItemBlocks2HTML(block, **kwargs) -> str:
    html_text = await blocks2html(block.blocks, **kwargs)
    return f"<li>{html_text}</li>"


async def PageBlockPreformatted2HTML(block, **kwargs) -> str:
    return await block2html(block.text, **kwargs)


async def PageBlockKicker2HTML(block, **kwargs) -> str:
    return await block2html(block.text, **kwargs)


async def PageBlockDivider2HTML(block, **kwargs) -> str:  # noqa
    return "<hr>"


async def PageBlockAnchor2HTML(block, **kwargs) -> str:  # noqa
    return f'<span id="{block.name}"></span>'


async def PageBlockDetails2HTML(block, **kwargs) -> str:
    title = await block2html(block.title, **kwargs)
    html_text = await blocks2html(block.blocks, **kwargs)
    return f"<details><summary>{title}</summary>{html_text}</details>"


async def PageBlockTable2HTML(block, **kwargs) -> str:
    title = await block2html(block.title, **kwargs)
    html_text = await blocks2html(block.rows, **kwargs)
    border = 'border="1"' if block.bordered else ""
    return f"<table {border}><caption>{title}</caption>{html_text}</table>"


async def PageTableRow2HTML(block, **kwargs) -> str:
    html_text = await blocks2html(block.cells, **kwargs)
    return f"<tr>{html_text}</tr>"


async def PageTableCell2HTML(block, **kwargs) -> str:
    text = await block2html(block.text, **kwargs)
    tag = "th" if block.header else "td"
    style = ""
    if block.align_center:
        style += "text-align:center;"
    elif block.align_right:
        style += "text-align:right;"
    if block.valign_middle:
        style += "vertical-align:middle;"
    elif block.valign_bottom:
        style += "vertical-align:bottom;"
    return f'<{tag} style="{style}" colspan="{block.colspan}" rowspan="{block.rowspan}">{text}</{tag}>'


async def PageBlockEmbedPost2HTML(block, **kwargs) -> str:
    return await blocks2html(block.blocks, **kwargs)


async def PageBlockEmbed2HTML(block, **kwargs) -> str:  # noqa
    return f'<video controls><source src="{block.url}"></video>' if block.url else ""


async def PageBlockAuthorDate2HTML(block, **kwargs) -> str:
    author = await block2html(block.author, **kwargs)
    date = block.published_date.strftime("%d/%m/%Y") if block.published_date else ""
    html_text = " - ".join(text for text in [date, author] if text)
    return f"<small>{html_text}</small>" if html_text else ""


async def PageCaption2HTML(block, **kwargs) -> str:
    text = await block2html(block.text, **kwargs)
    credit = await block2html(block.credit, **kwargs)
    html_text = " - ".join(text for text in [text, credit] if text)
    return f"<small>{html_text}</small>" if html_text else ""


async def PageBlockPhoto2HTML(block, **kwargs) -> str:
    msg = kwargs["msg"]
    photo = None
    try:
        if msg.web_preview.photo.id == block.photo_id:
            photo = msg.web_preview.photo
    except AttributeError:
        pass
    if not photo:
        try:
            if msg.media.webpage.photo.id == block.photo_id:
                photo = msg.media.webpage.photo
        except AttributeError:
            pass
    if not photo:
        for pic in msg.web_preview.cached_page.photos:
            if pic.id == block.photo_id:
                photo = pic
                break
    if photo:
        img = await _download_image(kwargs["logger"], kwargs["client"], photo)
        html_text = f'<center><img src="data:image/png;base64,{img}" alt="COVER" style="width:100%"/></center>'
        html_text += await block2html(block.caption, **kwargs)
        return html_text
    return ""
