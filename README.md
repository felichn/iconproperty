# Django + React Property Inventory Manager

This project provides a property inventory management system for real estate workflows with:

- Property data for **Rumah**, **Ruko**, and **Gudang**
- Listing mode (**Rent** or **Sell**)
- Price, width, length, floors, area, and owner WhatsApp number
- Multi-photo upload per property
- Sort/filter with paginated listing (**10 properties per page**)
- Shareable property page with all photos
- Downloadable ZIP file containing property photos

## Stack

- Django backend + templating
- React frontend (served in-browser via CDN)
- SQLite database
- Pillow (used in image-related tests)

## Setup

1. Install dependencies:

   ```bash
   pip3 install --user --break-system-packages -r requirements.txt
   ```

2. Run migrations:

   ```bash
   python3 manage.py migrate
   ```

3. Start the server:

   ```bash
   python3 manage.py runserver 0.0.0.0:8000
   ```

4. Open:

   - Main app: `http://127.0.0.1:8000/`
   - Admin: `http://127.0.0.1:8000/admin/`

## API Endpoints

- `GET/POST /api/properties/`
  - List properties with pagination, sort, and filters
  - Create a property
- `GET/PUT /api/properties/<property_id>/`
  - Retrieve or update one property
- `POST /api/properties/<property_id>/photos/`
  - Upload one or many photos (`photo` or `photos` files)
- `DELETE /api/photos/<photo_id>/`
  - Delete a photo
- `GET /api/properties/<property_id>/share-links/`
  - Returns `property_page_url`, `download_photos_url`, and `whatsapp_share_url`
- `GET /api/properties/<property_id>/download-photos/`
  - Downloads all property photos as a ZIP file

## Common list query parameters

- `page` (default `1`)
- `sort` (e.g. `-created_at`, `price`, `-price`, `width`, `-width`)
- `property_type` (`rumah`, `ruko`, `gudang`)
- `listing_mode` (`rent`, `sell`)
- `area` (contains match)
- `min_price`, `max_price`
- `min_floors`, `max_floors`
