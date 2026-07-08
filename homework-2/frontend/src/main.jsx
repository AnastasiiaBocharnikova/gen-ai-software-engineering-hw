import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  AlertCircle,
  CheckCircle2,
  Edit3,
  Filter,
  ListRestart,
  Plus,
  RefreshCw,
  Sparkles,
  Upload,
} from "lucide-react";
import "./styles.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:3000";

const emptyForm = {
  customer_id: "",
  customer_email: "",
  customer_name: "",
  subject: "",
  description: "",
  category: "other",
  priority: "medium",
  status: "new",
  assigned_to: "",
  tags: "",
  metadata_source: "web_form",
  metadata_browser: "",
  metadata_device_type: "desktop",
};

const categories = [
  "account_access",
  "technical_issue",
  "billing_question",
  "feature_request",
  "bug_report",
  "other",
];
const priorities = ["urgent", "high", "medium", "low"];
const statuses = ["new", "in_progress", "waiting_customer", "resolved", "closed"];
const sources = ["web_form", "email", "api", "chat", "phone"];
const devices = ["desktop", "mobile", "tablet"];

function App() {
  const [tickets, setTickets] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [filters, setFilters] = useState({ category: "", priority: "", status: "" });
  const [form, setForm] = useState(emptyForm);
  const [mode, setMode] = useState("create");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [importFormat, setImportFormat] = useState("csv");
  const [importFile, setImportFile] = useState(null);
  const [autoClassifyImport, setAutoClassifyImport] = useState(true);

  const selectedTicket = tickets.find((ticket) => ticket.id === selectedId) || null;

  const query = useMemo(() => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });
    return params.toString();
  }, [filters]);

  async function request(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, options);
    if (response.status === 204) return null;
    const data = await response.json();
    if (!response.ok) {
      const detail = data.detail ? JSON.stringify(data.detail) : data.message;
      throw new Error(detail || "Request failed");
    }
    return data;
  }

  async function loadTickets() {
    setLoading(true);
    try {
      const data = await request(`/tickets${query ? `?${query}` : ""}`);
      setTickets(data);
      if (selectedId && !data.some((ticket) => ticket.id === selectedId)) {
        setSelectedId(data[0]?.id || null);
      }
      setMessage(null);
    } catch (error) {
      setMessage({ type: "error", text: error.message });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTickets();
  }, [query]);

  function updateForm(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function ticketPayload() {
    return {
      customer_id: form.customer_id.trim(),
      customer_email: form.customer_email.trim(),
      customer_name: form.customer_name.trim(),
      subject: form.subject.trim(),
      description: form.description.trim(),
      category: form.category,
      priority: form.priority,
      status: form.status,
      assigned_to: form.assigned_to.trim() || null,
      tags: form.tags
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean),
      metadata: {
        source: form.metadata_source,
        browser: form.metadata_browser.trim(),
        device_type: form.metadata_device_type,
      },
    };
  }

  function validateForm() {
    if (!form.customer_id.trim()) return "Customer ID is required.";
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.customer_email)) {
      return "Customer email must be valid.";
    }
    if (!form.customer_name.trim()) return "Customer name is required.";
    if (!form.subject.trim() || form.subject.length > 200) {
      return "Subject must be 1-200 characters.";
    }
    if (form.description.length < 10 || form.description.length > 2000) {
      return "Description must be 10-2000 characters.";
    }
    return null;
  }

  async function submitTicket(event) {
    event.preventDefault();
    const validationError = validateForm();
    if (validationError) {
      setMessage({ type: "error", text: validationError });
      return;
    }

    try {
      const payload = ticketPayload();
      const saved =
        mode === "edit" && selectedTicket
          ? await request(`/tickets/${selectedTicket.id}`, {
              method: "PUT",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload),
            })
          : await request("/tickets", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload),
            });
      setSelectedId(saved.id);
      setMode("edit");
      setMessage({ type: "success", text: mode === "edit" ? "Ticket updated." : "Ticket created." });
      await loadTickets();
    } catch (error) {
      setMessage({ type: "error", text: error.message });
    }
  }

  function startCreate() {
    setMode("create");
    setForm(emptyForm);
    setSelectedId(null);
  }

  function startEdit(ticket) {
    setMode("edit");
    setSelectedId(ticket.id);
    setForm({
      customer_id: ticket.customer_id,
      customer_email: ticket.customer_email,
      customer_name: ticket.customer_name,
      subject: ticket.subject,
      description: ticket.description,
      category: ticket.category,
      priority: ticket.priority,
      status: ticket.status,
      assigned_to: ticket.assigned_to || "",
      tags: ticket.tags.join(", "),
      metadata_source: ticket.metadata.source,
      metadata_browser: ticket.metadata.browser,
      metadata_device_type: ticket.metadata.device_type,
    });
  }

  async function classifyTicket() {
    if (!selectedTicket) return;
    try {
      const result = await request(`/tickets/${selectedTicket.id}/auto-classify`, {
        method: "POST",
      });
      setMessage({
        type: "success",
        text: `Classified as ${label(result.category)} with ${result.priority} priority.`,
      });
      await loadTickets();
    } catch (error) {
      setMessage({ type: "error", text: error.message });
    }
  }

  async function deleteTicket() {
    if (!selectedTicket) return;
    try {
      await request(`/tickets/${selectedTicket.id}`, { method: "DELETE" });
      setSelectedId(null);
      setMode("create");
      setForm(emptyForm);
      setMessage({ type: "success", text: "Ticket deleted." });
      await loadTickets();
    } catch (error) {
      setMessage({ type: "error", text: error.message });
    }
  }

  async function importTickets(event) {
    event.preventDefault();
    if (!importFile) {
      setMessage({ type: "error", text: "Choose a CSV, JSON, or XML file." });
      return;
    }

    const data = new FormData();
    data.append("file", importFile);
    try {
      const summary = await request(
        `/tickets/import?format=${importFormat}&auto_classify=${autoClassifyImport}`,
        { method: "POST", body: data },
      );
      setMessage({
        type: summary.failed ? "error" : "success",
        text: `Import finished: ${summary.successful} created, ${summary.failed} failed.`,
      });
      await loadTickets();
    } catch (error) {
      setMessage({ type: "error", text: error.message });
    }
  }

  return (
    <main className="app-shell">
      <section className="topbar">
        <div>
          <p className="eyebrow">Agent workspace</p>
          <h1>Support Tickets</h1>
        </div>
        <div className="topbar-actions">
          <button type="button" className="icon-button" onClick={loadTickets} title="Refresh tickets">
            <RefreshCw size={18} />
          </button>
          <button type="button" className="primary-action" onClick={startCreate}>
            <Plus size={18} />
            New ticket
          </button>
        </div>
      </section>

      {message && (
        <div className={`notice ${message.type}`}>
          {message.type === "success" ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
          <span>{message.text}</span>
        </div>
      )}

      <section className="workspace">
        <aside className="ticket-panel">
          <div className="panel-header">
            <div>
              <h2>Queue</h2>
              <p>{loading ? "Loading..." : `${tickets.length} ticket${tickets.length === 1 ? "" : "s"}`}</p>
            </div>
            <Filter size={18} />
          </div>

          <div className="filters">
            <Select label="Category" value={filters.category} onChange={(value) => setFilters({ ...filters, category: value })} options={categories} allowAll />
            <Select label="Priority" value={filters.priority} onChange={(value) => setFilters({ ...filters, priority: value })} options={priorities} allowAll />
            <Select label="Status" value={filters.status} onChange={(value) => setFilters({ ...filters, status: value })} options={statuses} allowAll />
            <button type="button" className="secondary-action" onClick={() => setFilters({ category: "", priority: "", status: "" })}>
              <ListRestart size={16} />
              Clear filters
            </button>
          </div>

          <div className="ticket-list">
            {tickets.map((ticket) => (
              <button
                key={ticket.id}
                type="button"
                className={`ticket-row ${ticket.id === selectedId ? "selected" : ""}`}
                onClick={() => startEdit(ticket)}
              >
                <span className={`priority-dot ${ticket.priority}`} />
                <span>
                  <strong>{ticket.subject}</strong>
                  <small>{ticket.customer_email}</small>
                </span>
                <StatusPill status={ticket.status} />
              </button>
            ))}
            {!tickets.length && <p className="empty-state">No tickets match the current filters.</p>}
          </div>
        </aside>

        <section className="detail-panel">
          <div className="detail-grid">
            <TicketForm
              form={form}
              mode={mode}
              onChange={updateForm}
              onSubmit={submitTicket}
            />

            <div className="side-stack">
              <TicketDetail
                ticket={selectedTicket}
                onClassify={classifyTicket}
                onDelete={deleteTicket}
              />
              <ImportPanel
                importFormat={importFormat}
                setImportFormat={setImportFormat}
                setImportFile={setImportFile}
                autoClassifyImport={autoClassifyImport}
                setAutoClassifyImport={setAutoClassifyImport}
                onSubmit={importTickets}
              />
            </div>
          </div>
        </section>
      </section>
    </main>
  );
}

