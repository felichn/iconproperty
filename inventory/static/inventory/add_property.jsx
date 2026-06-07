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
  width: "",
  length: "",
  floors: 1,
  area: "Villa Pasir Putih",
  owner_whatsapp_number: "+62",
};

function AddPropertyApp() {
  const [formData, setFormData] = useState(defaultForm);
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

  function formatContactValue(rawValue) {
    if (!rawValue) {
      return "+62";
    }
    if (rawValue.startsWith("+62")) {
      return rawValue;
    }
    const trimmed = rawValue.replace(/^\+/, "");
    if (trimmed.startsWith("62")) {
      return `+${trimmed}`;
    }
    return `+62${trimmed}`;
  }

  async function createProperty(event) {
    event.preventDefault();
    setErrorMessage("");
    setStatusMessage("");
    setSaving(true);
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
      const areaOptions = areaOptionsByPropertyType[formData.property_type] || [""];
      setFormData({
        ...defaultForm,
        property_type: formData.property_type,
        listing_mode: formData.listing_mode,
        area: areaOptions[0],
      });
      setStatusMessage(`Unit "${data.unit}" created successfully.`);
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="card shadow-sm border-0">
      <div className="card-body p-4">
        <p className="text-muted mb-4">Lengkapi data unit properti.</p>
        <form onSubmit={createProperty}>
          <div className="row g-3">
            <div className="col-md-3">
              <label className="form-label">Type</label>
              <select
                className="form-select"
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

            <div className="col-md-3">
              <label className="form-label">Area</label>
              <select
                className="form-select"
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

            <div className="col-md-3">
              <label className="form-label">Blok</label>
              <input
                className="form-control"
                value={formData.block}
                onChange={(e) => setFormData((prev) => ({ ...prev, block: e.target.value }))}
                placeholder="Contoh: 1, F, C2"
                required
              />
            </div>

            <div className="col-md-3">
              <label className="form-label">No.</label>
              <input
                className="form-control"
                value={formData.unit_no}
                onChange={(e) => setFormData((prev) => ({ ...prev, unit_no: e.target.value }))}
                placeholder="Contoh: 38"
                required
              />
            </div>

            <div className="col-md-4">
              <label className="form-label d-block">Rent or Sell</label>
              <div className="d-flex gap-3 pt-1">
                {listingModeOptions.map((option) => (
                  <div className="form-check" key={option.value}>
                    <input
                      className="form-check-input"
                      type="radio"
                      name="listing_mode"
                      value={option.value}
                      id={`listing-mode-${option.value}`}
                      checked={formData.listing_mode === option.value}
                      onChange={(e) => setFormData((prev) => ({ ...prev, listing_mode: e.target.value }))}
                    />
                    <label className="form-check-label" htmlFor={`listing-mode-${option.value}`}>
                      {option.label}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            <div className="col-md-4">
              <label className="form-label">Harga</label>
              <input
                className="form-control"
                type="number"
                step="0.01"
                value={formData.price}
                onChange={(e) => setFormData((prev) => ({ ...prev, price: e.target.value }))}
                placeholder="Contoh: 2500000000"
                required
              />
            </div>

            <div className="col-md-4">
              <label className="form-label">Lantai</label>
              <input
                className="form-control"
                type="number"
                min="1"
                value={formData.floors}
                onChange={(e) => setFormData((prev) => ({ ...prev, floors: e.target.value }))}
                required
              />
            </div>

            <div className="col-md-6">
              <label className="form-label">Width</label>
              <input
                className="form-control"
                type="number"
                step="0.01"
                value={formData.width}
                onChange={(e) => setFormData((prev) => ({ ...prev, width: e.target.value }))}
                required
              />
            </div>

            <div className="col-md-6">
              <label className="form-label">Length</label>
              <input
                className="form-control"
                type="number"
                step="0.01"
                value={formData.length}
                onChange={(e) => setFormData((prev) => ({ ...prev, length: e.target.value }))}
                required
              />
            </div>

            <div className="col-md-6">
              <label className="form-label">Contact</label>
              <input
                className="form-control"
                value={formData.owner_whatsapp_number}
                onChange={(e) => setFormData((prev) => ({
                  ...prev,
                  owner_whatsapp_number: formatContactValue(e.target.value),
                }))}
                placeholder="+628123456789"
                required
              />
            </div>
          </div>

          <div className="d-flex flex-wrap gap-2 mt-4">
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? "Saving..." : "Save Property"}
            </button>
            <button type="button" className="btn btn-outline-secondary" onClick={() => window.location.assign("/")}>
              Go to Property Inventory
            </button>
          </div>
        </form>

        {errorMessage && <div className="alert alert-danger mt-3 mb-0">{errorMessage}</div>}
        {statusMessage && <div className="alert alert-success mt-3 mb-0">{statusMessage}</div>}
      </div>
    </section>
  );
}

const root = ReactDOM.createRoot(document.getElementById("add-property-root"));
root.render(<AddPropertyApp />);
