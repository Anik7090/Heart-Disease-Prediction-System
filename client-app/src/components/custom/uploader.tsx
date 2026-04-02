"use client";
import React, { useState, useRef } from "react";
import Modal from "./modal";
import { IconUpload, IconX } from "@tabler/icons-react";
import { useDropzone } from "react-dropzone";
import { motion } from "motion/react";
import { cn } from "@/lib/utils";

export const UploadBox = ({
  onChange,
}: {
  onChange?: (file: File | null) => void;
}) => {
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (newFiles: File[]) => {
    const firstFile = newFiles[0] || null;
    setFile(firstFile);
    onChange?.(firstFile);
  };

  const { getRootProps, isDragActive } = useDropzone({
    multiple: false, // single file only
    noClick: true,
    onDrop: handleFileChange,
    onDropRejected: (err) => console.log(err),
  });

  const handleClick = () => fileInputRef.current?.click();

  return (
    <div className="w-full max-w-3xl mx-auto p-4">
      {/* Upload Zone */}
      <div
        {...getRootProps()}
        onClick={handleClick}
        className={cn(
          "relative border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center cursor-pointer transition",
          isDragActive
            ? "border-accent bg-accent/10"
            : "border-muted-foreground/30 hover:border-accent"
        )}
      >
        <input
          ref={fileInputRef}
          type="file"
          onChange={(e) => handleFileChange(Array.from(e.target.files || []))}
          className="hidden"
        />
        <IconUpload className="h-10 w-10 text-muted-foreground mb-3" />
        <p className="font-semibold text-neutral-700 dark:text-neutral-200">
          {isDragActive
            ? "Drop your file here"
            : "Click or drag a file to upload"}
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          Supported: mkv, mp4, avi, 3gp
        </p>
      </div>

      {/* File Preview */}
      {file && (
        <motion.div
          key={file.name}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative flex flex-col rounded-lg border bg-card shadow-sm p-4 mt-6"
        >
          {/* Remove Button */}
          <button
            className="absolute top-2 right-2 text-muted-foreground hover:text-red-500"
            onClick={() => {
              setFile(null);
              onChange?.(null);
            }}
          >
            <IconX className="h-4 w-4" />
          </button>

          {/* File Info */}
          <p className="font-medium text-sm truncate">{file.name}</p>
          <p className="text-xs text-muted-foreground mt-1">
            {(file.size / (1024 * 1024)).toFixed(2)} MB
          </p>

          <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
            <span className="px-2 py-0.5 bg-muted rounded-md">
              {file.type || "unknown"}
            </span>
            <span>{new Date(file.lastModified).toLocaleDateString()}</span>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export const UploadIcon = ({ className }: { className?: string }) => {
  const [isOpen, setOpen] = useState<boolean>(false);
  const toggleOpen = () => setOpen(!isOpen);

  return (
    <>
      <IconUpload onClick={toggleOpen} className={cn(className)} />
      {isOpen && (
        <Modal>
          <span className="w-max h-max p-2 absolute top-10 right-10">
            <IconX onClick={() => setOpen(false)} />
          </span>
          <UploadBox />
        </Modal>
      )}
    </>
  );
};

export const UploadProvider = ({
  children,
  onChange,
  className,
}: {
  children: React.ReactNode;
  onChange: (file: File) => void;
  className?: string;
}) => {
  const [file, setFile] = useState<File>();
  const fileInputRef = useRef<HTMLInputElement>(null);
  console.log(file);

  const handleFileChange = (newFiles: File[]) => {
    const firstFile = newFiles[0];
    if (!firstFile) return;
    setFile(firstFile);
    onChange(firstFile);
  };

  const { getRootProps, isDragActive } = useDropzone({
    multiple: false, // single file only
    noClick: true,
    onDrop: handleFileChange,
    onDropRejected: (err) => console.log(err),
  });

  const handleClick = () => fileInputRef.current?.click();

  return (
    <div
      {...getRootProps()}
      onClick={handleClick}
      className={cn(
        "relative border border-dashed rounded-sm grid place-items-center cursor-pointer transition",
        className,
        isDragActive
          ? "border-accent bg-accent/10"
          : "border-muted-foreground/30 hover:border-accent"
      )}
    >
      <input
        ref={fileInputRef}
        type="file"
        onChange={(e) => handleFileChange(Array.from(e.target.files || []))}
        className="hidden"
      />
      {children}
    </div>
  );
};
