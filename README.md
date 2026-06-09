# Django + React Property Inventory Manager

This project provides a property inventory management system for real estate workflows with:

- Property data for **Rumah**, **Ruko**, and **Gudang**
- Listing mode (**Rent** or **Sell**)
- Unique unit identity from **Blok** + **No.** (displayed as **Unit** code)
- Price, width, length, floors, area, and owner WhatsApp number
- Sort/filter with paginated listing (**10 properties per page**)
- Shareable property page with all photos
- Downloadable ZIP file containing property photos

## Stack

- Django backend + templating
- React frontend (served in-browser via CDN)
- SQLite database

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

   - Property display page: `http://127.0.0.1:8000/`
   - Add property page: `http://127.0.0.1:8000/properties/add/`
   - Admin: `http://127.0.0.1:8000/admin/`

## API Endpoints

- `GET/POST /api/properties/`
  - List properties with pagination, sort, and filters
  - Create a property
- `GET/PUT /api/properties/<property_id>/`
  - Retrieve or update one property
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

## Unit code format

Each property stores `block` (**Blok**) and `unit_no` (**No.**) and exposes a computed `unit` code.

Examples:
- `Villa Pasir Putih` Blok `1` No. `38` -> `V5S1-038`
- `Villa Pasir Putih` Blok `3` No. `3` -> `V5S3-003`
- `Hollywood` (Ruko) Blok `F` No. `1` -> `MBHW-F01`
- `Bizpark` (Gudang) Blok `C2` No. `55` -> `BPC2-055`
