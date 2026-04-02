"use client";
import React, { useState, useEffect, createContext, useContext } from "react";
import { createPortal } from "react-dom";
import { IconX } from "@tabler/icons-react";

const Modal = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="w-screen h-screen fixed z-40 bg-background/10 backdrop-blur-[2px] top-0 left-0 flex items-center justify-center">
      {children}
    </div>
  );
};

export default Modal;

interface DialogContextType {
  open: boolean;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

const DialogContext = createContext<DialogContextType | undefined>(undefined);

export const ModalDialog = ({ children }: { children: React.ReactNode }) => {
  const [open, setOpen] = useState(false);
  return (
    <DialogContext.Provider value={{ open, setOpen }}>
      {children}
    </DialogContext.Provider>
  );
};

export const ModalTrigger = ({ children }: { children: React.ReactNode }) => {
  const ctx = useContext(DialogContext);
  if (!ctx) throw new Error("UploadTrigger must be used within UploadDialog");

  return <span onClick={() => ctx.setOpen(true)}>{children}</span>;
};

export const ModalContent = ({ children }: { children: React.ReactNode }) => {
  const ctx = useContext(DialogContext);
  if (!ctx) throw new Error("UploadContent must be used within UploadDialog");

  const { open, setOpen } = ctx;

  // ✅ Track if component is mounted to avoid SSR mismatch
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  // ✅ Close on Escape key
  useEffect(() => {
    if (!open) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, setOpen]);

  // Nothing rendered until after hydration
  if (!mounted || !open) return null;

  return createPortal(
    <div className="w-screen h-screen fixed z-[9999] bg-background/10 backdrop-blur-[2px] top-0 left-0 flex items-center justify-center ">
      <button
        onClick={() => setOpen(false)}
        className="absolute top-3 right-3 p-1 rounded-full hover:bg-accent transition cursor-pointer"
        aria-label="Close upload dialog"
      >
        <IconX className="w-8 h-8" />
      </button>
      {children}
    </div>,
    document.body
  );
};
