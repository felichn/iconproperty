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
  owner_whatsapp_number: "",
  description: "",
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
      setFormData({
        ...defaultForm,
        property_type: formData.property_type,
        listing_mode: formData.listing_mode,
        area: (areaOptionsByPropertyType[formData.property_type] || [""])[0],
      });
      setStatusMessage(`Unit "${data.unit}" created successfully.`);
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
        <div>
          <label>Price</label>
          <input
            type="number"
            step="0.01"
            value={formData.price}
            onChange={(e) => setFormData((prev) => ({ ...prev, price: e.target.value }))}
            required
          />
        </div>
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
        <div>
          <label>Floors</label>
          <input
            type="number"
            min="1"
            value={formData.floors}
            onChange={(e) => setFormData((prev) => ({ ...prev, floors: e.target.value }))}
            required
          />
        </div>
        <div>
          <label>Owner WhatsApp</label>
          <input
            value={formData.owner_whatsapp_number}
            onChange={(e) => setFormData((prev) => ({ ...prev, owner_whatsapp_number: e.target.value }))}
            required
          />
        </div>
        <div style={{ gridColumn: "1 / -1" }}>
          <label>Description</label>
          <textarea
            rows="3"
            value={formData.description}
            onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
          />
        </div>
        <div style={{ gridColumn: "1 / -1" }}>
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
        <div className="actions-inline">
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
