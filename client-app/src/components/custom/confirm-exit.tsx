"use client";
import React, { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { IconX } from "@tabler/icons-react";

/**
 * Controlled modal — doesn't rely on context.
 * Usage: <ConfirmExitModal open={open} onClose={...} onConfirm={...} />
 */
export function ConfirmExitModal({
  open,
  onClose,
  onConfirm,
}: {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
}) {
  const [mounted, setMounted] = useState(false);

  // ensure portal only renders after hydration
  useEffect(() => setMounted(true), []);

  // close on Escape
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!mounted || !open) return null;

  return createPortal(
    <div
      className="w-screen h-screen fixed z-[9999] top-0 left-0 flex items-center justify-center bg-background/10 backdrop-blur-[2px]"
      onMouseDown={(e) => {
        // click on backdrop to close (but not when clicking inside modal)
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="relative bg-card rounded-xl p-6 shadow-lg w-[92%] max-w-sm">
        <button
          onClick={onClose}
          className="absolute top-3 right-3 p-1 rounded-full hover:bg-accent transition"
          aria-label="Close"
        >
          <IconX className="w-6 h-6" />
        </button>

        <h2 className="text-lg font-semibold mb-2">Discard changes?</h2>
        <p className="text-sm text-muted-foreground mb-4">
          You have unsaved changes. If you leave, all changes will be lost.
        </p>

        <div className="flex justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="px-3 py-2 rounded-md bg-muted text-sm"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className="px-3 py-2 rounded-md bg-destructive text-sm text-white"
          >
            Discard
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}
