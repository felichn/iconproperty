import json
import math
import uuid
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import quote_plus

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from PIL import Image

from .models import Property, PropertyPhoto


def inventory_page(request):
    return render(request, "inventory/index.html")


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


def _validate_int(value, field_name):
    if value in (None, ""):
        raise ValueError(f"{field_name} is required.")
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be an integer.")
    if parsed < 0:
        raise ValueError(f"{field_name} cannot be negative.")
    return parsed


def _serialize_photo(photo, request):
    return {
        "id": photo.id,
        "image_url": request.build_absolute_uri(photo.image.url),
        "uploaded_at": photo.uploaded_at.isoformat(),
    }


def _serialize_property(property_obj, request):
    photos = list(property_obj.photos.all())
    return {
        "id": property_obj.id,
        "title": property_obj.title,
        "property_type": property_obj.property_type,
        "property_type_label": property_obj.get_property_type_display(),
        "listing_mode": property_obj.listing_mode,
        "listing_mode_label": property_obj.get_listing_mode_display(),
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
        "title",
        "property_type",
        "listing_mode",
        "price",
        "width",
        "length",
        "floors",
        "area",
        "owner_whatsapp_number",
    )
    for field in required_fields:
        if field not in payload:
            raise ValueError(f"{field} is required.")

    property_obj.title = str(payload["title"]).strip()
    property_obj.property_type = payload["property_type"]
    property_obj.listing_mode = payload["listing_mode"]
    property_obj.price = _validate_decimal(payload["price"], "price")
    property_obj.width = _validate_decimal(payload["width"], "width")
    property_obj.length = _validate_decimal(payload["length"], "length")
    property_obj.floors = _validate_int(payload["floors"], "floors")
    property_obj.area = str(payload["area"]).strip()
    property_obj.owner_whatsapp_number = str(payload["owner_whatsapp_number"]).strip()
    property_obj.description = str(payload.get("description", "")).strip()

    if not property_obj.title:
        raise ValueError("title is required.")
    if not property_obj.area:
        raise ValueError("area is required.")
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


@require_http_methods(["POST"])
@csrf_exempt
def property_photo_upload_api(request, property_id):
    property_obj = get_object_or_404(Property, pk=property_id)
    files = request.FILES.getlist("photos")
    if not files:
        single_photo = request.FILES.get("photo")
        if single_photo:
            files = [single_photo]
    if not files:
        return JsonResponse({"error": "No photos uploaded."}, status=400)

    saved_photos = []
    for file_obj in files:
        photo = PropertyPhoto.objects.create(property=property_obj, image=file_obj)
        saved_photos.append(_serialize_photo(photo, request))

    return JsonResponse({"photos": saved_photos}, status=201)


@require_http_methods(["DELETE"])
@csrf_exempt
def property_photo_delete_api(request, photo_id):
    photo = get_object_or_404(PropertyPhoto, pk=photo_id)
    photo.image.delete(save=False)
    photo.delete()
    return JsonResponse({"deleted": True})


@require_http_methods(["POST"])
@csrf_exempt
def property_collage_api(request, property_id):
    property_obj = get_object_or_404(Property.objects.prefetch_related("photos"), pk=property_id)
    payload = {}
    if request.body:
        try:
            payload = _parse_json_body(request)
        except ValueError:
            return JsonResponse({"error": "Invalid JSON body."}, status=400)

    selected_photo_ids = payload.get("photo_ids")
    photos = property_obj.photos.all()
    if isinstance(selected_photo_ids, list) and selected_photo_ids:
        photos = photos.filter(id__in=selected_photo_ids)
    photos = list(photos)

    if not photos:
        return JsonResponse({"error": "No property photos available."}, status=400)

    images = []
    for photo in photos:
        try:
            with Image.open(photo.image.path) as img:
                images.append(img.convert("RGB"))
        except (FileNotFoundError, OSError):
            continue

    if not images:
        return JsonResponse({"error": "Uploaded images could not be read."}, status=400)

    cell_size = 900
    cols = min(3, len(images))
    rows = math.ceil(len(images) / cols)
    collage = Image.new("RGB", (cols * cell_size, rows * cell_size), color=(248, 248, 248))

    for index, image in enumerate(images):
        image.thumbnail((cell_size - 20, cell_size - 20))
        x_offset = (index % cols) * cell_size + (cell_size - image.width) // 2
        y_offset = (index // cols) * cell_size + (cell_size - image.height) // 2
        collage.paste(image, (x_offset, y_offset))

    collages_dir = Path(settings.MEDIA_ROOT) / "collages"
    collages_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.jpg"
    saved_path = collages_dir / filename
    collage.save(saved_path, format="JPEG", quality=90)

    collage_url = f"{settings.MEDIA_URL}collages/{filename}"
    absolute_collage_url = request.build_absolute_uri(collage_url)
    whatsapp_text = quote_plus(
        f"Property photo collage for {property_obj.title}: {absolute_collage_url}"
    )

    return JsonResponse(
        {
            "collage_url": absolute_collage_url,
            "whatsapp_share_url": f"https://wa.me/?text={whatsapp_text}",
        }
    )

# Create your views here.
