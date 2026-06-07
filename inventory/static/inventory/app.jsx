const { useEffect, useState } = React;

const defaultForm = {
  property_type: "rumah",
  listing_mode: "sell",
  block: "",
  unit_no: "",
  price: "",
  width: "",
  length: "",
  floors: 1,
  area: "Villa Pasir Putih",
  owner_whatsapp_number: "",
  description: "",
};

function InventoryApp() {
  const areaOptionsByPropertyType = {
    rumah: ["Villa Pasir Putih"],
    gudang: ["Bizpark"],
    ruko: ["Hollywood", "Manhattan", "Broadway"],
  };
  const allAreaOptions = Array.from(new Set(Object.values(areaOptionsByPropertyType).flat()));

  const [formData, setFormData] = useState(defaultForm);
  const [filters, setFilters] = useState({
    property_type: "",
    listing_mode: "",
    area: "",
    min_price: "",
    max_price: "",
    sort: "-created_at",
  });
  const [properties, setProperties] = useState([]);
  const [pagination, setPagination] = useState({
    page: 1,
    num_pages: 1,
    total_items: 0,
    has_next: false,
    has_previous: false,
  });
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [uploadFiles, setUploadFiles] = useState({});

  const propertyTypeOptions = [
    { value: "rumah", label: "Rumah" },
    { value: "ruko", label: "Ruko" },
    { value: "gudang", label: "Gudang" },
  ];

  const listingModeOptions = [
    { value: "sell", label: "Sell" },
    { value: "rent", label: "Rent" },
  ];

  const sortOptions = [
    { value: "-created_at", label: "Newest" },
    { value: "created_at", label: "Oldest" },
    { value: "price", label: "Price: Low to High" },
    { value: "-price", label: "Price: High to Low" },
    { value: "width", label: "Width: Low to High" },
    { value: "-width", label: "Width: High to Low" },
    { value: "length", label: "Length: Low to High" },
    { value: "-length", label: "Length: High to Low" },
    { value: "-floors", label: "Floors: High to Low" },
  ];

  async function fetchProperties(nextPage = page) {
    setLoading(true);
    setErrorMessage("");
    try {
      const params = new URLSearchParams();
      params.set("page", String(nextPage));
      params.set("sort", filters.sort);
      Object.entries(filters).forEach(([key, value]) => {
        if (key !== "sort" && value !== "") {
          params.set(key, value);
        }
      });
      const response = await fetch(`/api/properties/?${params.toString()}`);
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Failed to load properties.");
      }
      setProperties(data.results);
      setPagination(data.pagination);
      setPage(data.pagination.page);
      setStatusMessage(`Showing ${data.results.length} of ${data.pagination.total_items} properties.`);
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchProperties(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.property_type, filters.listing_mode, filters.area, filters.min_price, filters.max_price, filters.sort]);

  async function createProperty(event) {
    event.preventDefault();
    setErrorMessage("");
    setStatusMessage("");
    try {
      const response = await fetch("/api/properties/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Failed to create property.");
      }
      setFormData(defaultForm);
      setStatusMessage(`Unit "${data.unit}" created.`);
      fetchProperties(1);
    } catch (error) {
      setErrorMessage(error.message);
    }
  }

  async function uploadPropertyPhotos(propertyId) {
    const files = uploadFiles[propertyId];
    if (!files || files.length === 0) {
      setErrorMessage("Select one or more photos first.");
      return;
    }
    const payload = new FormData();
    files.forEach((file) => payload.append("photos", file));
    try {
      const response = await fetch(`/api/properties/${propertyId}/photos/`, {
        method: "POST",
        body: payload,
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Failed to upload photos.");
      }
      setStatusMessage(`${data.photos.length} photo(s) uploaded.`);
      setUploadFiles((prev) => ({ ...prev, [propertyId]: [] }));
      fetchProperties(page);
    } catch (error) {
      setErrorMessage(error.message);
    }
  }

  async function deletePhoto(photoId) {
    try {
      const response = await fetch(`/api/photos/${photoId}/`, {
        method: "DELETE",
      });
      const data = await response.json();
      if (!response.ok || !data.deleted) {
        throw new Error(data.error || "Failed to delete photo.");
      }
      setStatusMessage("Photo deleted.");
      fetchProperties(page);
    } catch (error) {
      setErrorMessage(error.message);
    }
  }

  function getTimeGreetingLabel() {
    const hour = new Date().getHours();
    if (hour < 11) {
      return "Pagi";
    }
    if (hour < 18) {
      return "Siang";
    }
    return "Malam";
  }

  function buildOwnerWhatsappLink(property) {
    const phoneNumber = (property.owner_whatsapp_number || "").replace(/\D/g, "");
    if (!phoneNumber) {
      return null;
    }
    const greetingLabel = getTimeGreetingLabel();
    const propertyType = property.property_type_label || property.property_type || "Properti";
    const area = property.area || "-";
    const listingModeValue = (property.listing_mode || "").toLowerCase();
    const listingModeText =
      listingModeValue === "sell"
        ? "dijual"
        : listingModeValue === "rent"
          ? "disewakan"
          : "dipasarkan";
    const text = encodeURIComponent(
      `Selamat ${greetingLabel}, saya Felicia dari Icon Property.\n${propertyType} di ${area} ${listingModeText} nett di harga berapa?`
    );
    return `https://wa.me/${phoneNumber}?text=${text}`;
  }

  function buildClientWhatsappShareLink(property) {
    const propertyPageUrl = property.property_page_url || `/properties/${property.id}/`;
    const downloadUrl = property.download_photos_url || `/api/properties/${property.id}/download-photos/`;
    const text = encodeURIComponent(
      `Berikut halaman foto properti Unit ${property.unit}: ${propertyPageUrl}\nDownload semua foto: ${downloadUrl}`
    );
    return `https://wa.me/?text=${text}`;
  }

  function getFilterAreaOptions() {
    if (filters.property_type && areaOptionsByPropertyType[filters.property_type]) {
      return areaOptionsByPropertyType[filters.property_type];
    }
    return allAreaOptions;
  }

  return (
    <div>
      <section className="panel">
        <h2>Add Property</h2>
        <form onSubmit={createProperty} className="grid columns-4">
          <div>
            <label>Type</label>
            <select
              value={formData.property_type}
              onChange={(e) => {
                const selectedType = e.target.value;
                const areaOptions = areaOptionsByPropertyType[selectedType] || [];
                setFormData((prev) => ({
                  ...prev,
                  property_type: selectedType,
                  area: areaOptions[0] || "",
                }));
              }}
            >
              {propertyTypeOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
          </div>
          <div>
            <label>Rent or Sell</label>
            <div className="actions-inline">
              {listingModeOptions.map((option) => (
                <label key={option.value} style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: 0 }}>
                  <input
                    type="radio"
                    name="listing_mode"
                    value={option.value}
                    checked={formData.listing_mode === option.value}
                    onChange={(e) => setFormData((prev) => ({ ...prev, listing_mode: e.target.value }))}
                    style={{ width: "auto" }}
                  />
                  {option.label}
                </label>
              ))}
            </div>
          </div>
          <div>
            <label>Price</label>
            <input type="number" step="0.01" value={formData.price} onChange={(e) => setFormData((prev) => ({ ...prev, price: e.target.value }))} required />
          </div>
          <div>
            <label>Blok</label>
            <input value={formData.block} onChange={(e) => setFormData((prev) => ({ ...prev, block: e.target.value }))} required />
          </div>
          <div>
            <label>No.</label>
            <input value={formData.unit_no} onChange={(e) => setFormData((prev) => ({ ...prev, unit_no: e.target.value }))} required />
          </div>
          <div>
            <label>Width</label>
            <input type="number" step="0.01" value={formData.width} onChange={(e) => setFormData((prev) => ({ ...prev, width: e.target.value }))} required />
          </div>
          <div>
            <label>Length</label>
            <input type="number" step="0.01" value={formData.length} onChange={(e) => setFormData((prev) => ({ ...prev, length: e.target.value }))} required />
          </div>
          <div>
            <label>Floors</label>
            <input type="number" min="1" value={formData.floors} onChange={(e) => setFormData((prev) => ({ ...prev, floors: e.target.value }))} required />
          </div>
          <div>
            <label>Area</label>
            <select
              value={formData.area}
              onChange={(e) => setFormData((prev) => ({ ...prev, area: e.target.value }))}
              required
            >
              {(areaOptionsByPropertyType[formData.property_type] || []).map((areaOption) => (
                <option key={areaOption} value={areaOption}>
                  {areaOption}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label>Owner WhatsApp</label>
            <input value={formData.owner_whatsapp_number} onChange={(e) => setFormData((prev) => ({ ...prev, owner_whatsapp_number: e.target.value }))} required />
          </div>
          <div style={{ gridColumn: "1 / -1" }}>
            <label>Description</label>
            <textarea rows="2" value={formData.description} onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}></textarea>
          </div>
          <div>
            <button type="submit">Save Property</button>
          </div>
        </form>
      </section>

      <section className="panel">
        <h2>Filter & Sort (10 properties per page)</h2>
        <div className="grid columns-4">
          <div>
            <label>Type</label>
            <select
              value={filters.property_type}
              onChange={(e) => setFilters((prev) => ({
                ...prev,
                property_type: e.target.value,
                area: "",
              }))}
            >
              <option value="">All</option>
              {propertyTypeOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
          </div>
          <div>
            <label>Listing Mode</label>
            <select value={filters.listing_mode} onChange={(e) => setFilters((prev) => ({ ...prev, listing_mode: e.target.value }))}>
              <option value="">All</option>
              {listingModeOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
          </div>
          <div>
            <label>Area</label>
            <select value={filters.area} onChange={(e) => setFilters((prev) => ({ ...prev, area: e.target.value }))}>
              <option value="">All</option>
              {getFilterAreaOptions().map((areaOption) => (
                <option key={areaOption} value={areaOption}>
                  {areaOption}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label>Sort</label>
            <select value={filters.sort} onChange={(e) => setFilters((prev) => ({ ...prev, sort: e.target.value }))}>
              {sortOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
          </div>
          <div>
            <label>Min Price</label>
            <input type="number" step="0.01" value={filters.min_price} onChange={(e) => setFilters((prev) => ({ ...prev, min_price: e.target.value }))} />
          </div>
          <div>
            <label>Max Price</label>
            <input type="number" step="0.01" value={filters.max_price} onChange={(e) => setFilters((prev) => ({ ...prev, max_price: e.target.value }))} />
          </div>
          <div className="actions-inline">
            <button className="light" type="button" onClick={() => {
              setFilters({
                property_type: "",
                listing_mode: "",
                area: "",
                min_price: "",
                max_price: "",
                sort: "-created_at",
              });
              setPage(1);
            }}>
              Reset
            </button>
            <button type="button" onClick={() => fetchProperties(1)}>Apply</button>
          </div>
        </div>
      </section>

      {errorMessage && <p className="status-error">{errorMessage}</p>}
      {statusMessage && <p className="status-success">{statusMessage}</p>}

      <section className="panel">
        <h2>Property Inventory</h2>
        {loading && <p className="muted">Loading...</p>}
        {!loading && properties.length === 0 && <p className="muted">No properties found.</p>}
        <div className="grid columns-3">
          {properties.map((property) => {
            const ownerWhatsappLink = buildOwnerWhatsappLink(property);
            return (
            <article key={property.id} className="property-card">
              <div className="property-header">
                <h3>Unit: {property.unit}</h3>
                <span>{property.property_type_label}</span>
              </div>
              <p className="property-meta">
                {property.listing_mode_label} | Price: Rp {property.price}<br />
                Size: {property.width} x {property.length} | Floors: {property.floors}<br />
                Area: {property.area} | Blok: {property.block} | No.: {property.unit_no}<br />
                Owner WA: {property.owner_whatsapp_number}
              </p>
              <div className="actions-inline" style={{ marginBottom: "10px" }}>
                <a href={property.property_page_url} target="_blank" rel="noreferrer">
                  <button type="button" className="light">Open Property Page</button>
                </a>
                <a href={property.download_photos_url} target="_blank" rel="noreferrer">
                  <button type="button" className="secondary">Download Photos (.zip)</button>
                </a>
              </div>
              {ownerWhatsappLink ? (
                <div className="actions-inline">
                  <a href={ownerWhatsappLink} target="_blank" rel="noreferrer">
                    <button type="button">Contact Owner via WhatsApp</button>
                  </a>
                  <a href={buildClientWhatsappShareLink(property)} target="_blank" rel="noreferrer">
                    <button type="button" className="light">Share Property Page to Client</button>
                  </a>
                </div>
              ) : (
                <p className="muted">Owner WhatsApp number is not valid.</p>
              )}
              <div className="photo-row">
                {property.photos.map((photo) => (
                  <div className="photo-item" key={photo.id}>
                    <img src={photo.image_url} alt={`Property ${property.id} photo ${photo.id}`} />
                    <button className="danger" type="button" onClick={() => deletePhoto(photo.id)}>
                      Delete
                    </button>
                  </div>
                ))}
              </div>
              <div className="grid" style={{ marginTop: "12px" }}>
                <div>
                  <label>Upload Photos</label>
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={(e) => {
                      setUploadFiles((prev) => ({
                        ...prev,
                        [property.id]: Array.from(e.target.files || []),
                      }));
                    }}
                  />
                </div>
                <div className="actions-inline">
                  <button type="button" onClick={() => uploadPropertyPhotos(property.id)}>
                    Upload
                  </button>
                </div>
              </div>
            </article>
            );
          })}
        </div>

        <div className="pagination">
          <button type="button" className="light" disabled={!pagination.has_previous} onClick={() => fetchProperties(page - 1)}>
            Previous
          </button>
          <span className="muted">
            Page {pagination.page} / {pagination.num_pages} (Total: {pagination.total_items})
          </span>
          <button type="button" className="light" disabled={!pagination.has_next} onClick={() => fetchProperties(page + 1)}>
            Next
          </button>
        </div>
      </section>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("inventory-root"));
root.render(<InventoryApp />);
