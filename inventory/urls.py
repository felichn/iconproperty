from django.urls import path

from . import views

urlpatterns = [
    path("", views.inventory_page, name="inventory-page"),
    path("api/properties/", views.property_collection_api, name="property-collection-api"),
    path(
        "api/properties/<int:property_id>/",
        views.property_item_api,
        name="property-item-api",
    ),
    path(
        "api/properties/<int:property_id>/photos/",
        views.property_photo_upload_api,
        name="property-photo-upload-api",
    ),
    path(
        "api/properties/<int:property_id>/collage/",
        views.property_collage_api,
        name="property-collage-api",
    ),
    path(
        "api/photos/<int:photo_id>/",
        views.property_photo_delete_api,
        name="property-photo-delete-api",
    ),
]
