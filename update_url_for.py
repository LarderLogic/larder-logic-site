import os


mapping = {
    "routes.login": "auth.login",
    "routes.logout": "auth.logout",
    "routes.admin": "auth.admin",
    "routes.admin_dashboard": "dashboard.admin_dashboard",
    "routes.admin_list_articles": "article.admin_list_articles",
    "routes.admin_new_article": "article.admin_new_article",
    "routes.admin_edit_article": "article.admin_edit_article",
    "routes.admin_delete_article": "article.admin_delete_article",
    "routes.admin_add_tag_to_article": "article.admin_add_tag_to_article",
    "routes.admin_link_images_to_article": "article.admin_link_images_to_article",
    "routes.admin_list_tags": "tag.admin_list_tags",
    "routes.admin_new_tag": "tag.admin_new_tag",
    "routes.admin_edit_tag": "tag.admin_edit_tag",
    "routes.admin_delete_tag": "tag.admin_delete_tag",
    "routes.admin_add_tag_to_items": "tag.admin_add_tag_to_items",
    "routes.admin_link_articles_to_tag": "tag.admin_link_articles_to_tag",
    "routes.admin_images": "image.admin_images",
    "routes.admin_list_images": "image.admin_list_images",
    "routes.admin_upload_images": "image.admin_upload_images",
    "routes.admin_upload_image": "image.admin_upload_image",
    "routes.admin_bulk_upload_images": "image.admin_bulk_upload_images",
    "routes.admin_stage_images": "image.admin_stage_images",
    "routes.admin_add_tag_to_image": "image.admin_add_tag_to_image",
    "routes.admin_link_article_to_image": "image.admin_link_article_to_image",
    "routes.admin_edit_image": "image.admin_edit_image",
    "routes.admin_delete_image": "image.admin_delete_image",
    "routes.mark_contact_reviewed": "contact.mark_contact_reviewed",
    "routes.admin_review_contact": "contact.admin_review_contact",
    "routes.admin_clear_all_contacts": "contact.admin_clear_all_contacts",
}


def update_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    original = content


    for old, new in mapping.items():
        # Replace both single and double-quoted url_for
        content = content.replace(f"url_for('{old}')", f"url_for('{new}')")
        content = content.replace(f"url_for(\"{old}\")", f"url_for('{new}')")


    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated: {filepath}")


for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py") or file.endswith(".html"):
            update_file(os.path.join(root, file))

