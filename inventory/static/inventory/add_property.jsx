const { useState } = React;

const areaOptionsByPropertyType = {
  rumah: ["Villa Pasir Putih"],
  gudang: ["Bizpark"],
  ruko: ["Hollywood", "Manhattan", "Broadway"],
};

const defaultForm = {
  property_type: "rumah",
  listing_mode: "sell",
  block: "",
  unit_no: "",
  price: "",
  price_unit: "juta",
  width: "",
  length: "",
  floors: 1,
  area: "Villa Pasir Putih",
  owner_whatsapp_number: "+62",
};

function expandPriceValue(amount, unit) {
  const normalizedAmount = String(amount).trim().replace(/,/g, ".");
  if (!normalizedAmount || Number(normalizedAmount) <= 0) {
    throw new Error("Harga is required.");
  }

  const [rawWholePart, decimalPart = ""] = normalizedAmount.split(".");
  const wholePart = rawWholePart || "0";
  if (!/^\d+$/.test(wholePart) || (decimalPart && !/^\d+$/.test(decimalPart))) {
    throw new Error("Harga must be a valid number.");
  }

  const multiplier = unit === "milyar" ? "1000000000" : "1000000";
  const decimals = decimalPart.length;
  const combinedDigits = `${wholePart}${decimalPart}`.replace(/^0+(?=\d)/, "");
  const expanded = BigInt(combinedDigits || "0") * BigInt(multiplier);
  const divisor = 10n ** BigInt(decimals);

  return (expanded / divisor).toString();
}

function AddPropertyApp() {
  const [formData, setFormData] = useState(defaultForm);
  const [photos, setPhotos] = useState([]);
  const [statusMessage, setStatusMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [saving, setSaving] = useState(false);

  const propertyTypeOptions = [
    { value: "rumah", label: "Rumah" },
    { value: "ruko", label: "Ruko" },
    { value: "gudang", label: "Gudang" },
  ];

  const listingModeOptions = [
    { value: "sell", label: "Sell" },
    { value: "rent", label: "Rent" },
  ];

  async function createProperty(event) {
    event.preventDefault();
    setErrorMessage("");
    setStatusMessage("");
    setSaving(true);
    try {
      const { price_unit, ...payload } = formData;
      payload.price = expandPriceValue(formData.price, price_unit);

      const response = await fetch("/api/properties/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Failed to create property.");
      }
      if (photos.length > 0) {
        const photoPayload = new FormData();
        photos.forEach((photo) => photoPayload.append("photos", photo));
        const photoResponse = await fetch(`/api/properties/${data.id}/photos/`, {
          method: "POST",
          body: photoPayload,
        });
        const photoData = await photoResponse.json();
        if (!photoResponse.ok) {
          throw new Error(photoData.error || "Property saved, but photos could not be attached.");
        }
      }
      setFormData({
        ...defaultForm,
        property_type: formData.property_type,
        listing_mode: formData.listing_mode,
        area: (areaOptionsByPropertyType[formData.property_type] || [""])[0],
      });
      setPhotos([]);
      event.target.reset();
      const photoMessage = photos.length === 1 ? " with 1 photo" : photos.length > 1 ? ` with ${photos.length} photos` : "";
      setStatusMessage(`Unit "${data.unit}" created successfully${photoMessage}.`);
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="panel">
      <p className="eyebrow">Listing details</p>
      <h2>Property Information</h2>
      <form onSubmit={createProperty} className="property-form">
        <div className="form-row">
          <label>Rent or Sell</label>
          <div className="mode-options">
            {listingModeOptions.map((option) => (
              <label key={option.value} className="mode-option">
                <input
                  type="radio"
                  name="listing_mode"
                  value={option.value}
                  checked={formData.listing_mode === option.value}
                  onChange={(e) => setFormData((prev) => ({ ...prev, listing_mode: e.target.value }))}
                />
                <span>{option.label}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="form-row two-columns">
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
              {propertyTypeOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
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
        </div>

        <div className="form-row two-columns">
          <div>
            <label>Blok</label>
            <input
              value={formData.block}
              onChange={(e) => setFormData((prev) => ({ ...prev, block: e.target.value }))}
              required
            />
          </div>
          <div>
            <label>No.</label>
            <input
              value={formData.unit_no}
              onChange={(e) => setFormData((prev) => ({ ...prev, unit_no: e.target.value }))}
              required
            />
          </div>
        </div>

        <div className="form-row">
          <label>Harga</label>
          <div className="price-input">
            <input
              type="number"
              step="0.01"
              value={formData.price}
              onChange={(e) => setFormData((prev) => ({ ...prev, price: e.target.value }))}
              required
            />
            <select
              aria-label="Harga unit"
              value={formData.price_unit}
              onChange={(e) => setFormData((prev) => ({ ...prev, price_unit: e.target.value }))}
            >
              <option value="juta">Juta</option>
              <option value="milyar">Milyar</option>
            </select>
          </div>
        </div>

        <div className="form-row measurement-row">
          <div>
            <label>Width</label>
            <input
              type="number"
              step="0.01"
              value={formData.width}
              onChange={(e) => setFormData((prev) => ({ ...prev, width: e.target.value }))}
              required
            />
          </div>
          <span aria-hidden="true" className="measurement-separator">x</span>
          <div>
            <label>Length</label>
            <input
              type="number"
              step="0.01"
              value={formData.length}
              onChange={(e) => setFormData((prev) => ({ ...prev, length: e.target.value }))}
              required
            />
          </div>
        </div>

        <div className="form-row">
          <label>Lantai</label>
          <input
            type="number"
            min="1"
            value={formData.floors}
            onChange={(e) => setFormData((prev) => ({ ...prev, floors: e.target.value }))}
            required
          />
        </div>

        <div className="form-row">
          <label>Contact</label>
          <input
            value={formData.owner_whatsapp_number}
            onChange={(e) => setFormData((prev) => ({ ...prev, owner_whatsapp_number: e.target.value }))}
            required
          />
        </div>

        <div className="form-row">
          <label>Photos</label>
          <div className="photo-attach">
            <label className="attach-button" htmlFor="property-photos">Attach Photos</label>
            <input
              id="property-photos"
              type="file"
              accept="image/*"
              multiple
              onChange={(e) => setPhotos(Array.from(e.target.files || []))}
            />
            <span>{photos.length ? `${photos.length} selected` : "No photos selected"}</span>
          </div>
        </div>

        <div className="actions-inline form-actions">
          <button type="submit" disabled={saving}>
            {saving ? "Saving..." : "Save Property"}
          </button>
          <button type="button" className="light" onClick={() => window.location.assign("/inventory/")}>
            Go to Inventory
          </button>
        </div>
      </form>
      {errorMessage && <p className="status-error">{errorMessage}</p>}
      {statusMessage && <p className="status-success">{statusMessage}</p>}
    </section>
  );
}

const root = ReactDOM.createRoot(document.getElementById("add-property-root"));
root.render(<AddPropertyApp />);
