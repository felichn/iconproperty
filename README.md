# Django + React Property Inventory Manager

This project provides a property inventory management system for real estate workflows with:

- Property data for **Rumah**, **Ruko**, and **Gudang**
- Listing mode (**Rent** or **Sell**)
- Price, width, length, floors, area, and owner WhatsApp number
- Multi-photo upload per property
- Sort/filter with paginated listing (**10 properties per page**)
- Photo collage generation to share via WhatsApp

## Stack

- Django backend + templating
- React frontend (served in-browser via CDN)
- SQLite database
- Pillow for image processing (collage generation)

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
- `POST /api/properties/<property_id>/collage/`
  - Generate collage from all or selected photos (`photo_ids`)
  - Returns direct collage URL + WhatsApp share URL

## Common list query parameters

- `page` (default `1`)
- `sort` (e.g. `-created_at`, `price`, `-price`, `width`, `-width`)
- `property_type` (`rumah`, `ruko`, `gudang`)
- `listing_mode` (`rent`, `sell`)
- `area` (contains match)
- `min_price`, `max_price`
- `min_floors`, `max_floors`
