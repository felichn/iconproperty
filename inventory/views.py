import json
import zipfile
from decimal import Decimal, InvalidOperation
from io import BytesIO
from urllib.parse import quote_plus

from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Property, PropertyPhoto


def inventory_list_page(request):
    return render(request, "inventory/index.html")


def property_add_page(request):
    return render(request, "inventory/add_property.html")


def property_public_page(request, property_id):
    property_obj = get_object_or_404(Property.objects.prefetch_related("photos"), pk=property_id)
    return render(
        request,
        "inventory/property_detail.html",
        {
            "property": property_obj,
            "photos": property_obj.photos.all(),
        },
    )


def _parse_json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError("Invalid JSON body")


def _validate_decimal(value, field_name):
    if value in (None, ""):
        raise ValueError(f"{field_name} is required.")
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValueError(f"{field_name} must be a valid number.")


def _validate_int(value, field_name, minimum=0):
    if value in (None, ""):
        raise ValueError(f"{field_name} is required.")
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be an integer.")
    if parsed < minimum:
        if minimum == 0:
            raise ValueError(f"{field_name} cannot be negative.")
        raise ValueError(f"{field_name} must be at least {minimum}.")
    return parsed


def _serialize_photo(photo, request):
    return {
        "id": photo.id,
        "image_url": request.build_absolute_uri(photo.image.url),
        "uploaded_at": photo.uploaded_at.isoformat(),
    }


def _serialize_property(property_obj, request):
    photos = list(property_obj.photos.all())
    property_page_url = request.build_absolute_uri(
        reverse("property-public-page", args=[property_obj.id])
    )
    download_photos_url = request.build_absolute_uri(
        reverse("property-photo-download-api", args=[property_obj.id])
    )
    return {
        "id": property_obj.id,
        "title": property_obj.title,
        "property_type": property_obj.property_type,
        "property_type_label": property_obj.get_property_type_display(),
        "listing_mode": property_obj.listing_mode,
        "listing_mode_label": property_obj.get_listing_mode_display(),
        "block": property_obj.block,
        "unit_no": property_obj.unit_no,
        "unit": property_obj.unit,
        "price": str(property_obj.price),
        "width": str(property_obj.width),
        "length": str(property_obj.length),
        "floors": property_obj.floors,
        "area": property_obj.area,
        "owner_whatsapp_number": property_obj.owner_whatsapp_number,
        "description": property_obj.description,
        "created_at": property_obj.created_at.isoformat(),
        "updated_at": property_obj.updated_at.isoformat(),
        "photos": [_serialize_photo(photo, request) for photo in photos],
        "property_page_url": property_page_url,
        "download_photos_url": download_photos_url,
        "primary_photo_url": (
            request.build_absolute_uri(photos[0].image.url) if photos else None
        ),
    }


def _apply_property_payload(property_obj, payload):
    property_type = payload.get("property_type")
    listing_mode = payload.get("listing_mode")
    if property_type and property_type not in Property.PropertyType.values:
        raise ValueError("property_type must be one of: rumah, ruko, gudang.")
    if listing_mode and listing_mode not in Property.ListingMode.values:
        raise ValueError("listing_mode must be one of: rent, sell.")

    required_fields = (
        "property_type",
        "listing_mode",
        "price",
        "width",
        "length",
        "floors",
        "area",
        "block",
        "unit_no",
        "owner_whatsapp_number",
    )
    for field in required_fields:
        if field not in payload:
            raise ValueError(f"{field} is required.")

    property_obj.property_type = payload["property_type"]
    property_obj.listing_mode = payload["listing_mode"]
    property_obj.price = _validate_decimal(payload["price"], "price")
    property_obj.width = _validate_decimal(payload["width"], "width")
    property_obj.length = _validate_decimal(payload["length"], "length")
    property_obj.floors = _validate_int(payload["floors"], "floors", minimum=1)
    property_obj.area = str(payload["area"]).strip()
    property_obj.block = str(payload["block"]).strip()
    property_obj.unit_no = _validate_int(payload["unit_no"], "unit_no", minimum=1)
    property_obj.owner_whatsapp_number = str(payload["owner_whatsapp_number"]).strip()
    property_obj.description = str(payload.get("description", "")).strip()

    requested_title = payload.get("title")
    if requested_title is None or not str(requested_title).strip():
        property_obj.title = property_obj.area
    else:
        property_obj.title = str(requested_title).strip()

    if not property_obj.area:
        raise ValueError("area is required.")
    allowed_areas = Property.AREA_OPTIONS_BY_PROPERTY_TYPE.get(property_obj.property_type, [])
    if allowed_areas and property_obj.area not in allowed_areas:
        raise ValueError(
            f"area must be one of: {', '.join(allowed_areas)}."
        )
    if not property_obj.block:
        raise ValueError("block is required.")
    if not property_obj.owner_whatsapp_number:
        raise ValueError("owner_whatsapp_number is required.")


