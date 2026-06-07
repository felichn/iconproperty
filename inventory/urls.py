from django.urls import path

from . import views

urlpatterns = [
    path("", views.inventory_list_page, name="inventory-page"),
    path("properties/add/", views.property_add_page, name="property-add-page"),
    path(
        "properties/<int:property_id>/",
        views.property_public_page,
        name="property-public-page",
    ),
    path("api/properties/", views.property_collection_api, name="property-collection-api"),
    path(
        "api/properties/<int:property_id>/",
        views.property_item_api,
        name="property-item-api",
    ),
    path(
        "api/properties/<int:property_id>/share-links/",
        views.property_share_links_api,
        name="property-share-links-api",
    ),
    path(
        "api/properties/<int:property_id>/download-photos/",
        views.property_photo_download_api,
        name="property-photo-download-api",
    ),
    path(
        "api/photos/<int:photo_id>/",
        views.property_photo_delete_api,
        name="property-photo-delete-api",
    ),
]
