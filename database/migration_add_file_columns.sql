-- =========================================
-- Migration: Add File Upload Columns to teacher_materials
-- Date: 2026-01-06
-- Purpose: Support file upload feature for teacher materials
-- =========================================

USE `emotiva_math`;

-- Add new columns for file upload support
ALTER TABLE teacher_materials
  ADD COLUMN file_path VARCHAR(500) NULL COMMENT 'Path to uploaded file' AFTER konten,
  ADD COLUMN file_name VARCHAR(255) NULL COMMENT 'Original filename' AFTER file_path,
  ADD COLUMN file_type VARCHAR(50) NULL COMMENT 'File extension (pdf, doc, etc)' AFTER file_name;

-- Make konten column nullable for backward compatibility
ALTER TABLE teacher_materials
  MODIFY COLUMN konten TEXT NULL COMMENT 'Materi lengkap dari guru (optional if file uploaded)';

-- Create index for file queries
CREATE INDEX idx_file_type ON teacher_materials(file_type);

-- Verify the changes
DESCRIBE teacher_materials;

SELECT 'Migration completed successfully!' as status;