@require_http_methods(["GET", "POST"])
@csrf_exempt
def property_collection_api(request):
    if request.method == "GET":
        queryset = Property.objects.prefetch_related("photos").all()
        filters = {
            "property_type": request.GET.get("property_type"),
            "listing_mode": request.GET.get("listing_mode"),
            "area": request.GET.get("area"),
            "min_price": request.GET.get("min_price"),
            "max_price": request.GET.get("max_price"),
            "min_floors": request.GET.get("min_floors"),
            "max_floors": request.GET.get("max_floors"),
        }
        sort = request.GET.get("sort", "-created_at")
        allowed_sort_fields = {
            "price",
            "-price",
            "width",
            "-width",
            "length",
            "-length",
            "floors",
            "-floors",
            "created_at",
            "-created_at",
            "area",
            "-area",
        }
        if sort not in allowed_sort_fields:
            sort = "-created_at"

        if filters["property_type"] in Property.PropertyType.values:
            queryset = queryset.filter(property_type=filters["property_type"])
        if filters["listing_mode"] in Property.ListingMode.values:
            queryset = queryset.filter(listing_mode=filters["listing_mode"])
        if filters["area"]:
            queryset = queryset.filter(area__icontains=filters["area"])
        if filters["min_price"]:
            try:
                queryset = queryset.filter(price__gte=Decimal(filters["min_price"]))
            except InvalidOperation:
                pass
        if filters["max_price"]:
            try:
                queryset = queryset.filter(price__lte=Decimal(filters["max_price"]))
            except InvalidOperation:
                pass
        if filters["min_floors"]:
            try:
                queryset = queryset.filter(floors__gte=int(filters["min_floors"]))
            except ValueError:
                pass
        if filters["max_floors"]:
            try:
                queryset = queryset.filter(floors__lte=int(filters["max_floors"]))
            except ValueError:
                pass

        queryset = queryset.order_by(sort)
        paginator = Paginator(queryset, 10)
        page_number = request.GET.get("page", "1")
        try:
            page_obj = paginator.page(page_number)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages or 1)

        return JsonResponse(
            {
                "results": [_serialize_property(prop, request) for prop in page_obj],
                "pagination": {
                    "page": page_obj.number,
                    "page_size": 10,
                    "num_pages": paginator.num_pages,
                    "total_items": paginator.count,
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous(),
                },
            }
        )

    try:
        payload = _parse_json_body(request)
        property_obj = Property()
        _apply_property_payload(property_obj, payload)
        property_obj.full_clean()
        property_obj.save()
    except (ValueError, ValidationError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse(_serialize_property(property_obj, request), status=201)


@require_http_methods(["GET", "PUT"])
@csrf_exempt
def property_item_api(request, property_id):
    property_obj = get_object_or_404(Property.objects.prefetch_related("photos"), pk=property_id)
    if request.method == "GET":
        return JsonResponse(_serialize_property(property_obj, request))

    try:
        payload = _parse_json_body(request)
        _apply_property_payload(property_obj, payload)
        property_obj.full_clean()
        property_obj.save()
    except (ValueError, ValidationError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse(_serialize_property(property_obj, request))


@require_http_methods(["DELETE"])
@csrf_exempt
def property_photo_delete_api(request, photo_id):
    photo = get_object_or_404(PropertyPhoto, pk=photo_id)
    photo.image.delete(save=False)
    photo.delete()
    return JsonResponse({"deleted": True})


@require_http_methods(["GET"])
@csrf_exempt
def property_share_links_api(request, property_id):
    property_obj = get_object_or_404(Property.objects.prefetch_related("photos"), pk=property_id)
    property_page_url = request.build_absolute_uri(
        reverse("property-public-page", args=[property_obj.id])
    )
    download_photos_url = request.build_absolute_uri(
        reverse("property-photo-download-api", args=[property_obj.id])
    )
    whatsapp_text = quote_plus(
        (
            f"Selamat, berikut halaman foto properti Unit {property_obj.unit} di {property_obj.area}: "
            f"{property_page_url}. Download semua foto di: {download_photos_url}"
        )
    )
    return JsonResponse(
        {
            "property_page_url": property_page_url,
            "download_photos_url": download_photos_url,
            "whatsapp_share_url": f"https://wa.me/?text={whatsapp_text}",
        }
    )


@require_http_methods(["GET"])
@csrf_exempt
def property_photo_download_api(request, property_id):
    property_obj = get_object_or_404(Property.objects.prefetch_related("photos"), pk=property_id)
    photos = list(property_obj.photos.all())
    if not photos:
        return JsonResponse({"error": "No property photos available for download."}, status=400)

    zip_buffer = BytesIO()
    written_count = 0
    with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for index, photo in enumerate(photos, start=1):
            file_ext = photo.image.name.rsplit(".", 1)[-1].lower() if "." in photo.image.name else "jpg"
            file_name = f"photo-{index}.{file_ext}"
            folder_name = slugify(property_obj.title) or f"property-{property_obj.id}"
            archive_path = f"{folder_name}/{file_name}"
            try:
                with photo.image.open("rb") as image_file:
                    archive.writestr(archive_path, image_file.read())
                    written_count += 1
            except OSError:
                continue

    if written_count == 0:
        return JsonResponse({"error": "Unable to read property photos for download."}, status=400)

    zip_buffer.seek(0)
    download_name = f"{slugify(property_obj.title) or f'property-{property_obj.id}'}-photos.zip"
    response = HttpResponse(zip_buffer.read(), content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename="{download_name}"'
    return response