function TicketForm({ form, mode, onChange, onSubmit }) {
  return (
    <form className="form-panel" onSubmit={onSubmit}>
      <div className="panel-header">
        <div>
          <h2>{mode === "edit" ? "Edit ticket" : "Create ticket"}</h2>
          <p>{mode === "edit" ? "Update assignment, status, or content." : "Create a ticket through the API."}</p>
        </div>
        <Edit3 size={18} />
      </div>

      <div className="form-grid">
        <Input label="Customer ID" value={form.customer_id} onChange={(value) => onChange("customer_id", value)} />
        <Input label="Email" type="email" value={form.customer_email} onChange={(value) => onChange("customer_email", value)} />
        <Input label="Name" value={form.customer_name} onChange={(value) => onChange("customer_name", value)} />
        <Input label="Assigned to" value={form.assigned_to} onChange={(value) => onChange("assigned_to", value)} />
        <Input className="wide" label="Subject" value={form.subject} maxLength={200} onChange={(value) => onChange("subject", value)} />
        <label className="field wide">
          <span>Description</span>
          <textarea value={form.description} minLength={10} maxLength={2000} onChange={(event) => onChange("description", event.target.value)} />
        </label>
        <Select label="Category" value={form.category} onChange={(value) => onChange("category", value)} options={categories} />
        <Select label="Priority" value={form.priority} onChange={(value) => onChange("priority", value)} options={priorities} />
        <Select label="Status" value={form.status} onChange={(value) => onChange("status", value)} options={statuses} />
        <Select label="Source" value={form.metadata_source} onChange={(value) => onChange("metadata_source", value)} options={sources} />
        <Input label="Browser" value={form.metadata_browser} onChange={(value) => onChange("metadata_browser", value)} />
        <Select label="Device" value={form.metadata_device_type} onChange={(value) => onChange("metadata_device_type", value)} options={devices} />
        <Input className="wide" label="Tags" value={form.tags} onChange={(value) => onChange("tags", value)} />
      </div>

      <button type="submit" className="primary-action full-width">
        <CheckCircle2 size={18} />
        {mode === "edit" ? "Save changes" : "Create ticket"}
      </button>
    </form>
  );
}

