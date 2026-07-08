"use client";

import { useState } from "react";

/**
 * JobDescriptionForm — Structured input form for job descriptions.
 *
 * Converts structured fields (title, description, responsibilities, etc.)
 * into a natural-language job description payload for the backend agent.
 *
 * This is a STUB — the frontend engineer will wire form submission to
 * the Zustand store and the /api/chat SSE endpoint.
 *
 * SAD v2 §3.3.1: "Structured <Form> with <Input>, <Textarea>, <Select> fields
 * that convert structured input into a natural-language job description."
 */

interface JobDescription {
  title: string;
  description: string;
  responsibilities: string[];
  qualifications: string[];
  preferred_qualifications: string[];
  perks: string[];
}

export function JobDescriptionForm() {
  const [jd, setJd] = useState<JobDescription>({
    title: "",
    description: "",
    responsibilities: [""],
    qualifications: [""],
    preferred_qualifications: [""],
    perks: [""],
  });

  const updateField = (field: keyof JobDescription, value: string | string[]) => {
    setJd((prev) => ({ ...prev, [field]: value }));
  };

  const updateListItem = (
    field: "responsibilities" | "qualifications" | "preferred_qualifications" | "perks",
    index: number,
    value: string
  ) => {
    const items = [...jd[field]];
    items[index] = value;
    updateField(field, items);
  };

  const addListItem = (field: "responsibilities" | "qualifications" | "preferred_qualifications" | "perks") => {
    updateField(field, [...jd[field], ""]);
  };

  const removeListItem = (
    field: "responsibilities" | "qualifications" | "preferred_qualifications" | "perks",
    index: number
  ) => {
    const items = jd[field].filter((_, i) => i !== index);
    updateField(field, items.length ? items : [""]);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Wire to Zustand store and trigger /api/chat SSE stream
    console.log("Submitting job description:", jd);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white border border-border rounded-lg p-4 space-y-4">
      <h2 className="text-sm font-semibold text-foreground">Job Description</h2>

      {/* Title */}
      <div>
        <label className="block text-xs font-medium text-muted-foreground mb-1">
          Job Title *
        </label>
        <input
          type="text"
          value={jd.title}
          onChange={(e) => updateField("title", e.target.value)}
          placeholder="e.g., Senior Python Developer"
          className="w-full px-3 py-2 text-sm border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          required
        />
      </div>

      {/* Description */}
      <div>
        <label className="block text-xs font-medium text-muted-foreground mb-1">
          Job Description * (min. 100 chars)
        </label>
        <textarea
          value={jd.description}
          onChange={(e) => updateField("description", e.target.value)}
          placeholder="Describe the role, team, and company..."
          rows={4}
          className="w-full px-3 py-2 text-sm border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
          required
        />
        <span className="text-xs text-muted-foreground">{jd.description.length} chars</span>
      </div>

      {/* Responsibilities */}
      <div>
        <label className="block text-xs font-medium text-muted-foreground mb-1">
          Key Responsibilities * (min. 3)
        </label>
        {jd.responsibilities.map((item, i) => (
          <div key={i} className="flex gap-2 mb-1">
            <input
              type="text"
              value={item}
              onChange={(e) => updateListItem("responsibilities", i, e.target.value)}
              placeholder={`Responsibility ${i + 1}`}
              className="flex-1 px-3 py-1.5 text-sm border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            {jd.responsibilities.length > 1 && (
              <button
                type="button"
                onClick={() => removeListItem("responsibilities", i)}
                className="text-xs text-red-500 hover:text-red-700 px-1"
              >
                ✕
              </button>
            )}
          </div>
        ))}
        <button
          type="button"
          onClick={() => addListItem("responsibilities")}
          className="text-xs text-primary-600 hover:text-primary-800"
        >
          + Add responsibility
        </button>
      </div>

      {/* Qualifications */}
      <div>
        <label className="block text-xs font-medium text-muted-foreground mb-1">
          Required Qualifications * (min. 3)
        </label>
        {jd.qualifications.map((item, i) => (
          <div key={i} className="flex gap-2 mb-1">
            <input
              type="text"
              value={item}
              onChange={(e) => updateListItem("qualifications", i, e.target.value)}
              placeholder={`Qualification ${i + 1}`}
              className="flex-1 px-3 py-1.5 text-sm border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            {jd.qualifications.length > 1 && (
              <button
                type="button"
                onClick={() => removeListItem("qualifications", i)}
                className="text-xs text-red-500 hover:text-red-700 px-1"
              >
                ✕
              </button>
            )}
          </div>
        ))}
        <button
          type="button"
          onClick={() => addListItem("qualifications")}
          className="text-xs text-primary-600 hover:text-primary-800"
        >
          + Add qualification
        </button>
      </div>

      {/* Submit */}
      <button
        type="submit"
        className="w-full bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium py-2 px-4 rounded-md transition-colors"
      >
        Start Recruitment Workflow
      </button>
    </form>
  );
}