function TicketDetail({ ticket, onClassify, onDelete }) {
  if (!ticket) {
    return (
      <section className="info-panel">
        <h2>Ticket details</h2>
        <p className="empty-state">Select a ticket to inspect classification, metadata, and timestamps.</p>
      </section>
    );
  }

  return (
    <section className="info-panel">
      <div className="panel-header">
        <div>
          <h2>Ticket details</h2>
          <p>{ticket.id}</p>
        </div>
        <StatusPill status={ticket.status} />
      </div>
      <dl className="facts">
        <div><dt>Customer</dt><dd>{ticket.customer_name}</dd></div>
        <div><dt>Category</dt><dd>{label(ticket.category)}</dd></div>
        <div><dt>Priority</dt><dd>{label(ticket.priority)}</dd></div>
        <div><dt>Source</dt><dd>{label(ticket.metadata.source)}</dd></div>
        <div><dt>Device</dt><dd>{label(ticket.metadata.device_type)}</dd></div>
        <div><dt>Confidence</dt><dd>{ticket.classification_confidence ?? "Not classified"}</dd></div>
      </dl>
      {ticket.classification_reasoning && <p className="reasoning">{ticket.classification_reasoning}</p>}
      <div className="button-row">
        <button type="button" className="secondary-action" onClick={onClassify}>
          <Sparkles size={16} />
          Auto-classify
        </button>
        <button type="button" className="danger-action" onClick={onDelete}>Delete</button>
      </div>
    </section>
  );
}

function ImportPanel({ importFormat, setImportFormat, setImportFile, autoClassifyImport, setAutoClassifyImport, onSubmit }) {
  return (
    <form className="info-panel" onSubmit={onSubmit}>
      <div className="panel-header">
        <div>
          <h2>Bulk import</h2>
          <p>Upload CSV, JSON, or XML tickets.</p>
        </div>
        <Upload size={18} />
      </div>
      <Select label="Format" value={importFormat} onChange={setImportFormat} options={["csv", "json", "xml"]} />
      <label className="field">
        <span>File</span>
        <input type="file" accept=".csv,.json,.xml" onChange={(event) => setImportFile(event.target.files[0] || null)} />
      </label>
      <label className="toggle-row">
        <input type="checkbox" checked={autoClassifyImport} onChange={(event) => setAutoClassifyImport(event.target.checked)} />
        <span>Auto-classify imported tickets</span>
      </label>
      <button type="submit" className="secondary-action full-width">
        <Upload size={16} />
        Import tickets
      </button>
    </form>
  );
}

function Input({ label: fieldLabel, value, onChange, type = "text", className = "", ...props }) {
  return (
    <label className={`field ${className}`}>
      <span>{fieldLabel}</span>
      <input type={type} value={value} onChange={(event) => onChange(event.target.value)} {...props} />
    </label>
  );
}

function Select({ label: fieldLabel, value, onChange, options, allowAll = false }) {
  return (
    <label className="field">
      <span>{fieldLabel}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {allowAll && <option value="">All</option>}
        {options.map((option) => (
          <option key={option} value={option}>{label(option)}</option>
        ))}
      </select>
    </label>
  );
}

function StatusPill({ status }) {
  return <span className={`status-pill ${status}`}>{label(status)}</span>;
}

function label(value) {
  return String(value).replaceAll("_", " ");
}

createRoot(document.getElementById("root")).render(<App />);
